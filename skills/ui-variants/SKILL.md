---
name: ui-variants
description: Designs 3-5 numbered, interactive HTML variants for a user-interface change - built from the application's real design tokens and real CSS, each with its rationale, pros and cons, and opened in the browser automatically. Use this skill whenever someone says they don't like something about the interface, asks for alternatives or variants, is unsure how a control should look or behave, sends a screenshot with a complaint, or wants something to be "different" or "nicer" - even when the word "variant" is never said. Likewise when you yourself face a design question with several defensible answers: show them instead of silently picking one.
license: MIT
compatibility: Requires Python 3.9+ and, for the interactive review page, a browser on the same machine. Works without one via --build-only.
---

# UI variants

Design questions are hard to settle in chat. A description like "a floating
handle on the divider" produces two different pictures in your head and in the
human's, and you only find out once it is built. This skill reverses the order:
see first, then decide.

The result is a local page with several numbered variants that look and feel
like the real application, because they use its tokens and its CSS. The human
clicks through them, picks one and writes down what they want changed - and that
comes straight back into the session.

## The steps

### 1. Understand what actually bothers them

Ask if the complaint is vague - but ask *once* and precisely, not in a chain.
What you need to know:

- **Which section?** A single control, a bar, a whole screen. Smaller is
  better: the tighter the section, the more honest the comparison, because the
  surroundings don't distract.
- **Is it the look or the behaviour?** "Too easy to miss" is look, "I can never
  find the button again" is behaviour. For behaviour the variants have to be
  operable, otherwise they don't answer the question.
- **What is already settled?** Existing patterns the variants should follow, or
  explicitly should not.

### 2. Get hold of the current state

The variants are only as convincing as their resemblance to the original. So
gather from the project:

- **The canonical token source** - the file where colours, radii, shadows and
  spacing live as CSS custom properties. In many projects it is called
  `tokens.css`, `variables.css` or `theme.css`. If there is design
  documentation or a project skill, read there which file is the truth.
- **The CSS of the affected component** - the actual file, not your memory.
- **The markup of the affected component** - so your variants use the same
  structure and not a similar-looking invention.

Plus a **screenshot of the current state**, if the application is running or can
be started. Crop it to the same section your variants show, and at a comparable
size - it stands next to them at original size, and two different scales side by
side compare badly.

The same question applies to the crop as to the variants: is the disputed thing
in frame, and enough surroundings to place it? For a handle on a sidebar that
means the header, a piece of content, the edge and a strip of the neighbouring
surface - not half the application, but not the handle alone either, since its
position is precisely the point. It is placed alongside as "variant 0". That is
the anchor: without it the human compares your designs against their memory, and
memory is more generous than reality.

If you can't get a screenshot - app won't run, login in the way - say so and
carry on without one. An invented "before" state is worse than none.

### 3. Design variants that genuinely differ

This is the part that decides between useful and a waste of time.

Three designs differing in spacing, colour and radius are **one** variant in
three coats of paint. They force the human to judge details while the real
question is still open. Instead ask yourself, for each variant: *which different
answer to the problem does it embody?*

An example - complaint: "I don't like the icon for collapsing and expanding the
sidebar."

| | Different answer to the problem |
| --- | --- |
| 1 | The handle belongs on the edge between panel and content, not inside the panel - it separates the two, after all |
| 2 | No handle: clicking the narrow rail itself expands it |
| 3 | The handle stays but becomes a labelled surface at the top of the panel |
| 4 | No visible control at all - the panel collapses by itself when you leave it |

Each of those has different costs. That is exactly why the comparison is worth
it. Three to five is right; fewer is no choice, more is an imposition.

**The variants have to be operable** when the complaint is about behaviour. If a
panel expands and collapses, it expands and collapses in the variant too - with
a few lines of JavaScript directly in the variant file. A still image cannot
answer whether something feels good.

**The disputed thing must be visible - immediately, and in both states.** This is
the mistake that happens most easily: you faithfully rebuild the panel, and the
button that the whole thing is about disappears inside it, or isn't visible at
all in the state you show. Then the human cannot judge the variant, no matter how
good the rationale next to it is.

