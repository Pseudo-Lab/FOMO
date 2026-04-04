# FOMO Crew W2: OMX, OpenClaw, Clawhip — 운영 루프를 실험하는 주

---

## 1. 지식의 입력 (W2 Input Flow)

|        구분        | 활동 내용                                                                                                                                                                                                                                                                                                                                                                                     | 관리 상태 |
| :----------------: | :-------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- | :-------: |
|   **Deep-Dive**    | [아티클] The Claude Code Leak 정독                                                                                                                                                                                                                                                                                                                                                            |  ✅ 완료  |
|   **Deep-Dive**    | [Hada] 관련 토픽 읽기                                                                                                                                                                                                                                                                                                                                                                         |  ✅ 완료  |
| **Reference Scan** | [Sigrid 포스트](https://x.com/realsigridjin/status/2039472968624185713?s=20) 확인                                                                                                                                                                                                                                                                                                             |  ✅ 완료  |
|   **Deep-Dive**    | [AI Frontier Ep.92](https://aifrontier.kr/ko/episodes/ep92/) 청취                                                                                                                                                                                                                                                                                                                             |  ✅ 완료  |
| **Reference Scan** | [Minho Hwang: harness / agent / team / skill 공유](https://www.linkedin.com/posts/hwang-minho_%EB%93%9C%EB%94%94%EC%96%B4-harness-agent-team-skill-%ED%94%8C%EB%9F%AC%EA%B7%B8%EC%9D%B8-%EA%B3%B5%EC%9C%A0%ED%95%A9%EB%8B%88%EB%8B%A4-share-7443630930742734848-4xPp?utm_source=social_share_send&utm_medium=ios_app&rcm=ACoAAEm0aQkBXuejzCXPDeKUuCrJeFfN_R-od9M&utm_campaign=copy_link) 확인 |  ✅ 완료  |

### 공유 아티클 / 자료 목록

1. [The Claude Code Leak](https://build.ms/2026/4/1/the-claude-code-leak/)
2. [Hada 토픽](https://news.hada.io/topic?id=28061)
3. [Sigrid 포스트](https://x.com/realsigridjin/status/2039472968624185713?s=20)
4. [AI Frontier Ep.92](https://aifrontier.kr/ko/episodes/ep92/)
5. [Minho Hwang: harness / agent / team / skill](https://www.linkedin.com/posts/hwang-minho_%EB%93%9C%EB%94%94%EC%96%B4-harness-agent-team-skill-%ED%94%8C%EB%9F%AC%EA%B7%B8%EC%9D%B8-%EA%B3%B5%EC%9C%A0%ED%95%A9%EB%8B%88%EB%8B%A4-share-7443630930742734848-4xPp?utm_source=social_share_send&utm_medium=ios_app&rcm=ACoAAEm0aQkBXuejzCXPDeKUuCrJeFfN_R-od9M&utm_campaign=copy_link)

### 이번 주 입력에서 얻은 핵심 포인트

- 운영 루프는 단순한 에이전트 연결이 아니라, **어떤 레이어가 어떤 책임을 가지는지**가 더 중요하다.
- Sigrid 포스트를 통해 **OMX / OpenClaw / Clawhip** 조합을 운영 루프의 중심축으로 보게 되었다.
- 하네스, agent, team, skill의 조합은 단일 제품보다 **역할 분리와 실험 구조**를 만드는 데 유효하다고 느꼈다.

---

## 2. 기술의 축적 (W2 Output Archive)

### 2-1. 운영 루프의 기준점 재정의

이번 주에는 운영 구조의 기준점을 **OMX**로 두고, 그 주변에 **OpenClaw**와 **Clawhip**을 놓는 방식으로 생각을 정리했다.

이 관점에서:

- **OMX**는 운영 루프의 기준점
- **OpenClaw**는 상위 대화/연속성/운영 진입점
- **Clawhip**은 세션 관측과 운영 신호를 전달하는 계층

즉 이번 주의 핵심은  
**"무엇을 중심으로 루프를 돌릴 것인가"**를 정하는 것이었다.

### 2-2. oh-my-pi와 PiOS를 비교군으로 둔 실험

이번 주에는 `oh-my-pi`와 `PiOS`를 서로 다른 실험체로 보기 시작했다.

#### oh-my-pi (OMP)

- OMX / OMC를 Pi로 포팅하는 구조에 가깝다
- Pi 위에서 OMX / OMC가 어떻게 돌아갈 수 있는지 확인하는 쪽에 초점
- 어느 정도 완성도가 있는 프로젝트라서, 비교군으로 포팅 실험을 진행 중
- 현재 상태: **포팅 진행중**

#### PiOS

- 내가 생각한 **kernel / runtime / operation** 구성의 하네스 실험
- 설계를 계속하다 보니 너무 과도하게 설계하는 것은 아닌가를 점검하는 대상
- 구조적인 운영체계 설계에 초점
- 현재 상태: **설계중**

둘은 같은 문제를 풀지만, 접근이 다르다.

- oh-my-pi(OMP): **포팅과 운영 가능성 검증 실험**
- PiOS: **하네스 구조와 운영 계층 설계 실험**

### 2-3. OMX / OpenClaw / Clawhip 운영 루프 탐색

이번 주의 가장 중요한 축은 이 루프였다.

- **OMX**를 기준점으로 보고
- **OpenClaw**가 상위 입력/연속성 역할을 하며
- **Clawhip**이 관측과 운영 신호를 넘기는 구조

이 구조를 보면서, 단순히 하나의 agent shell을 만드는 게 아니라  
**운영 루프 전체를 어떻게 설계할지**에 집중하게 되었다.

### 2-4. PiOS 하니스 구상

PiOS에서는 내가 원래 생각했던 구조를 더 분명히 정리해보려 했다.

- **Kernel**
  - 최소 핵심 규칙과 정합성
- **Runtime**
  - 실제 실행과 상태 전이
- **Operation**
  - 운영 루프와 개입 지점

이 3층 구조를 기준으로,
PiOS를 단순한 도구가 아니라 **운영 하니스**로 설계하는 방향을 잡고 있다.

---

## 3. 고민

| 고민                                          | 현재 생각                                                                                                         |
| :-------------------------------------------- | :---------------------------------------------------------------------------------------------------------------- |
| **OMX의 위치를 어디로 옮길 수 있는가?**       | PiOS나 oh-my-pi가 OMX의 역할을 대체할 수 있는지 실험해보고 있다.                                                  |
| **오버엔지니어링과 설계를 어떻게 인지할 수 있는가?** | 설계를 계속하다 보면 과도해질 수 있어서, 어디까지가 구조이고 어디서부터가 오버엔지니어링인지 구분하는 기준이 필요하다. 빠른 실행 루프를 만들면서도 신뢰도를 쌓는 방법을 고민하고 있다. |
| **운영 루프에서 핵심은 무엇인가?**            | 기능 자체보다 레이어별 책임 분리와, 어떤 계층이 기준점이 되는지 정하는 일이 더 중요하다고 느끼고 있다.            |

---

## 4. Next Week

### oh-my-pi

- `omc` / `omx` 포팅 실험 이어가기
- OMX 대체 가능성 검토
- 운영 루프 실험체로서의 역할 명확화

### PiOS

- kernel / runtime / operation 하니스 구체화
- 운영 구조 설계의 책임 경계 더 분명하게 만들기
- OpenClaw / Clawhip과의 관계를 루프 단위로 정리하기

---

_FOMO — 운영 루프를 만들고, 비교하고, 검증한다._
