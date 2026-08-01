---
name: gui-varianten
description: Entwirft 3–5 durchnummerierte, interaktive HTML-Varianten für eine Oberflächen-Änderung — gebaut aus den echten Tokens und dem echten CSS der Anwendung, jede mit Begründung, Vor- und Nachteilen, und automatisch im Browser geöffnet. Nutze diese Skill immer, wenn jemand sagt, dass ihm etwas an der Oberfläche nicht gefällt, nach Alternativen oder Varianten fragt, unsicher ist wie ein Bedienelement aussehen oder sich verhalten soll, einen Screenshot mit einer Unzufriedenheit schickt, oder etwas "anders" oder "schöner" haben will — auch dann, wenn das Wort "Variante" gar nicht fällt. Ebenso, wenn du selbst vor einer Gestaltungsfrage stehst, die mehrere vertretbare Antworten hat: Dann zeig sie, statt eine davon stillschweigend zu wählen.
---

# GUI-Varianten

Gestaltungsfragen lassen sich schlecht im Chat entscheiden. Eine Beschreibung
wie „ein schwebender Griff auf der Trennlinie" erzeugt bei dir und beim
Menschen zwei verschiedene Bilder, und das merkt ihr erst, wenn es gebaut ist.
Diese Skill dreht die Reihenfolge um: erst sehen, dann entscheiden.

Das Ergebnis ist eine lokale Seite mit mehreren durchnummerierten Varianten,
die aussehen und sich anfühlen wie die echte Anwendung, weil sie deren Tokens
und CSS benutzen. Der Mensch klickt sie durch, wählt eine aus und schreibt
dazu, was er anders will — das kommt direkt in der Sitzung an.

## Ablauf

### 1. Verstehen, was eigentlich stört

Frag nach, wenn die Beschwerde vage ist — aber frag *einmal* und gezielt, nicht
in einer Kette. Was du wissen musst:

- **Welcher Ausschnitt?** Ein einzelnes Bedienelement, eine Leiste, ein ganzer
  Bildschirm. Kleiner ist besser: Je enger der Ausschnitt, desto ehrlicher der
  Vergleich, weil das Drumherum nicht ablenkt.
- **Stört das Aussehen oder das Verhalten?** „Zu unauffällig" ist Aussehen,
  „ich finde den Knopf nicht wieder" ist Verhalten. Bei Verhalten müssen die
  Varianten bedienbar sein, sonst beantworten sie die Frage nicht.
- **Was ist schon entschieden?** Bestehende Muster, an die sich die Varianten
  halten sollen, oder ausdrücklich nicht.

### 2. Den Ist-Zustand beschaffen

Die Varianten sind nur so überzeugend wie ihre Ähnlichkeit mit dem Original.
Such deshalb im Projekt zusammen:

- **Die kanonische Token-Quelle** — die Datei, in der Farben, Radien, Schatten
  und Abstände als CSS-Custom-Properties stehen. In vielen Projekten heißt sie
  `tokens.css`, `variables.css` oder `theme.css`. Gibt es eine Design-Doku oder
  eine Projekt-Skill, lies dort nach, welche Datei die Wahrheit ist.
- **Das CSS der betroffenen Komponente** — die tatsächliche Datei, nicht dein
  Gedächtnis.
- **Das Markup der betroffenen Komponente** — damit deine Varianten dieselbe
  Struktur benutzen und nicht eine ähnlich aussehende Erfindung.

Dazu ein **Screenshot des Ist-Zustands**, wenn die Anwendung läuft oder sich
starten lässt. Schneid ihn auf denselben Ausschnitt zu, den auch deine
Varianten zeigen, und in vergleichbarer Größe — er steht in Originalgröße
neben ihnen, und zwei verschiedene Maßstäbe nebeneinander vergleichen sich
schlecht.

Für den Zuschnitt gilt dieselbe Frage wie für die Varianten: Ist das
Umstrittene drauf, und genug Umgebung, um es einzuordnen? Bei einem Griff an
einer Seitenleiste also Kopfzeile, ein Stück Inhalt, die Kante und ein Streifen
der Nachbarfläche — nicht die halbe Anwendung, aber auch nicht nur der Griff
allein, denn seine Lage ist ja gerade der Punkt. Er wird als „Variante 0" danebengestellt. Das ist der Anker:
Ohne ihn vergleicht der Mensch deine Entwürfe mit seiner Erinnerung, und die
ist großzügiger als die Wirklichkeit.

