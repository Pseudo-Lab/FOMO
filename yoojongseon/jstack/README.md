# JStack — Zero-Dependency Harness for Claude Code

> 5-gear workflow harness that turns Claude Code into a structured engineering team.  
> G Stack's prompt depth + OMC's orchestration ideas — without any external dependencies.

## What is this?

JStack is a **harness** — an operating system for AI coding agents. It provides structured workflows, safety guardrails, and persistent memory so Claude Code produces consistent, high-quality results across any project.

```
"모델을 교체하면 성능이 10~15% 향상되지만,
 하네스를 교체하면 시스템의 작동 여부 자체가 결정된다."
```

## Features

- **5-gear workflow**: `/office-hours` → `/plan` → `/build` → `/review` → `/ship`
- **Project auto-detection**: New project? Starts with `/office-hours`. Existing project? Resumes from CHECKPOINT.md.
- **Complexity gate**: Simple (1-3 days) / Medium (1-4 weeks) / Complex (1+ month) — different interview depth for each.
- **Forcing Questions**: Structured Ask → Push until → Red flags pattern (inspired by G Stack).
- **Architecture protection**: `/build` blocks architecture changes without approval.
- **Scope creep prevention**: No features outside the plan. Observations are logged, not implemented.
- **CHECKPOINT state machine**: Phase tracking across sessions. Knowledge survives session boundaries.
- **Zero dependencies**: Pure markdown files. No npm, no bun, no tmux, no Playwright.

## Quick Start

```bash
# Clone
git clone https://github.com/YOUR_USERNAME/jstack.git

# Copy to Claude Code config
cp -r jstack/.claude/ ~/.claude/

# Start any project
cd ~/my-new-project
claude
# Type: /office-hours
```

## Architecture

```
.claude/
├── CLAUDE.md                  ← L4: Global rules (always loaded)
├── settings.json              ← L2: Sandbox + hooks (always active)
├── commands/                  ← L3: 5 gears (loaded on invocation)
│   ├── office-hours.md        ← Gear 1: Idea validation
│   ├── plan.md                ← Gear 2: Architecture design
│   ├── build.md               ← Gear 3: Implementation
│   ├── review.md              ← Gear 4: Code review
│   └── ship.md                ← Gear 5: Deploy + retrospective
└── rules/                     ← L4: Conditional rules (auto-loaded by file type)
    ├── python.md              ← *.py
    ├── typescript.md          ← *.ts, *.tsx
    ├── react-native.md        ← Mobile patterns
    └── general.md             ← All files
```

### 4-Layer Harness Architecture

| Layer | Purpose | Always Active? |
|-------|---------|----------------|
| L4 Control | CLAUDE.md + rules/ — what to know and follow | Yes |
| L3 Execution | commands/*.md — which role, which workflow | On invocation only |
| L2 Quality | settings.json + hooks — physical safety | Yes |
| L1 Structure | CHECKPOINT.md + AUDIT.log — persistent memory | Yes |

## Workflow

### New Project (Strict)
```
/office-hours → /plan → /build → /review → /ship
```
No skipping phases. No code before `/plan` is approved.

### Existing Project (Flexible)
- New feature → `/plan` → `/build` → `/review` → `/ship`
- Bug fix → `/build` → `/review`
- Hotfix → `/build` → `/ship`

## Comparison

| | G Stack | OMC | JStack |
|---|---------|-----|--------|
| Size | 150KB+ | 300KB+ | 44KB |
| Dependencies | Bun, Playwright | npm, tmux | None |
| Prompt density | High | Low | High |
| Phase connection | ls file search | Session memory | CHECKPOINT state machine |
| Project auto-gen | ✕ | ✕ | ✅ |
| Architecture protection | ✕ | △ | ✅ |
| Scope creep prevention | ✕ | ✕ | ✅ |
| Parallel execution | △ | ✅ | ✕ (planned) |
| Model routing | ✕ | ✅ | ✕ (planned) |

## Inspired By

- **[G Stack](https://github.com/garrytan/gstack)** by Garry Tan — Forcing Questions pattern, Operating Principles, Anti-slop rules, role-based skill design
- **[oh-my-claudecode](https://github.com/Yeachan-Heo/oh-my-claudecode)** by Yeachan Heo — Multi-agent orchestration concepts, model routing ideas
- **[FOMO](https://pseudo-lab.com)** by 김재현 (Pseudo Lab) — 4-layer harness architecture, 12 harness principles, Rippable harness concept

## Roadmap

- [ ] JStack agents (`team-roles/`) for parallel execution
- [ ] Model routing (Haiku/Sonnet/Opus per task complexity)
- [ ] Browser QA integration
- [ ] Harness self-improvement loop

## License

MIT
