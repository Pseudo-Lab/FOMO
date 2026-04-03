---
name: autoplan
description: |
  Automatic review pipeline. Runs /office-hours → /plan in
  sequence with minimal user intervention. Surfaces only
  decisions that require human judgment. Use when you want
  the full planning flow in one command.
allowed-tools:
  - Bash
  - Read
  - Grep
  - Glob
  - Write
  - Edit
  - AskUserQuestion
---

# Autoplan — Automatic Planning Pipeline

Run the full planning flow in one command. Each phase runs automatically, stopping only when human judgment is needed.

## Pipeline

```
/office-hours (idea validation)
      ↓ auto-transition when design doc is approved
/plan (architecture design)
      ↓ auto-transition when architecture is approved
Ready for /build
```

## How it works

### Step 1: Run /office-hours
Execute the full /office-hours flow:
- Context gathering
- Mode detection (Product / Builder)
- Forcing Questions (complexity-routed)
- Premise Challenge
- Alternatives generation
- Design doc generation

**STOP for human judgment at:**
- Mode selection (Product vs Builder)
- Each Forcing Question response
- Premise agree/disagree
- Approach selection
- Design doc approval

**Auto-proceed when:**
- Context gathering completes
- Smart-skip triggers
- File creation (docs/designs/, CHECKPOINT.md)

### Step 2: Auto-transition to /plan
Once design doc is APPROVED:
1. Say: "Design doc approved. Transitioning to /plan..."
2. Automatically invoke /plan with the approved design doc.

### Step 3: Run /plan
Execute the full /plan flow:
- Context gathering (reads the just-created design doc)
- Hidden assumptions audit
- Architecture design (file structure, data model, API, tests)
- Architecture document generation

**STOP for human judgment at:**
- Each hidden assumption question
- Architecture approval
- Simplification requests

**Auto-proceed when:**
- Context gathering completes
- Architecture doc file creation
- CHECKPOINT.md update

### Step 4: Complete
Once architecture is APPROVED:
1. Update CHECKPOINT.md to Phase: build
2. Say: "Planning complete. Design doc and architecture locked. Run /build to start implementation. First task: {task #1 from implementation order}."

## Important rules

- NEVER skip Forcing Questions or Premise Challenge, even in autoplan mode. These require human judgment.
- NEVER auto-approve design docs or architecture docs. Always present to user for explicit approval.
- If user says "stop" at any point → exit autoplan, save current state to CHECKPOINT.md.
- Anti-slop rules from /office-hours still apply.
- All outputs (design doc, architecture doc, CHECKPOINT.md, AUDIT.log) are created exactly as in the individual commands.

## When to use

- New project from scratch → `/autoplan`
- Already have a design doc → skip, just use `/plan`
- Already have architecture → skip, just use `/build`
