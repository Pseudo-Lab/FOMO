# FOMO Crew W1: OPTC와 PiOS — 하네스의 형태를 다시 정한 주

---

## 1. 지식의 입력 (W1 Input Flow)

|         구분          | 활동 내용                                                       | 관리 상태 |
| :-------------------: | :-------------------------------------------------------------- | :-------: |
|   **Daily Insight**   | [영상] AI/에이전트/하네스 관련 YouTube 자료 시청                |  ✅ 완료  |
|     **Deep-Dive**     | [Anthropic] Harness design for long-running apps 정독           |  ✅ 완료  |
|     **Deep-Dive**     | [Mario Zechner] Thoughts on slowing the fuck down 읽기          |  ✅ 완료  |
|  **Reference Scan**   | 해병가재 블로그 탐색                                            |  ✅ 완료  |
|  **Reference Scan**   | [Feynman](https://github.com/getcompanion-ai/feynman) 구조 분석 |  ✅ 완료  |
| **Hands-On / Design** | OPTC와 PiOS 설계 방향 정리                                      |  ✅ 진행  |

### 공유 아티클 / 자료 목록

1. [YouTube 참고 영상](https://youtu.be/A8PMyC7W_vg?si=UsOFSk5xuJcNQXH-)
2. [Anthropic — Harness design for long-running apps](https://www.anthropic.com/engineering/harness-design-long-running-apps)
3. [Mario Zechner — Thoughts on slowing the fuck down](https://mariozechner.at/posts/2026-03-25-thoughts-on-slowing-the-fuck-down/)
4. [해병가재 블로그](https://haebyunggajae.com/)
5. [Feynman](https://github.com/getcompanion-ai/feynman)

### 이번 주 입력에서 얻은 핵심 포인트

- 장기 실행형 에이전트 시스템은 단순 프롬프트 조합이 아니라 **상태, 복구, 리뷰, 관측**을 포함한 하네스 설계가 중요하다.
- Feynman을 보며 PiOS를 extension 형식으로 만들기보다는, **Pi 위에 올라가는 wrapper/app-shell**로 두는 방향이 더 적절하다는 판단을 하게 되었다.

---

## 2. 기술의 축적 (W1 Output Archive)

### 2-1. OPTC 설계 방향 정리

OPTC는 다음 레이어로 이해된다.

- **OpenClaw**: 대화, 기억, 연속성의 상위 껍질
- **Chopchu**: OpenClaw 에이전트. 사용자-facing 오케스트레이션과 정책 적용
- **PiOS**: 코딩 세션 내부에서 동작하는 internal orchestrator
- **tmux**: 실제 실행이 보이는 runtime substrate
- **clawhip**: 세션 운영, 관측, 라우팅 계층

핵심은 모든 것을 하나의 에이전트에 몰아넣지 않고,
**대화 / 오케스트레이션 / 실행 / 관측의 책임을 분리하는 구조**를 만드는 것이다.
discord 에서 명령주고, 실행하고, 관측하는 루프. 허예찬님 사례보고 구축해보기로 마음먹었다.

### OPTC 플로우

기본적인 흐름은 다음과 같이 상상하고 있다.

1. **OpenClaw**에서 사용자 요청과 연속성을 받는다.
2. **Chopchu**가 요청을 해석하고 작업 단위를 구조화한다.
3. 필요하면 적절한 세션을 만들거나 라우팅한다.
4. 실제 코딩 세션 내부에서는 **PiOS**가 internal orchestrator로 동작한다.
5. 실행은 **tmux** 위에서 가시적으로 돌아간다.
6. **clawhip**이 세션 상태, 이벤트, 관측 신호를 바깥으로 끌어올린다.
7. Chopchu는 그 신호를 읽고 다음 액션을 결정한다.

즉 OPTC는 단순한 실행 체인이 아니라,
**사용자 요청 → 오케스트레이션 → 세션 내부 조율 → 가시적 실행 → 관측/라우팅 → 다음 결정**
의 흐름을 가지는 운영 모델이다.

### 2-2. PiOS 설계 전환 — 독립 런타임이 아니라 wrapper

초기에는 PiOS를 하나의 큰 시스템처럼 상상했지만,
Feynman 분석 이후 현재 방향은 훨씬 명확해졌다.

- PiOS는 **Pi 위에서 동작하는 higher-level work operating system**이다
- 실행은 Pi가 담당하고,
- **상태 / 리뷰 / 복구 / 완료 권한은 PiOS가 가진다**

### 2-3. Track A / Track B 분리

PiOS를 한 번에 크게 만들기보다, 현재는 두 트랙으로 나누어 생각하고 있다.

#### Track A — wrapper MVP

먼저 해야 하는 것:

- `pios`라는 Pi-like shell boundary 확보
- `setup`, `doctor`, `status` 같은 lifecycle surface 정리
- Pi runtime 위에서 동작하는 wrapper/app-shell 경계 확립

#### Track B — internal harness

Track A 이후에 다룰 것:

- 더 넓은 internal orchestration
- control plane 고도화
- richer recovery / operator surface
- workflow widening

바로 내부 하네스를 무겁게 확장하기보다,
먼저 wrapper로서의 usable boundary를 만드는 쪽으로 방향을 정리했다.

### 2-4. OpenClaw 에이전트 분리 실험

이번 주에는 OpenClaw 에이전트를 역할별로 분리하는 실험도 진행했다.

- 관리용 에이전트
- 개발용 에이전트
- 소셜용 에이전트

이 작업은 단순히 에이전트를 늘리는 것이 아니라,
**역할 / 책임 / 컨텍스트를 분리해 운영하는 방식**을 테스트하는 의미가 있었다.

---

## 3. 고민

| 고민                                                                       | 현재 생각                                                                                                                                                         |
| :------------------------------------------------------------------------- | :---------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| **이 시스템이 slop인지 아닌지는 어떻게 판단할 수 있는가?**                 | 단지 AI를 붙였다고 운영체계가 되는 것은 아니다. 상태, 규칙, 검증, 복구 같은 구조가 실제로 작동하는지가 더 중요하다고 느끼고 있다.                                 |
| **slop이 아니기 위해 무엇을 먼저 갖춰야 하는가?**                          | formatter, linter, test 같은 결정적 품질 요소는 필요하다고 생각한다. 다만 어느 정도 수준까지, 어떤 순서로, 어디에 먼저 적용해야 하는지는 아직 더 고민이 필요하다. |
| **코드 품질을 챙기며 MVP를 만들 것인가, 아니면 빠른 MVP를 우선할 것인가?** | 아직 답을 단정하지는 못했다. 다만 wrapper 경계나 상태 모델처럼 이후 구조를 크게 좌우하는 부분은 너무 가볍게 만들면 안 된다고 느끼고 있다.                         |

---

## 4. Next Week

### Track A

- PiOS가 **pi wrapper**로서 실제 동작하는 경계 마무리
- shell/lifecycle surface를 usable한 수준으로 정리

### Track B

- internal harness 구현 방향성 착수
- closed-loop work OS로 확장하기 위한 control-plane 고민 시작

---

_FOMO — 고민을 남기고, 구조를 만든다._
