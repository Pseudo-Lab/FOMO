# JStack — Claude Code용 제로 의존성 하네스

> G Stack의 프롬프트 깊이 + OMC의 오케스트레이션 아이디어를 결합한 4계층 범용 하네스.
> 외부 의존성 없이 마크다운 파일만으로 작동합니다.

---

## 한눈에 보기

| 항목 | 내용 |
|------|------|
| 크기 | 2,048줄 · 15개 파일 · 51KB |
| 외부 의존성 | 없음 (마크다운 파일만) |
| 워크플로 | 9개 커맨드: 5단 기어 + /autoplan + /careful + /freeze + /learn |
| 아키텍처 | 4계층: L4 통제 → L3 실행 → L2 품질 → L1 구조 |
| 영감 | G Stack (Garry Tan), OMC (oh-my-claudecode), FOMO (Pseudo Lab) |

## 핵심 기능

- **5단 기어 워크플로** — 아이디어 검증부터 배포+회고까지 구조화된 흐름
- **10-star product 사고법** — 요청을 곧이곧대로 구현하지 않고 숨은 10배짜리 제품을 찾기
- **자동 기획 파이프라인** — `/autoplan`으로 기획부터 아키텍처까지 한 커맨드에
- **안전 모드** — `/careful`로 위험 명령어 경고, `/freeze`로 디렉토리 잠금
- **세션 간 학습** — `/learn`으로 패턴과 실수를 저장, 다음 세션에서 자동 적용
- **프로젝트 자동 감지** — 새 프로젝트면 `/office-hours`부터, 기존이면 CHECKPOINT에서 재개
- **복잡도 게이트** — Simple/Medium/Complex 자동 분기로 프로젝트 규모에 맞는 인터뷰 깊이
- **아키텍처 보호** — `/build`에서 승인 없는 설계 변경을 물리적으로 차단
- **스코프 크리프 방지** — 계획에 없는 기능은 구현 안 하고 관찰만 기록
- **CHECKPOINT 상태머신** — 세션이 끊겨도 다음 세션에서 자동으로 맥락 복원
- **제로 의존성** — npm, bun, tmux, Playwright 필요 없음

## G Stack / OMC와 비교

| 지표 | G Stack | OMC | JStack |
|------|---------|-----|--------|
| 크기 | 150KB+ | 300KB+ | 51KB |
| 외부 의존성 | Bun, Playwright | npm, tmux | 없음 |
| 단계 간 연결 | ls로 파일 탐색 | 세션 메모리 의존 | CHECKPOINT 상태머신 |
| 프로젝트 자동 생성 | ✕ | ✕ | ✅ |
| 아키텍처 보호 | ✕ | △ | ✅ |
| 스코프 크리프 방지 | ✕ | ✕ | ✅ |
| 안전 모드 (/careful, /freeze) | ✅ | ✕ | ✅ |
| 세션 간 학습 (/learn) | ✅ | ✕ | ✅ |
| 자동 기획 (/autoplan) | ✅ | ✕ | ✅ |
| 병렬 실행 | △ | ✅ | ✕ (추후) |

## 빠른 시작

```bash
# 1. 클론
git clone https://github.com/YOUR_USERNAME/jstack.git

# 2. Claude Code 설정 폴더에 복사
cp -r jstack/.claude/ ~/.claude/

# 3. 아무 프로젝트에서 시작
cd ~/my-new-project
claude
# /office-hours 입력
```

---

## 이게 뭔가요?

이 하네스는 Claude Code가 일관되고 안전하게 작동하도록 만드는 **AI 운영체제**입니다.
어떤 프로젝트를 시작하든 동일한 품질의 워크플로를 보장합니다.

---

## 폴더 구조

```
~/.claude/                          ← 글로벌 (모든 프로젝트 공통)
├── CLAUDE.md                       ← 이 파일. 항상 로딩됨.
├── commands/                       ← 9개 커맨드 (슬래시 커맨드)
│   ├── office-hours.md             ← /office-hours: 아이디어 검증 + 10-star 사고법
│   ├── plan.md                     ← /plan: 아키텍처 설계
│   ├── build.md                    ← /build: 구현
│   ├── review.md                   ← /review: 코드 리뷰 + QA
│   ├── ship.md                     ← /ship: 배포 + 회고
│   ├── autoplan.md                 ← /autoplan: office-hours→plan 자동 연쇄
│   ├── careful.md                  ← /careful: 위험 명령어 경고 모드
│   ├── freeze.md                   ← /freeze: 디렉토리 잠금 모드
│   └── learn.md                    ← /learn: 세션 간 학습 관리
├── rules/                          ← 조건부 규칙 (파일 타입별 자동 적용)
│   ├── python.md                   ← *.py 파일에 자동 적용
│   ├── typescript.md               ← *.ts, *.tsx 파일에 자동 적용
│   ├── react-native.md             ← 모바일 전용 패턴
│   └── general.md                  ← 모든 파일에 적용 (커밋 메시지 등)
└── settings.json                   ← 샌드박스 (Allow/Deny 리스트)

{프로젝트}/                          ← 프로젝트별 (자동 생성됨)
├── CLAUDE.md                       ← 프로젝트 전용 규칙 + 도메인 지식
├── CHECKPOINT.md                   ← 마일스톤 추적 (세션 간 기억 유지)
├── AUDIT.log                       ← 의사결정 기록 (추가 전용)
└── docs/designs/                   ← 디자인 문서 저장소
```

