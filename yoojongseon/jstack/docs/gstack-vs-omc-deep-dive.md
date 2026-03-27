# G Stack Skills vs OMC Agents — 프롬프트 해부 비교

> 작성일: 2026-03-26  
> 목적: 범용 하네스 설계를 위한 레퍼런스 분석

---

## 1. 구조적 차이 한눈에 보기

### G Stack: "역할 = 파일"

```
gstack/
├── office-hours/SKILL.md.tmpl    ← 517줄, 24.5KB (YC 파트너 역할)
├── plan-ceo-review/SKILL.md.tmpl ← CEO/Founder 제품 리뷰
├── plan-eng-review/SKILL.md.tmpl ← Eng Manager 아키텍처 리뷰
├── review/SKILL.md.tmpl          ← Staff Engineer 코드 리뷰
├── qa/SKILL.md.tmpl              ← QA Engineer + Playwright 브라우저
├── ship/SKILL.md.tmpl            ← Release Engineer
├── retro/SKILL.md.tmpl           ← 회고
└── SKILL.md                      ← /browse (공통 브라우저)
```

- 각 SKILL.md는 **하나의 거대한 마크다운 프롬프트**
- 평균 300~500줄, 역할 철학 + 단계별 워크플로 + 출력 템플릿이 모두 하나의 파일에
- `{{PREAMBLE}}` 블록으로 공통 초기화 (업데이트 체크, 세션 트래킹, 텔레메트리)
- `.tmpl` → 빌드 시 `SKILL.md`로 변환 (메타데이터 주입)

### OMC: "에이전트 = 역할 + 모델 + 도구 조합"

```
~/.claude/agents/
├── architect.md       ← Opus 모델, 분석 전문
├── executor.md        ← Sonnet 모델, 구현 전문
├── explore.md         ← Haiku 모델, 검색 전문
├── designer.md        ← Sonnet 모델, 프론트엔드
├── planner.md         ← Opus 모델, 계획
├── critic.md          ← Opus 모델, 비판
├── analyst.md         ← Opus 모델, 사전 분석
├── qa-tester.md       ← Sonnet 모델, 테스트
├── writer.md          ← Haiku 모델, 문서
├── vision.md          ← Sonnet 모델, 시각 분석
├── security-reviewer.md
├── debugger.md
├── test-engineer.md
├── code-reviewer.md
├── scientist.md
├── tracer.md
├── document-specialist.md
└── ...  (총 18~32개)
```

- 각 에이전트 파일은 **짧은 YAML 헤더 + 시스템 프롬프트**
- 핵심은 `model:` 필드 — 에이전트마다 다른 모델 티어를 지정
- 도구(tools) 접근 권한이 에이전트마다 다름
- 오케스트레이터(메인 Claude)가 Task tool로 호출

---

## 2. G Stack `/office-hours` 전문 해부

### 2.1 메타데이터 (YAML Front Matter)

```yaml
name: office-hours
version: 2.0.0
description: |
  YC Office Hours — two modes. Startup mode: six forcing questions that expose
  demand reality, status quo, desperate specificity, narrowest wedge, observation,
  and future-fit. Builder mode: design thinking brainstorming for side projects.
  Saves a design doc.
  Use before /plan-ceo-review or /plan-eng-review.
allowed-tools:
  - Bash
  - Read
  - Grep
  - Glob
  - Write
  - Edit
  - AskUserQuestion
```

**주목할 점:**
- `allowed-tools`로 이 스킬에서 사용할 수 있는 도구를 **명시적으로 제한**
- `AskUserQuestion`이 핵심 도구 — 대화형 질문이 이 스킬의 본질
- 코드 실행 도구가 없음 → "이 스킬은 코드를 쓰지 않는다"는 제약이 도구 수준에서 강제됨

### 2.2 역할 정의 — 단 두 문장

```
You are a **YC office hours partner**. Your job is to ensure the problem is 
understood before solutions are proposed.
```

