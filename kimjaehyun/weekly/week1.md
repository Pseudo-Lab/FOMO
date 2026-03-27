# FOMO Crew W1: Harness Engineering — 멀티에이전트 오케스트레이션

> **"1주차: 바이브 코딩에서 하네스 엔지니어링으로의 전환"**

---

## 1. 지식의 입력 (W1 Input Flow)

| 구분 | 활동 내용 | 관리 상태 |
|:---:|:---|:---:|
| **Daily Insight** | Anthropic의 'Computer Use' API 실무 적용 사례 공유 | ✅ 완료 |
| **Deep-Dive** | 라이언 달의 '코딩의 종말' + 하네스 전략 발표 | ✅ 완료 |
| **Weekly Sync** | 'Vibe Coding'에서 'Harness Engineering'으로의 전환 | ✅ 완료 |
| **Hands-On** | TTH 멀티에이전트 하네스 시스템 설계 및 구현 | ✅ 완료 |
| **Hands-On** | Ralph Loop Stop Hook — 자율 반복 수렴 메커니즘 구현 | ✅ 완료 |

### 공유 아티클 목록

1. [Anthropic Computer Use API - Practical Guide](https://docs.anthropic.com/en/docs/agents-and-tools/computer-use)
2. [The End of Coding as We Know It - Ryan Dahl](https://www.youtube.com/watch?v=LJmugMQLdfY)
3. [Building Effective Agents — Anthropic](https://www.anthropic.com/engineering/building-effective-agents)
4. [Claude Code CLI — Hooks & Multi-Agent](https://docs.anthropic.com/en/docs/claude-code)
5. [Multi-Agent Orchestration Patterns](https://langchain-ai.github.io/langgraph/concepts/multi_agent/)

---

## 2. 기술의 축적 (W1 Output Archive)

### Hands-On: TTH (Toss-Tesla Harness) 멀티에이전트 시스템

이번 주 핵심 작업은 **TTH 하네스** — 토스의 사일로 조직문화 + 머스크의 5-Step Engineering Process + Ralph Loop의 반복 수렴 메커니즘을 결합한 멀티에이전트 오케스트레이션 시스템을 설계하고 구현한 것이다.

#### 아키텍처 개요

```
사티아 (PO/팀리드) — Opus
├── 피차이 (Architect) — Opus
├── 팀쿡 (Frontend Lead) — Sonnet
├── 젠슨 (Backend) — Sonnet
├── 저커버그 (Frontend Dev) — Sonnet
└── 베조스 (QA/삭제 분석) — Sonnet
```

각 팀원은 DRI(Directly Responsible Individual)로서 자기 도메인에서 최종 결정권을 가진다. 파일 경계가 명확히 분리되어 충돌이 없다.

#### Ralph Loop — 자율 반복 수렴

Claude Code의 Stop Hook을 활용하여 **세션 종료 시 자동으로 다음 반복을 시작**하는 메커니즘을 구현했다.

```
Stop Hook 발동
  ↓
.ralph-loop/state.json 확인
  ↓ active=true?
inject_prompt로 다음 반복 주입
  ↓
팀원 상태 확인 (teammates.json)
  ↓ running 팀원이 있으면?
"SendMessage(to=이름)로 재사용" 안내
  ↓
모든 스토리 완료?
  ↓ yes
<promise>DONE</promise> → 루프 종료
```

#### SubagentStart/Stop Hook — stdin JSON 기반 추적

Claude Code의 서브에이전트 훅은 `stdin`으로 JSON을 받는다. 환경변수가 아님을 실제 테스트로 확인했다.

```json
// stdin으로 받는 데이터
{
  "agent_id": "a554f699704941e2f",
  "agent_type": "general-purpose",
  "session_id": "...",
  "cwd": "/home/kdb"
}
```

핵심 발견: `agent_name`은 stdin에 포함되지 않는다. 따라서 **오케스트레이터가 스폰 후 teammates.json에 이름을 매핑**하는 2단계 등록 구조를 설계했다.

#### flock 동시성 보호

3개 에이전트를 병렬 스폰할 때 teammates.json 동시 쓰기 충돌이 발생한다. `flock`으로 해결:

```bash
(
  flock -w 5 200 || exit 0
  # read-modify-write teammates.json
) 200>"${TEAMMATES_FILE}.lock"
```

테스트 결과: 3/3 병렬 등록 성공, 데이터 유실 없음.

### Code

| 파일 | 설명 |
|:---|:---|
| [`agent_core_v0.1.py`](../code/agent_core_v0.1.py) | Claude API 기반 에이전트 체이닝 기본 구현 |
| [`ralph_loop_hook.sh`](../code/ralph_loop_hook.sh) | Ralph Loop Stop Hook — 자율 반복 수렴 메커니즘 |
| [`subagent_tracker.sh`](../code/subagent_tracker.sh) | SubagentStart Hook — stdin JSON 기반 팀원 추적 |

### Doc (Pain Point & Solution)

| Pain Point | 시도한 해결책 | 결과 |
|:---|:---|:---|
| 에이전트 간 컨텍스트 유실 | 구조화된 JSON 메시지 포맷 도입 | 컨텍스트 전달률 향상 |
| 서브에이전트 이름 추적 불가 | `CLAUDE_SUBAGENT_NAME` env var 시도 → 실패 | stdin JSON + 오케스트레이터 매핑으로 해결 |
| teammates.json 동시 쓰기 충돌 | flock 파일 락 도입 | 병렬 3개 에이전트 등록 100% 성공 |
| Ralph Loop에서 새 에이전트 계속 생성 | inject_prompt에 활성 팀원 안내 추가 | SendMessage 재사용으로 전환 |
| inject_prompt에 모델이 아는 정보 반복 | 취리히 대학 연구 기반 간결화 | 토큰 낭비 감소 |

### Retrospective

> "직접 코드를 짤 때보다, 에이전트 간의 통신 규격을 정하는 데 시간을 더 썼다.
> 하네스 엔지니어링의 핵심은 코드가 아니라 **에이전트가 실패했을 때 어떻게 복구하느냐**의 설계다.
> 환경변수가 없다는 사실을 시뮬레이션이 아닌 실제 테스트에서 발견한 것이 이번 주의 가장 큰 교훈."

---

*하네스는 코드를 짜는 기술이 아니라, 에이전트가 스스로 학습하고 수렴하는 환경을 만드는 기술이다.*
