#!/usr/bin/env python3
"""Findet Klassennamen, die in mehreren CSS-Dateien vergeben sind.

    python3 css_kollisionen.py datei-a.module.css datei-b.module.css …

Warum das nötig ist: In der laufenden Anwendung trennt der Bundler gleich
benannte Klassen aus verschiedenen CSS-Modulen per Hash — `.active` aus
`IconButton.module.css` und `.active` aus `PanelTabRail.module.css` sind dort
zwei verschiedene Dinge. Für die Varianten-Seite werden die Quelldateien aber
wörtlich hintereinandergehängt, und dann ist es derselbe Selektor: Die zuletzt
eingebundene Regel gewinnt, und eine Variante sieht unerklärlich kaputt aus.

Wer eine Kollision kennt, kann sie umgehen — nur die Datei einbinden, auf die
es ankommt, und den Rest im Variantenrumpf inline nachbauen. Wer sie nicht
kennt, sucht den Fehler im eigenen Markup.
"""

from __future__ import annotations

import re
import sys
from collections import defaultdict
from pathlib import Path

# Klassenselektoren am Regelanfang; bewusst grob — hier zählt Vollständigkeit
# mehr als Genauigkeit, ein falscher Treffer kostet nur einen Blick.
KLASSE = re.compile(r"\.(-?[_a-zA-Z][\w-]*)")


def main() -> int:
    if len(sys.argv) < 3:
        print(__doc__)
        return 2

    vorkommen: dict[str, set[str]] = defaultdict(set)
    for arg in sys.argv[1:]:
        pfad = Path(arg)
        if not pfad.exists():
            print(f"! Nicht gefunden: {pfad}", file=sys.stderr)
            continue
        text = pfad.read_text(encoding="utf-8")
        # Inhalte von Deklarationsblöcken ausblenden, damit z. B.
        # `background: url(.../a.png)` keine Klasse vortäuscht.
        ohne_bloecke = re.sub(r"\{[^{}]*\}", " ", text)
        for treffer in KLASSE.finditer(ohne_bloecke):
            vorkommen[treffer.group(1)].add(pfad.name)

    kollisionen = {k: v for k, v in vorkommen.items() if len(v) > 1}
    if not kollisionen:
        print("Keine doppelt vergebenen Klassennamen. Alle Dateien können zusammen rein.")
        return 0

    print(f"{len(kollisionen)} doppelt vergebene Klassennamen — hier gewinnt die zuletzt")
    print("eingebundene Datei, und zwar wörtlich:\n")
    for name in sorted(kollisionen):
        dateien = ", ".join(sorted(kollisionen[name]))
        print(f"  .{name:<20} {dateien}")
    print(
        "\nEntscheide je Name, welche Datei du wirklich brauchst. Die andere Rolle"
        "\nbaust du im Variantenrumpf inline nach, statt beide CSS-Dateien"
        "\neinzubinden und zu hoffen."
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