**HARD GATE:** 
```
Do NOT invoke any implementation skill, write any code, scaffold any project, 
or take any implementation action. Your only output is a design document.
```

**패턴 분석:** 
G Stack은 역할을 "너는 ~이다"로 짧게 정의하되, **하면 안 되는 것(negative constraint)**을 
매우 강하게 명시합니다. 이것이 프롬프트 밀도를 높이는 핵심 기법입니다.

### 2.3 Phase 구조 — 6단계 워크플로

```
Phase 1: Context Gathering → 코드베이스/기존 문서 파악
Phase 2A: Startup Mode (6 Forcing Questions)  ← 또는
Phase 2B: Builder Mode (디자인 파트너)
Phase 2.5: Related Design Discovery → 기존 디자인 문서 검색
Phase 3: Premise Challenge → 전제 도전
Phase 4: Alternatives Generation → 2-3개 대안 생성 (MANDATORY)
Phase 4.5: Founder Signal Synthesis → 파운더 시그널 수집
Phase 5: Design Doc → 디자인 문서 생성
Phase 6: Handoff → 마무리 + YC 추천
```

### 2.4 핵심 중의 핵심 — The Six Forcing Questions (Startup Mode)

이것이 G Stack의 진짜 가치입니다. 각 질문의 구조를 보세요:

**Q1: Demand Reality (수요 현실)**
```
Ask: "What's the strongest evidence you have that someone actually 
wants this — not 'is interested,' not 'signed up for a waitlist,' 
but would be genuinely upset if it disappeared tomorrow?"

Push until you hear: Specific behavior. Someone paying. Someone 
expanding usage. Someone who would have to scramble if you vanished.

Red flags: "People say it's interesting." "We got 500 waitlist 
signups." "VCs are excited about the space." None of these are demand.
```

**구조 패턴:** `Ask` → `Push until you hear` → `Red flags`
- Ask: 질문 자체 (구체적이고 도전적)
- Push until: 만족스러운 답변의 기준 (수용 조건)
- Red flags: 경고해야 할 나쁜 답변 패턴

**Q2: Status Quo (현상 유지)**
```
Ask: "What are your users doing right now to solve this problem 
— even badly?"

Red flags: "Nothing — there's no solution, that's why the 
opportunity is so big." If truly nothing exists and no one is doing 
anything, the problem probably isn't painful enough.
```

**Q3: Desperate Specificity (절박한 구체성)**
```
Ask: "Name the actual human who needs this most. What's their 
title? What gets them promoted? What gets them fired?"

Red flags: Category-level answers. "Healthcare enterprises." 
"SMBs." "Marketing teams." These are filters, not people. 
You can't email a category.
```

**Q4: Narrowest Wedge (가장 좁은 쐐기)**
```
Ask: "What's the smallest possible version of this that someone 
would pay real money for — this week, not after you build the platform?"

Bonus push: "What if the user didn't have to do anything at all 
to get value? No login, no integration, no setup."
```

**Q5: Observation & Surprise (관찰과 놀라움)**
```
Ask: "Have you actually sat down and watched someone use this 
without helping them? What did they do that surprised you?"

The gold: Users doing something the product wasn't designed for. 
That's often the real product trying to emerge.
```

**Q6: Future-Fit (미래 적합성)**
```
Ask: "If the world looks meaningfully different in 3 years 
— and it will — does your product become more essential or less?"

Red flags: "The market is growing 20% per year." Growth rate 
is not a vision.
```

### 2.5 스마트 라우팅 — 단계 건너뛰기

```
Smart routing based on product stage:
- Pre-product → Q1, Q2, Q3
- Has users → Q2, Q4, Q5  
- Has paying customers → Q4, Q5, Q6
- Pure engineering/infra → Q2, Q4 only
```

**패턴 분석:** 모든 질문을 기계적으로 하지 않고, 상황에 따라 건너뜁니다.
"이미 답변된 질문은 다시 묻지 말라"는 규칙도 있습니다.

### 2.6 Operating Principles — 행동 원칙

