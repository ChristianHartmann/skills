"""Checks the comparison page's own markup and stylesheet.

These guard one invariant that has now broken twice in this codebase: an
element meant to be invisible actually being invisible. Component CSS almost
always gives such an element a `display`, and any `display` beats the browser's
built-in `[hidden]` rule - so the element stays on screen while the code
reads as if it were gone.
"""

from __future__ import annotations

import re
import unittest

from helpers import SKILL_DIR

TEMPLATE = SKILL_DIR / "assets" / "page-template.html"


def split_template() -> tuple[str, str]:
    text = TEMPLATE.read_text(encoding="utf-8")
    style = re.search(r"<style>(.*?)</style>", text, re.S).group(1)
    body = text[text.index("</style>") :]
    return style, body


def rule_for(style: str, selector: str) -> str:
    """The declarations of the first rule whose selector list ends in `selector`."""
    pattern = re.compile(
        r"(?:^|[},])\s*([^{}]*?" + re.escape(selector) + r")\s*\{([^{}]*)\}", re.M
    )
    match = pattern.search(style)
    return match.group(2) if match else ""


def has_working_hidden_override(style: str) -> bool:
    """A `[hidden]` rule strong enough to beat a class that sets `display`."""
    for match in re.finditer(r"\[hidden\]\s*\{([^{}]*)\}", style):
        body = match.group(1).replace(" ", "")
        if "display:none!important" in body:
            return True
    return False


class HiddenElementsTest(unittest.TestCase):
    def test_elements_marked_hidden_are_really_hidden(self):
        """Any element carrying the hidden attribute must actually disappear."""
        style, body = split_template()
        override = has_working_hidden_override(style)

        for match in re.finditer(r"<(\w+)([^>]*)>", body):
            attributes = match.group(2)
            if not re.search(r"(?<![\w-])hidden(?=[\s>])", attributes):
                continue
            class_match = re.search(r'class="([^"]*)"', attributes)
            if not class_match:
                continue
            for name in class_match.group(1).split():
                declarations = rule_for(style, "." + name)
                if "display:" in declarations.replace(" ", ""):
                    self.assertTrue(
                        override,
                        f".{name} sets a display and the element uses the hidden "
                        "attribute, but no [hidden] override beats it - the element "
                        "stays visible",
                    )


class NotePanelTest(unittest.TestCase):
    def test_panel_is_not_visible_before_it_is_asked_for(self):
        """The whole point of the panel is that the page stays quiet until you
        click Comment. If it starts open, closing it is also broken, because the
        same mechanism is doing both."""
        style, body = split_template()
        opening = re.search(r"<aside[^>]*class=\"notePanel\"[^>]*>", body)
        self.assertIsNotNone(opening, "the note panel should be an <aside>")

        default = rule_for(style, ".notePanel").replace(" ", "")
        hidden_by_css = "display:none" in default
        hidden_by_attribute = bool(
            re.search(r"(?<![\w-])hidden(?=[\s>])", opening.group(0))
        ) and has_working_hidden_override(style)

        self.assertTrue(
            hidden_by_css or hidden_by_attribute,
            "the note panel is displayed on load: neither its own rule hides it "
            "nor does a working [hidden] override exist",
        )

    def test_panel_closes_through_two_named_buttons(self):
        """A cross reads as "discard" to some and "put aside" to others, and
        here those are different outcomes - so both are spelled out."""
        _, body = split_template()
        panel = body[body.index('class="notePanel"') : body.index("</aside>")]
        self.assertIn('id="panelOk"', panel)
        self.assertIn('id="panelCancel"', panel)
        self.assertNotIn("&times;", panel, "the cross should be gone")

    def test_cancel_restores_instead_of_deleting(self):
        """Cancel after fixing a typo must not throw away the note underneath."""
        _, body = split_template()
        self.assertIn("draftBefore", body)
        cancel = re.search(r"function cancel\(\)\s*\{([^}]*)\}", body).group(1)
        self.assertIn("draftBefore", cancel)

    def test_panel_is_revealed_by_the_same_state_class_that_widens_the_page(self):
        """Two mechanisms for one state is how it drifts apart: the page grew
        wider while the panel stayed put."""
        style, _ = split_template()
        self.assertIn(".shell.withPanel", style)
        revealed = rule_for(style, ".withPanel .notePanel").replace(" ", "")
        self.assertIn("display:flex", revealed)


if __name__ == "__main__":
    unittest.main()