Kriegst du keinen Screenshot — App läuft nicht, Anmeldung im Weg —, dann sag
das und mach ohne weiter. Ein erfundener „Vorher"-Zustand ist schlimmer als
gar keiner.

### 3. Varianten entwerfen, die sich wirklich unterscheiden

Das ist der Teil, der über Nutzen oder Zeitverschwendung entscheidet.

Drei Entwürfe, die sich in Abstand, Farbe und Radius unterscheiden, sind
**eine** Variante in drei Anstrichen. Sie zwingen den Menschen, Kleinigkeiten
zu bewerten, obwohl die eigentliche Frage noch offen ist. Frag dich stattdessen
bei jeder Variante: *Welche andere Antwort auf das Problem verkörpert sie?*

Ein Beispiel — Beschwerde: „Das Icon zum Ein- und Ausklappen der Seitenleiste
gefällt mir nicht."

| | Andere Antwort auf das Problem |
| --- | --- |
| 1 | Der Griff gehört an die Kante zwischen Leiste und Inhalt, nicht in die Leiste — er trennt ja beides |
| 2 | Kein Griff: Ein Klick auf die schmale Schiene selbst klappt auf |
| 3 | Der Griff bleibt, wird aber zur beschrifteten Fläche am Kopf der Leiste |
| 4 | Gar kein sichtbares Bedienelement — die Leiste klappt beim Verlassen von selbst zu |

Jede davon hat andere Kosten. Genau darum lohnt der Vergleich. Drei bis fünf
sind richtig; darunter wird es keine Wahl, darüber eine Zumutung.

**Die Varianten müssen bedienbar sein**, wenn die Beschwerde das Verhalten
betrifft. Klappt eine Leiste auf und zu, dann klappt sie in der Variante auch
auf und zu — mit ein paar Zeilen JavaScript direkt in der Variantendatei.
Ein Standbild kann nicht beantworten, ob sich etwas gut anfühlt.

**Das Umstrittene muss man sehen — sofort und in beiden Zuständen.** Das ist
der Fehler, der am leichtesten passiert: Man baut das Panel getreu nach, und
der Knopf, um den es eigentlich geht, geht darin unter oder ist im gezeigten
Zustand gar nicht sichtbar. Dann kann der Mensch die Variante nicht beurteilen,
egal wie gut die Begründung daneben ist.

Bau die Bühne deshalb um das strittige Element herum, nicht um die Komponente:
Es sitzt im Blickfeld, ist in beiden Zuständen erreichbar, und der Rest ist so
weit angedeutet, wie es zum Einordnen reicht. Vor dem Weitergehen der
Selbsttest: *Sieht man auf dem ersten Blick, worum es geht?* Wenn du selbst
suchen musst, muss der Mensch es auch.

Setz `hoehe` so, dass der Inhalt den Rahmen füllt. Ein 460 hoher Rahmen mit
180 Pixel Inhalt sieht aus, als wäre etwas kaputt.

**Sieh dir jeden Zustand tatsächlich an, bevor du weitergehst.** Nicht den
Quelltext lesen und im Kopf durchspielen — rendern und anschauen. Hat eine
Variante zwei Zustände, baust du beide einmal isoliert und siehst sie dir an.
Das ist keine Förmlichkeit: In einem Testlauf trugen alle vier Varianten
denselben Fehler, weil die echte Komponente die Kopfzeile im eingeklappten
Zustand aus dem DOM *entfernt* und der Nachbau sie nur versteckt hat. Im Code
sah das richtig aus; im Bild überlagerte die Kopfzeile die Schiene. Solche
Fehler findet nur das Auge.

Wie du renderst, ist gleich — Screenshot mit einem Headless-Browser, oder die
fertige Seite kurz öffnen und hinschauen. Was zählt: Du hast es gesehen,
bevor der Mensch es sieht.

**Baue auf dem echten CSS auf, nicht daneben.** Benutze die Klassennamen aus
der Komponentendatei und die Token-Variablen. Braucht eine Variante eine Farbe
oder ein Maß, das es im Design-System nicht gibt, ist das kein Detail, sondern
ein Nachteil — schreib ihn in die Contra-Liste. Sonst wählt der Mensch etwas
aus, das beim Bauen teurer wird als gedacht.

