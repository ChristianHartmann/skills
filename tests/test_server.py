"""Tests for the return channel - the part that makes this more than a viewer.

If the POST handler breaks, the human submits, the page says "Received", and
the answer never reaches the session. That failure is silent from both ends,
which is exactly why it is worth a test.
"""

from __future__ import annotations

import contextlib
import http.client
import io
import json
import socket
import tempfile
import threading
import unittest
from pathlib import Path

from helpers import MINIMAL_DATA, write_variant_folder

import show_variants


def free_port() -> int:
    with socket.socket() as sock:
        sock.bind(("127.0.0.1", 0))
        return sock.getsockname()[1]


def serve_quietly(*args) -> None:
    """`serve` prints the address and the timeout notice - useful in a session,
    noise in a test run."""
    with contextlib.redirect_stdout(io.StringIO()):
        show_variants.serve(*args)


class ServerTest(unittest.TestCase):
    def setUp(self):
        self._tmp = tempfile.TemporaryDirectory()
        self.folder = Path(self._tmp.name)
        self.addCleanup(self._tmp.cleanup)
        write_variant_folder(self.folder, MINIMAL_DATA, {1: "<p>one</p>"})

        self.port = free_port()
        self.thread = threading.Thread(
            target=serve_quietly,
            args=(self.folder, self.port, False, 20),
            daemon=True,
        )
        self.thread.start()
        self._wait_until_listening()

    def _wait_until_listening(self, attempts: int = 100) -> None:
        for _ in range(attempts):
            try:
                with socket.create_connection(("127.0.0.1", self.port), timeout=0.1):
                    return
            except OSError:
                threading.Event().wait(0.05)
        self.fail("server never came up")

    def _request(self, method: str, path: str, body: bytes | None = None):
        connection = http.client.HTTPConnection("127.0.0.1", self.port, timeout=5)
        headers = {"Content-Type": "application/json"} if body else {}
        connection.request(method, path, body=body, headers=headers)
        response = connection.getresponse()
        payload = response.read()
        connection.close()
        return response.status, payload

    def test_root_serves_the_page(self):
        status, payload = self._request("GET", "/")
        self.assertEqual(status, 200)
        self.assertIn(b"First answer", payload)

    def test_paths_outside_the_folder_are_refused(self):
        status, _ = self._request("GET", "/../../../../etc/passwd")
        self.assertEqual(status, 404)

    def test_unknown_post_target_is_refused(self):
        status, _ = self._request("POST", "/somewhere-else", b"{}")
        self.assertEqual(status, 404)

    def test_submitting_writes_choice_and_history(self):
        status, payload = self._request(
            "POST", "/choice", json.dumps({"variant": 1, "note": "more contrast"}).encode()
        )
        self.assertEqual(status, 200)
        self.assertEqual(json.loads(payload), {"ok": True})

        self.thread.join(timeout=5)
        self.assertFalse(self.thread.is_alive(), "serve() should return once a choice arrives")

        choice = json.loads((self.folder / "choice.json").read_text(encoding="utf-8"))
        self.assertEqual(choice["variant"], 1)
        self.assertEqual(choice["note"], "more contrast")
        self.assertIn("time", choice, "the timestamp is what makes the history readable")

        history = json.loads((self.folder / "history.json").read_text(encoding="utf-8"))
        self.assertEqual(history, [choice])

    def test_per_variant_notes_survive_the_round_trip(self):
        """They are the most specific thing the human sends; losing them is worse
        than losing the pick."""
        payload = {"variant": None, "note": "", "notes": {"1": "too small", "3": "unreadable"}}
        status, _ = self._request("POST", "/choice", json.dumps(payload).encode())
        self.assertEqual(status, 200)
        self.thread.join(timeout=5)

        choice = json.loads((self.folder / "choice.json").read_text(encoding="utf-8"))
        self.assertEqual(choice["notes"], {"1": "too small", "3": "unreadable"})
        self.assertIsNone(choice["variant"])


class StaleChoiceTest(unittest.TestCase):
    def test_previous_choice_is_removed_on_start(self):
        """Otherwise a watcher fires instantly with the last round's answer."""
        with tempfile.TemporaryDirectory() as name:
            folder = Path(name)
            write_variant_folder(folder, MINIMAL_DATA, {1: "<p>one</p>"})
            (folder / "choice.json").write_text('{"variant": 9}', encoding="utf-8")
            (folder / "history.json").write_text("[]", encoding="utf-8")

            thread = threading.Thread(
                target=serve_quietly,
                args=(folder, free_port(), False, 1),
                daemon=True,
            )
            thread.start()
            thread.join(timeout=10)

            self.assertFalse((folder / "choice.json").exists())
            self.assertTrue((folder / "history.json").exists(), "history survives a new round")


class TimeoutTest(unittest.TestCase):
    def test_serve_returns_when_nobody_submits(self):
        """Agents that cap command runtime need this to end on its own terms."""
        with tempfile.TemporaryDirectory() as name:
            folder = Path(name)
            write_variant_folder(folder, MINIMAL_DATA, {1: "<p>one</p>"})
            thread = threading.Thread(
                target=serve_quietly,
                args=(folder, free_port(), False, 1),
                daemon=True,
            )
            thread.start()
            thread.join(timeout=10)
            self.assertFalse(thread.is_alive(), "serve() should give up after the timeout")


if __name__ == "__main__":
    unittest.main()
