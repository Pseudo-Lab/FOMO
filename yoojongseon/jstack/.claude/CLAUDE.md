# Global Harness

You are operating inside a structured harness. Follow these rules in every session.

## Available commands

| Command | Phase | Purpose |
|---------|-------|---------|
| /office-hours | Ideation | Validate the idea before planning. Produces a design doc. |
| /plan | Architecture | Lock technical decisions, data flow, and test strategy. |
| /build | Implementation | Write code following the approved plan. |
| /review | Quality | Find bugs that pass CI but break in production. |
| /ship | Delivery | Sync, test, commit, and write release notes. |

## Command routing

When the user describes a task, suggest the right command:

- Vague idea, new project, "I want to build..." → /office-hours
- Architecture decisions, tech stack, "how should I structure..." → /plan
- Write code, implement, fix, add feature → /build
- Check quality, find bugs, review PR → /review
- Deploy, push, merge, release → /ship

## Workflow rules

- For NEW projects (no project CLAUDE.md exists):
  STRICT: Must follow /office-hours → /plan → /build → /review → /ship.
  Do NOT skip phases. Do NOT write code before /plan is approved.

- For EXISTING projects (project CLAUDE.md exists):
  Start at the appropriate phase based on the task:
  - New feature → /plan → /build → /review → /ship
  - Bug fix → /build → /review
  - Hotfix → /build → /ship
  Always ask: "This looks like a [bug fix]. Starting at /build — correct?"

- Each phase produces an artifact that the next phase reads.
- Between phases, STOP and wait for user confirmation before proceeding.
- If no project CLAUDE.md exists, suggest running /office-hours first.

---

## Coding conventions

### Universal rules (all languages)
- Write small, focused functions. Max 50 lines per function.
- Name variables and functions descriptively. No single-letter names except loop counters.
- Add error handling for all external calls (API, DB, file I/O).
- Never hardcode secrets, API keys, or credentials. Use environment variables.
- Write tests alongside implementation. No PR without tests.

### Language-specific rules
Conditional rules are loaded from `~/.claude/rules/` based on file type.
Do NOT repeat these rules here — they are injected automatically.

Available rule files:
- `python.md` → globs: `*.py` — PEP8, type hints, docstrings
- `typescript.md` → globs: `*.ts, *.tsx` — strict mode, no any
- `react-native.md` → globs: `*.tsx` — mobile-specific patterns
- `general.md` → globs: `*` — git commit message format

### Git conventions
- Branch naming: `feat/{slug}`, `fix/{slug}`, `refactor/{slug}`
- Commit messages: conventional commits format
  - `feat: add whisky tasting note CRUD`
  - `fix: resolve Supabase RLS policy conflict`
  - `refactor: extract analysis module`
- Commit frequently. One logical change per commit.

---

## Context management

### Context budget
- Keep context window usage below 40%. When approaching this limit, use /compact to summarize and free space.
- After 3 compacts in one session, start a new session with /clear.
- Transfer key decisions to CHECKPOINT.md before clearing.

### What NOT to put in this file
- Directory structures the agent can discover via Glob/Grep
- Rules that linters/formatters already enforce
- Domain knowledge (belongs in project CLAUDE.md)
- Full API documentation (link to external docs instead)

### File reading priority
When starting a task, read files in this order:
1. Project CLAUDE.md (if exists)
2. CHECKPOINT.md (if exists)
3. Relevant source files for the task
Do NOT read the entire codebase. Read only what the current task requires.

---

## Memory & file rules

### Project memory structure
Every project must maintain these files:

| File | Purpose | Update timing |
|------|---------|---------------|
| CHECKPOINT.md | Milestones, current status, next steps | After each phase completion |
| docs/designs/*.md | Design docs from /office-hours and /plan | Created during planning |
| AUDIT.log | Append-only decision log | After every significant decision |

### CHECKPOINT.md format
```
# Checkpoint
## Current status
Phase: [office-hours | plan | build | review | ship]
Last updated: {date}

## Completed
- [x] Design doc approved
- [x] Architecture locked

## In progress
- [ ] API endpoints implementation

## Key decisions
- Chose Supabase over Firebase because: {reason}
- Using SHAP over LIME because: {reason}

## Next steps
1. {next action}
```

### File rules
- NEVER delete CHECKPOINT.md or AUDIT.log.
- AUDIT.log is append-only. Never edit or overwrite existing entries.
- Design docs are immutable once approved. Create a new version instead of editing.
- Before starting any session, read CHECKPOINT.md to restore context.

---

## Project detection

### New vs existing project
On session start, check:
1. Does `./CLAUDE.md` (project-level) exist?
   - NO → This is a new project. Say: "No project harness detected. Run /office-hours to set up this project." Do NOT write any code until /office-hours is complete.
   - YES → Read it. Follow project-specific rules.

2. Does `./CHECKPOINT.md` exist?
   - YES → Read it. Resume from last known state.
   - NO → If project CLAUDE.md exists but no CHECKPOINT, create CHECKPOINT.md with status "Phase: build".

### Complexity gate
When /office-hours or /plan runs, assess project complexity:

- **Simple** (1-3 day effort): Single feature, one data model, no auth.
  → Short interview. Lightweight design doc. Minimal architecture.

- **Medium** (1-4 week effort): Multiple features, auth, external APIs.
  → Standard interview. Full design doc. Architecture diagrams.

- **Complex** (1+ month effort): Domain-specific logic, multi-tenancy, data pipelines, multiple integrations.
  → Deep interview with Forcing Questions. Comprehensive design doc. Full architecture review. Consider splitting into sub-projects.

The agent determines complexity from user answers, NOT from the initial request. A "simple app" may reveal complex requirements during questioning.
