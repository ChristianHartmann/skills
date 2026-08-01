"""Checks SKILL.md against the Agent Skills specification.

https://agentskills.io/specification - agents load `name` and `description` at
startup for every installed skill, so a malformed frontmatter doesn't produce
an error, it produces a skill that is silently never used.

Deliberately no PyYAML: the frontmatter this skill needs is two flat string
fields, and a test dependency would be the only one in the whole repo.
"""

from __future__ import annotations

import re
import unittest

from helpers import SKILL_DIR

NAME_PATTERN = re.compile(r"^[a-z0-9]+(-[a-z0-9]+)*$")


def read_frontmatter(text: str) -> dict[str, str]:
    if not text.startswith("---\n"):
        raise AssertionError("SKILL.md must start with YAML frontmatter")
    end = text.index("\n---\n", 3)
    fields: dict[str, str] = {}
    for line in text[4:end].splitlines():
        if not line.strip() or line.startswith(("#", " ", "\t")):
            continue
        key, _, value = line.partition(":")
        fields[key.strip()] = value.strip()
    return fields


class SkillMetadataTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.text = (SKILL_DIR / "SKILL.md").read_text(encoding="utf-8")
        cls.fields = read_frontmatter(cls.text)

    def test_required_fields_are_present(self):
        self.assertIn("name", self.fields)
        self.assertIn("description", self.fields)

    def test_name_matches_the_directory(self):
        self.assertEqual(self.fields["name"], SKILL_DIR.name)

    def test_name_follows_the_spec(self):
        name = self.fields["name"]
        self.assertLessEqual(len(name), 64)
        self.assertRegex(name, NAME_PATTERN, "lowercase, digits and single hyphens only")

    def test_description_is_within_the_limit(self):
        description = self.fields["description"]
        self.assertTrue(description)
        self.assertLessEqual(len(description), 1024)

    def test_compatibility_is_within_the_limit(self):
        if "compatibility" in self.fields:
            self.assertLessEqual(len(self.fields["compatibility"]), 500)

    def test_referenced_files_exist(self):
        """A reference to a file that isn't there wastes a tool call and trust."""
        for match in re.finditer(r"`(references/[\w./-]+)`", self.text):
            with self.subTest(reference=match.group(1)):
                self.assertTrue((SKILL_DIR / match.group(1)).exists())
        for name in ("claude-code.md", "codex.md", "cursor.md", "generic.md"):
            with self.subTest(reference=name):
                self.assertIn(f"`{name}`", self.text)
                self.assertTrue((SKILL_DIR / "references" / name).exists())

    def test_scripts_named_in_the_body_exist(self):
        for match in re.finditer(r"(scripts/[\w.]+\.py)", self.text):
            with self.subTest(script=match.group(1)):
                self.assertTrue((SKILL_DIR / match.group(1)).exists())

    def test_body_stays_within_the_recommended_length(self):
        """The spec recommends keeping SKILL.md under 500 lines."""
        self.assertLess(len(self.text.splitlines()), 500)


if __name__ == "__main__":
    unittest.main()