```
Specificity is the only currency.
Interest is not demand.
The user's words beat the founder's pitch.
Watch, don't demo.
The status quo is your real competitor.
Narrow beats wide, early.
```

**패턴 분석:** 이것이 "역할에 빙의"하게 만드는 핵심입니다.
단순히 "CEO처럼 생각해"가 아니라, CEO가 어떤 **원칙**으로 판단하는지를 명시합니다.
이 원칙들은 질문의 방향을 결정하고, 답변을 평가하는 기준이 됩니다.

### 2.7 Response Posture — 어조 지침

```
Be direct, not cruel.
Push once, then push again.
Praise specificity when it shows up.
Name common failure patterns.
End with the assignment.
```

### 2.8 Design Doc 출력 템플릿

Startup Mode와 Builder Mode에서 각각 다른 디자인 문서 템플릿을 생성합니다.
문서는 `~/.gstack/projects/{slug}/` 에 저장되며, 후속 스킬들이 자동으로 발견합니다.

```
~/.gstack/projects/{slug}/{user}-{branch}-design-{datetime}.md
```

이 파일 경로 규칙이 중요합니다 — **스킬 간 데이터 전달이 파일 시스템을 통해 이루어집니다.**

### 2.9 Anti-Slop 규칙 (Founder Signal Synthesis)

```
GOOD: "You didn't say 'small businesses' — you said 'Sarah, 
the ops manager at a 50-person logistics company.' That 
specificity is rare."

BAD: "You showed great specificity in identifying your 
target user."
```

