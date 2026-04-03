# JStack — Zero-Dependency Harness for Claude Code

> 9-command workflow harness that turns Claude Code into a structured engineering team.
> G Stack's prompt depth + OMC's orchestration ideas — without any external dependencies.

## What is this?

JStack is a **harness** — an operating system for AI coding agents. It provides structured workflows, safety guardrails, and persistent memory so Claude Code produces consistent, high-quality results across any project.

## Features

- **5-gear workflow**: `/office-hours` → `/plan` → `/build` → `/review` → `/ship`
- **Autoplan**: `/autoplan` runs the full planning pipeline in one command
- **Safety modes**: `/careful` warns before destructive commands, `/freeze` locks edits to one directory
- **Session learning**: `/learn` saves patterns and pitfalls across sessions, supports cross-project learning
- **10-star product thinking**: Don't build the literal request — find the 10x product hiding inside it
- **Project auto-detection**: New project? Starts with `/office-hours`. Existing? Resumes from CHECKPOINT.md
- **Complexity gate**: Simple / Medium / Complex — different interview depth for each
- **Architecture protection**: `/build` blocks architecture changes without approval
- **Scope creep prevention**: No features outside the plan. Observations logged, not implemented
- **CHECKPOINT state machine**: Phase tracking across sessions. Knowledge survives session boundaries
- **Zero dependencies**: Pure markdown files. No npm, no bun, no tmux, no Playwright

## Quick Start

```bash
git clone https://github.com/YOUR_USERNAME/jstack.git
cp -r jstack/.claude/ ~/.claude/
cd ~/my-new-project && claude
# Type: /office-hours
```

## Architecture

```
.claude/
├── CLAUDE.md                  ← L4: Global rules (always loaded)
├── settings.json              ← L2: Sandbox + hooks (always active)
├── commands/                  ← L3: 9 commands (loaded on invocation)
│   ├── office-hours.md        ← Idea validation + 10-star product thinking
│   ├── plan.md                ← Architecture design
│   ├── build.md               ← Implementation
│   ├── review.md              ← Code review
│   ├── ship.md                ← Deploy + retrospective
│   ├── autoplan.md            ← Auto pipeline: office-hours → plan
│   ├── careful.md             ← Warn before destructive commands
│   ├── freeze.md              ← Lock edits to specific directory
│   └── learn.md               ← Session learning manager
└── rules/                     ← L4: Conditional rules (auto-loaded)
    ├── python.md              ← *.py
    ├── typescript.md          ← *.ts, *.tsx
    ├── react-native.md        ← Mobile patterns
    └── general.md             ← All files
```

### 4-Layer Harness Architecture

| Layer | Purpose | Always Active? |
|-------|---------|----------------|
| L4 Control | CLAUDE.md + rules/ | Yes |
| L3 Execution | commands/*.md | On invocation only |
| L2 Quality | settings.json + hooks | Yes |
| L1 Structure | CHECKPOINT.md + AUDIT.log + learnings | Yes |

## Comparison

| | G Stack | OMC | JStack |
|---|---------|-----|--------|
| Size | 150KB+ | 300KB+ | 51KB |
| Dependencies | Bun, Playwright | npm, tmux | None |
| Commands | 31 | 40+ skills | 9 |
| Prompt density | High | Low | High |
| Phase connection | ls file search | Session memory | CHECKPOINT state machine |
| Project auto-gen | ✕ | ✕ | ✅ |
| Architecture protection | ✕ | △ | ✅ |
| Scope creep prevention | ✕ | ✕ | ✅ |
| Session learning | ✅ /learn | ✕ | ✅ /learn |
| Safety modes | ✅ /freeze /careful | ✕ | ✅ /freeze /careful |
| Parallel execution | △ | ✅ | ✕ (planned) |

## Inspired By

- **[G Stack](https://github.com/garrytan/gstack)** by Garry Tan — Forcing Questions, Anti-slop, 10-star product thinking, /freeze + /careful safety modes, /learn session learning
- **[oh-my-claudecode](https://github.com/Yeachan-Heo/oh-my-claudecode)** by Yeachan Heo — Multi-agent orchestration concepts
- **[FOMO](https://pseudo-lab.com)** by Pseudo Lab — 4-layer harness architecture, 12 harness principles

## Roadmap

- [ ] JStack agents (`team-roles/`) for parallel execution
- [ ] Model routing (Haiku/Sonnet/Opus per task complexity)
- [ ] Browser QA integration
- [ ] /codex cross-model review
- [ ] Harness self-improvement loop

## License

MIT
