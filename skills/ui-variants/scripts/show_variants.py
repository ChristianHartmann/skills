#!/usr/bin/env python3
"""Builds the variant comparison page, serves it locally and opens the browser.

Usage:
    python3 show_variants.py <dir> [--port 0] [--no-browser]
                                   [--build-only] [--timeout SECONDS]

Expects inside <dir>:
    variants.json       metadata (see below)
    variants/variant-1.html … variant-N.html
    current.png         optional, screenshot of the current state

On submit it writes <dir>/choice.json, prints it and exits. That blocking
behaviour is deliberate: an agent without a background primitive can simply run
this in the foreground and read the answer from the command output.

Why every variant gets its own <iframe>: variants are sketches, not shipped
software. Two of them may use the same class names, set global selectors or
touch `document` without breaking their neighbour. Without that isolation you
end up debugging collisions instead of judging designs.
"""

from __future__ import annotations

import argparse
import json
import re
import sys
import threading
import webbrowser
from datetime import datetime
from http.server import BaseHTTPRequestHandler, HTTPServer
from pathlib import Path

TEMPLATE = Path(__file__).resolve().parent.parent / "assets" / "page-template.html"


def html_escape(text: str) -> str:
    return (
        str(text)
        .replace("&", "&amp;")
        .replace("<", "&lt;")
        .replace(">", "&gt;")
        .replace('"', "&quot;")
    )


def read_css(paths: list[str], base: Path) -> str:
    """Concatenates the application's real stylesheets.

    CSS module files often contain `composes:` or `:global(...)`, neither of
    which works outside the bundler. Both are defused so the file still applies
    in the browser - the colours and measurements that matter for the
    comparison survive that untouched.
    """
    pieces = []
    for entry in paths:
        path = Path(entry)
        if not path.is_absolute():
            path = (base / path).resolve()
        if not path.exists():
            print(f"  ! CSS not found, skipped: {path}", file=sys.stderr)
            continue
        text = path.read_text(encoding="utf-8")
        text = re.sub(r"^\s*composes:[^;]+;\s*$", "", text, flags=re.MULTILINE)
        text = re.sub(r":global\(([^)]*)\)", r"\1", text)
        pieces.append(f"/* ---- {path.name} ---- */\n{text}")
    return "\n\n".join(pieces)


def build_variant_document(raw_html: str, css: str) -> str:
    """Turns a variant body into a complete document for srcdoc.

    The `[hidden]` rule comes after the component CSS on purpose. Toggling a
    state usually means hiding an element that the component stylesheet gives a
    `display` to - and any `display` beats the browser's built-in `[hidden]`
    rule, so the element stays visible. Without this line the collapsed state
    shows both halves at once, and the mistake looks like a bug in the variant.
    """
    return (
        "<!doctype html><html><head><meta charset='utf-8'>"
        "<style>"
        "html,body{margin:0;padding:0;font:15px/1.5 ui-sans-serif,system-ui,sans-serif}"
        f"{css}"
        "[hidden]{display:none!important}"
        "</style></head><body>"
        f"{raw_html}"
        "</body></html>"
    )