### 4. Die Dateien schreiben

Leg einen Arbeitsordner an (im Scratchpad-Verzeichnis, nicht im Projekt — das
sind Wegwerf-Entwürfe):

```
<ordner>/
├── varianten.json
├── ist.png                  (optional)
└── varianten/
    ├── variante-1.html
    ├── variante-2.html
    └── …
```

`varianten.json`:

```json
{
  "titel": "Auf- und Zuklappen der linken Seitenleiste",
  "kontext": "packages/ui/src/editor/Editor.tsx · Editor.module.css · tokens.css",
  "ist_bild": "ist.png",
  "ist_notiz": "Heute sitzt ein kleines Chevron-Icon oben rechts in der Leiste.",
  "tokens_css": ["/abs/pfad/tokens.css"],
  "extra_css": ["/abs/pfad/Editor.module.css"],
  "varianten": [
    {
      "nummer": 1,
      "titel": "Schwebende Pille auf der Trennlinie",
      "hoehe": 420,
      "gedanke": "Der Griff gehört dorthin, wo die Grenze verläuft …",
      "pro": ["Immer an derselben Stelle, egal wie breit die Leiste ist"],
      "contra": ["Überlagert bei sehr schmalem Fenster den Inhalt"]
    }
  ]
}
```

`kontext` nennt die Dateien, aus denen du das Aussehen bezogen hast. Das ist
keine Fußnote: Der Mensch sieht daran, wie viel vom Look echt ist und wie viel
du erfunden hast. **Kurz halten** — die Dateinamen reichen, ohne Pfade und ohne
Erläuterung. Was du zu einzelnen Entscheidungen zu sagen hast, gehört in den
`gedanke` der betroffenen Variante, nicht in die Kopfzeile.

Jede `variante-N.html` enthält nur den **Rumpf** — Markup, ein `<style>` für
das Variantenspezifische, ein `<script>` fürs Verhalten. Tokens und
Komponenten-CSS spannt das Skript automatisch davor. Jede Variante läuft in
einem eigenen `<iframe>`, du musst dir also über Klassennamen-Kollisionen
zwischen Varianten keine Gedanken machen.

`gedanke` ist kein Werbetext. Schreib den Überlegungsweg auf, der zu dieser
Lösung geführt hat — was du für das eigentliche Problem hältst und warum diese
Variante darauf antwortet. Der Mensch entscheidet besser, wenn er deine
Begründung kennt, und kann dir widersprechen, wenn dein Problemverständnis
danebenliegt.

### 5. Zeigen

```bash
python3 ~/.claude/skills/gui-varianten/scripts/varianten_zeigen.py <ordner>
```

Das Skript baut die Seite, startet einen lokalen Server und öffnet den Browser.
Starte es **im Hintergrund**, sonst blockiert es die Sitzung, bis der Mensch
abgesendet hat.

Sag danach in einem Satz, was du gebaut hast und worin sich die Varianten
unterscheiden — nicht die ganze Begründung wiederholen, die steht ja auf der
Seite. Nenn ausdrücklich, dass er im Browser auswählen und dazuschreiben kann
oder einfach hier antworten darf, wie er will.

**Dann setz den Wächter auf, ohne den der Rückkanal nur halb funktioniert.**
Startest du ihn nicht, muss der Mensch nach dem Absenden zusätzlich hier
Bescheid sagen — und weiß nicht, dass er das muss, weil die Seite ihm
„Angekommen" gemeldet hat. Ein Hintergrund-Befehl, der wartet, bis die Datei
auftaucht, und dann von selbst diese Sitzung weckt:

```bash
until [ -f "<ordner>/auswahl.json" ]; do sleep 3; done
cat "<ordner>/auswahl.json"
```

**Im Hintergrund starten** (`run_in_background`), nicht im Vordergrund — sonst
blockiert er, bis abgesendet wurde. Sobald er endet, bist du wieder dran und
liest die Antwort aus seiner Ausgabe.

Das Skript löscht `auswahl.json` beim Start, damit der Wächter nicht sofort mit
der Antwort der letzten Runde feuert. `verlauf.json` bleibt liegen.

### 6. Die Antwort aufnehmen

