# Experiment Framework

## 목적

김정수 폴더의 실험은 "아이디어 메모"가 아니라 **반복 가능한 실험 절차**로 남긴다.
각 실험은 반드시 아래 4가지를 가져야 한다.

1. 무엇을 알고 싶은가
2. 단계를 왜 나누는가
3. 각 단계는 무엇을 새로 추가하는가
4. 단계별 성공/실패를 어떻게 판정하는가

---

## 실험 계약

모든 실험은 아래 계약을 만족해야 한다.

이 계약은 `revfactory/harness`의 6-Phase workflow, 실행 모드 선택, 그리고 `skill-testing-guide.md`의 평가 방법론을 참고해 재구성했다.
여기에 `garrytan/gstack`의 `office-hours`, `review`, 그리고 sprint handoff 구조를 더해 실험 전 질문과 단계 간 인수인계 규칙을 추가했다.

---

## gstack에서 가져온 실험 전 질문

`gstack /office-hours`의 forcing questions 아이디어를 실험 설계에 맞게 변형한다.
스크립트를 쓰기 전에 최소 아래 질문에 답한다.

### Q1. Decision Reality

**Ask:** 이 실험 결과가 어떤 실제 결정을 바꾸는가?

**Push until:** "출력 예쁘게 만들기"가 아니라 "무엇부터 읽을지", "어떤 디렉토리를 먼저 열지" 같은 행동 변화가 나온다.

### Q2. Status Quo

**Ask:** 지금은 이 문제를 어떻게 해결하고 있는가?

**Push until:** 현재 워크플로가 `find`, `rg --files`, 수동 읽기처럼 구체적인 명령이나 행동 단위로 설명된다.

### Q3. Narrowest Wedge

**Ask:** 가장 작은 단계에서 이미 유용해지는 출력은 무엇인가?

**Push until:** 첫 단계만으로도 쓸모가 있어야 한다. 예를 들어 "파일 수와 확장자 분포"처럼 바로 판단에 도움 되는 최소 신호가 있어야 한다.

### Q4. Observation & Surprise

**Ask:** 이 실험이 기대와 다르게 보여주길 바라는 신호는 무엇인가?

**Push until:** "문서형일 줄 알았는데 코드가 몰린 디렉토리가 보였다"처럼 가설을 흔드는 관측이 나온다.

### Q5. Future-Fit

**Ask:** 실험이 커질 때도 지금의 단계 분리가 유지되는가?

**Push until:** stage가 늘어나도 각 단계 질문이 여전히 독립적이어야 한다. 아니면 지금 설계가 잘못된 것이다.

---

## Service Lens First

기술 실험이라도 서비스의 본질보다 앞서면 안 된다.
구조 분석은 어디까지나 **서비스를 더 빨리 이해하기 위한 도구**다.

그래서 모든 실험은 기술 단계 전에 아래 `Stage 0`을 가진다.

### Stage 0. Service Lens

기술을 보기 전에 먼저 고정할 질문:

1. **누가 이 서비스를 쓰는가**
   - 직무, 상황, 사용 맥락
2. **이 서비스가 대신 해결하는 일은 무엇인가**
   - 사용자가 달성하려는 핵심 job
3. **가장 중요한 가치 순간은 언제인가**
   - 사용자가 "이건 쓸만하다"를 느끼는 첫 순간
4. **기술이 담당하는 역할은 무엇인가**
   - 기술은 본질이 아니라 가치 전달을 위한 수단이어야 한다
5. **지금 보지 않아도 되는 기술은 무엇인가**
   - 서비스 본질과 무관한 세부 구현은 뒤로 미룬다

### Stage 0 Hard Gate

- Stage 0이 비어 있으면 기술 단계 해석을 확정하지 않는다
- "React라서", "FastAPI라서" 같은 답은 서비스 설명이 아니다
- 기술 선택은 반드시 사용자 가치나 운영 비용과 연결되어야 한다

좋은 해석:

- "웹 앱을 먼저 보는 이유는 사용자가 직접 접하는 가치 순간이 거기 있기 때문이다"
- "서비스 디렉토리를 두 번째로 보는 이유는 개인화 로직이 가치 품질을 결정하기 때문이다"

나쁜 해석:

- "TypeScript가 있으니 프론트가 중요하다"
- "Python이 있으니 백엔드를 먼저 봐야 한다"