**패턴 분석:** AI가 흔히 빠지는 "칭찬 슬롭"을 명시적으로 금지하고, 
구체적 인용(show, don't tell)을 강제합니다.

---

## 3. G Stack `/plan-ceo-review` 핵심 내용 (부분 확보)

### 3.1 4가지 스코프 모드

```
SCOPE EXPANSION — dream big. The agent proposes the ambitious version.
SELECTIVE EXPANSION — hold current scope, surface opportunities one by one.
HOLD SCOPE — maximum rigor on existing plan. No expansions.
SCOPE REDUCTION — find the minimum viable version.
```

**패턴 분석:** 동일한 "CEO 리뷰"인데 사용자가 현재 원하는 것이 
확장인지 축소인지에 따라 완전히 다른 모드로 작동합니다.

### 3.2 Office Hours와의 연결

```bash
# 디자인 문서 자동 발견
DESIGN=$(ls -t ~/.gstack/projects/$SLUG/*-$BRANCH-design-*.md 2>/dev/null | head -1)
```

Office Hours에서 생성된 디자인 문서를 자동으로 읽고, 
이를 "source of truth"로 사용합니다.

### 3.3 CEO Plan 산출물

```
~/.gstack/projects/$SLUG/ceo-plans/{feature}-{date}.md
```

30일 이상된 계획이나 머지된 브랜치의 계획은 자동 아카이브를 제안합니다.

---

## 4. OMC 에이전트 구조 해부

### 4.1 에이전트 정의 파일 형식

```yaml
---
name: architect
description: Your custom description
tools: Read, Grep, Glob, Bash, Edit
model: opus  # or sonnet, haiku
---
Your custom system prompt here...
```

**G Stack과의 결정적 차이:**
- G Stack의 SKILL.md는 300~500줄의 워크플로 전체를 담지만
- OMC의 에이전트 MD는 **짧은 역할 정의 + 모델/도구 지정**이 핵심
- "어떻게 일할지"는 에이전트가 아니라 **스킬(skill)**이 담당

### 4.2 에이전트 계층 구조

```
┌─────────────────┐  ┌─────────────────┐  ┌─────────────────┐
│   PLANNING      │  │   EXECUTION     │  │   SUPPORT       │
├─────────────────┤  ├─────────────────┤  ├─────────────────┤
│ planner (Opus)  │  │ architect(Opus) │  │ explore (Haiku) │
│ critic  (Opus)  │  │ designer (Son)  │  │ writer  (Haiku) │
│ analyst (Opus)  │  │ executor (Son)  │  │ vision  (Son)   │
│                 │  │ qa-tester(Son)  │  │ researcher(Son) │
│                 │  │ debugger (Son)  │  │ doc-specialist  │
│                 │  │ test-engr(Son)  │  │                 │
│                 │  │ code-rev (Opus) │  │                 │
│                 │  │ security (Son)  │  │                 │
└─────────────────┘  └─────────────────┘  └─────────────────┘
```

### 4.3 모델 라우팅 매트릭스

```
Domain        LOW (Haiku)       MEDIUM (Sonnet)    HIGH (Opus)
─────────────────────────────────────────────────────────────
Analysis      architect-low     architect-medium   architect
Execution     executor-low      executor           executor-high
Search        explore           -                  explore-high
Research      -                 document-specialist -
Frontend      designer-low      designer           designer-high
Docs          writer            -                  -
Visual        -                 vision             -
Planning      -                 -                  planner
Critique      -                 -                  critic
Testing       -                 qa-tester          -
Security      security-rev-low  -                  security-reviewer
Data Science  -                 scientist          scientist-high
```

**패턴 분석:** 동일 역할이 3개 모델 티어로 분화되어 있습니다.
"아키텍처 설계"는 Opus, "간단한 구조 파악"은 Haiku — 토큰 비용 최적화.

### 4.4 Task Tool 호출 방식

```python
Task(
    subagent_type="oh-my-claudecode:executor",
    model="sonnet",
    prompt="Implement feature..."
)
```

OMC의 핵심: **메인 Claude(오케스트레이터)가 Task tool로 서브에이전트를 호출**합니다.
각 서브에이전트는 독립적 컨텍스트 윈도우를 가지므로, 
프로젝트 전체 맥락이 아니라 **위임된 작업의 맥락만** 전달받습니다.

### 4.5 OMC의 스킬 계층

```
Execution Skills:   default, planner, orchestrate
Enhancement Skills: ultrawork, git-master, frontend-ui-ux
Guarantee Skills:   ralph (완료 보증)
```

스킬은 에이전트와 다릅니다:
- **에이전트** = "누가" (architect, executor, designer...)
- **스킬** = "어떻게" (ultrawork=병렬, ralph=끝까지, planner=인터뷰)

스킬이 합성(compose)됩니다:
```
Task: "ultrawork: refactor API with proper commits"
Skills activated: ultrawork + default + git-master
```

---

## 5. 핵심 비교 — 같은 역할, 다른 깊이

### "계획/리뷰" 역할 비교

| 차원 | G Stack (office-hours + ceo-review) | OMC (planner + analyst + critic) |
|------|-------------------------------------|-----------------------------------|
| **프롬프트 길이** | office-hours만 517줄/24.5KB | 에이전트 정의 각 ~20-50줄 |
| **철학 명시** | 6가지 Operating Principles 명시 | 없음 (범용 역할 설명만) |
| **질문 설계** | 6개 Forcing Questions + Push/Red flags | "Socratic questioning" (구조 미명시) |
| **단계 구조** | 6 Phase + 서브단계 | 없음 (에이전트가 자율 판단) |
| **출력 형식** | 디자인 문서 템플릿 명시 | 없음 (자유 형식) |
| **anti-slop** | Good/Bad 예시로 구체적 금지 | 없음 |
| **상태 전달** | 파일 시스템 (~/.gstack/projects/) | 메모리/노트 (세션 내) |
| **모드 분기** | Startup/Builder 모드 자동 감지 | 없음 |

### "구현" 역할 비교

| 차원 | G Stack (없음 — Claude 네이티브 의존) | OMC (executor + 다수 에이전트) |
|------|---------------------------------------|--------------------------------|
| **구현 워크플로** | 없음 | ultrawork로 병렬 구현 |
| **모델 선택** | 단일 세션 | Haiku/Sonnet/Opus 자동 라우팅 |
| **병렬 처리** | Conductor로 별도 세션 | tmux split-pane 내장 |
| **완료 보증** | 없음 | ralph 모드 (architect 검증) |

### "리뷰/QA" 역할 비교

| 차원 | G Stack (/review + /qa) | OMC (qa-tester + code-reviewer) |
|------|--------------------------|----------------------------------|
| **리뷰 깊이** | "paranoid staff engineer" 페르소나 | 범용 코드 리뷰 |
| **브라우저 QA** | Playwright 컴파일 바이너리, 실 브라우저 | visual-verdict 스킬 (스크린샷 비교) |
| **상태 유지** | 쿠키, localStorage 지속 | 세션 스코프 |

---

## 6. 하네스 설계를 위한 핵심 교훈

### 교훈 1: 프롬프트 밀도가 결과를 결정한다

G Stack의 가치는 스킬 개수가 아니라 **각 스킬 내부의 지침 밀도**에 있습니다.
`/office-hours` 하나가 24.5KB인 이유는:
- "CEO처럼 생각해"가 아니라 "이 6가지 질문을 이 순서로 물어보되, 
  이런 답이 나오면 빨간 깃발을 세워"라고 구체적으로 지시하기 때문

### 교훈 2: 제약(Constraint)이 품질을 만든다

```
HARD GATE: Do NOT invoke any implementation skill, write any code...
```

"하면 안 되는 것"을 명시하는 게 "해야 할 것"을 명시하는 것보다 
AI 행동 제어에 더 효과적입니다.

### 교훈 3: 상태 전달은 파일 시스템이 답이다

G Stack: `~/.gstack/projects/{slug}/` 에 디자인 문서, CEO 계획 저장
→ 다음 스킬이 `ls -t` + `head -1`로 최신 문서를 자동 발견

OMC: 세션 내 메모리/노트에 의존
→ 세션이 끊기면 맥락이 사라짐

### 교훈 4: "모델 라우팅"은 비용 최적화의 핵심

OMC의 가장 실용적인 기여는 "간단한 검색은 Haiku, 아키텍처 판단은 Opus"
라는 자동 모델 라우팅입니다. 이건 Claude Code 네이티브로도 구현 가능합니다.

### 교훈 5: 워크플로 > 에이전트 수

- G Stack: 5-6개 스킬로 전체 개발 수명 주기 커버
- OMC: 32개 에이전트인데 각각의 프롬프트가 얇음

**결론: 적은 수의 깊은 프롬프트가 많은 수의 얕은 프롬프트보다 효과적입니다.**

---

## 7. 범용 하네스 설계 시 차용할 패턴들

### G Stack에서 가져올 패턴

1. **Forcing Questions 패턴** (Ask → Push until → Red flags)
2. **Phase 구조** (번호가 매겨진 단계 + 각 단계의 입출력 명시)
3. **Operating Principles** (역할의 판단 기준을 원칙으로 명시)
4. **HARD GATE** (하면 안 되는 것을 도구 수준에서 제한)
5. **Smart Routing** (상황에 따라 단계 건너뛰기)
6. **Anti-slop 규칙** (Good/Bad 예시로 출력 품질 제어)
7. **파일 시스템 상태 전달** (~/.gstack/projects/ 패턴)
8. **디자인 문서 템플릿** (구조화된 출력 형식)

### OMC에서 가져올 패턴

1. **모델 티어 라우팅** (작업 복잡도 → 적절한 모델)
2. **도구 접근 권한 분리** (에이전트마다 다른 allowed-tools)
3. **스킬 합성(Composition)** (여러 스킬이 동시 활성화)
4. **ralph 패턴** (완료까지 반복 + architect 검증)
5. **Team 런타임** (독립적 컨텍스트의 병렬 워커)

---

*이 문서는 종선행님의 범용 하네스 설계를 위한 참고 자료입니다.*
*실제 프롬프트 설계 시 이 패턴들을 ProcessLens 및 미래 프로젝트에 맞게 조합하세요.*
