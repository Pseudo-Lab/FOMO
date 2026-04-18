# Use Case: Business Planning Revenue Cockpit

## 상황

이 유즈케이스의 서비스는 사업기획팀, FP&A, Revenue Operations 리드가
주간 운영 회의 전에 매출 전망과 핵심 가정을 빠르게 정리하도록 돕는 `revenue planning cockpit`이다.

대상 고객은 다음과 같다.

- 100~500명 규모 B2B SaaS 회사의 사업기획팀
- FP&A 매니저
- Revenue Operations 리드
- CEO/COO에게 주간 매출 전망을 보고해야 하는 전략기획 담당자

이 팀의 월요일 오전 status quo는 보통 이렇다.

- CRM pipeline report를 열고
- BI dashboard에서 plan vs actual 차이를 확인하고
- 영업팀, 마케팅팀, CS팀의 업데이트를 따로 확인하고
- board update와 weekly operating meeting에 들어갈 숫자를 수동으로 맞춘다

즉 고객의 진짜 문제는 "데이터가 없다"가 아니라
**어떤 매출 가정과 리스크를 먼저 조정해야 이번 주 의사결정이 흔들리지 않는지 빠르게 정리되지 않는다**는 점이다.

서비스 목표는 아래와 같다.

- 주간 매출 전망에서 먼저 봐야 할 가정과 리스크를 정렬한다.
- 영업, 마케팅, CS가 얽힌 cross-functional blocker를 사업기획팀이 먼저 확인하게 한다.
- board-facing 숫자와 운영 회의 액션을 한 번에 연결한다.

---

## Stage 0: Service Lens

### 사용자

- 사업기획팀
- FP&A 매니저
- Revenue Operations 리드
- 주간 매출 전망을 책임지는 전략기획 담당자

### 핵심 Job

- "이번 주 매출 전망을 흔들 수 있는 가정과 리스크 중 무엇을 먼저 확인해야 하는지 결정하고 싶다"

### 가치 순간

- 주간 계획 회의 전에 cockpit을 열었을 때 forecast gap, revenue impact, cross-team dependency가 우선순위로 정리되어 있는 순간

### 기술의 역할

- Forecasting service는 매출 가정과 리스크를 점수화하는 가치 엔진이다.
- Planning console은 사업기획팀이 추천된 우선순위를 검토하고 공유하는 의사결정 접점이다.
- 문서는 운영 회의 흐름과 지표 정의를 빠르게 복원하는 도구다.

### 지금 보지 않아도 되는 것

- 대시보드 시각화 세부 스타일
- 특정 BI 도구 선호
- CRM connector의 세부 구현 최적화

---

## 의사결정 질문

1. 이 저장소의 핵심 가치가 planning console에 있는가, forecast prioritization engine에 있는가?
2. forecast engine과 decision surface의 anchor는 각각 어디에 있는가?
3. 상위 디렉토리 중 어디부터 읽는 것이 사업기획팀의 의사결정을 가장 빨리 복원하는가?
4. 지금 바로 열 파일 5개는 무엇인가?

---

## 단계별 실험 내용

### Stage 1

- 목적: 저장소가 문서+엔진+의사결정 UI를 함께 가지는지 본다
- 보고 싶은 신호: markdown, python, json, typescript가 함께 존재하고, metrics/weekly review 문서가 같이 있는지
- 기대 해석: 단순 dashboard가 아니라 forecast engine, decision surface, 운영 리뷰 문서가 같이 있는 혼합형 저장소다

### Stage 2

- 목적: forecast engine과 planning console anchor를 찾는다
- 보고 싶은 신호: `services/forecasting/pyproject.toml`, `services/forecasting/.env.example`, `apps/planning-console/package.json`, 각 README, `docs/metrics.md`, `docs/weekly_review_log.md`
- 기대 해석: 매출 리스크를 계산하는 엔진, 사업기획팀이 보는 console, 주간 리뷰 운영 문서가 책임 분리되어 있다

### Stage 3

- 목적: 어떤 영역부터 파야 하는지 정한다
- 보고 싶은 신호: `services`가 1위, `apps`가 2위
- 기대 해석: forecast prioritization 품질을 만드는 엔진부터 보고, console은 그 다음에 본다

### Stage 4

- 목적: 바로 열 파일을 정한다
- 보고 싶은 신호: 루트 README, forecasting service README, planning console README, service manifest가 상위 추천
- 기대 해석: 온보딩 순서가 `전체 사업 문제 -> 가치 엔진 설명 -> 의사결정 접점 설명 -> 실행/설정 정보`로 흐른다

---

## 실행 방법

```bash
bash kimjungsu/code/run_project_scan_usecase.sh biz-planning
```

---

## 기대 결과 요약

- stage 1: 혼합형 planning 서비스로 분류할 수 있어야 한다
- stage 2: service/app anchor를 정확히 찾을 수 있어야 한다
- stage 3: `services > apps > ROOT > docs` 순위가 나와야 한다
- stage 4: 루트 README와 forecasting service README가 planning console README보다 앞서야 한다
- 보강 확인: metrics/weekly review 문서는 현실적인 운영 맥락을 주지만, 핵심 가치 엔진 우선순위를 뒤집지는 않아야 한다
