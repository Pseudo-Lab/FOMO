# FOMO Crew W1: 코드베이스 분석 하네스 시작하기

> **"프로젝트 분석도 감이 아니라 흐름으로 남긴다."**

---

## 1. 이번 주 목표

- 템플릿 상태였던 개인 폴더를 실제 작업 가능한 구조로 전환
- 첫 실험 주제를 "코드베이스 분석 하네스"로 고정
- 반복해서 사용할 수 있는 최소 스캔 스크립트 추가

---

## 2. Output Archive

### 2-1. 폴더 구조 초기화

- `weekly/` 디렉토리 생성
- `code/` 디렉토리 생성
- README를 템플릿에서 실제 진행 문서로 업데이트

### 2-2. 첫 실험 주제 선정

이번 첫 실험은 **프로젝트 구조를 빠르게 파악하는 경량 스캔 하네스**다.

핵심 질문은 다음과 같다.

1. 이 저장소는 문서 중심인가, 코드 중심인가?
2. 실행 가능한 하위 프로젝트는 어디에 몰려 있는가?
3. 처음 읽어야 할 파일은 무엇인가?
4. 이 기술 구조가 결국 어떤 고객의 어떤 서비스 가치를 전달하려는 것인가?

### 2-3. 첫 코드 산출물

[`project_scan.sh`](../code/project_scan.sh)

이 스크립트는 단계별로 다른 질문에 답한다.

- Stage 0: 서비스의 사용자, 핵심 가치, 가치 순간을 먼저 본다
- Stage 1: 저장소를 추측 없이 계수한다
- Stage 2: 진입점과 ecosystem anchor를 찾는다
- Stage 3: 상위 디렉토리 우선순위로 바꾼다
- Stage 4: 실제 read-first 파일 추천으로 내린다

[`verify_project_scan.sh`](../code/verify_project_scan.sh)

이 스크립트는 다음 4층 검증을 실행한다.

- invariant check
- fixture check
- boundary check
- baseline comparison
- smoke check

[`baseline_project_scan.sh`](../code/baseline_project_scan.sh)

이 스크립트는 `revfactory/harness`의 with-skill vs baseline 관점을 가져온 비교용 최소 baseline이다.
핵심은 "실험 스크립트가 baseline보다 실제로 더 구조화된 신호를 제공하는가"를 확인하는 것이다.

[`run_project_scan_usecase.sh`](../code/run_project_scan_usecase.sh)

이 스크립트는 준비된 유즈케이스를 stage 1~4로 실제 실행하고,
각 단계가 어떤 결정을 돕는지까지 같이 출력한다.

[`service_value_eval.sh`](../code/service_value_eval.sh)

이 스크립트는 서비스의 핵심 가치 알고리즘을
고정 fixture 위에서 baseline과 비교 평가한다.

- briefing: "무엇을 먼저 해야 하는가" ranking
- ops handoff: "무엇을 먼저 대응해야 하는가" prioritization

핵심은 알고리즘을 "모델 취향"이 아니라
**서비스 가설 검증 대상**으로 다루는 것이다.

[`verify_service_value_eval.sh`](../code/verify_service_value_eval.sh)

이 스크립트는 다음을 검증한다.

- hypothesis run 2회 반복 실행 동일성
- baseline 대비 품질 차이
- gold item rank 재현

### 2-4. 단계별 실험 설계

| 단계 | 질문 | 가정 수준 | 새로 얻는 정보 | 검증 기준 | 이전 단계와의 차이 |
|:---:|:---|:---:|:---|:---|:---|
| 0 | 누구의 어떤 가치를 이해하려는가 | Product | 고객, status quo, 핵심 가치 순간, 기술의 역할 | 유즈케이스 문서와 실행 출력에서 서비스 렌즈가 설명되는가 | 기술 해석의 기준을 먼저 세운다 |
| 1 | 무엇이 얼마나 있는가 | Low | 전체 파일 수, 확장자 분포 | 숫자 형식, subtotal <= total | 추측 없이 계수만 한다 |
| 2 | 무엇이 진입점인가 | Medium | README, 설정 파일, ecosystem anchor | fixture에서 정확한 anchor 목록 일치 | 수량에서 의미 있는 파일 분류로 이동한다 |
| 3 | 어느 영역부터 읽을 것인가 | High | top-level area priority, 점수, 이유 | fixture에서 area 순위와 점수 일치 | 분류 결과를 디렉토리 우선순위로 바꾼다 |
| 4 | 어떤 파일부터 열 것인가 | High | top file recommendation, 이유 | fixture에서 추천 파일 순위 일치 | 디렉토리 우선순위를 실제 파일 순서로 내린다 |

