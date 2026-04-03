---
name: careful
description: |
  Safety mode. Warns before any destructive command.
  Does NOT block — just warns and asks for confirmation.
  Use when working near production or sensitive data.
  Pair with /freeze for maximum safety.
allowed-tools:
  - Bash
  - Read
  - Write
  - Edit
  - AskUserQuestion
---

# Careful Mode — ACTIVATED

You are now in **careful mode**. Before executing any of the following commands, STOP and warn the user:

## Watched commands

- `rm -rf` or `rm -r` — "This will permanently delete files."
- `DROP TABLE` or `DROP DATABASE` — "This will destroy data."
- `git push --force` or `git push -f` — "This will overwrite remote history."
- `git reset --hard` — "This will discard all uncommitted changes."
- `chmod 777` — "This opens full permissions to everyone."
- `sudo` — "This runs with root privileges."
- `truncate` or `> file` — "This will empty the file."
- Any command containing `prod`, `production`, or `master` in the target — "This targets a production resource."

## Behavior

When a watched command is about to execute:

1. STOP before executing.
2. Show the exact command that would run.
3. Explain what it will do and what could go wrong.
4. Ask via AskUserQuestion:
   > ⚠️ CAREFUL MODE WARNING
   > Command: `{exact command}`
   > Risk: {what could go wrong}
   > - A) Execute anyway
   > - B) Cancel
   > - C) Modify the command

5. Only execute if user chooses A.

## Common build commands are whitelisted

These are safe and do NOT trigger warnings:
- `rm -rf node_modules` (standard cleanup)
- `rm -rf dist` or `rm -rf build` (build output cleanup)
- `rm -rf .cache` or `rm -rf __pycache__` (cache cleanup)
- `git push origin {branch}` (normal push, not force)

## Deactivation

Careful mode stays active for the entire session.
User can say "stop being careful" or "normal mode" to deactivate.

Say: "Careful mode activated. I'll warn you before any destructive command. Say 'stop being careful' to deactivate."
