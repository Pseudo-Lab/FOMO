# Use Case: Support Ops Morning Handoff

## 상황

이 유즈케이스의 서비스는 support operations lead가
출근 직후 야간 이슈와 우선 대응 계정을 빠르게 파악하도록 돕는 `morning handoff` 서비스다.

대상 고객은 다음과 같다.

- 30~200명 규모 SaaS 회사의 support operations lead
- 혹은 CX lead / escalation manager

이 고객의 아침 status quo는 보통 이렇다.

- Zendesk에서 야간 티켓을 보고
- Slack의 incident 채널을 읽고
- VIP 계정 메모를 다시 열고
- 온콜 로그와 내부 공유 문서를 훑으며
- 오늘 가장 먼저 대응할 항목을 수동으로 정리한다

즉 고객의 진짜 문제는 "정보가 없다"가 아니라
**어떤 고객과 어떤 이슈를 먼저 대응해야 하는지 아침 5분 안에 정리되지 않는다**는 점이다.

서비스 목표는 아래와 같다.

- 야간 이슈, 위험 계정, 우선 대응 순서를 자동 handoff로 정리한다
- 출근 직후 첫 5분 안에 대응 우선순위를 확정하게 한다
- admin UI는 결과를 점검하는 보조 수단이고, 핵심 가치는 digest 엔진이 만든다

---

## Stage 0: Service Lens

### 사용자

- support operations lead
- CX lead
- escalation manager

### 핵심 Job

- "오늘 가장 먼저 대응해야 할 고객과 이슈를 5분 안에 결정하고 싶다"

### 가치 순간

- 출근 직후 handoff를 열었을 때 긴급도와 우선순위가 이미 정리되어 있는 순간

### 기술의 역할

- Python 서비스는 handoff 품질과 우선순위 로직을 만드는 가치 엔진이다
- admin 웹은 운영자가 결과를 검토하는 보조 접점이다
- 문서는 운영 흐름과 제품 의도를 빠르게 복원하는 도구다

### 지금 보지 않아도 되는 것

- admin UI의 세부 스타일
- 프레임워크 취향
- 내부 구현 미세 최적화

---

## 의사결정 질문

1. 이 저장소의 핵심 가치가 admin UI에 있는가, digest 엔진에 있는가?
2. 가치 엔진과 운영용 보조 UI의 anchor는 각각 어디에 있는가?
3. 상위 디렉토리 중 어디부터 읽는 것이 서비스 복원에 가장 빠른가?
4. 지금 바로 열 파일 5개는 무엇인가?

---

## 단계별 실험 내용

### Stage 1

- 목적: 저장소가 문서+엔진+UI를 함께 가지는지 본다
- 보고 싶은 신호: markdown, python, json이 함께 존재하는지
- 기대 해석: 단순 admin UI가 아니라 가치 엔진이 있는 혼합형 저장소다

### Stage 2

- 목적: 가치 엔진과 보조 UI anchor를 찾는다
- 보고 싶은 신호: `services/digest/pyproject.toml`, `services/digest/.env.example`, `apps/admin/package.json`, 각 README
- 기대 해석: digest 엔진과 admin UI가 책임 분리되어 있다

### Stage 3

- 목적: 어떤 영역부터 파야 하는지 정한다
- 보고 싶은 신호: `services`가 1위, `apps`가 2위
- 기대 해석: handoff 품질을 만드는 엔진부터 보고, 운영용 UI는 그 다음에 본다

### Stage 4

- 목적: 바로 열 파일을 정한다
- 보고 싶은 신호: 루트 README, service README, app README, service manifest가 상위 추천
- 기대 해석: 온보딩 순서가 `전체 설명 -> 가치 엔진 설명 -> 보조 UI 설명 -> 실행/설정 정보`로 흐른다

---

## 실행 방법

```bash
bash kimjungsu/code/run_project_scan_usecase.sh ops-handoff
```

---

## 기대 결과 요약

- stage 1: 혼합형 저장소로 분류할 수 있어야 한다
- stage 2: service/app anchor를 정확히 찾을 수 있어야 한다
- stage 3: `services > apps > ROOT > docs` 순위가 나와야 한다
- stage 4: 루트 README와 service README가 app README보다 앞서고, service manifest가 뒤를 받쳐야 한다