### 2-5. 실행 예시

```bash
./kimjungsu/code/project_scan.sh --stage 1 .
./kimjungsu/code/project_scan.sh --stage 2 .
./kimjungsu/code/project_scan.sh --stage 3 .
./kimjungsu/code/project_scan.sh --stage 4 .
./kimjungsu/code/verify_project_scan.sh .
bash ./kimjungsu/code/run_project_scan_usecase.sh briefing-app
```

### 2-6. 검증 입력 설계

fixture를 따로 두는 이유는 실제 저장소를 정답으로 쓰면 검증이 흔들리기 때문이다.

- `fixtures/sample_app`
  - Python 백엔드와 TypeScript 프론트엔드가 같이 있는 혼합형 저장소
  - anchor, 코드 파일, 문서 파일이 모두 있어 stage 1/2/3 검증에 적합

- `fixtures/docs_only`
  - 문서만 있는 저장소
  - anchor가 거의 없는 상황에서도 stage 2/3/4가 깨지지 않는지 확인

- `fixtures/briefing_app`
  - 실제 제품 저장소를 흉내낸 간단한 daily briefing app 모노레포
  - stage별 결과를 실제 온보딩 의사결정과 연결해 해석할 수 있다
  - 기술 구조를 서비스 가치와 연결하는 Stage 0 설명을 포함한다

- `fixtures/ops_handoff`
  - support ops용 morning handoff 서비스 저장소
  - 고객 가치가 web보다 digest engine에 더 가까운 상황을 검증한다
  - `.env.example` 같은 숨김 운영 파일도 가치 엔진의 책임 신호로 반영되는지 본다
  - 동일한 스크립트가 `apps-first`가 아니라 `services-first`를 낼 수 있는지 본다

- `fixtures/service_value`
  - 서비스 핵심 가치 알고리즘 평가용 고정 TSV fixture
  - briefing / ops handoff 두 서비스의 gold priority case를 담는다
  - baseline과 hypothesis를 같은 입력에서 비교할 수 있게 한다

### 2-7. revfactory/harness에서 가져온 설계 포인트

- `Phase 0 audit`
  - 실행 전에 현재 실험 자산의 drift를 먼저 점검한다
- `Pipeline`
  - stage 1 -> 2 -> 3은 순차 의존으로 설계한다
- `Producer-Reviewer`
  - `project_scan.sh`는 생성자, `verify_project_scan.sh`는 채점자 역할을 맡는다
- `With-skill vs Baseline`
  - `baseline_project_scan.sh`와 비교해 구조화된 실험의 차이를 본다
- `Non-discriminating assertion 금지`
  - "출력이 있다" 같은 약한 검증 대신, 정확한 anchor/priority assertion을 사용한다

### 2-8. gstack에서 가져온 설계 포인트

- `Forcing Questions`
  - 이 실험이 실제로 바꾸는 결정이 무엇인지 먼저 고정한다
- `Service Lens`
  - 기술 분석 전에 고객, status quo, 핵심 가치, 가치 순간을 먼저 고정한다
- `Hard Gate`
  - stage 1은 추천을 하지 않고, stage 2는 점수화를 하지 않는다
- `Artifact Handoff`
  - 한 단계 출력이 다음 단계 입력이 되는 구조를 유지한다
- `Evidence-first Review`
  - "좋아 보인다" 대신 fixture와 assertion으로 말한다
- `Question -> Design -> Build -> Verify -> Retro`
  - 실험도 작은 스프린트처럼 운영한다

### 2-9. 핵심 가치 알고리즘 실험 설계

이제 구조 분석과 별도로,
서비스의 핵심 가치를 구현하는 알고리즘도 별도 실험으로 다룬다.

| 단계 | 질문 | 가정 수준 | 새로 얻는 정보 | 검증 기준 | 이전 단계와의 차이 |
|:---:|:---|:---:|:---|:---|:---|
| 0 | 어떤 서비스 결정을 더 잘 만들려는가 | Product | 고객 판단, hypothesis, baseline | 서비스 언어로 가설이 적혔는가 | 기술 최적화가 아니라 서비스 결정을 먼저 고정한다 |
| 1 | 어떤 고정 case set으로 평가할 것인가 | Low | case 수, row 수, gold label | fixture integrity | 즉흥 예시 대신 버전 고정 데이터를 쓴다 |
| 2 | 알고리즘이 어떤 순위를 내는가 | Medium | case별 predicted rank와 이유 | stable sorting, tie-break | 결과를 결정론적 ranking으로 만든다 |
| 3 | baseline보다 실제로 나아졌는가 | High | top1 accuracy, MRR, mean gold rank | baseline 비교 통과 | 그럴듯함이 아니라 품질 차이를 본다 |
| 4 | 다시 돌려도 같은가 | High | repeat run 동일 출력 | byte-for-byte equality | 성능뿐 아니라 재현성까지 검증한다 |

