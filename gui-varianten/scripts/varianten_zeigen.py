#!/usr/bin/env python3
"""Baut die Varianten-Vergleichsseite, serviert sie lokal und öffnet den Browser.

Aufruf:
    python3 varianten_zeigen.py <ordner> [--port 0] [--kein-browser]

Erwartet im <ordner>:
    varianten.json      Metadaten (siehe unten)
    varianten/variante-1.html … variante-N.html
    ist.png             optional, Screenshot des Ist-Zustands

Schreibt bei Absenden des Formulars <ordner>/auswahl.json und beendet sich.

Warum jede Variante in einem eigenen <iframe> landet: Varianten sind
Entwürfe, keine fertige Software. Zwei davon dürfen dieselben Klassennamen
benutzen, globale Selektoren setzen oder auf `document` zugreifen, ohne dass
die Nachbarvariante davon kaputtgeht. Ohne diese Trennung debuggt man beim
Vergleichen Kollisionen statt Entwürfe zu beurteilen.
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

VORLAGE = Path(__file__).resolve().parent.parent / "assets" / "seite.html"


def html_escape(text: str) -> str:
    return (
        str(text)
        .replace("&", "&amp;")
        .replace("<", "&lt;")
        .replace(">", "&gt;")
        .replace('"', "&quot;")
    )


def lies_css(pfade: list[str], basis: Path) -> str:
    """Fügt die echten Stylesheets der Anwendung zusammen.

    CSS-Module-Dateien enthalten oft `composes:` oder `:global(...)`, was
    außerhalb des Bundlers nicht funktioniert. Beides wird entschärft, damit
    die Datei im Browser trotzdem greift — die Farben und Maße, auf die es
    beim Vergleich ankommt, überleben das unbeschadet.
    """
    stuecke = []
    for eintrag in pfade:
        pfad = Path(eintrag)
        if not pfad.is_absolute():
            pfad = (basis / pfad).resolve()
        if not pfad.exists():
            print(f"  ! CSS nicht gefunden, übersprungen: {pfad}", file=sys.stderr)
            continue
        text = pfad.read_text(encoding="utf-8")
        text = re.sub(r"^\s*composes:[^;]+;\s*$", "", text, flags=re.MULTILINE)
        text = re.sub(r":global\(([^)]*)\)", r"\1", text)
        stuecke.append(f"/* ---- {pfad.name} ---- */\n{text}")
    return "\n\n".join(stuecke)


def baue_variantendokument(rohes_html: str, css: str) -> str:
    """Macht aus dem Variantenschnipsel ein vollständiges Dokument für srcdoc."""
    return (
        "<!doctype html><html><head><meta charset='utf-8'>"
        "<style>"
        "html,body{margin:0;padding:0;font:15px/1.5 ui-sans-serif,system-ui,sans-serif}"
        f"{css}"
        "</style></head><body>"
        f"{rohes_html}"
        "</body></html>"
    )


def baue_seite(ordner: Path) -> str:
    daten = json.loads((ordner / "varianten.json").read_text(encoding="utf-8"))
    css = lies_css(daten.get("tokens_css", []) + daten.get("extra_css", []), ordner)

    abschnitte: list[str] = []
    sprungmarken: list[str] = []
    knoepfe: list[str] = []

    # Relativer Pfad, nicht "/ist.png": Unter dem Server ist beides gleich,
    # aber bei --nur-bauen öffnet der Mensch die Datei per file:// — dort
    # zeigt ein führender Schrägstrich auf die Dateisystemwurzel und das
    # Vorher-Bild bliebe leer. Ausgerechnet in dem Modus, der für Sitzungen
    # ohne Browser gedacht ist.
    ist_bild = daten.get("ist_bild")
    if ist_bild and (ordner / ist_bild).exists():
        sprungmarken.append('<a href="#v0">0 · Ist</a>')
        abschnitte.append(
            '<section class="variante" id="v0">'
            '<div class="kopfzeile"><span class="nummer ist">0</span>'
            "<h2>Ist-Zustand</h2></div>"
            f'<div class="buehne"><img src="{html_escape(ist_bild)}" alt="Ist-Zustand"></div>'
            '<div class="denken"><p>'
            f'{html_escape(daten.get("ist_notiz", "So sieht es heute aus."))}'
            "</p></div></section>"
        )

    for variante in daten["varianten"]:
        nummer = variante["nummer"]
        datei = ordner / "varianten" / f"variante-{nummer}.html"
        if not datei.exists():
            raise SystemExit(f"Fehlt: {datei}")
        dokument = baue_variantendokument(datei.read_text(encoding="utf-8"), css)
        hoehe = variante.get("hoehe", 420)

        pro = "".join(f"<li>{html_escape(x)}</li>" for x in variante.get("pro", []))
        contra = "".join(f"<li>{html_escape(x)}</li>" for x in variante.get("contra", []))

        sprungmarken.append(f'<a href="#v{nummer}">{nummer} · {html_escape(variante["titel"])}</a>')
        knoepfe.append(
            f'<label><input type="radio" name="variante" value="{nummer}">'
            f'<span>{nummer} · {html_escape(variante["titel"])}</span></label>'
        )
        abschnitte.append(
            f'<section class="variante" id="v{nummer}">'
            f'<div class="kopfzeile"><span class="nummer">{nummer}</span>'
            f'<h2>{html_escape(variante["titel"])}</h2></div>'
            f'<div class="buehne"><iframe height="{hoehe}" '
            f'srcdoc="{html_escape(dokument)}" title="Variante {nummer}"></iframe></div>'
            f'<div class="denken"><h3>Der Gedanke dahinter</h3>'
            f'<p>{html_escape(variante["gedanke"])}</p></div>'
            f'<div class="waage"><div class="pro"><h3>Spricht dafür</h3><ul>{pro}</ul></div>'
            f'<div class="contra"><h3>Spricht dagegen</h3><ul>{contra}</ul></div></div>'
            "</section>"
        )

    seite = VORLAGE.read_text(encoding="utf-8")
    seite = seite.replace("__TITEL__", html_escape(daten["titel"]))
    seite = seite.replace("__KONTEXT__", html_escape(daten.get("kontext", "")))
    seite = seite.replace("__SPRUNGMARKEN__", "".join(sprungmarken))
    seite = seite.replace("__ABSCHNITTE__", "".join(abschnitte))
    seite = seite.replace("__AUSWAHLKNOEPFE__", "".join(knoepfe))
    seite = seite.replace("__VERLAUF__", baue_verlauf(ordner))
    return seite


def baue_verlauf(ordner: Path) -> str:
    """Frühere Rückmeldungen als Liste unter dem Formular.

    Ohne sie beginnt jede Runde bei null: Man erinnert sich nicht mehr, was man
    beim letzten Mal gewünscht hat, wünscht es nochmal — oder traut sich nicht,
    weil man unsicher ist, ob es schon gesagt war.
    """
    datei = ordner / "verlauf.json"
    if not datei.exists():
        return ""
    try:
        eintraege = json.loads(datei.read_text(encoding="utf-8"))
    except json.JSONDecodeError:
        return ""
    if not eintraege:
        return ""

    zeilen = []
    for nummer, eintrag in enumerate(eintraege, start=1):
        variante = eintrag.get("variante")
        gewaehlt = f"Variante {variante}" if variante is not None else "ohne Auswahl"
        zeit = eintrag.get("zeit", "")
        notiz = (eintrag.get("notiz") or "").strip() or "(nichts dazugeschrieben)"
        zeilen.append(
            f'<div class="eintrag"><div class="eKopf"><b>{nummer}.</b>'
            f"<span>{html_escape(gewaehlt)}</span><span>{html_escape(zeit)}</span></div>"
            f"<p>{html_escape(notiz)}</p></div>"
        )
    return (
        '<section class="verlauf"><h2>Bisher geschickt</h2>' + "".join(zeilen) + "</section>"
    )


def starte(ordner: Path, port: int, browser_oeffnen: bool) -> None:
    """Serviert die Seite, bis eine Auswahl eintrifft.

    `auswahl.json` wird beim Start gelöscht: Der Wächter, der auf sie wartet
    (siehe SKILL.md §5), erkennt eine neue Antwort daran, dass die Datei
    auftaucht. Bliebe die alte liegen, feuerte er sofort mit der Antwort der
    letzten Runde. `verlauf.json` bleibt selbstverständlich stehen.
    """
    (ordner / "auswahl.json").unlink(missing_ok=True)
    seite = baue_seite(ordner)
    fertig = threading.Event()

    class Handler(BaseHTTPRequestHandler):
        def log_message(self, *_args):  # Server-Rauschen unterdrücken
            pass

        def do_GET(self):
            pfad = self.path.split("?")[0].lstrip("/")
            if pfad in ("", "index.html"):
                nutzlast = seite.encode("utf-8")
                self.send_response(200)
                self.send_header("Content-Type", "text/html; charset=utf-8")
                self.send_header("Content-Length", str(len(nutzlast)))
                self.end_headers()
                self.wfile.write(nutzlast)
                return
            datei = (ordner / pfad).resolve()
            if datei.exists() and ordner.resolve() in datei.parents:
                typ = "image/png" if datei.suffix == ".png" else "application/octet-stream"
                inhalt = datei.read_bytes()
                self.send_response(200)
                self.send_header("Content-Type", typ)
                self.send_header("Content-Length", str(len(inhalt)))
                self.end_headers()
                self.wfile.write(inhalt)
                return
            self.send_error(404)

        def do_POST(self):
            if self.path != "/auswahl":
                self.send_error(404)
                return
            laenge = int(self.headers.get("Content-Length", 0))
            nutzlast = json.loads(self.rfile.read(laenge) or b"{}")
            nutzlast["zeit"] = datetime.now().strftime("%d.%m.%Y %H:%M")
            ziel = ordner / "auswahl.json"
            ziel.write_text(
                json.dumps(nutzlast, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
            )
            # Zusätzlich in den Verlauf, der über alle Runden hinweg bestehen
            # bleibt: Beim nächsten Bauen steht er unter den Varianten, damit
            # man sieht, was man schon geschickt hat — und nicht dreimal
            # dasselbe wünscht.
            verlauf_datei = ordner / "verlauf.json"
            verlauf = []
            if verlauf_datei.exists():
                try:
                    verlauf = json.loads(verlauf_datei.read_text(encoding="utf-8"))
                except json.JSONDecodeError:
                    verlauf = []
            verlauf.append(nutzlast)
            verlauf_datei.write_text(
                json.dumps(verlauf, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
            )
            self.send_response(200)
            self.send_header("Content-Type", "application/json")
            self.end_headers()
            self.wfile.write(b'{"ok":true}')
            print(f"AUSWAHL: {ziel}")
            print(json.dumps(nutzlast, ensure_ascii=False))
            sys.stdout.flush()
            fertig.set()

    server = HTTPServer(("127.0.0.1", port), Handler)
    adresse = f"http://127.0.0.1:{server.server_port}/"
    print(f"Varianten unter {adresse}")
    sys.stdout.flush()

    threading.Thread(target=server.serve_forever, daemon=True).start()
    if browser_oeffnen:
        webbrowser.open(adresse)

    # Nach dem Absenden noch kurz weiterlaufen, damit die Quittung ankommt.
    fertig.wait()
    threading.Timer(1.5, server.shutdown).start()


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("ordner", type=Path)
    parser.add_argument("--port", type=int, default=0)
    parser.add_argument("--kein-browser", action="store_true")
    parser.add_argument(
        "--nur-bauen",
        action="store_true",
        help="Seite nach seite.html schreiben, ohne Server — für Selbsttests.",
    )
    args = parser.parse_args()

    ordner = args.ordner.resolve()
    if args.nur_bauen:
        ziel = ordner / "seite.html"
        ziel.write_text(baue_seite(ordner), encoding="utf-8")
        print(ziel)
        return
    starte(ordner, args.port, not args.kein_browser)


if __name__ == "__main__":
    main()
