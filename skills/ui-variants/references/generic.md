# Any other agent

## If your agent supports Agent Skills

Most agents that read the [Agent Skills](https://agentskills.io) format scan
either `~/.agents/skills/` (the vendor-neutral location) or a directory of their
own. Symlink the skill into whichever your agent uses:

```bash
mkdir -p ~/.agents/skills
ln -s "$PWD/skills/ui-variants" ~/.agents/skills/ui-variants
```

Check your agent's documentation for the exact path. Gemini CLI, GitHub Copilot
and VS Code, OpenCode, Amp, Goose, Kiro and Factory all support the format; the
locations differ.

## If your agent has no skill support

The skill still works - it just has to be pointed at. Reference it from whatever
instruction file your agent reads (`AGENTS.md`, `GEMINI.md`,
`.github/copilot-instructions.md`):

```markdown
When a user-interface design question comes up with more than one defensible
answer, follow the instructions in `skills/ui-variants/SKILL.md`.
```

The only real requirement is that the agent can run shell commands and write
files. Python 3.9+ with the standard library is enough; there are no
dependencies to install.

## Running the script

```bash
python3 <path-to-skill>/scripts/show_variants.py <dir>
```

Foreground is the portable mode: the command blocks until the human submits,
then prints the choice as JSON and exits, and you read it from the output. Add
`--timeout <seconds>` if your agent cuts off long-running commands - the script
then ends cleanly with a message telling you to ask in the chat.

If your agent can run detached commands *and* wake up when one finishes, the
background mode from `claude-code.md` applies to it too.

## No display, or a remote agent

The script serves on `127.0.0.1` and tries to open a browser. Two fallbacks:

- `--no-browser` - the server runs as usual, so the return channel still works;
  only the browser is not launched. Print the URL and let the human open it.
  Right when the agent has no display but the human is on the same machine.
- `--build-only` - writes a single self-contained `page.html` and exits, no
  server. Right when the human cannot reach `127.0.0.1` at all: an agent in a
  container, a VM or a cloud sandbox. There is no return channel then - the
  human answers in the chat, using the variant numbers.

If you are unsure whether the human can reach the port, say which mode you chose
and why, so they can correct you in one sentence.

## Working directory

Variants are throwaway drafts and do not belong in the user's project. Use your
agent's scratchpad or temp directory if it has one, otherwise `mktemp -d`. If the
sandbox forbids writing outside the workspace, use a gitignored directory inside
the repository and say so.