---

## 3. 이번 주 핵심 인사이트

- 프로젝트 분석 요청은 즉흥적으로 읽는 것보다, 같은 형식으로 반복 가능한 출력이 더 유용하다.
- "무슨 프로젝트인지"를 설명하려면 먼저 파일 밀도와 핵심 설정 파일 위치를 봐야 한다.
- 작은 스크립트 하나만 있어도 이후 분석 품질과 속도가 같이 올라간다.
- 단계별 출력 차이가 분명해야 실험이 "추가된 것"을 설명할 수 있다.
- 검증 스크립트가 있으면 실험이 문서가 아니라 반복 가능한 절차가 된다.
- 실제 저장소 검증만으로는 부족하고, fixture 기반 정확도 검증이 필요하다.
- 단계 분리는 "출력 화면"이 아니라 "가정 수준"의 차이로 설명되어야 한다.
- structured workflow가 baseline보다 더 좋은지 비교해야 실험 가치가 생긴다.
- 실험 전 질문이 약하면 단계 설계도 흐려진다. 질문 설계가 먼저다.
- 실제 유즈케이스가 있어야 각 단계가 어떤 의사결정을 돕는지 더 분명해진다.
- 기술은 구조를 읽기 위한 도구일 뿐이고, 최종 해석은 서비스 가치와 연결되어야 한다.
- 고객 정의가 구체적일수록 stage 3/4 우선순위도 더 일관되게 설명할 수 있다.
- 고객 가치가 UI 중심인지 엔진 중심인지에 따라 stage 3/4 결과도 달라져야 한다.
- 숨김 운영 파일을 빼면 서비스 엔진이 축소 해석될 수 있으므로, dotfile도 실험 범위에 포함해야 한다.
- 서비스 핵심 알고리즘은 "점수식"이 아니라 "서비스 가설"로 정의해야 한다.
- 핵심 가치 알고리즘은 baseline 비교와 고정 fixture 없이는 객관적 검증이 어렵다.
- 재현성은 좋은 결과의 부가 옵션이 아니라 실험 계약 자체여야 한다.

---

## 4. Pain Point & Next Action

| Pain Point | 현재 대응 | 다음 액션 |
|:---|:---|:---|
| 기술 분석이 서비스 이해보다 앞설 수 있음 | Stage 0 service lens를 먼저 둔다 | 유즈케이스별 service lens 다양화 |
| 처음 보는 저장소에서 어디부터 읽어야 할지 애매함 | 파일 수, 핵심 파일, 상위 디렉토리 분포를 먼저 본다 | 읽기 우선순위 추천 규칙 추가 |
| 프로젝트 분석 결과가 사람마다 들쭉날쭉함 | stage별 출력 형식을 고정한다 | Markdown 보고서 저장 모드 추가 |
| 단계가 늘어날수록 차이점이 흐려질 수 있음 | boundary check로 섞임을 검사한다 | stage diff 요약 자동 생성 |
| 구조화된 실험이 정말 효과적인지 애매함 | baseline과 직접 비교한다 | with-structure vs baseline 차이 지표 추가 |
| 문서형 저장소와 코드형 저장소를 한눈에 구분하기 어려움 | 확장자별 수량을 함께 본다 | 산출물 밀도 점수 추가 |
| 실험 결과가 실제 판단과 연결되지 않을 수 있음 | briefing app 유즈케이스로 단계별 의사결정을 연결한다 | 유즈케이스 다양화 |
| 핵심 가치 알고리즘이 감으로만 튜닝될 수 있음 | 고정 fixture와 baseline 비교를 붙인다 | 온라인 로그 기반 평가로 확장 |

---

## 5. Next Week

- 스캔 결과를 `weekly/` 보고서 초안으로 연결
- "실행 가능한 하위 프로젝트" 후보를 자동으로 표시
- 핵심 파일 우선순위 추천 로직 추가
- 단계별 차이를 한 줄 요약으로 자동 생성
- 실제 저장소 리포트 저장 모드 추가

---

_FOMO — 고민을 기록하고, 흐름을 만든다._
