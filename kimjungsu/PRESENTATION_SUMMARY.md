# 김정수 발표용 정리

## 한 줄 메시지

제가 이번에 한 일은 크게 두 가지입니다.

1. 처음 보는 프로젝트를 **서비스 관점에서 더 빨리 이해하는 실험 흐름**을 만들었습니다.
2. 서비스의 핵심 가치를 만드는 알고리즘을 **객관적이고 재현 가능하게 검증하는 실험 흐름**을 만들었습니다.

짧게 말하면,
**"감으로 읽고 감으로 튜닝하던 일을, 단계와 검증이 있는 실험으로 바꿨다"**고 정리할 수 있습니다.

---

## 왜 이 작업을 시작했는가

프로젝트를 처음 받으면 보통 이런 일이 생깁니다.

- 파일이 많아서 어디부터 읽어야 할지 모르고
- 기술 스택만 보고 성급하게 판단하고
- 서비스의 핵심 가치가 어디서 만들어지는지 놓치고
- 알고리즘은 "이 점수식이 좋아 보인다" 수준에서 튜닝되기 쉽습니다

저는 이 문제를 두 층으로 나눠서 봤습니다.

### 1. 구조 이해 문제

처음 보는 저장소에서
"무엇부터 읽어야 하는가"를 재현 가능한 흐름으로 바꿔야 했습니다.

### 2. 가치 검증 문제

서비스의 핵심 가치를 만드는 알고리즘은
"그럴듯해 보이는가"가 아니라
"서비스에서 세운 가설을 실제로 더 잘 만족시키는가"로 검증해야 했습니다.

즉 이번 작업의 핵심 질문은 이것입니다.

- 프로젝트를 서비스 관점에서 더 빨리 이해할 수 있는가?
- 서비스 가치 알고리즘을 객관적이고 재현 가능하게 평가할 수 있는가?

---

## 이번에 만든 것

### A. 프로젝트 구조 분석 하네스

관련 스크립트:

- `kimjungsu/code/project_scan.sh`
- `kimjungsu/code/run_project_scan_usecase.sh`
- `kimjungsu/code/verify_project_scan.sh`

이 실험은 단순히 파일 목록을 보여주는 것이 아니라,
서비스를 이해하기 위한 읽기 순서를 단계적으로 만듭니다.

단계는 아래와 같습니다.

1. Stage 0: 이 서비스가 누구를 위한 무엇인지 먼저 본다
2. Stage 1: 저장소를 추측 없이 계수한다
3. Stage 2: README, package, pyproject 같은 anchor를 찾는다
4. Stage 3: 어느 디렉토리부터 볼지 우선순위를 만든다
5. Stage 4: 실제로 어떤 파일부터 열어야 할지 추천한다

핵심은
**기술 스택을 먼저 해석하지 않고, 서비스의 가치 순간을 먼저 고정한다**는 점입니다.

### B. 서비스 가치 알고리즘 평가 하네스

관련 스크립트:

- `kimjungsu/code/service_value_eval.sh`
- `kimjungsu/code/verify_service_value_eval.sh`

이 실험은 알고리즘을 "좋아 보이는 점수식"이 아니라
**서비스 가설을 검증하는 대상**으로 다룹니다.

단계는 아래와 같습니다.

1. Stage 0: 이 알고리즘이 어떤 결정을 더 잘 만들려는지 적는다
2. Stage 1: 고정 fixture와 gold label을 확인한다
3. Stage 2: 결정론적으로 ranking을 만든다
4. Stage 3: baseline보다 실제 품질이 나아졌는지 본다
5. Stage 4: 같은 입력에서 다시 돌려도 같은 결과가 나오는지 본다

핵심은
**서비스 가설 -> baseline -> 고정 데이터 -> metric -> 재현성** 순서로 본다는 점입니다.

---

## 쉽게 설명하면

이번 작업은 "프로젝트 읽기"와 "알고리즘 검증"을 둘 다
`감`에서 `실험`으로 바꾸는 작업이었습니다.

이걸 발표에서는 이렇게 설명하면 이해가 쉽습니다.

- 프로젝트 분석은 "도면 없이 건물에 들어가는 것"과 비슷합니다.
- 알고리즘 튜닝은 "정답표 없이 시험 문제를 푸는 것"과 비슷합니다.

제가 만든 것은 그 반대입니다.

- 프로젝트 분석에는 `어디부터 볼지 알려주는 도면`
- 알고리즘 평가에는 `고정 문제집과 채점표`

를 붙인 것입니다.

---

## 사례 1: Daily Briefing App

### 서비스 상황

대상 고객은 10~80명 규모 스타트업의 팀 리드 또는 운영 리드입니다.

이 사람은 아침마다

- 일정 확인
- 중요한 미팅 준비
- 팀 이슈 파악
- 오늘의 우선순위 결정

을 여러 도구에서 따로 해야 합니다.

