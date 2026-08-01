"""Tests for show_variants.py.

The page is what the human judges the designs on, so the things worth pinning
down are the ones that quietly ruin it: an unreplaced placeholder, a stylesheet
that never made it into the iframe, a missing file that fails silently.
"""

from __future__ import annotations

import contextlib
import io
import json
import re
import tempfile
import unittest
from pathlib import Path

from helpers import EXAMPLE_DIR, MINIMAL_DATA, write_variant_folder

import show_variants


class BuildPageTest(unittest.TestCase):
    def setUp(self):
        self._tmp = tempfile.TemporaryDirectory()
        self.folder = Path(self._tmp.name)
        self.addCleanup(self._tmp.cleanup)

    def test_example_page_has_no_unreplaced_placeholders(self):
        page = show_variants.build_page(EXAMPLE_DIR)
        leftovers = re.findall(r"__[A-Z_]+__", page)
        self.assertEqual(leftovers, [], f"placeholders left in the page: {leftovers}")

    def test_example_page_shows_every_variant(self):
        data = json.loads((EXAMPLE_DIR / "variants.json").read_text(encoding="utf-8"))
        page = show_variants.build_page(EXAMPLE_DIR)
        for variant in data["variants"]:
            self.assertIn(f'id="v{variant["number"]}"', page)
            self.assertIn(variant["title"], page)
            self.assertIn(variant["rationale"], page)
            for entry in variant["pros"] + variant["cons"]:
                self.assertIn(entry, page)

    def test_token_css_reaches_the_iframe(self):
        """The whole promise of the skill is that variants use the real CSS."""
        page = show_variants.build_page(EXAMPLE_DIR)
        # Inside srcdoc everything is escaped, so look for the escaped form.
        self.assertIn("--panel-width", page)
        self.assertIn("tokens.css", page)
        self.assertIn("Editor.module.css", page)

    def test_missing_variant_file_names_the_path(self):
        write_variant_folder(self.folder, MINIMAL_DATA, bodies={})
        with self.assertRaises(SystemExit) as caught:
            show_variants.build_page(self.folder)
        self.assertIn("variant-1.html", str(caught.exception))

    def test_current_image_section_appears_only_when_the_file_exists(self):
        data = dict(MINIMAL_DATA, current_image="current.png", current_note="Today.")
        write_variant_folder(self.folder, data, {1: "<p>one</p>"})

        without = show_variants.build_page(self.folder)
        self.assertNotIn('id="v0"', without)

        (self.folder / "current.png").write_bytes(b"not really a png")
        with_image = show_variants.build_page(self.folder)
        self.assertIn('id="v0"', with_image)
        self.assertIn("Today.", with_image)

    def test_every_variant_gets_a_comment_button(self):
        """Without it there is no way to say anything about one variant."""
        page = show_variants.build_page(EXAMPLE_DIR)
        data = json.loads((EXAMPLE_DIR / "variants.json").read_text(encoding="utf-8"))
        for variant in data["variants"]:
            self.assertIn(f'class="noteBtn" data-variant="{variant["number"]}"', page)

    def test_variant_body_is_wrapped_but_not_altered(self):
        write_variant_folder(self.folder, MINIMAL_DATA, {1: "<p class='handle'>hi</p>"})
        page = show_variants.build_page(self.folder)
        self.assertIn("&lt;p class='handle'&gt;hi&lt;/p&gt;", page)

    def test_html_in_metadata_is_escaped(self):
        data = dict(MINIMAL_DATA, title="<script>alert(1)</script>")
        write_variant_folder(self.folder, data, {1: "<p>one</p>"})
        page = show_variants.build_page(self.folder)
        self.assertNotIn("<script>alert(1)</script>", page)
        self.assertIn("&lt;script&gt;alert(1)&lt;/script&gt;", page)


class VariantDocumentTest(unittest.TestCase):
    def test_hidden_beats_a_display_from_the_component_css(self):
        """The bug this guards against cost a full render cycle to spot.

        Component CSS almost always gives the toggled element a `display`, and
        that beats the browser's built-in `[hidden]` rule - so the collapsed
        state shows both halves at once and it looks like the variant is broken.
        """
        document = show_variants.build_variant_document("<div></div>", ".rail{display:flex}")
        self.assertLess(
            document.index(".rail{display:flex}"),
            document.index("[hidden]{display:none!important}"),
            "the [hidden] rule has to come after the component CSS to win",
        )


