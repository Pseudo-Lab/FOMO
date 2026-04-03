---
name: freeze
description: |
  Lock edits to a specific directory. All file modifications
  outside the boundary are blocked. Use when debugging or
  working on a specific module to prevent accidental changes
  elsewhere. Pair with /careful for maximum safety.
allowed-tools:
  - Bash
  - Read
  - Write
  - Edit
  - Grep
  - Glob
  - AskUserQuestion
---

# Freeze Mode

You are now restricting all file edits to a specific boundary.

## Activation

The user will provide a directory path:
- `/freeze src/billing` → only src/billing/ can be modified
- `/freeze .` → only current directory (no parent access)
- `/freeze src/api src/models` → multiple directories allowed

## Behavior

### ALLOWED inside the boundary:
- Write new files
- Edit existing files
- Delete files
- All Bash commands that modify files

### BLOCKED outside the boundary:
When you are about to Write or Edit a file outside the boundary:
1. STOP.
2. Say: "BLOCKED — Edit outside freeze boundary ({boundary}). File: {filepath}. Skipping this change."
3. Do NOT make the change.
4. Continue with the next action.

### ALWAYS ALLOWED (regardless of boundary):
- Read any file (reading is safe)
- Grep/Glob any directory (searching is safe)
- Bash commands that only read (cat, ls, git log, git diff)
- Git operations (add, commit, push) for files inside boundary

## Important notes

- This blocks Write and Edit tools only.
- Bash commands like `sed` can still modify files outside the boundary — this is accident prevention, not a security sandbox.
- If you genuinely need to edit outside the boundary, tell the user and suggest running `/unfreeze` first.

## Deactivation

User says "unfreeze", "stop freeze", or runs `/unfreeze`.

Say: "Freeze mode activated. Edits restricted to {boundary}. Run /unfreeze to remove the restriction."
