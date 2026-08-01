# Codex

## Install

Codex scans `$HOME/.agents/skills` for personal skills and
`$REPO_ROOT/.agents/skills` for repository skills. Symlinked skill folders are
supported, so the repo stays the single source of truth:

```bash
mkdir -p ~/.agents/skills
ln -s "$PWD/skills/ui-variants" ~/.agents/skills/ui-variants
```

Project-scoped instead: `ln -s … .agents/skills/ui-variants` in the repository.

If a change to the skill doesn't show up, restart Codex.

## Running the script

```bash
python3 ~/.agents/skills/ui-variants/scripts/show_variants.py <dir>
```

## Foreground mode

Run the server in the foreground and wait. It blocks until the human submits,
then prints the choice as JSON and exits, and you read it from the command
output. That is the whole return channel - no watcher needed.

If your sandbox or approval settings kill long-running commands, add
`--timeout 600`. The script then ends on its own terms with a message telling
you to ask in the chat, instead of being killed mid-wait.

## Working directory

`mktemp -d` - the variants are throwaway drafts and do not belong in the user's
project. Note that a Codex sandbox may restrict writes outside the workspace; if
`mktemp -d` is not writable, use a gitignored directory inside the repo and say
so.