So build the stage around the disputed element, not around the component: it
sits in the field of view, it is reachable in both states, and the rest is
suggested only as far as it takes to place it. Before moving on, the self-test:
*can you see at a glance what this is about?* If you have to search for it, so
does the human.

Set `height` so the content fills the frame. A 460-tall frame with 180 pixels of
content looks like something is broken.

**Actually look at every state before you move on.** Not read the source and play
it through in your head - render it and look. If a variant has two states, you
build both once in isolation and look at them. This is not a formality: in one
test run all four variants carried the same bug, because the real component
*removes* the header from the DOM in the collapsed state and the rebuild only
hid it. In the code that looked right; in the picture the header covered the
rail. Only the eye finds mistakes like that.

How you render is irrelevant - a screenshot with a headless browser, or briefly
opening the finished page and looking. What counts: you saw it before the human
did.

**Build on the real CSS, not next to it.** Use the class names from the component
file and the token variables. If a variant needs a colour or a measurement that
doesn't exist in the design system, that is not a detail but a drawback - write
it into the cons list. Otherwise the human picks something that turns out more
expensive to build than expected.

### 4. Write the files

Create a working directory - throwaway drafts belong outside the project. Use
your agent's scratchpad or temp directory if it has one, otherwise `mktemp -d`.

```
<dir>/
├── variants.json
├── current.png              (optional)
└── variants/
    ├── variant-1.html
    ├── variant-2.html
    └── …
```

`variants.json`:

```json
{
  "title": "Collapsing and expanding the left sidebar",
  "context": "Editor.tsx · Editor.module.css · tokens.css",
  "current_image": "current.png",
  "current_note": "Today a small chevron icon sits at the top right of the panel.",
  "tokens_css": ["/abs/path/tokens.css"],
  "extra_css": ["/abs/path/Editor.module.css"],
  "variants": [
    {
      "number": 1,
      "title": "Floating pill on the divider",
      "height": 420,
      "rationale": "The handle belongs where the boundary runs …",
      "pros": ["Always in the same place, however wide the panel is"],
      "cons": ["Overlaps the content in a very narrow window"]
    }
  ]
}
```

`context` names the files you took the appearance from. That is not a footnote:
it shows the human how much of the look is real and how much you invented. **Keep
it short** - the file names are enough, without paths and without explanation.
Whatever you have to say about individual decisions belongs in the `rationale` of
the variant concerned, not in the header.

Each `variant-N.html` contains only the **body** - markup, a `<style>` for what
is specific to the variant, a `<script>` for the behaviour. Tokens and component
CSS are prepended automatically by the script. Each variant runs in its own
`<iframe>`, so you don't have to think about class-name collisions between
variants.

`rationale` is not marketing copy. Write down the line of reasoning that led to
this solution - what you take the actual problem to be and why this variant
answers it. The human decides better knowing your reasoning, and can contradict
you when your understanding of the problem is off.

### 5. Show it

```bash
python3 <skill-dir>/scripts/show_variants.py <dir>
```

`<skill-dir>` is the directory this SKILL.md lives in. See `references/` for the
exact command and the background idiom in your agent - `claude-code.md`,
`codex.md`, `cursor.md` or `generic.md`.

The script builds the page, starts a local server and opens the browser. There
are two ways to run it:

**In the foreground - works in every agent.** The command blocks until the human
submits, then prints the choice as JSON and exits, and you read it from the
output. If your agent kills commands after a fixed time, pass
`--timeout <seconds>` so it ends on its own terms with a usable message instead
of being killed.

**In the background - if your agent can run detached commands and wake up when
one finishes.** Start the script detached, then set a watcher on the result file:

```bash
until [ -f "<dir>/choice.json" ]; do sleep 3; done
cat "<dir>/choice.json"
```

**Don't skip the watcher if you went the background route.** Without it the human
has to additionally report back here after submitting - and doesn't know they
have to, because the page told them "Received".