---

## 단계 간 handoff 규칙

`gstack`는 각 skill이 다음 skill의 입력 문서를 남긴다. 실험도 동일하게 본다.

- Stage 0 출력은 Stage 1~4 해석의 기준이 된다
- Stage 1 출력은 Stage 2의 입력이 된다
- Stage 2 출력은 Stage 3의 입력이 된다
- 검증 스크립트는 각 stage 산출물을 독립적으로 읽고 채점할 수 있어야 한다

즉 단계는 "화면 묶음"이 아니라 **이전 산출물을 소비하는 파이프라인**이어야 한다.

### Hard Gate

- Stage 1은 우선순위 판단을 하면 안 된다
- Stage 2는 점수화와 추천을 하면 안 된다
- Stage 3은 Stage 1/2에서 확인하지 않은 사실을 근거 없이 만들면 안 된다

단계가 답하면 안 되는 질문을 명시하는 것이 중요하다.

### 1. 단계는 질문 단위로 나눈다

- 한 단계는 하나의 질문에만 답해야 한다.
- 한 단계에서 두 가지 이상의 새로운 판단을 섞지 않는다.
- 단계 이름만 보고도 "무슨 정보가 추가되는지" 설명할 수 있어야 한다.

### 2. 단계마다 가정 수준을 명시한다

- `Low`: 계수, 존재 여부, 정렬 같은 거의 추측 없는 단계
- `Medium`: 규칙 기반 분류, anchor 탐지처럼 제한된 해석이 들어가는 단계
- `High`: 우선순위 추천, 점수화처럼 해석과 휴리스틱이 들어가는 단계

가정 수준이 올라갈수록 검증 강도도 올라가야 한다.

### 3. 단계 경계를 출력으로 확인할 수 있어야 한다

- Stage 1 출력에 Stage 2 전용 정보가 섞이면 안 된다.
- Stage 2 출력에 Stage 3 전용 점수화가 섞이면 안 된다.
- `verify` 스크립트에서 단계 간 경계가 깨졌는지 검사해야 한다.

### 4. 검증은 4층으로 나눈다

1. **Invariant check**
   - 숫자는 숫자여야 한다
   - 결과는 정렬되어야 한다
   - 중복이 없어야 한다

2. **Fixture check**
   - 구조를 아는 샘플 입력에 대해 정확한 결과가 나와야 한다
   - 회귀를 잡는 가장 중요한 층이다

3. **Boundary check**
   - Stage 1에는 Stage 2 정보가 없어야 한다
   - Stage 2에는 Stage 3 정보가 없어야 한다
   - 단계 차이가 흐려지지 않았는지 본다

4. **Smoke check**
   - 실제 저장소에서도 에러 없이 끝나는지 본다
   - 정확도보다 안정성을 확인하는 층이다

### 5. 가능하면 baseline을 둔다

`revfactory/harness`는 with-skill vs baseline 비교를 권장한다. 같은 입력에서 구조화된 설정이 실제로 차이를 만드는지 보려면 baseline이 필요하다.

- baseline은 일부러 단순해야 한다
- baseline은 실험의 핵심 가치를 아직 제공하지 않아야 한다
- baseline과 실험 출력의 차이가 assertion으로 드러나야 한다

예:

- baseline: 단순 파일 목록 출력
- experiment: 계수, anchor 탐지, 우선순위 추천까지 제공

### 6. non-discriminating assertion을 금지한다

`revfactory/harness`의 testing guide에서 강조하듯, 두 구성 모두 쉽게 통과하는 assertion은 차별력을 측정하지 못한다.

금지 예:

- "출력이 존재한다"
- "에러 없이 종료된다"

권장 예:

- "sample fixture에서 python anchor가 정확히 backend/pyproject.toml로 분류된다"
- "priority 1위가 frontend이고 score가 23이다"
- "stage 2 출력에는 priority 섹션이 없어야 한다"

### 7. Phase 0 audit를 둔다

`revfactory/harness`는 실행 전에 현황을 먼저 감사한다. 실험도 마찬가지로 시작 전에 아래를 본다.

- 기존 스크립트와 검증 스크립트가 있는가
- fixture와 문서의 버전이 맞는가
- 단계 정의와 실제 출력이 drift 상태가 아닌가