즉 진짜 문제는
정보가 없어서가 아니라,
**흩어진 정보를 아침 2분 안에 행동 순서로 정리하지 못한다**는 점입니다.

### 이 유즈케이스에서 얻은 것

이 서비스는 사용자가 직접 가치를 체감하는 접점이 웹 앱에 더 가깝습니다.
그래서 구조 분석 결과도 `apps > services`로 나와야 자연스럽습니다.

실제로 검증 결과는 이렇게 나왔습니다.

- Stage 3: `apps(score=23) > services(score=17)`
- Stage 4: `README.md -> apps/web/README.md -> services/briefing/README.md`

즉 이 저장소는
**사용자가 보는 가치 접점부터 이해하고, 그 다음에 품질 로직으로 내려가는 흐름**이 맞다고 해석할 수 있습니다.

### 발표용 한 문장

"이 케이스에서는 서비스 가치가 웹에서 먼저 체감되기 때문에, 구조 분석도 앱을 먼저 보도록 나와야 했고 실제로 그렇게 검증됐습니다."

---

## 사례 2: Support Ops Morning Handoff

### 서비스 상황

대상 고객은 30~200명 규모 SaaS 회사의 support operations lead 또는 CX lead입니다.

이 사람은 아침마다

- 야간 이슈 확인
- VIP 고객 이슈 점검
- 온콜 로그 확인
- 오늘 가장 먼저 대응할 고객 결정

을 수동으로 정리합니다.

즉 진짜 문제는
**어떤 고객과 어떤 이슈를 먼저 대응해야 하는지 아침 5분 안에 정리되지 않는다**는 점입니다.

### 이 유즈케이스에서 얻은 것

이 서비스는 admin UI보다 digest engine이 더 핵심입니다.
그래서 구조 분석 결과도 `services > apps`로 나와야 자연스럽습니다.

실제로 검증 결과는 이렇게 나왔습니다.

- Stage 3: `services(score=23) > apps(score=17)`
- Stage 4: `README.md -> services/digest/README.md -> apps/admin/README.md`

중간에 `.env.example` 같은 숨김 운영 파일도 반영해서,
서비스 엔진이 운영 책임까지 가진다는 해석이 가능해졌습니다.

### 발표용 한 문장

"같은 스크립트라도 서비스의 본질이 다르면 읽기 우선순위가 달라져야 하는데, ops handoff에서는 실제로 services-first가 나왔습니다."

---

## 사례 3: 서비스 가치 알고리즘 평가

여기서부터는 구조가 아니라 알고리즘 검증입니다.

### 3-1. Briefing 우선순위 알고리즘

서비스 가설은 이렇습니다.

- baseline: urgency만 보면 된다
- hypothesis: urgency만으로는 부족하고, `due time`, `prep need`, `team impact`, `user visibility`를 함께 봐야 한다

왜 이런 가설을 세웠냐면,
실제 사용자에게 중요한 것은 "긴급해 보이는 일"보다
**지금 당장 준비하지 않으면 바로 문제가 되는 일**일 수 있기 때문입니다.

대표 사례:

- `board_demo_prep`
- `triage_minor_bug`

urgency만 보면 bug가 먼저 올라갈 수 있습니다.
하지만 서비스 관점에서는 바로 준비가 필요한 board demo가 먼저여야 합니다.

실제 결과:

- hypothesis: `top1_accuracy=1.00`, `mrr=1.00`
- baseline: `top1_accuracy=0.33`, `mrr=0.61`

즉 이 실험은
"가설을 추가했더니 점수가 좋아졌다"가 아니라,
**사용자가 첫 행동을 더 맞게 고르게 되었다**고 말할 수 있게 해줍니다.

### 3-2. Ops Handoff 우선순위 알고리즘

서비스 가설은 이렇습니다.

- baseline: severity만 보면 된다
- hypothesis: severity만으로는 부족하고, `SLA risk`, `VIP`, `overnight incident`, `revenue risk`를 함께 봐야 한다

대표 사례:

- `vip_outage`
- `standard_bug`

severity만 보면 standard bug가 먼저 보일 수 있습니다.
하지만 운영 리드의 실제 판단에서는 VIP outage가 먼저여야 합니다.

실제 결과:

- hypothesis: `top1_accuracy=1.00`, `mrr=1.00`
- baseline: `top1_accuracy=0.00`, `mrr=0.50`

즉 이 실험은
**서비스의 핵심 판단 기준을 알고리즘에 반영했을 때 실제 선택 품질이 좋아진다**는 것을 보여줍니다.

### 발표용 한 문장

"좋은 알고리즘은 복잡한 알고리즘이 아니라, 서비스가 중요하다고 말한 판단을 더 정확하게 재현하는 알고리즘입니다."

---

## 이번 작업에서 중요한 변화

### 1. 기술 중심 해석에서 서비스 중심 해석으로 이동

예전에는

- TypeScript가 있으니 프론트가 중요하겠지
- Python이 있으니 백엔드가 중요하겠지

