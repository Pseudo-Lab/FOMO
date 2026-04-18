# FOMO Crew W4: 전민정

> **"4주차: 도구를 벼려라, 제한이 성능이다"**

---

## 1. 지식의 입력 (W4 Input Flow)

|       구분        | 활동 내용 | 관리 상태 |
| :---------------: | :-------- | :-------: |
| **Daily Insight** | [아티클] ① AI Agent Memory - MemKraft ② Claude Opus 4.7 업데이트 요약 공유 | ✅ 완료 (카톡) |
|  **Weekly Sync**  | FOMO 크루 - **발표**: DeerFlow vs SWE-Agent 비교 분석 (4/18 오전 11시) | 🎤 발표 예정 |
|   **Hands-On**    | DeerFlow vs SWE-Agent 리서치 및 비교 분석 | 🚧 진행 중 |

### 공유 아티클 목록

1. [해시드 김서준 대표님의 MemKraft & Garry Tan Y 컴피니에이터 (LinkedIn)](https://www.linkedin.com/posts/%EC%83%81%ED%98%84-%EC%97%84-5a03b628a_%ED%95%B4%EC%8B%9C%EB%93%9C-%EA%B9%80%EC%84%9C%EC%A4%80-%EB%8C%80%ED%91%9C%EB%8B%98%EC%9D%98-memkraft-garry-tan-y-%EC%BB%B4%ED%94%BC%EB%84%A4%EC%9D%B4%ED%84%B0-share-7449291698750517249-rTrI?utm_source=share&utm_medium=member_ios&rcm=ACoAAC9T5UAB1W5q9O0TQwejCV__Hjb9uRQSy0A) — AI Agent Memory 관련
2. Claude Opus 4.7 업데이트 쉬운 요약 — 카톡 공유

---

## 2. 기술의 축적 (W4 Output Archive)

### Hands-On

#### DeerFlow vs SWE-Agent 비교 분석

- 이번 주 발표 주제로 DeerFlow와 SWE-Agent 두 프레임워크를 비교 분석
- 아키텍처, 에이전트 구성, 사용 사례 측면에서 차이점 정리
- **핵심 학습**:
  1. **인터페이스 > 모델** — 같은 GPT-4 Turbo에서 ACI만 적용해 SWE-bench 7.3% → 18.0% (+10.7pp). 모델을 바꾸기 전에 도구부터 점검할 것
  2. **제한이 성능을 높인다** — 검색 50개 캡, 파일 100줄 뷰, 팀원 3명 제한 등 "더 적절하게" 주는 설계가 AI 집중력을 만듦
  3. **가드레일 ROI가 가장 높다** — Linter Guard(+3.3pp)가 새 도구 추가(+2.0~2.7pp)보다 효과적. 실수를 못 하게 막는 것이 능력을 추가하는 것보다 낫다

### Doc (Pain Point & Solution)

| Pain Point | 시도한 해결책 | 결과 |
| :--------- | :------------ | :--- |
|            |               |      |

### Retrospective

> "AI 에이전트를 steering하는 방법이 이렇게 다양하다는 걸 두 오픈소스를 뜯어보며 체감했다. 환경을 통제하는 방식(DeerFlow)과 도구를 정밀 설계하는 방식(SWE-Agent) — 현업에서 직접 부딪혀야 알 수 있을 것 같은 설계 감각을, 오픈소스 코드와 논문으로 압축적으로 배울 수 있다는 가능성이 흥미롭다. 다만 실제 프로덕션의 맥락 없이 어디까지 체화할 수 있을지는 계속 고민이 남는다."

---

*여러분이 남길 기록의 첫 줄은 무엇입니까?*