def build_page(folder: Path) -> str:
    data = json.loads((folder / "variants.json").read_text(encoding="utf-8"))
    css = read_css(data.get("tokens_css", []) + data.get("extra_css", []), folder)

    sections: list[str] = []
    jump_links: list[str] = []
    buttons: list[str] = []

    # A relative path, not "/current.png": under the server both are the same,
    # but with --build-only the human opens the file via file:// - and there a
    # leading slash points at the filesystem root, leaving the before-image
    # blank. In exactly the mode meant for sessions without a browser.
    current_image = data.get("current_image")
    if current_image and (folder / current_image).exists():
        jump_links.append('<a href="#v0">0 · Current</a>')
        sections.append(
            '<section class="variant" id="v0">'
            '<div class="head"><span class="number current">0</span>'
            "<h2>Current state</h2></div>"
            f'<div class="stage"><img src="{html_escape(current_image)}" alt="Current state"></div>'
            '<div class="thinking"><p>'
            f'{html_escape(data.get("current_note", "This is how it looks today."))}'
            "</p></div></section>"
        )

    for variant in data["variants"]:
        number = variant["number"]
        file = folder / "variants" / f"variant-{number}.html"
        if not file.exists():
            raise SystemExit(f"Missing: {file}")
        document = build_variant_document(file.read_text(encoding="utf-8"), css)
        height = variant.get("height", 420)

        pros = "".join(f"<li>{html_escape(x)}</li>" for x in variant.get("pros", []))
        cons = "".join(f"<li>{html_escape(x)}</li>" for x in variant.get("cons", []))

        jump_links.append(f'<a href="#v{number}">{number} · {html_escape(variant["title"])}</a>')
        buttons.append(
            f'<label><input type="radio" name="variant" value="{number}">'
            f'<span>{number} · {html_escape(variant["title"])}</span></label>'
        )
        sections.append(
            f'<section class="variant" id="v{number}">'
            f'<div class="head"><span class="number">{number}</span>'
            f'<h2>{html_escape(variant["title"])}</h2>'
            f'<button type="button" class="noteBtn" data-variant="{number}">Comment</button>'
            "</div>"
            f'<div class="stage"><iframe height="{height}" '
            f'srcdoc="{html_escape(document)}" title="Variant {number}"></iframe></div>'
            f'<div class="thinking"><h3>The thinking behind it</h3>'
            f'<p>{html_escape(variant["rationale"])}</p></div>'
            f'<div class="tradeoffs"><div class="pros"><h3>Speaks for it</h3><ul>{pros}</ul></div>'
            f'<div class="cons"><h3>Speaks against it</h3><ul>{cons}</ul></div></div>'
            "</section>"
        )

    page = TEMPLATE.read_text(encoding="utf-8")
    page = page.replace("__TITLE__", html_escape(data["title"]))
    page = page.replace("__CONTEXT__", html_escape(data.get("context", "")))
    page = page.replace("__JUMP_LINKS__", "".join(jump_links))
    page = page.replace("__SECTIONS__", "".join(sections))
    page = page.replace("__CHOICE_BUTTONS__", "".join(buttons))
    page = page.replace("__HISTORY__", build_history(folder))
    return page


def build_history(folder: Path) -> str:
    """Earlier replies, listed below the form.

    Without them every round starts from zero: you no longer remember what you
    asked for last time, so you ask again - or you hold back because you are
    not sure whether you already said it.
    """
    file = folder / "history.json"
    if not file.exists():
        return ""
    try:
        entries = json.loads(file.read_text(encoding="utf-8"))
    except json.JSONDecodeError:
        return ""
    if not entries:
        return ""

    rows = []
    for index, entry in enumerate(entries, start=1):
        variant = entry.get("variant")
        chosen = f"Variant {variant}" if variant is not None else "no variant picked"
        time = entry.get("time", "")
        general = (entry.get("note") or "").strip()

        # Per-variant notes came later than the plain reply, so an older
        # history file simply has none. Reading them with .get keeps those
        # entries displayable instead of blanking the whole block.
        per_variant = "".join(
            f'<p class="perVariant"><b>{html_escape(number)}</b> {html_escape(text.strip())}</p>'
            for number, text in sorted((entry.get("notes") or {}).items())
            if text.strip()
        )
        if not general and not per_variant:
            general = "(nothing written)"

        rows.append(
            f'<div class="entry"><div class="entryHead"><b>{index}.</b>'
            f"<span>{html_escape(chosen)}</span><span>{html_escape(time)}</span></div>"
            + (f"<p>{html_escape(general)}</p>" if general else "")
            + per_variant
            + "</div>"
        )
    return '<section class="history"><h2>Sent so far</h2>' + "".join(rows) + "</section>"