처럼 보기 쉬웠습니다.

이제는

- 누가 이 서비스를 쓰는가
- 어디서 가치를 체감하는가
- 어떤 엔진이 핵심 가치를 만드는가

를 먼저 고정하고 기술을 해석합니다.

### 2. "좋아 보인다"에서 "검증된다"로 이동

예전에는 알고리즘을 설명할 때
"이 조합이 더 그럴듯하다"로 끝날 수 있었습니다.

이제는

- 고정 fixture
- baseline 비교
- 명시적 metric
- repeat run reproducibility

까지 포함해 말할 수 있습니다.

### 3. 문서와 실행이 연결됨

이번 작업은 문서만 만든 것이 아닙니다.
실제로 실행 가능한 스크립트와 검증 스크립트까지 붙였습니다.

즉 발표에서
"이렇게 생각했습니다"가 아니라
**"이렇게 실행했고, 이렇게 통과했습니다"**라고 말할 수 있습니다.

---

## 실제 검증 결과

### 프로젝트 구조 분석 실험

실행:

```bash
bash kimjungsu/code/verify_project_scan.sh /home/kjs/projects/FOMO
```

결과:

- fixture 검증 통과
- usecase 검증 통과
- boundary 검증 통과
- baseline 비교 통과
- smoke 검증 통과

### 서비스 가치 알고리즘 실험

실행:

```bash
bash kimjungsu/code/verify_service_value_eval.sh
```

결과:

- briefing reproducibility 통과
- ops-handoff reproducibility 통과
- baseline 대비 metric 개선 확인
- hypothesis 결과 재현 확인

---

## 한계도 분명합니다

이번 결과를 발표할 때는 강점만 말하지 말고 한계도 같이 말하는 편이 좋습니다.

### 1. 아직 offline fixture 중심이다

지금은 고정 TSV fixture로 평가하고 있습니다.
즉 실제 사용자 로그를 직접 본 것은 아닙니다.

그래서 지금 단계의 의미는

- "서비스 가설을 정직하게 실험할 수 있는 최소 구조를 만들었다"

이지,

- "실서비스에서 이미 완전히 검증했다"

는 아닙니다.

### 2. project_scan은 아직 실제 저장소 오염 문제가 남아 있다

`fixtures/`, `usecases/`가 분석 대상에 같이 들어가면
실험 자산이 실제 결과를 오염시킬 수 있습니다.

즉 구조 분석 하네스는 유즈케이스와 fixture에서는 잘 동작하지만,
실제 대규모 저장소 분석에서는 제외 규칙을 더 정교하게 붙일 필요가 있습니다.

### 3. 알고리즘 metric도 더 확장할 수 있다

지금은 `top1_accuracy`, `MRR`, `mean_gold_rank` 중심입니다.
이후에는

- recall 계열
- segment별 성능
- 실제 사용자 선택 로그

까지 연결할 수 있습니다.

---

## 다음 단계

다음 작업은 세 방향으로 이어갈 수 있습니다.

1. `project_scan`에 실제 저장소 분석용 exclude 모드를 추가한다
2. 서비스 가치 알고리즘 실험을 실제 로그 기반 평가로 확장한다
3. 결과를 발표용 리포트 또는 Markdown 보고서로 자동 저장한다

발표에서는 이 문장으로 마무리하면 자연스럽습니다.

**"이번 작업의 핵심은 기술을 더 많이 붙인 것이 아니라, 서비스 이해와 가치 검증을 반복 가능한 실험으로 바꿨다는 점입니다."**

---

## 발표 흐름 예시

5~7분 발표라면 아래 순서가 가장 자연스럽습니다.

1. 문제 제기
   - 프로젝트는 감으로 읽고, 알고리즘은 감으로 튜닝되는 문제가 있었다
2. 접근
   - 구조 분석 하네스와 가치 알고리즘 평가 하네스를 분리해 만들었다
3. 사례 1
   - briefing app에서 왜 apps-first가 나와야 하는지 설명
4. 사례 2
   - ops handoff에서 왜 services-first가 나와야 하는지 설명
5. 사례 3
   - baseline과 hypothesis의 metric 차이 설명
6. 검증 결과
   - verify 통과와 재현성 강조
7. 한계와 다음 단계
   - offline fixture에서 online validation으로 확장 계획 제시

---

## 바로 데모할 명령

```bash
bash kimjungsu/code/run_project_scan_usecase.sh briefing-app
bash kimjungsu/code/run_project_scan_usecase.sh ops-handoff
bash kimjungsu/code/service_value_eval.sh briefing
bash kimjungsu/code/service_value_eval.sh --mode baseline briefing
bash kimjungsu/code/service_value_eval.sh ops-handoff
bash kimjungsu/code/verify_project_scan.sh /home/kjs/projects/FOMO
bash kimjungsu/code/verify_service_value_eval.sh
```
