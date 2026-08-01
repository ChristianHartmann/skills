# Claude Code

## Install

Symlink rather than copy, so the repo stays the single source of truth:

```bash
ln -s "$PWD/skills/ui-variants" ~/.claude/skills/ui-variants
```

Project-scoped instead of personal: `.claude/skills/ui-variants` inside the
repository.

## Running the script

Personal or project install:

```bash
python3 ~/.claude/skills/ui-variants/scripts/show_variants.py <dir>
```

Installed as a plugin, the skill directory is under `${CLAUDE_PLUGIN_ROOT}`:

```bash
python3 "${CLAUDE_PLUGIN_ROOT}/skills/ui-variants/scripts/show_variants.py" <dir>
```

## Background mode

Claude Code has a background primitive and wakes the session when a background
command finishes, so use it. Two commands:

1. Start the server with `run_in_background: true`. In the foreground it would
   block the Bash tool until the human submits, and the tool caps out at ten
   minutes.
2. Start the watcher, also with `run_in_background: true`. When it exits you are
   invoked again and read the answer from its output.

```bash
until [ -f "<dir>/choice.json" ]; do sleep 3; done
cat "<dir>/choice.json"
```

Without the watcher the return channel only half works: the page tells the human
"Received", so they think they are done, while nothing wakes the session.

The watcher's output does not appear in the transcript - all that is recorded is
that a background command finished. So quote the answer verbatim in your reply
before acting on it, as step 6 of SKILL.md says. Otherwise the session keeps no
trace of what was actually asked for.

## Working directory

Use the session scratchpad directory named in your system prompt. Variants are
throwaway drafts and do not belong in the user's project.