Sendet er im Browser ab, landet die Auswahl in `<ordner>/auswahl.json`:

```json
{ "variante": 3, "notiz": "aber mit dem Icon aus 1 und weniger Abstand oben" }
```

Läuft der Wächter, bekommst du sie von selbst — arbeite direkt damit weiter,
ohne dass der Mensch hier noch etwas sagen muss. Antwortet er stattdessen im
Chat, ist das genauso gut; die Nummern sind das gemeinsame Vokabular.

**Jede Rückmeldung landet zusätzlich in `verlauf.json`** und steht beim
nächsten Bauen unter den Varianten als „Bisher geschickt". Du musst dafür
nichts tun — aber es lohnt, vor einer neuen Runde hineinzusehen: Was dort
steht, ist die Geschichte dieser Gestaltungsfrage, und ein Wunsch, den du zum
zweiten Mal übergehst, war beim ersten Mal schon wichtig.

**Die Nummern bleiben stabil.** Baust du eine weitere Runde, behalten die
überlebenden Varianten ihre Nummer, und Neues bekommt neue Nummern. Sonst
zeigt „mach 3 wie besprochen" plötzlich woandershin.

## Fallen

**Markup aus dem Gedächtnis.** Du hast die Komponente vielleicht in dieser
Sitzung schon gelesen und meinst, sie zu kennen. Lies sie trotzdem. Eine
Variante, deren Struktur von der echten abweicht, verspricht eine Umsetzung,
die dann teurer wird als gezeigt.

**CSS-Module-Klassennamen.** Im Browser tragen sie gehashte Namen
(`_handle_7ea8y_186`), in der `.module.css` stehen die einfachen (`.handle`).
Das Skript liest die Quelldatei, dein Markup benutzt also die **einfachen**
Namen. Nimmst du versehentlich einen gehashten aus dem laufenden Browser,
greift keine Regel und die Variante steht nackt da.

**Gleiche Klassennamen in verschiedenen CSS-Modulen.** Im echten Build trennt
das Hashing sie; hier werden die Quelldateien wörtlich hintereinandergehängt,
und `.tab` aus der einen Datei überschreibt `.tab` aus der anderen. Das ist der
häufigste Grund, warum eine Variante unerklärlich zerschossen aussieht — und
man sucht den Fehler dann im eigenen Markup.

Such nicht von Hand danach:

```bash
python3 ~/.claude/skills/gui-varianten/scripts/css_kollisionen.py <deine CSS-Dateien…>
```

Meldet es Kollisionen, entscheide je Name, welche Datei du wirklich brauchst,
und bau die andere Rolle im Variantenrumpf inline nach.

**Erfundene Tokens.** `var(--irgendwas-neues)` fällt still auf nichts zurück,
und die Variante sieht kaputt aus, ohne dass klar wird warum. Benutze nur
Variablen, die in der Token-Datei wirklich stehen — und wenn eine fehlt, ist
das ein Contra-Punkt, kein Freibrief.

**Fünf Anstriche derselben Idee.** Wenn du beim Schreiben der `gedanke`-Texte
merkst, dass sie sich ähneln, ist das das Signal: Verwirf eine und such eine
Variante, die das Problem anders angeht.

**Zu große Bühne.** Eine ganze Bildschirmmaske als Variante zu bauen kostet
viel und lenkt vom Punkt ab. Zeig den betroffenen Ausschnitt plus so viel
Umgebung, dass man ihn einordnen kann — bei einer Seitenleiste also die Leiste
und ein angedeuteter Inhaltsbereich, nicht die komplette Anwendung.

„Angedeutet" heißt wörtlich angedeutet: eine Fläche in der richtigen
Hintergrundfarbe mit einem Wort darauf („Zeichenfläche") reicht. Sie ist da,
damit die Proportionen stimmen und der Blick eine Kante hat — nicht, damit sie
selbst begutachtet wird. Zeit, die du in den Nachbau der Umgebung steckst,
fehlt bei den Varianten.

## Wenn kein Browser da ist

Läuft die Sitzung ohne Anzeige, erzeugt

```bash
python3 …/varianten_zeigen.py <ordner> --nur-bauen
```

eine einzelne `seite.html`, die der Mensch selbst öffnen kann. Der Rückkanal
entfällt dann — er antwortet im Chat.