실험이 실패하는 이유가 로직 때문인지, 환경 drift 때문인지 먼저 분리해야 한다.

### 8. 리뷰는 evidence-first로 한다

`gstack /review`처럼 "실제 근거를 읽고 말한다"를 유지한다.

- 안전하다고 주장하면 그 근거가 출력 또는 fixture에 있어야 한다
- 잘 동작한다고 주장하면 검증 스크립트 결과가 있어야 한다
- 애매한 표현 대신 assertion으로 쪼갠다

---

## 단계 설계 원칙

### 좋은 단계 분리

- Stage 0: "이 서비스의 핵심 가치는 무엇인가"
- Stage 1: "무엇이 얼마나 있는가"
- Stage 2: "무엇이 중요한 파일인가"
- Stage 3: "그래서 무엇부터 읽을 것인가"

좋은 분리의 핵심은 **이전 단계 출력 없이 다음 단계가 설명되지 않는 구조**다.

### 나쁜 단계 분리

- Stage 1: 파일 수 + anchor 탐지 + 우선순위 추천
- Stage 2: 사실상 Stage 1 반복
- Stage 3: 이름만 다르고 출력 차이가 없음

이런 경우는 단계가 아니라 화면 분할일 뿐이다.

### 패턴 선택 원칙

`revfactory/harness`의 아키텍처 패턴을 실험 설계에도 적용한다.

- **Pipeline**
  - 단계가 순차 의존일 때 사용
  - 예: inventory -> anchor detection -> priority
- **Fan-out/Fan-in**
  - 독립 평가를 병렬로 돌릴 때 사용
  - 예: invariant, fixture, boundary, smoke 평가를 나눠 실행 후 종합
- **Producer-Reviewer**
  - 산출물 생성과 검증을 분리할 때 사용
  - 예: `project_scan.sh`가 생성자, `verify_project_scan.sh`가 채점자
- **Expert Pool**
  - 특정 오류 유형만 따로 보고 싶을 때 사용
  - 예: 성능 검증, trigger 검증, assertion 검증을 선택 실행

현재 `project_scan`은

- 서비스 해석은 `Service Lens`
- 실행 단계는 `Pipeline`
- 검증 단계는 `Producer-Reviewer + Fan-out`

구조로 해석한다.

또한 운영 흐름은 `gstack`의 sprint chain을 축약해 다음처럼 본다.

`Question -> Service Lens -> Design -> Build -> Verify -> Retro`

- Question: forcing questions로 실험 목적 고정
- Service Lens: 서비스 가치, 사용자, 핵심 순간 고정
- Design: 단계와 hard gate 정의
- Build: 스크립트 구현
- Verify: fixture/boundary/baseline/smoke 검증

---

## 핵심 가치 알고리즘 실험 계약

서비스의 핵심 가치를 만드는 알고리즘은
"좋아 보인다"가 아니라 **서비스 가설을 실제로 검증하는 실험**으로 다뤄야 한다.

예:

- morning briefing에서 "무엇을 먼저 해야 하는가"를 정하는 ranking
- support ops handoff에서 "어떤 고객과 이슈를 먼저 대응해야 하는가"를 정하는 prioritization

이런 알고리즘은 아래 계약을 만족해야 한다.

### 1. 가설은 서비스 언어로 적는다

좋은 가설:

- "고객에게 바로 보이는 일정과 팀 전체를 막는 이슈를 함께 반영하면, 첫 행동 선택이 더 정확해진다"
- "severity만 보지 않고 SLA, VIP, revenue risk를 함께 반영하면 support lead의 첫 대응 선택이 더 맞아진다"

나쁜 가설:

- "가중치를 조금 바꿨더니 점수가 좋아 보인다"
- "모델이 더 똑똑해 보인다"

즉 알고리즘 가설은 반드시
**누구의 어떤 판단을 더 잘 만들려는가**로 써야 한다.

### 2. 평가 단위는 실제 결정이어야 한다

출력 한 줄보다 중요한 것은
"그 순간 어떤 항목을 1순위로 올렸는가" 같은 실제 행동 결정이다.

그래서 가능한 한 아래 단위로 평가한다.

- case 단위: 한 번의 아침 브리핑, 한 번의 handoff 묶음
- action 단위: case 안에서 가장 먼저 해야 할 항목
- ranking 단위: 1위뿐 아니라 gold item이 몇 위에 왔는가

