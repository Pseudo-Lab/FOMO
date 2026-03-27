# FOMO Crew W1: 전민정

> **"1주차: 읽는 것에서 직접 만드는 것으로"**

---

## 1. 지식의 입력 (W1 Input Flow)

|       구분        | 활동 내용                                                                  |   관리 상태    |
| :---------------: | :------------------------------------------------------------------------- | :------------: |
| **Daily Insight** | [아티클] HyperAgents 소개 및 공유                                          | ✅ 완료 (카톡) |
|   **Deep-Dive**   | 멀티 TTS 서빙 아키텍처 설계 고민                                           |    ✅ 완료     |
|  **Weekly Sync**  | [OT] FOMO 크루 킥오프 - 자기소개, 그라운드 룰, 하네스 엔지니어링 발표 청강 |    ✅ 참석     |
|   **Hands-On**    | Hooks Notification 만들기 — Claude 작업 완료 시 맥북 알림 설정             |    ✅ 완료     |
|   **Hands-On**    | 나만의 코드 분석 에이전트 만들기                                           |    ✅ 완료     |

### 공유 아티클 목록

1. [GStack - Garry Tan's AI Stack](https://github.com/garrytan/gstack) / [소개 영상](https://www.youtube.com/watch?v=vfn_Ezu1qfk)
2. [AutoResearchClaw AI 소개 (PyTorch KR)](https://discuss.pytorch.kr/t/autoresearchclaw-ai/9329)
3. [OpenClaw v2026.3.23 Release](https://github.com/openclaw/openclaw/releases/tag/v2026.3.23) / [정리글 (LinkedIn)](https://www.linkedin.com/feed/update/urn:li:activity:7441993741424525313/?utm_source=share&utm_medium=member_desktop&rcm=ACoAAC9T5UAB1W5q9O0TQwejCV__Hjb9uRQSy0A)
4. [HyperAgents 소개 (위키독스)](https://wikidocs.net/blog/@jaehong/9838/)
5. [DeerFlow v2 SuperAgent Harness feat. ByteDance (PyTorch KR)](https://discuss.pytorch.kr/t/deerflow-v2-superagent-harness-feat-bytedance/9325)

---

## 2. 기술의 축적 (W1 Output Archive)

### Hands-On

#### Hooks Notification 만들기

- Claude Code 작업 완료 시 맥북 알림을 받도록 Hooks 설정
- 동영상 팁을 따라 직접 구성하며 체득
- **핵심 학습**: 글로 읽는 것과 직접 해보는 것의 차이를 실감. 현재도 계속 사용 중

#### 나만의 코드 분석 에이전트 만들기

- 코드베이스를 자동으로 분석하는 에이전트 구축
- 서브에이전트로 코드 분석을 위임하고, 메인 작업은 병렬로 동시 진행
- 분석 결과가 메인 컨텍스트를 오염시키지 않는 컨텍스트 분리 효과 체험
- **핵심 학습**: 에이전트 역할 분담과 병렬 오케스트레이션의 실용성을 직접 체감. 하네스 설정(hooks, agents)을 만들며 에이전트 제어의 감각을 익힘

#### 회사 챗봇 시스템 설계도

- PPT로 직접 그리면서 챗봇과 다른 시스템 간 연동 구조 파악
- **핵심 학습**: 시스템 간 연동 포인트를 시각화하면서 전체 아키텍처를 이해. 먼 미래지만 앞으로 할 일이 기대됨

### Doc (Pain Point & Solution)

| Pain Point                   | 시도한 해결책           | 결과                           |
| :--------------------------- | :---------------------- | :----------------------------- |
| Claude Code 작업 완료를 놓침 | Hooks Notification 설정 | 실시간 알림으로 작업 효율 향상 |
| 코드베이스 파악에 시간 소모  | 코드 분석 에이전트 구축 | 자동 분석으로 파악 시간 단축   |

### Retrospective

> "글이나 정리된 문서로만 보던 내용을 동영상 팁을 따라 직접 해보니, 같은 내용이라도 체득의 깊이가 완전히 달랐다.
> Hooks Notification 설정으로 Claude 작업 완료 시 맥북 알림을 받도록 구성했는데, 지금도 계속 쓰고 있다.
> '읽는 것'과 '직접 해보는 것'의 차이를 다시 한번 실감한 한 주."

---

_여러분이 남길 기록의 첫 줄은 무엇입니까?_
