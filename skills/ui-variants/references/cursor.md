# Cursor

## Install

Cursor discovers skills in `~/.agents/skills/` and `~/.cursor/skills/`
(personal) and `.agents/skills/` and `.cursor/skills/` (project). It also reads
the Claude Code and Codex locations, so if you already installed the skill for
one of those, Cursor picks it up as well.

The vendor-neutral location is the best default:

```bash
mkdir -p ~/.agents/skills
ln -s "$PWD/skills/ui-variants" ~/.agents/skills/ui-variants
```

## Running the script

```bash
python3 ~/.agents/skills/ui-variants/scripts/show_variants.py <dir>
```

## Foreground mode

Run the server in the foreground and wait. It blocks until the human submits,
then prints the choice as JSON and exits, and you read it from the command
output. No watcher needed.

Add `--timeout 600` if long-running commands get cut off.

## Working directory

`mktemp -d`. The variants are throwaway drafts and do not belong in the user's
project.