### 3. fixture는 고정하고 버전 관리한다

핵심 가치 알고리즘은 임의 입력으로 그때그때 평가하면 재현성이 없다.

반드시 아래를 고정한다.

- 고정 fixture 파일 경로
- 컬럼 정의
- 기대 정답
- scorer version

fixture가 바뀌면 문서와 검증도 같이 바뀌어야 한다.

### 4. baseline을 반드시 둔다

서비스 가설이 맞는지 보려면
"그 가설 없이도 나오는 결과"와 비교해야 한다.

예:

- briefing baseline: urgency만 보는 단순 정렬
- ops baseline: severity만 보는 단순 정렬

이 비교가 없으면 가설의 기여도를 분리할 수 없다.

### 5. metric은 객관적이고 차별적이어야 한다

권장 metric:

- `top1_accuracy`
- `MRR`
- `mean_gold_rank`

금지 metric:

- "결과가 그럴듯해 보인다"
- "팀이 좋아할 것 같다"

metric은 baseline과 실험을 실제로 구분할 수 있어야 한다.

### 6. scorer는 결정론적이어야 한다

재현성을 위해 아래를 고정한다.

- 랜덤 시드 없음 또는 명시
- tie-break 규칙 고정
- 입력 정렬 규칙 고정
- 출력 포맷 고정
- 같은 입력 두 번 실행 시 완전히 같은 출력

즉 "비슷하게"가 아니라
**두 번 돌려도 byte-for-byte로 같아야 한다**를 목표로 둔다.

### 7. 검증은 5층으로 본다

1. `Fixture integrity`
   - case 수, row 수, 정답 레이블이 맞는가
2. `Scoring correctness`
   - 특정 case의 1위 항목이 기대와 맞는가
3. `Metric quality`
   - hypothesis가 baseline보다 metric이 좋은가
4. `Reproducibility`
   - 동일 명령 2회 실행 결과가 완전히 같은가
5. `Interpretability`
   - 왜 그 항목이 1위인지 score 이유를 설명할 수 있는가

### 8. 온라인 실험 전까지는 offline proxy를 정직하게 쓴다

지금 당장 실사용 로그가 없으면
offline fixture를 써도 된다.
대신 아래를 명확히 적는다.

- 이 fixture가 무엇을 대리 측정하는가
- 무엇은 아직 측정하지 못하는가
- 온라인 검증으로 넘어갈 때 무엇을 추가해야 하는가

즉 offline score를
"진짜 사용자 가치의 완전한 대체"로 과장하면 안 된다.
- Retro: 무엇이 surprise였는지 기록

---

## 실험 템플릿

| 항목 | 질문 |
|:---|:---|
| Goal | 이 실험이 최종적으로 알고 싶은 것은 무엇인가 |
| Service Lens | 누구의 어떤 가치를 더 빨리 이해하려는가 |
| Stage 1 | 가장 낮은 가정으로 무엇을 확인하는가 |
| Stage 2 | 어떤 규칙을 추가해 더 의미 있는 신호를 얻는가 |
| Stage 3 | 어떤 휴리스틱으로 행동 가능한 출력으로 바꾸는가 |
| Invariants | 어떤 값은 항상 성립해야 하는가 |
| Fixtures | 어떤 샘플 입력으로 정확도를 보장할 것인가 |
| Boundary | 각 단계에 나오면 안 되는 정보는 무엇인가 |
| Smoke | 실제 입력에서 최소 무엇을 보장할 것인가 |

---

## project_scan에 적용한 해석

- Stage 0: 서비스의 사용자, 핵심 가치, 가치 순간을 먼저 고정한다
- Stage 1: 저장소를 추측 없이 계수한다
- Stage 2: 진입점과 설정 anchor를 찾는다
- Stage 3: 읽기 우선순위로 바꾼다

즉 `서비스 본질 고정 -> 계수 -> 분류 -> 우선순위화` 흐름이다.

여기에 `revfactory/harness` 관점을 더하면:

- `baseline_project_scan.sh` = without-skill baseline
- `project_scan.sh` = structured workflow
- `verify_project_scan.sh` = grader/reviewer

즉 "구조화된 단계가 실제로 baseline보다 더 유의미한 정보를 만드는가"를 보는 실험이 된다.