class ReadCssTest(unittest.TestCase):
    def setUp(self):
        self._tmp = tempfile.TemporaryDirectory()
        self.folder = Path(self._tmp.name)
        self.addCleanup(self._tmp.cleanup)

    def test_composes_is_stripped_and_global_is_unwrapped(self):
        (self.folder / "a.css").write_text(
            ".panel {\n  composes: shell;\n  color: red;\n}\n:global(.sr-only) { width: 1px; }\n",
            encoding="utf-8",
        )
        css = show_variants.read_css(["a.css"], self.folder)
        self.assertNotIn("composes:", css)
        self.assertNotIn(":global(", css)
        self.assertIn(".sr-only", css)
        self.assertIn("color: red;", css)

    def test_missing_file_is_skipped_rather_than_fatal(self):
        (self.folder / "there.css").write_text(".a{color:red}", encoding="utf-8")
        with contextlib.redirect_stderr(io.StringIO()) as warning:
            css = show_variants.read_css(["gone.css", "there.css"], self.folder)
        self.assertIn(".a{color:red}", css)
        self.assertIn("gone.css", warning.getvalue(), "a skipped file has to be reported")

    def test_absolute_and_relative_paths_both_work(self):
        (self.folder / "a.css").write_text(".a{color:red}", encoding="utf-8")
        relative = show_variants.read_css(["a.css"], self.folder)
        absolute = show_variants.read_css([str(self.folder / "a.css")], Path("/nowhere"))
        self.assertEqual(relative, absolute)


class HistoryTest(unittest.TestCase):
    def setUp(self):
        self._tmp = tempfile.TemporaryDirectory()
        self.folder = Path(self._tmp.name)
        self.addCleanup(self._tmp.cleanup)

    def test_absent_history_renders_nothing(self):
        self.assertEqual(show_variants.build_history(self.folder), "")

    def test_entries_are_numbered_and_labelled(self):
        (self.folder / "history.json").write_text(
            json.dumps(
                [
                    {"variant": 3, "note": "less space above", "time": "2026-01-01 09:00"},
                    {"variant": None, "note": "", "time": "2026-01-02 09:00"},
                ]
            ),
            encoding="utf-8",
        )
        html = show_variants.build_history(self.folder)
        self.assertIn("Sent so far", html)
        self.assertIn("Variant 3", html)
        self.assertIn("less space above", html)
        self.assertIn("no variant picked", html)
        self.assertIn("(nothing written)", html)

    def test_per_variant_notes_keep_their_number(self):
        """A note that lost its subject reads as a contradiction later."""
        (self.folder / "history.json").write_text(
            json.dumps(
                [
                    {
                        "variant": 2,
                        "note": "closer",
                        "time": "2026-01-01 09:00",
                        "notes": {"1": "too small", "3": "unreadable"},
                    }
                ]
            ),
            encoding="utf-8",
        )
        html = show_variants.build_history(self.folder)
        self.assertIn("closer", html)
        self.assertIn("<b>1</b> too small", html)
        self.assertIn("<b>3</b> unreadable", html)

    def test_entry_without_notes_still_renders(self):
        """History written before per-variant notes existed must stay readable."""
        (self.folder / "history.json").write_text(
            json.dumps([{"variant": 1, "note": "an older entry", "time": "2026-01-01 09:00"}]),
            encoding="utf-8",
        )
        html = show_variants.build_history(self.folder)
        self.assertIn("an older entry", html)

    def test_entry_with_only_per_variant_notes_says_so(self):
        (self.folder / "history.json").write_text(
            json.dumps([{"variant": None, "note": "", "notes": {"2": "make it wider"}}]),
            encoding="utf-8",
        )
        html = show_variants.build_history(self.folder)
        self.assertIn("make it wider", html)
        self.assertNotIn("(nothing written)", html)

    def test_malformed_history_is_ignored_rather_than_fatal(self):
        """A broken history file must not cost the human the whole page."""
        (self.folder / "history.json").write_text("{not json", encoding="utf-8")
        self.assertEqual(show_variants.build_history(self.folder), "")


if __name__ == "__main__":
    unittest.main()