The script deletes `choice.json` on start, so the watcher doesn't fire
immediately with the previous round's answer. `history.json` stays.

Afterwards, say in one sentence what you built and how the variants differ - not
the whole rationale again, that is on the page. Explicitly mention that they can
pick and comment in the browser, or simply answer here, whichever they prefer.

### 6. Take in the answer

When they submit in the browser, the choice lands in `<dir>/choice.json`:

```json
{
  "variant": 3,
  "note": "but with the icon from 1 and less space above",
  "notes": {
    "1": "the icon is right, the position is not",
    "4": "too clever, forget this one"
  }
}
```

`variant` is the favourite and may be `null` - none of them was it. `note` is
the general reply. `notes` holds remarks written against a single variant
through its Comment button, keyed by number; it is absent when there are none.
Read all three: a `notes` entry is the most specific thing you get, because the
human wrote it with that variant in front of them.

Carry on with it directly, without the human having to say anything more here.
If they answer in the chat instead, that is just as good; the numbers are the
shared vocabulary.

**Write the answer out before you act on it.** Quote the chosen number and the
note verbatim in your reply, then say what you take it to mean. The reply came
in through a channel the session log does not show: what stands there is that a
background command finished, not what the human asked for. Without you repeating
it, neither of you can reconstruct weeks later why the work went the way it did
- and the human cannot catch it when you have understood the note differently
than it was meant.

**Every reply also lands in `history.json`** and appears below the variants as
"Sent so far" the next time the page is built. You don't have to do anything for
that - but it is worth looking in before a new round: what is in there is the
history of this design question, and a wish you pass over for the second time was
already important the first time.

**The numbers stay stable.** If you build another round, the surviving variants
keep their number and new things get new numbers. Otherwise "make 3 the way we
discussed" suddenly points somewhere else.

## Pitfalls

**Markup from memory.** You may have read the component earlier in this session
and think you know it. Read it anyway. A variant whose structure differs from the
real one promises an implementation that then costs more than what was shown.

**CSS module class names.** In the browser they carry hashed names
(`_handle_7ea8y_186`), in the `.module.css` the plain ones (`.handle`) are what
you find. The script reads the source file, so your markup uses the **plain**
names. If you accidentally take a hashed one from the running browser, no rule
matches and the variant stands there naked.

**Identical class names in different CSS modules.** In the real build the hashing
keeps them apart; here the source files are concatenated verbatim, and `.tab`
from one file overrides `.tab` from the other. This is the most common reason a
variant looks inexplicably broken - and you then go looking for the bug in your
own markup.

Don't search for them by hand:

```bash
python3 <skill-dir>/scripts/css_collisions.py <your CSS files…>
```

If it reports collisions, decide per name which file you actually need, and
rebuild the other role inline in the variant body.

**Invented tokens.** `var(--something-new)` silently falls back to nothing, and
the variant looks broken without it being clear why. Use only variables that
really exist in the token file - and if one is missing, that is a cons entry, not
a licence.

**Five coats of paint on the same idea.** If, while writing the `rationale`
texts, you notice they resemble each other, that is the signal: throw one away
and look for a variant that approaches the problem differently.

**Too big a stage.** Building a whole screen as a variant costs a lot and
distracts from the point. Show the affected section plus enough surroundings to
place it - for a sidebar that means the panel and a suggested content area, not
the complete application.

"Suggested" means literally suggested: a surface in the right background colour
with one word on it ("Canvas") is enough. It is there so the proportions are
right and the eye has an edge to rest on - not so it gets judged itself. Time you
put into rebuilding the surroundings is missing from the variants.

## When there is no browser

If the session runs without a display,

```bash
python3 <skill-dir>/scripts/show_variants.py <dir> --build-only
```

produces a single `page.html` the human can open themselves. There is no return
channel in that mode - they answer in the chat.

`--no-browser` is the milder version: the server runs as usual and the return
channel works, only the browser isn't launched. Print the URL and let the human
open it. Use this when the agent has no display but the human is on the same
machine.
