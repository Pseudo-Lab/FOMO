---
name: learn
description: |
  Manage learnings across sessions. Save patterns, pitfalls,
  and preferences discovered during work. Learnings persist
  in AUDIT.log and docs/learnings.md. Search and apply them
  in future sessions. Supports cross-project learning.
allowed-tools:
  - Bash
  - Read
  - Write
  - Edit
  - Grep
  - Glob
  - AskUserQuestion
---

# Learn — Session Learning Manager

You manage what was learned across sessions so the harness gets smarter on this codebase over time.

## Commands

The user can invoke /learn with a sub-command:

### /learn save
Save a new learning from the current session.

Ask via AskUserQuestion:
> What did you learn? Pick a category:
> - A) Pattern — a reusable approach that worked well
> - B) Pitfall — a mistake to avoid next time
> - C) Preference — a style or tool choice to remember

Then ask: "Describe the learning in one sentence."

Write to `docs/learnings.md`:
```
## [{date}] {Category}: {title}
Context: {what was being worked on}
Learning: {the one-sentence description}
Impact: {why this matters for future sessions}
Tags: {relevant keywords for search}
```

Also append to AUDIT.log:
```
[{date}] LEARNING SAVED: {category} — {title}
```

### /learn list
Show all learnings for this project:
```bash
cat docs/learnings.md
```
Display as a numbered list with categories and dates.

### /learn search {query}
Search learnings by keyword:
```bash
grep -i "{query}" docs/learnings.md
```
If cross-project learning is enabled, also search other projects:
```bash
find ~/*/docs/learnings.md -exec grep -il "{query}" {} \;
```

### /learn apply
At the start of any session, automatically search for relevant learnings based on the current task.

1. Read CHECKPOINT.md to understand current context.
2. Search docs/learnings.md for keywords matching the current task.
3. If matches found, display: "Relevant learnings from previous sessions:" and list them.
4. Apply the learnings silently (adjust behavior based on past pitfalls and patterns).

### /learn prune
Review and clean up old or irrelevant learnings:
1. List all learnings with numbers.
2. Ask which ones to remove.
3. Remove selected entries from docs/learnings.md.

## Cross-project learning

If multiple projects exist with docs/learnings.md, /learn can search across all of them.

Ask on first use:
> Enable cross-project learning? This searches learnings from your other projects on this machine. Recommended for solo developers. Skip if you work on separate client codebases.
> - A) Enable
> - B) Keep project-only

Store the preference in project CLAUDE.md under a `## Learning preferences` section.

## Auto-apply rule

When any command (/office-hours, /plan, /build, /review, /ship) starts its Context Gathering phase, automatically run `/learn apply` to surface relevant past learnings.