---

## 5단 기어 워크플로

```
/office-hours → /plan → /build → /review → /ship
(또는 /autoplan으로 기획~설계를 한 번에)
```

| 기어 | 역할 | 산출물 |
|------|------|--------|
| /office-hours | 아이디어 검증, 10-star product 사고, 문제 정의 | 디자인 문서 (docs/designs/) |
| /plan | 기술 스택 확정, 아키텍처 설계, 테스트 전략 | 프로젝트 CLAUDE.md + 아키텍처 문서 |
| /build | 승인된 계획에 따라 코드 작성 | 구현된 코드 + 테스트 |
| /review | CI는 통과하지만 프로덕션에서 깨지는 버그 탐색 | 리뷰 리포트 + 수정 사항 |
| /ship | 동기화, 테스트, 커밋, 릴리즈 노트 작성 | 배포 완료 + CHECKPOINT 업데이트 |

### 추가 커맨드

| 커맨드 | 카테고리 | 역할 |
|--------|---------|------|
| /autoplan | 자동화 | /office-hours → /plan을 한 커맨드로 자동 연쇄 실행. 사람 판단 필요한 곳에서만 멈춤 |
| /careful | 안전 | 위험 명령어(rm -rf, DROP TABLE, force push 등) 실행 전 경고. 빌드 클린업은 화이트리스트로 통과 |
| /freeze | 안전 | 특정 디렉토리만 수정 가능하게 잠금. 디버깅 시 다른 모듈 건드리는 것 방지. /unfreeze로 해제 |
| /learn | 메타 | 세션에서 배운 패턴/실수/선호도를 docs/learnings.md에 저장. 다음 세션에서 자동 적용. 프로젝트 간 교차 학습 가능 |

### 새 프로젝트 규칙 (엄격)
- 반드시 /office-hours부터 시작
- 단계 건너뛰기 절대 금지
- /plan 승인 전 코드 작성 금지

### 기존 프로젝트 규칙 (유연)
- 작업 성격에 맞는 단계에서 시작 가능
- 새 기능: /plan부터
- 버그 수정: /build부터
- 핫픽스: /build → /ship

---

## 복잡도 게이트

/office-hours 또는 /plan 실행 시 프로젝트 복잡도를 자동 평가합니다:

| 복잡도 | 기간 | 예시 | 인터뷰 깊이 |
|--------|------|------|-----------|
| Simple | 1-3일 | 위스키 테이스팅 노트 앱 MVP | 짧은 인터뷰 |
| Medium | 1-4주 | 인증 + 외부 API 연동 앱 | 표준 인터뷰 |
| Complex | 1개월+ | ProcessLens (멀티테넌시, 도메인 로직) | Forcing Questions 심층 인터뷰 |

---

## 메모리 시스템

### CHECKPOINT.md
- 세션이 끝나도 지식이 유지되게 하는 핵심 파일
- 현재 상태, 완료된 작업, 진행 중 작업, 핵심 결정, 다음 단계를 기록
- 모든 세션 시작 시 자동으로 읽어서 컨텍스트 복원

### AUDIT.log
- 추가 전용 (절대 수정/삭제 금지)
- "왜 이런 결정을 했는지"를 기록
- 나중에 코스 코렉션(방향 수정) 시 참고

### docs/designs/
- /office-hours에서 생성된 디자인 문서 저장
- 승인 후 불변 — 수정 대신 새 버전 생성

---

## 컨텍스트 관리 규칙

- 컨텍스트 윈도우 사용량 40% 이하 유지 (Dumb Zone 회피)
- 한 세션에서 /compact 3번 후 → /clear로 새 세션
- 클리어 전 반드시 CHECKPOINT.md에 핵심 결정 기록
- 전체 코드베이스를 읽지 말 것 — 현재 작업에 필요한 것만

---

## 레이어 구조

```
L4 통제 (Control):    CLAUDE.md + rules/        ← 항상 작동
L3 실행 (Execution):  commands/*.md              ← 호출 시만 로딩
L2 품질 (Quality):    settings.json + hooks      ← 항상 작동
L1 구조 (Structure):  CHECKPOINT.md + AUDIT.log  ← 항상 작동
```

---

## 다음 단계

이 CLAUDE.md는 L4(통제 계층)입니다. 완전한 하네스를 위해 추가로 필요한 것:

- [ ] L3: commands/*.md (5개 커맨드 프롬프트)
- [ ] L2: settings.json + hooks 설정
- [ ] L1: CHECKPOINT.md 템플릿 (이미 CLAUDE.md에 포함)
- [ ] rules/*.md (Python, TypeScript, React Native, General)
