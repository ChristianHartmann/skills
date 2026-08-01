"""Tests for css_collisions.py.

The script exists because a collision is invisible: the variant just looks
broken and you go hunting in your own markup. A false negative here therefore
costs far more than a false positive, which is why the detection is coarse on
purpose - and why the "don't count things inside declaration blocks" rule is
worth pinning down.
"""

from __future__ import annotations

import contextlib
import io
import sys
import tempfile
import unittest
from pathlib import Path

from helpers import SCRIPTS_DIR  # noqa: F401  (puts the scripts dir on sys.path)

import css_collisions


class CollisionTest(unittest.TestCase):
    def setUp(self):
        self._tmp = tempfile.TemporaryDirectory()
        self.folder = Path(self._tmp.name)
        self.addCleanup(self._tmp.cleanup)

    def run_on(self, *files: str) -> tuple[int, str]:
        argv = ["css_collisions.py", *[str(self.folder / f) for f in files]]
        buffer = io.StringIO()
        with contextlib.redirect_stdout(buffer), contextlib.redirect_stderr(io.StringIO()):
            old, sys.argv = sys.argv, argv
            try:
                code = css_collisions.main()
            finally:
                sys.argv = old
        return code, buffer.getvalue()

    def write(self, name: str, text: str) -> None:
        (self.folder / name).write_text(text, encoding="utf-8")

    def test_shared_class_name_is_reported_with_both_files(self):
        self.write("a.module.css", ".active { color: red; }\n.only-a { color: blue; }\n")
        self.write("b.module.css", ".active { color: green; }\n.only-b { color: black; }\n")
        code, output = self.run_on("a.module.css", "b.module.css")
        self.assertEqual(code, 0)
        self.assertIn(".active", output)
        self.assertIn("a.module.css", output)
        self.assertIn("b.module.css", output)
        self.assertNotIn(".only-a", output)

    def test_disjoint_files_report_nothing(self):
        self.write("a.css", ".alpha { color: red; }")
        self.write("b.css", ".beta { color: red; }")
        code, output = self.run_on("a.css", "b.css")
        self.assertEqual(code, 0)
        self.assertIn("No duplicate class names", output)

    def test_dotted_values_inside_a_block_are_not_classes(self):
        """`url(../img/a.png)` must not masquerade as a class called `png`."""
        self.write("a.css", ".alpha { background: url(../img/logo.png); }")
        self.write("b.css", ".beta { background: url(../other/logo.png); }")
        code, output = self.run_on("a.css", "b.css")
        self.assertEqual(code, 0)
        self.assertIn("No duplicate class names", output)

    def test_missing_file_does_not_stop_the_run(self):
        self.write("a.css", ".alpha { color: red; }")
        self.write("b.css", ".alpha { color: blue; }")
        code, output = self.run_on("a.css", "gone.css", "b.css")
        self.assertEqual(code, 0)
        self.assertIn(".alpha", output)

    def test_fewer_than_two_files_prints_usage(self):
        self.write("a.css", ".alpha { color: red; }")
        code, output = self.run_on("a.css")
        self.assertEqual(code, 2)
        self.assertIn("css_collisions.py", output)


if __name__ == "__main__":
    unittest.main()
