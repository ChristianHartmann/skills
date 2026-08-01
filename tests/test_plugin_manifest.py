"""Checks the Claude Code marketplace catalogue and plugin manifest.

Nothing in the normal workflow reads these files, so a typo in them stays
invisible until someone tries to install the plugin and it silently offers no
skills. That is the failure this guards against.
"""

from __future__ import annotations

import json
import re
import unittest

from helpers import REPO_ROOT

MANIFEST_DIR = REPO_ROOT / ".claude-plugin"
NAME_PATTERN = re.compile(r"^[a-z0-9]+(-[a-z0-9]+)*$")

# Reserved for Anthropic; a marketplace using one of these stops loading.
# https://code.claude.com/docs/en/plugin-marketplaces
RESERVED = {
    "claude-code-marketplace",
    "claude-code-plugins",
    "claude-plugins-official",
    "claude-plugins-community",
    "claude-community",
    "anthropic-marketplace",
    "anthropic-plugins",
    "agent-skills",
    "anthropic-agent-skills",
    "knowledge-work-plugins",
    "life-sciences",
    "claude-for-legal",
    "claude-for-financial-services",
    "financial-services-plugins",
    "first-party-plugins",
    "healthcare",
}


def load(name: str) -> dict:
    return json.loads((MANIFEST_DIR / name).read_text(encoding="utf-8"))


class MarketplaceTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.marketplace = load("marketplace.json")

    def test_required_fields_are_present(self):
        self.assertIn("name", self.marketplace)
        self.assertIn("owner", self.marketplace)
        self.assertIn("name", self.marketplace["owner"])
        self.assertTrue(self.marketplace["plugins"])

    def test_marketplace_name_is_usable(self):
        name = self.marketplace["name"]
        self.assertRegex(name, NAME_PATTERN, "kebab-case, no spaces")
        self.assertNotIn(name, RESERVED, "reserved names stop loading entirely")

    def test_every_plugin_points_at_something_that_exists(self):
        for plugin in self.marketplace["plugins"]:
            with self.subTest(plugin=plugin.get("name")):
                self.assertRegex(plugin["name"], NAME_PATTERN)
                source = plugin["source"]
                self.assertIsInstance(source, str, "local sources are relative paths")
                self.assertFalse(source.startswith(".."), "must stay inside the repo")
                self.assertTrue((REPO_ROOT / source).is_dir())

                for path in plugin.get("skills", []):
                    self.assertTrue(
                        (REPO_ROOT / path / "SKILL.md").is_file(),
                        f"{path} carries no SKILL.md, so the plugin installs empty",
                    )

    def test_plugin_root_is_self_contained(self):
        """Installing copies the plugin directory into a cache, so anything it
        reaches for through `..` is simply not there afterwards."""
        for plugin in self.marketplace["plugins"]:
            for path in plugin.get("skills", []):
                with self.subTest(path=path):
                    self.assertFalse(path.startswith("../"))
                    resolved = (REPO_ROOT / path).resolve()
                    self.assertTrue(resolved.is_relative_to(REPO_ROOT.resolve()))


class PluginManifestTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.plugin = load("plugin.json")
        cls.marketplace = load("marketplace.json")

    def test_name_matches_the_catalogue_entry(self):
        """The two are written by hand in separate files and drift silently."""
        names = [entry["name"] for entry in self.marketplace["plugins"]]
        self.assertIn(self.plugin["name"], names)

    def test_descriptions_agree(self):
        entry = next(
            e for e in self.marketplace["plugins"] if e["name"] == self.plugin["name"]
        )
        self.assertEqual(entry.get("description"), self.plugin.get("description"))

    def test_version_is_absent_so_every_commit_ships(self):
        """With a version set, pushing without bumping it reaches nobody - the
        cached copy keeps being served. Omitting it uses the commit SHA."""
        self.assertNotIn("version", self.plugin)
        for entry in self.marketplace["plugins"]:
            self.assertNotIn("version", entry)


if __name__ == "__main__":
    unittest.main()
