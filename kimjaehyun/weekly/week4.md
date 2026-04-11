# FOMO Crew W4: 하네스 진화 — mgrep + Codex Hybrid + 랜덤 리뷰어

> **"4주차: 하네스를 더 날카롭게 만드는 세 가지 업그레이드"**

---

## 1. 지식의 입력 (W4 Input Flow)

| 구분 | 활동 내용 | 관리 상태 |
|:---:|:---|:---:|
| **Deep-Dive** | The Claude Code Leak — 시스템 프롬프트 전문 분석 | ✅ 완료 |
| **Deep-Dive** | Mixedbread mgrep — 시맨틱 코드 검색 플러그인 실험 | ✅ 완료 |
| **Deep-Dive** | OpenAI Codex Plugin for Claude Code — Hybrid 셋업 | ✅ 완료 |
| **Hands-On** | mgrep 플러그인 하네스 통합 — SessionStart/End Hook 구성 | ✅ 완료 |
| **Hands-On** | Codex Hybrid 설정 — rescue/review/stop-gate 파이프라인 구축 | ✅ 완료 |
| **Hands-On** | FOMO 크루 PR 랜덤 리뷰어 배정 시스템 구축 (AgentOps) | ✅ 완료 |

### 공유 아티클 목록

1. [The Claude Code Leak](https://build.ms/2026/4/1/the-claude-code-leak/)
2. [Mixedbread mgrep — Semantic Search for Code](https://github.com/mixedbread-ai/mgrep)
3. [OpenAI Codex Plugin for Claude Code](https://github.com/openai/codex-plugin-cc)
4. [Minho Hwang: harness / agent / team / skill 공유](https://www.linkedin.com/posts/hwang-minho_%EB%93%9C%EB%94%94%EC%96%B4-harness-agent-team-skill-%ED%94%8C%EB%9F%AC%EA%B7%B8%EC%9D%B8-%EA%B3%B5%EC%9C%A0%ED%95%A9%EB%8B%88%EB%8B%A4-share-7443630930742734848-4xPp)

### 이번 주 입력에서 얻은 핵심 포인트

- **검색 도구 분리**: 정확한 문자열은 built-in Grep, 시맨틱 탐색은 mgrep, 웹 검색은 Tavily/Exa — 도구 오버랩 제거가 토큰 효율의 핵심
- **교차 모델 검증**: 같은 모델이 만든 것을 같은 모델이 검증하면 안 된다 → Codex(GPT-5.4)가 Claude의 산출물을 검증하는 하이브리드 구조
- **리뷰 자동화**: 사람이 일일이 리뷰어를 지정하면 병목 → 랜덤 배정으로 해결

---

## 2. 기술의 축적 (W4 Output Archive)

### 2-1. mgrep 플러그인 통합 — 시맨틱 검색으로 하네스 업그레이드

기존 하네스에서 코드 탐색은 built-in Grep/Glob에 의존했다. 정확한 문자열 검색은 빠르지만, "이 코드베이스에서 인증 로직이 어디 있어?" 같은 시맨틱 질문에는 무력하다.

**mgrep**은 Mixedbread의 시맨틱 검색 엔진을 Claude Code 플러그인으로 통합한 것이다.

#### 아키텍처

```
SessionStart Hook (mgrep_watch.py)
  ↓ mgrep watch 백그라운드 프로세스 시작
  ↓ .gitignore/.mgrepignore 기반 인덱싱
  
검색 요청
  ↓ mgrep "query"           → 로컬 시맨틱 검색
  ↓ mgrep --web --answer    → 웹 검색 + 요약
  
SessionEnd Hook (mgrep_watch_kill.py)
  ↓ 백그라운드 프로세스 정리 + PID 파일 삭제
```

#### 도구 오버랩 해소 정책

| 용도 | 사용할 도구 | 사용 금지 |
|:---|:---|:---|
| 정확한 문자열/정규식 | built-in Grep, Glob | — |
| 시맨틱 코드 탐색 | mgrep | — |
| 웹 일반 검색 | Tavily MCP | WebSearch (deny) |
| 코드 예제 검색 | Exa MCP | WebSearch (deny) |
| 라이브러리 문서 | Context7 MCP | WebFetch (deny) |

핵심: WebSearch/WebFetch를 settings.json에서 deny로 차단하고, 각 용도별 전용 도구를 명시하여 **도구 간 역할 충돌을 원천 제거**했다.

### 2-2. Codex Hybrid 셋업 — 교차 모델 검증 파이프라인

W1에서 만든 TTH(멀티에이전트)의 약점은 **모든 에이전트가 같은 Claude 모델**이라는 점이었다. 같은 모델이 만든 코드를 같은 모델이 검증하면, 동일한 맹점(blind spot)을 공유한다.

이를 해결하기 위해 **OpenAI Codex를 Claude Code 안에 플러그인으로 통합**하여 교차 검증 루프를 구축했다.

#### 통합 구조

```
settings.json
├── enabledPlugins: { "codex@openai-codex": true }
└── extraKnownMarketplaces: { "openai-codex": { repo: "openai/codex-plugin-cc" } }
```

#### 교차 검증 루프

```
1. [Claude] 코드 1차 작성
2. [Codex/GPT-5.4] /codex:rescue → 1차 검증 + 수정 제안
3. [Claude] 수정 반영 + 2차 검증
4. [Codex] 최종 검증 → PR 단계
```

#### 주요 커맨드

| 커맨드 | 역할 |
|:---|:---|
| `/codex:setup` | Codex CLI 상태 확인 + stop-gate 토글 |
| `/codex:rescue` | 디버깅/구현 작업을 Codex에 위임 |
| `/codex:review` | git 변경사항에 대한 Codex 코드 리뷰 |
| `/codex:adversarial-review` | 도전적 관점의 설계 리뷰 |

#### Stop-Gate Hook — 자동 품질 관문

```
사용자가 /stop 시
  ↓ stop-review-gate-hook.mjs 발동
  ↓ 마지막 Claude 턴에 코드 변경이 있었나?
  ↓ yes → Codex가 자동 리뷰
  ↓ ALLOW: 세션 종료 / BLOCK: 이슈 해결 필요
```

이 구조의 핵심: **"Codex는 포워딩 아키텍처"** — Claude Code가 직접 문제를 풀지 않고, Codex에 그대로 전달하고 결과를 있는 그대로 반환한다. 중간에 해석이나 가공이 없다.

### 2-3. FOMO 크루 PR 랜덤 리뷰어 배정

FOMO 크루 14명이 매주 PR을 올리는데, 리뷰어를 수동 지정하면 항상 같은 사람에게 리뷰가 몰리는 문제가 있었다.

**랜덤 리뷰어 시스템**을 도입하여:
- PR 생성 시 크루 멤버 중 랜덤으로 리뷰어 자동 배정
- AgentOps로 리뷰 활동 추적 — 누가 얼마나 리뷰했는지 관측 가능
- 리뷰 편중 방지 + 크로스 러닝 촉진

### Code

| 파일 | 설명 |
|:---|:---|
| [`agent_core_v0.1.py`](../code/agent_core_v0.1.py) | Claude API 기반 에이전트 체이닝 기본 구현 (W1) |
| [`ralph_loop_hook.sh`](../code/ralph_loop_hook.sh) | Ralph Loop Stop Hook (W1) |
| [`subagent_tracker.sh`](../code/subagent_tracker.sh) | SubagentStart Hook (W1) |

### Doc (Pain Point & Solution)

| Pain Point | 시도한 해결책 | 결과 |
|:---|:---|:---|
| 시맨틱 질문에 Grep이 무력 | mgrep 플러그인 도입 + 도구 오버랩 정책 수립 | 시맨틱 탐색 가능, 토큰 ~2x 절감 |
| 같은 모델의 자기 검증 맹점 | Codex Hybrid 교차 검증 루프 | Claude 작성 → Codex 검증의 이종 모델 파이프라인 |
| WebSearch/WebFetch 도구 충돌 | settings.json deny + MCP별 역할 분리 | 도구 오버랩 제로 달성 |
| PR 리뷰어 편중 | 랜덤 리뷰어 + AgentOps 관측 | 크루 전원 균등 리뷰 참여 |

### Retrospective

> "1주차에 멀티에이전트 오케스트레이션을 만들었다면, 2주차에는 그 에이전트들의 **눈과 감시자**를 달았다.
> mgrep은 에이전트의 탐색 능력을, Codex Hybrid는 검증 능력을 한 단계 올렸다.
> 하네스 엔지니어링의 진짜 힘은 도구 하나하나가 아니라, **도구 간 역할이 겹치지 않도록 정책을 설계하는 것**에 있다."

---

## 3. 고민

| 고민 | 현재 생각 |
|:---|:---|
| **mgrep의 인덱싱 비용은 어디까지 허용할 것인가?** | 세션마다 watch 프로세스가 뜨는데, 대규모 모노레포에서는 부담이 될 수 있다. .mgrepignore 튜닝이 필요. |
| **Codex Stop-Gate를 상시 켜야 하는가?** | 모든 /stop마다 리뷰가 돌면 15분짜리 작업이 번거로워진다. 3단계 이상 작업에만 선별 적용이 현실적. |
| **랜덤 리뷰어의 품질 편차를 어떻게 관리할 것인가?** | 리뷰 경험이 다른 크루원끼리 배정되면 리뷰 품질이 들쑥날쑥. 리뷰 체크리스트를 표준화하는 것이 선행 과제. |

---

## 4. Next Week

- mgrep `.mgreprc.yaml` 프로젝트별 커스텀 설정 최적화
- Codex adversarial-review를 아키텍처 변경 시 자동 트리거하는 Hook 설계
- 랜덤 리뷰어 시스템 GitHub Actions 자동화 + AgentOps 대시보드 연동
- 하네스 전체 건강도 진단 (`/harness-audit`) 정례화

---

*하네스는 도구를 추가하는 기술이 아니라, 도구 간 경계를 설계하는 기술이다.*
