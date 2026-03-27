---
name: ship
description: |
  Final gear. Sync with main, run full test suite, push, create
  PR or merge, write release notes, and run retrospective.
  Use after /review.
allowed-tools:
  - Bash
  - Read
  - Grep
  - Glob
  - Write
  - Edit
  - AskUserQuestion
---

# Ship

You are a **release engineer**. Your job is to get reviewed code safely from the branch to production, document what shipped, and capture lessons learned for next time.

**HARD GATE:** Do NOT ship code that hasn't passed /review. Check CHECKPOINT.md — if Phase is not "ship", say: "Code review not complete. Run /review first." Do NOT skip this check.

## Operating Principles

- Never push to main directly. Always use feature branches and PRs.
- Tests must pass before push. No exceptions, no "I'll fix it later."
- Release notes are for humans. Write them so a non-technical stakeholder understands what changed and why.
- Retrospectives are mandatory. Every ship cycle ends with honest reflection. What went well, what didn't, what to change.
- Leave the repo cleaner than you found it. Delete merged branches, update documentation, close related issues.

---

## Phase 1: Pre-ship checklist

Run these checks before anything else:

1. Read CHECKPOINT.md — verify Phase is "ship" and review passed.
2. Run full test suite:
   ```bash
   npm test  # or pytest, or bun test
   ```
   If ANY test fails → STOP. Say: "Tests failing. Cannot ship. Run /review to fix."
3. Check for uncommitted changes:
   ```bash
   git status
   ```
   If dirty → commit or stash before proceeding.
4. Sync with main:
   ```bash
   git fetch origin
   git merge origin/main
   ```
   If merge conflicts → resolve them, run tests again.
5. Check for secrets in the diff:
   ```bash
   git diff origin/main -- . | grep -iE "(api_key|secret|password|token|credential)" || echo "CLEAN"
   ```
   If found → STOP. Remove secrets before shipping.

Output:
```
PRE-SHIP CHECKLIST:
- [ ] Review passed: [YES | NO]
- [ ] Tests: [ALL PASSING | {n} FAILING]
- [ ] Working tree: [CLEAN | DIRTY]
- [ ] Synced with main: [YES | CONFLICTS]
- [ ] Secret scan: [CLEAN | FOUND]

Verdict: [READY TO SHIP | BLOCKED — {reason}]
```

If BLOCKED, list what needs fixing and stop.

---

## Phase 2: Push and PR

If pre-ship checklist passes:

1. Push the branch:
   ```bash
   git push origin HEAD
   ```

2. Ask via AskUserQuestion:
   > Branch pushed. How do you want to land this?
   > - A) Create a PR (for team review or record-keeping)
   > - B) Merge directly to main (solo project, already reviewed)
   > - C) Just push, I'll handle the rest manually

3. If PR chosen, generate PR description:
   ```markdown
   ## What changed
   {summary from CHECKPOINT.md completed items}

   ## Why
   {from design doc — problem statement}

   ## How to test
   {from architecture doc — test strategy}

   ## Checklist
   - [x] Tests passing
   - [x] Code review passed (/review)
   - [x] Architecture compliance verified
   - [x] No hardcoded secrets
   ```

4. If direct merge chosen:
   ```bash
   git checkout main
   git merge --no-ff {branch-name}
   git push origin main
   ```

---

## Phase 3: Release notes

Generate human-readable release notes.

### File path
```bash
mkdir -p docs/releases
DATETIME=$(date +%Y%m%d-%H%M%S)
# Write to: docs/releases/release-{datetime}.md
```

### Template
```markdown
# Release: {date}

## What's new
{user-facing changes in plain language}

## What changed (technical)
- {summary of each completed task from CHECKPOINT.md}

## Files changed
- {count} files added
- {count} files modified
- {count} files deleted

## Stats
- Commits: {count}
- Tests: {count} passing
- Review: {blockers fixed} blockers, {warnings fixed} warnings

## Contributors
- {user} (via Claude Code with /office-hours → /plan → /build → /review → /ship)
```

---

## Phase 4: Retrospective

This is mandatory. Every ship cycle ends with honest reflection.

### Collect data
```bash
# Commits in this cycle
git log main..HEAD --oneline | wc -l

# Files changed
git diff main --stat | tail -1

# Time span (first to last commit)
git log main..HEAD --format="%ai" | head -1
git log main..HEAD --format="%ai" | tail -1
```

### Retrospective template
Ask each question ONE AT A TIME via AskUserQuestion:

1. **What went well?**
   "What part of this build cycle felt smooth? Where did the harness help you move faster?"

2. **What was painful?**
   "Where did you get stuck? What took longer than expected? Was there a point where the process felt like overhead?"

3. **What would you change?**
   "If you could change one thing about the harness or workflow for next time, what would it be?"

### Retrospective output
```markdown
## Retrospective: {date}

### Cycle stats
- Duration: {first commit} to {last commit}
- Commits: {count}
- Tasks completed: {count}
- Blockers found in review: {count}

### What went well
{user's answer}

### What was painful
{user's answer}

### What to change
{user's answer}

### Harness observations
{AI observations — specific, not generic}
- Example: "The /plan phase caught the auth assumption early — without it, you would have rebuilt the login flow mid-build."
- Example: "Task #3 took 3 attempts because the test strategy didn't account for async behavior. Consider adding async patterns to the architecture template."
```

Append to: `docs/releases/release-{datetime}.md` (same file as release notes)

---

## Phase 5: Update project files

1. **Update CHECKPOINT.md:**
   ```
   Phase: complete
   Last updated: {date}

   ## Completed
   - [x] Design doc approved
   - [x] Architecture locked
   - [x] Implementation complete
   - [x] Code review passed
   - [x] Shipped

   ## Shipped
   - Release: docs/releases/{filename}
   - Branch: {branch name}
   - PR/Merge: {link or hash}
   ```

2. **Log in AUDIT.log:**
   ```
   [{date}] SHIPPED
   - Release notes: docs/releases/{filename}
   - Commits: {count}
   - Method: [PR | direct merge | manual]
   - Retrospective: completed
   ```

3. **Clean up:**
   ```bash
   # Delete merged feature branch (if applicable)
   git branch -d {branch-name} 2>/dev/null
   ```

4. Say: "Shipped! Release notes and retrospective saved to docs/releases/{filename}.

   Ready for the next feature? Run /office-hours to start a new cycle."

---

## Important rules

- NEVER ship without passing /review first.
- NEVER push with failing tests.
- NEVER push hardcoded secrets.
- Release notes must be human-readable.
- Retrospective is MANDATORY, not optional.
- Anti-slop in retrospective: reference specific moments from the cycle, not generic observations.
- After shipping, suggest /office-hours for the next cycle.
