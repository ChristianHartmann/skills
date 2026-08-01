#!/usr/bin/env python3
"""Finds class names that are defined in more than one CSS file.

    python3 css_collisions.py file-a.module.css file-b.module.css …

Why this is needed: in the running application the bundler keeps identically
named classes from different CSS modules apart by hashing them - `.active` from
`IconButton.module.css` and `.active` from `PanelTabRail.module.css` are two
different things there. For the variant page the source files are concatenated
verbatim, and then it is the same selector: the rule included last wins, and a
variant looks inexplicably broken.

Whoever knows about a collision can work around it - include only the file that
matters and rebuild the other role inline in the variant body. Whoever doesn't
goes looking for the bug in their own markup.
"""

from __future__ import annotations

import re
import sys
from collections import defaultdict
from pathlib import Path

# Class selectors at the start of a rule; deliberately coarse - completeness
# matters more than precision here, and a false hit costs one glance.
CLASS = re.compile(r"\.(-?[_a-zA-Z][\w-]*)")


def main() -> int:
    if len(sys.argv) < 3:
        print(__doc__)
        return 2

    occurrences: dict[str, set[str]] = defaultdict(set)
    for arg in sys.argv[1:]:
        path = Path(arg)
        if not path.exists():
            print(f"! Not found: {path}", file=sys.stderr)
            continue
        text = path.read_text(encoding="utf-8")
        # Blank out the contents of declaration blocks so that e.g.
        # `background: url(.../a.png)` doesn't masquerade as a class.
        without_blocks = re.sub(r"\{[^{}]*\}", " ", text)
        for match in CLASS.finditer(without_blocks):
            occurrences[match.group(1)].add(path.name)

    collisions = {k: v for k, v in occurrences.items() if len(v) > 1}
    if not collisions:
        print("No duplicate class names. All files can go in together.")
        return 0

    count = len(collisions)
    noun = "class name" if count == 1 else "class names"
    print(f"{count} {noun} defined more than once - here the file included")
    print("last wins, and it wins literally:\n")
    for name in sorted(collisions):
        files = ", ".join(sorted(collisions[name]))
        print(f"  .{name:<20} {files}")
    print(
        "\nDecide per name which file you actually need. Rebuild the other role"
        "\ninline in the variant body, instead of including both CSS files and"
        "\nhoping."
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
