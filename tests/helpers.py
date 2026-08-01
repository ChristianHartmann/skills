"""Shared setup for the test modules.

The scripts live in `skills/ui-variants/scripts/` and are meant to be run
directly, not imported as a package - so the tests put that directory on the
path rather than inventing packaging the skill does not need.
"""

from __future__ import annotations

import json
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
SKILL_DIR = REPO_ROOT / "skills" / "ui-variants"
SCRIPTS_DIR = SKILL_DIR / "scripts"
EXAMPLE_DIR = REPO_ROOT / "examples" / "sidebar-handle"

if str(SCRIPTS_DIR) not in sys.path:
    sys.path.insert(0, str(SCRIPTS_DIR))


def write_variant_folder(folder: Path, data: dict, bodies: dict[int, str]) -> Path:
    """Creates a minimal but complete work folder, the way the skill describes it."""
    (folder / "variants").mkdir(parents=True, exist_ok=True)
    (folder / "variants.json").write_text(json.dumps(data), encoding="utf-8")
    for number, body in bodies.items():
        (folder / "variants" / f"variant-{number}.html").write_text(body, encoding="utf-8")
    return folder


MINIMAL_DATA = {
    "title": "A question",
    "variants": [
        {
            "number": 1,
            "title": "First answer",
            "rationale": "Because of this.",
            "pros": ["cheap"],
            "cons": ["ugly"],
        }
    ],
}
