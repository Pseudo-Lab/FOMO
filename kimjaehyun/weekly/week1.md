# FOMO Crew W1: Knowledge Management System

> **"1주차: 관성에서 벗어나 에이전트 설계자로의 첫 발"**

---

## 1. 지식의 입력 (W1 Input Flow)

| 구분 | 활동 내용 | 관리 상태 |
|:---:|:---|:---:|
| **Daily Insight** | [아티클] Anthropic의 'Computer Use' API 실무 적용 사례 공유 | ✅ 완료 (카톡) |
| **Deep-Dive** | [지정 발표] 라이언 달이 말하는 '코딩의 종말'과 우리의 하네스 전략 | 📄 PDF 업로드 |
| **Weekly Sync** | 'Vibe Coding'에서 'Harness Engineering'으로의 전환 기술 요약 | 🔗 GitHub Wiki |

### 공유 아티클 목록

1. [Anthropic Computer Use API - Practical Guide](https://docs.anthropic.com)
2. [The End of Coding as We Know It - Ryan Dahl](https://example.com)
3. [Agent Harness Pattern: Task Decomposition](https://example.com)
4. [Vibe Coding: From Concept to Production](https://example.com)
5. [Claude Code CLI - Advanced Workflow Tips](https://example.com)

---

## 2. 기술의 축적 (W1 Output Archive)

### Code

- **파일**: [`agent_core_v0.1.py`](../code/agent_core_v0.1.py)
- **설명**: Claude API를 활용한 기본 Task 분업 로직 구현
- **핵심 학습**: 프롬프트 체이닝을 직접 구현하며 에이전트 간 메시지 포맷의 중요성 체감

### Doc (Pain Point & Solution)

| Pain Point | 시도한 해결책 | 결과 |
|:---|:---|:---|
| 반복적인 API 문서 읽기 업무 | 가이드라인 에이전트 설계 | 프로토타입 완성, 정확도 개선 필요 |
| 에이전트 간 컨텍스트 유실 | 구조화된 JSON 메시지 포맷 도입 | 컨텍스트 전달률 향상 |

### Retrospective

> "직접 코드를 짤 때보다, 에이전트 간의 통신 규격을 정하는 데 시간을 더 썼다.
> 낯설지만 이것이 '하네스'의 시작임을 체감함."

---

## 3. 성장의 시각화 (W1 Stats)

| 항목 | 점수 | 코멘트 |
|:---:|:---:|:---|
| **성실성** | 10/10 | 첫 주 오프라인 전원 참석 및 커밋 완료 |
| **자료공유** | 15/10 | 예상보다 많은 5개의 고퀄리티 아티클 공유 |
| **혁신성** | 8/10 | 기존 라이브러리 대신 직접 프롬프트 체이닝 시도 |

---

## 4. 다음 주 목표 (W2 Preview)

- [ ] `agent_core_v0.2.py` — 멀티 에이전트 오케스트레이션 구현
- [ ] Pain Point 문서 업데이트 — 가이드라인 에이전트 정확도 개선 기록
- [ ] 아티클 3개 이상 공유

---

*여러분이 남길 기록의 첫 줄은 무엇입니까?*
