# Claude-Skills

Eigene Skills für Claude Code, versioniert. Eine Skill ist ein Ordner mit einer
`SKILL.md` und optionalem Beiwerk unter `scripts/` und `assets/`.

## Enthaltene Skills

| Skill | Wofür |
| --- | --- |
| [`gui-varianten`](gui-varianten/) | Baut zu einer Oberflächen-Frage 3–5 durchnummerierte, bedienbare HTML-Varianten aus den echten Tokens und dem echten CSS der Anwendung, öffnet sie im Browser und nimmt die Rückmeldung direkt in die Sitzung zurück. |

## Installieren

Claude Code sucht Skills unter `~/.claude/skills/`. Damit dieses Repo die
alleinige Quelle bleibt und nicht neben der installierten Fassung
auseinanderdriftet, verlinken statt kopieren:

```bash
ln -s ~/projects/skills/gui-varianten ~/.claude/skills/gui-varianten
```

Ist dort schon ein echtes Verzeichnis, vorher wegräumen — aber erst prüfen, ob
es Änderungen enthält, die hier noch fehlen:

```bash
diff -r ~/.claude/skills/gui-varianten ~/projects/skills/gui-varianten
```

Kopieren geht auch, kostet aber genau das, wofür dieses Repo da ist: Nach der
ersten Änderung an der installierten Fassung weiß niemand mehr, welche der
beiden die aktuelle ist.

## Arbeiten an einer Skill

Skills sind Prompts, keine Programme — sie lassen sich nicht kompilieren und
nicht mit Unit-Tests absichern. Was stattdessen trägt:

- **An einem echten Fall ausprobieren**, nicht am Schreibtisch beurteilen.
  Am ehrlichsten mit einem frischen Agenten, der nur die Anleitung bekommt: Was
  er falsch macht, ist eine Lücke in der Anleitung, kein Fehler des Agenten.
- **Nach dem Lauf nach Kritik fragen.** Wo war die Anleitung unklar, was musste
  geraten werden, was hat unnötig Zeit gekostet? Diese Rückmeldung ist der
  eigentliche Ertrag eines Testlaufs.
- **Wiederholte Handarbeit in ein Skript gießen.** Tut ein Agent bei jedem Lauf
  dieselbe mühsame Sache, gehört sie nach `scripts/` — einmal richtig statt
  jedes Mal neu erfunden.
- **Das Warum aufschreiben, nicht nur das Was.** Eine Anweisung, deren Grund
  dasteht, wird sinnvoll angewandt; eine ohne wird buchstabengetreu befolgt und
  am nächsten Sonderfall falsch.

## Beigelegte Skripte

`gui-varianten/scripts/` enthält zwei Werkzeuge, die auch außerhalb der Skill
nützlich sind:

- `varianten_zeigen.py` — baut die Vergleichsseite, serviert sie lokal, öffnet
  den Browser und nimmt die Auswahl per POST zurück. `--nur-bauen` erzeugt
  stattdessen eine einzelne HTML-Datei.
- `css_kollisionen.py` — findet Klassennamen, die in mehreren CSS-Dateien
  vergeben sind. Beim Zusammenfügen von CSS-Modulen außerhalb des Bundlers
  überschreiben die sich gegenseitig, und man sucht den Fehler dann im eigenen
  Markup.
