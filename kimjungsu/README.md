# 김정수 - FOMO Crew KMS

> **"먼저 구조를 읽고, 작은 자동화부터 붙인다."**

## Focus

- 프로젝트 분석을 반복 가능한 흐름으로 바꾸기
- 가벼운 하네스부터 시작해서 점진적으로 자동화 늘리기
- 문서와 스크립트가 함께 남는 개인 실험 저장소 만들기
- 서비스 가설을 객관적이고 재현 가능한 알고리즘 실험으로 바꾸기

## 현재 트랙

- W1 주제: 코드베이스 분석 하네스 시작하기
- 첫 실험: 프로젝트 구조를 빠르게 훑는 경량 스캔 스크립트 만들기
- 목표: "이 프로젝트가 뭐지?"를 재현 가능한 출력으로 바꾸기
- 두 번째 실험: 서비스 핵심 가치 알고리즘을 baseline과 비교 평가하기

## 실험 원칙

- 모든 실험은 `목표 -> 단계 -> 검증 -> 다음 단계` 순서로 남긴다
- 각 단계는 이전 단계와 무엇이 다른지 한 줄로 설명할 수 있어야 한다
- 검증 기준은 실행 가능한 체크로 적는다
- 한 번에 많은 기능을 추가하지 않고, 단계별로 출력 차이를 확인한다

참고 문서: [EXPERIMENT_FRAMEWORK.md](EXPERIMENT_FRAMEWORK.md)

## 폴더 구조

```text
kimjungsu/
├── README.md               # 개인 KMS 소개와 진행 현황
├── EXPERIMENT_FRAMEWORK.md # 실험 설계/검증 공통 규칙
├── fixtures/               # 단계 검증용 샘플 입력
├── usecases/               # 실제 실험 시나리오 문서
├── weekly/
│   └── week1.md            # 주차별 기록
└── code/
    ├── baseline_project_scan.sh
                             # 비교용 최소 baseline
    ├── project_scan.sh     # 단계 실행형 프로젝트 스캔 실험
    ├── run_project_scan_usecase.sh
                             # 유즈케이스 단위 실험 실행
    ├── service_value_eval.sh
                             # 서비스 가치 알고리즘 평가
    ├── verify_project_scan.sh
                             # fixture/boundary/baseline/smoke 검증
    └── verify_service_value_eval.sh
                             # 알고리즘 가설의 품질/재현성 검증
```

## 현재 실험 단계

| 단계 | 질문 | 가정 수준 | 검증 포인트 | 이전 단계와의 차이 |
|:---:|:---|:---:|:---|:---|
| 0 | 누구의 어떤 가치를 이해하려는가 | Product | 고객, status quo, 핵심 가치 순간, 기술의 역할이 설명되는가 | 기술 이전에 서비스 본질을 고정한다 |
| 1 | 무엇이 얼마나 있는가 | Low | 총 파일 수, 확장자별 수, 기본 invariant | 추측 없이 계수만 한다 |
| 2 | 무엇이 진입점/anchor인가 | Medium | anchor 분류 정확도, 중복 제거, 정렬 | 수량에서 의미 있는 파일 분류로 이동한다 |
| 3 | 어느 영역부터 볼 것인가 | High | area priority score, 순위 안정성, 이유 출력 | anchor를 디렉토리 우선순위로 바꾼다 |
| 4 | 어떤 파일부터 열 것인가 | High | top file recommendation, 이유 출력, 존재 파일만 추천 | 디렉토리 우선순위를 실제 읽기 순서로 내린다 |

## 핵심 가치 알고리즘 실험 단계

| 단계 | 질문 | 가정 수준 | 검증 포인트 | 이전 단계와의 차이 |
|:---:|:---|:---:|:---|:---|
| 0 | 이 알고리즘이 어떤 서비스 결정을 더 잘 만들려는가 | Product | 고객 판단, hypothesis, baseline이 서비스 언어로 적히는가 | 기술 점수식이 아니라 서비스 의사결정을 먼저 고정한다 |
| 1 | 어떤 고정 case set으로 평가할 것인가 | Low | case 수, row 수, gold label 존재 | 즉흥 입력이 아니라 버전 고정 fixture를 쓴다 |
| 2 | 결정론적으로 어떤 순위를 내는가 | Medium | 안정적인 sorting, tie-break, score 이유 | 결과를 설명 가능한 ranking으로 만든다 |
| 3 | baseline보다 실제 결정 품질이 나아지는가 | High | top1 accuracy, MRR, mean gold rank | 출력 존재가 아니라 품질 차이를 검증한다 |
| 4 | 같은 입력에서 반복 실행 결과가 같은가 | High | 2회 실행 동일 출력 | 성능뿐 아니라 재현성을 검증한다 |

## 검증 레이어

- Invariant: 값 형식과 기본 수학 관계 검증
- Fixture: 구조를 아는 샘플 저장소에서 정확도 검증
- Boundary: 단계 간 정보가 섞이지 않았는지 검증
- Baseline: 구조화된 실험이 단순 baseline보다 더 많은 신호를 주는지 검증
- Smoke: 실제 저장소에서 에러 없이 종료되는지 검증
- Reproducibility: 같은 입력 두 번 실행 시 완전히 같은 결과가 나오는지 검증

## Harness에서 가져온 원칙

- `Phase 0 audit`: 실행 전에 현재 스크립트/fixture/doc drift를 먼저 본다
- `Service Lens First`: 기술 전에 사용자, 가치, 핵심 순간을 먼저 고정한다
- `Pipeline`: stage 1 -> stage 2 -> stage 3은 순차 의존으로 설계한다
- `Producer-Reviewer`: 생성 스크립트와 검증 스크립트를 분리한다
- `With-skill vs Baseline`: 구조화된 실험이 정말 차이를 만드는지 비교한다
- `Non-discriminating assertion 금지`: 둘 다 쉽게 통과하는 테스트는 버린다
- `Forcing Questions`: 실험 전 "어떤 결정을 바꾸는가, 현재 상태는 무엇인가"를 먼저 묻는다
- `Hard Gate`: stage가 답하면 안 되는 질문을 명시한다
- `Artifact Handoff`: 한 단계 출력이 다음 단계 입력이 되도록 설계한다
- `Objective Evaluation`: 서비스 가설은 baseline과 고정 fixture 위에서 비교한다

## Weekly Archive

| 주차 | 주제 | 핵심 인사이트 | 링크 |
|:---:|:---|:---|:---|
| W1 | 코드베이스 분석 하네스 시작하기 | 프로젝트 분석도 재현 가능한 입력/출력 흐름으로 만들 수 있다 | [week1.md](weekly/week1.md) |

## Next Step

- 서비스 렌즈를 각 유즈케이스에 더 명확히 붙이기
- 유즈케이스별 기대 결과를 더 늘리기
- 고객 유형이 다를 때 stage 3/4 우선순위가 어떻게 달라지는지 비교하기
- stage 4 추천 이유를 더 서비스 흐름 중심으로 정교하게 만들기
- 결과를 Markdown 보고서로 저장하는 모드 추가
- 핵심 가치 알고리즘의 offline proxy를 온라인 지표와 연결하기