def serve(folder: Path, port: int, open_browser: bool, timeout: float) -> None:
    """Serves the page until a choice arrives.

    `choice.json` is deleted on start: a watcher waiting for it (see SKILL.md,
    "Show it") recognises a new answer by the file appearing. If the old one
    stayed behind, the watcher would fire immediately with the previous round's
    answer. `history.json` of course stays.
    """
    (folder / "choice.json").unlink(missing_ok=True)
    page = build_page(folder)
    done = threading.Event()

    class Handler(BaseHTTPRequestHandler):
        def log_message(self, *_args):  # suppress server noise
            pass

        def do_GET(self):
            path = self.path.split("?")[0].lstrip("/")
            if path in ("", "index.html"):
                payload = page.encode("utf-8")
                self.send_response(200)
                self.send_header("Content-Type", "text/html; charset=utf-8")
                self.send_header("Content-Length", str(len(payload)))
                self.end_headers()
                self.wfile.write(payload)
                return
            file = (folder / path).resolve()
            if file.exists() and folder.resolve() in file.parents:
                kind = "image/png" if file.suffix == ".png" else "application/octet-stream"
                content = file.read_bytes()
                self.send_response(200)
                self.send_header("Content-Type", kind)
                self.send_header("Content-Length", str(len(content)))
                self.end_headers()
                self.wfile.write(content)
                return
            self.send_error(404)

        def do_POST(self):
            if self.path != "/choice":
                self.send_error(404)
                return
            length = int(self.headers.get("Content-Length", 0))
            payload = json.loads(self.rfile.read(length) or b"{}")
            payload["time"] = datetime.now().strftime("%Y-%m-%d %H:%M")
            target = folder / "choice.json"
            target.write_text(
                json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
            )
            # Also into the history, which survives across rounds: next time the
            # page is built it appears below the variants, so you can see what
            # you already sent - and don't ask for the same thing three times.
            history_file = folder / "history.json"
            history = []
            if history_file.exists():
                try:
                    history = json.loads(history_file.read_text(encoding="utf-8"))
                except json.JSONDecodeError:
                    history = []
            history.append(payload)
            history_file.write_text(
                json.dumps(history, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
            )
            self.send_response(200)
            self.send_header("Content-Type", "application/json")
            self.end_headers()
            self.wfile.write(b'{"ok":true}')
            print(f"CHOICE: {target}")
            print(json.dumps(payload, ensure_ascii=False))
            sys.stdout.flush()
            done.set()

    server = HTTPServer(("127.0.0.1", port), Handler)
    address = f"http://127.0.0.1:{server.server_port}/"
    print(f"Variants at {address}")
    sys.stdout.flush()

    def stop() -> None:
        server.shutdown()
        server.server_close()

    threading.Thread(target=server.serve_forever, daemon=True).start()
    if open_browser:
        webbrowser.open(address)

    # A timeout matters when this runs in the foreground: some agents kill a
    # command after a fixed time, and being killed loses the explanation.
    # Ending on our own terms lets us say what happened and what to do instead.
    if not done.wait(timeout if timeout > 0 else None):
        stop()
        print("No choice submitted before the timeout. Ask in the chat instead.")
        sys.stdout.flush()
        return

    # Keep running briefly after submit so the receipt reaches the browser.
    threading.Timer(1.5, stop).start()


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("folder", type=Path)
    parser.add_argument("--port", type=int, default=0)
    parser.add_argument("--no-browser", action="store_true")
    parser.add_argument(
        "--build-only",
        action="store_true",
        help="Write the page to page.html without serving it - for self-checks.",
    )
    parser.add_argument(
        "--timeout",
        type=float,
        default=0,
        help="Seconds to wait for a choice; 0 waits forever (default).",
    )
    args = parser.parse_args()

    folder = args.folder.resolve()
    if args.build_only:
        target = folder / "page.html"
        target.write_text(build_page(folder), encoding="utf-8")
        print(target)
        return
    serve(folder, args.port, not args.no_browser, args.timeout)


if __name__ == "__main__":
    main()
