# 김정수 - FOMO Crew KMS

> **"먼저 구조를 읽고, 작은 자동화부터 붙인다."**

## Focus

- 서비스 관점 프로젝트 이해를 반복 가능한 실험 흐름으로 바꾸기
- 서비스 가치 알고리즘 평가를 객관적이고 재현 가능한 실험으로 바꾸기
- fixture에서 검증한 하네스를 실제 저장소와 실제 로그로 확장 가능하게 만들기
- 문서와 스크립트가 함께 남는 개인 실험 저장소 만들기

## 현재 트랙

- W1 주제: 코드베이스 분석 하네스 시작하기
- 첫 실험: 프로젝트 구조를 빠르게 훑는 경량 스캔 스크립트 만들기
- 두 번째 실험: 서비스 핵심 가치 알고리즘을 baseline과 비교 평가하기
- 현재 목표: 서비스 관점 프로젝트 이해와 서비스 가치 알고리즘 평가를, fixture에서 실제 저장소와 실제 로그로 확장 가능한 재현 실험 하네스로 만든다

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
├── PRESENTATION_DECK.md    # 7~10분 발표용 슬라이드형 자료
├── PRESENTATION_SUMMARY.md # 발표 준비용 긴 설명/멘트 정리
├── datasets/               # 공개 데이터셋 원본/변환 산출물/리서치 기록
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
    ├── prepare_biz_planning_crm_dataset.py
                             # 공개 CRM dataset을 biz-planning TSV로 변환
    ├── prepare_biz_planning_olist_dataset.py
                             # Olist 실제 공개 로그를 biz-planning TSV로 변환
    ├── build_gold_review_pack.py
                             # silver/gold 후보 dataset을 blind review pack으로 변환
    ├── apply_gold_review_labels.py
                             # reviewer rank를 service_value_eval dataset으로 적용
    ├── adjudicate_gold_reviews.py
                             # 복수 reviewer label을 합의/불일치 adjudication pack으로 병합
    ├── service_value_eval.sh
                             # 서비스 가치 알고리즘 평가
    ├── verify_dataset_preparation.sh
                             # 공개 CRM dataset 변환/평가 검증
    ├── verify_gold_review_workflow.sh
                             # human gold label 수집 workflow 계약 검증
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
| W2 | fixture에서 실제 입력으로 확장하기 | 실제 저장소/로그로 확장하려면 profile, report, dataset 계약이 필요하다 | [week2.md](weekly/week2.md) |

## Current Realistic Use Cases

| usecase | 고객 | 검증 질문 | 실행 |
|:---|:---|:---|:---|
| `briefing-app` | 팀 리드/운영 리드 | 아침 2분 안에 무엇을 먼저 해야 하는지 정할 수 있는가 | `bash kimjungsu/code/run_project_scan_usecase.sh briefing-app` |
| `ops-handoff` | Support Ops/CX 리드 | 출근 직후 어떤 고객과 이슈를 먼저 대응해야 하는지 정할 수 있는가 | `bash kimjungsu/code/run_project_scan_usecase.sh ops-handoff` |
| `biz-planning` | 사업기획팀/FP&A/Revenue Ops | 주간 운영 회의 전에 어떤 매출 가정과 리스크를 먼저 확인해야 하는지 정할 수 있는가 | `bash kimjungsu/code/run_project_scan_usecase.sh biz-planning` |

## Public Dataset Prep

1차 공개 데이터셋은 Maven Analytics의 `CRM Sales Opportunities`를 사용했다.
이 데이터셋은 B2B sales pipeline 형태라 하네스 smoke에는 좋지만, fictitious company 데이터이므로 실제 로그라고 보지는 않는다.

2차 공개 실제 로그는 Olist Marketing Funnel + Brazilian E-Commerce를 사용한다.
이 데이터셋은 실제 익명화/샘플링된 funnel 및 주문 로그라 `biz-planning` 현실성 보강에 더 적합하다.

- 리서치/출처/매핑 문서: [datasets/README.md](datasets/README.md)
- 원본 CSV: `datasets/raw/maven_crm_sales_opportunities/`
- Olist 원본 CSV: `datasets/raw/olist/`
- 변환 산출물: `datasets/prepared/maven_crm_biz_planning_silver.tsv`
- Olist 변환 산출물: `datasets/prepared/olist_biz_planning_silver.tsv`
- 변환 실행:
  `python3 kimjungsu/code/prepare_biz_planning_crm_dataset.py --crm-dir kimjungsu/datasets/raw/maven_crm_sales_opportunities --output kimjungsu/datasets/prepared/maven_crm_biz_planning_silver.tsv`
- Olist 변환 실행:
  `python3 kimjungsu/code/prepare_biz_planning_olist_dataset.py --olist-dir kimjungsu/datasets/raw/olist --output kimjungsu/datasets/prepared/olist_biz_planning_silver.tsv`
- 검증 실행:
  `./kimjungsu/code/verify_dataset_preparation.sh`
- gold review workflow 검증:
  `./kimjungsu/code/verify_gold_review_workflow.sh`

현재 공개 CRM silver dataset 평가 결과:

| mode | cases | top1_accuracy | mrr | mean_gold_rank |
|:---|---:|---:|---:|---:|
| hypothesis | 8 | 0.50 | 0.69 | 1.88 |
| baseline | 8 | 0.25 | 0.53 | 2.38 |

현재 Olist 실제 로그 기반 silver dataset 평가 결과:

| mode | cases | top1_accuracy | mrr | mean_gold_rank |
|:---|---:|---:|---:|---:|
| hypothesis | 12 | 0.83 | 0.90 | 1.25 |
| baseline | 12 | 0.33 | 0.54 | 2.58 |

## Gold Label Workflow

실서비스 정답 검증으로 가려면 silver `expected_rank`가 아니라 reviewer가 직접 찍은 rank가 필요하다.
이를 위해 Olist review pack을 생성했다.

- review pack: `datasets/review_packs/olist_biz_planning_review_pack.tsv`
- protocol: `datasets/gold_labels/README.md`
- pack 생성:
  `python3 kimjungsu/code/build_gold_review_pack.py --dataset kimjungsu/datasets/prepared/olist_biz_planning_silver.tsv --output kimjungsu/datasets/review_packs/olist_biz_planning_review_pack.tsv`
- reviewer label 적용:
  `python3 kimjungsu/code/apply_gold_review_labels.py --dataset kimjungsu/datasets/prepared/olist_biz_planning_silver.tsv --review path/to/completed_review.tsv --output kimjungsu/datasets/gold_labels/olist_biz_planning_gold.tsv`
- 2명 이상 reviewer adjudication:
  `python3 kimjungsu/code/adjudicate_gold_reviews.py --dataset kimjungsu/datasets/prepared/olist_biz_planning_silver.tsv --review fpna_a=path/to/reviewer_a.tsv --review revops_b=path/to/reviewer_b.tsv --output kimjungsu/datasets/gold_labels/olist_biz_planning_adjudicated_review.tsv --disagreements kimjungsu/datasets/gold_labels/olist_biz_planning_disagreements.tsv`

현재 `review_pack`에는 `expected_rank`가 없고, reviewer가 `reviewer_rank`와 `reviewer_rationale`을 채우는 구조다.
복수 reviewer가 완전히 합의한 case는 adjudication review에 rank를 자동으로 채우고, 불일치 case는 `reviewer_rank`를 비워 최종 adjudicator가 판단하게 한다.
실제 human gold label 파일은 아직 없다.

## W2 Active Plan

- [x] `project_scan`에 실제 저장소 분석용 exclude/profile 모드 추가
  - 목적: `fixtures/`, `usecases/`, 보고서 산출물이 실제 분석 결과를 오염시키지 않게 한다
  - 완료 기준: `kimjungsu` 폴더를 스캔해도 fixture README가 stage 4 상위 추천을 차지하지 않는다
  - 검증: `verify_project_scan.sh`에 exclude/profile fixture와 실제 폴더 smoke assertion을 추가한다
- [x] 결과를 Markdown 보고서로 저장하는 모드 추가
  - 목적: 재현 가능한 출력이 터미널 로그에만 남지 않고 공유 가능한 산출물로 남게 한다
  - 완료 기준: usecase 실행 결과가 `reports/` 아래 Markdown 파일로 저장된다
  - 검증: 같은 입력으로 다시 생성했을 때 핵심 섹션과 stage 순서가 유지된다
- [x] `service_value_eval`에 외부 dataset 입력 계약 추가
  - 목적: 고정 fixture 평가를 실제 로그 샘플 평가로 확장할 수 있게 한다
  - 완료 기준: `--dataset path.tsv`로 입력을 바꿀 수 있고 필수 컬럼, gold label, scorer version을 검증한다
  - 검증: 기존 fixture 결과는 유지하면서 로그 샘플 fixture도 같은 metric으로 평가한다
- [x] 서비스 렌즈와 stage 4 추천 이유를 실제 저장소용으로 정교화
  - 목적: 추천 이유가 기술 스택 이름보다 사용자 가치와 읽기 결정에 연결되게 한다
  - 완료 기준: stage 4 출력 또는 Markdown 보고서가 `왜 이 파일을 먼저 읽는가`를 서비스 언어로 설명한다
  - 검증: briefing, ops-handoff, 실제 저장소 smoke에서 추천 이유가 존재하고 빈 generic 문구가 아니다
- [x] 사업기획팀 현실 유즈케이스 추가
  - 목적: 사업기획팀/FP&A/Revenue Ops가 주간 매출 계획에서 어떤 가정과 리스크를 먼저 볼지 검증한다
  - 완료 기준: `biz-planning` 프로젝트 이해와 우선순위 알고리즘 평가가 기존 하네스에서 실행된다
  - 검증: `verify_project_scan.sh`와 `verify_service_value_eval.sh`에 `biz-planning` assertion을 추가한다
- [x] 사업기획팀 유즈케이스 현실성 보강
  - 목적: forecast-gap-only baseline을 무조건 틀리게 만드는 toy dataset을 피하고, 실제 사업기획팀 판단에 가까운 경계 사례를 넣는다
  - 완료 기준: `biz-planning` fixture가 5 cases/20 rows로 늘어나고, baseline도 일부 case를 맞춘다
  - 검증: hypothesis `top1_accuracy=1.00`, baseline `top1_accuracy=0.20`, 외부 로그 샘플 `cases=2`를 검증한다
- [x] 복수 reviewer adjudication workflow 추가
  - 목적: 단일 reviewer label이 아니라 2명 이상 reviewer의 합의/불일치를 분리해 실서비스 정답 검증을 더 엄격하게 만든다
  - 완료 기준: 합의 case는 자동 prefill되고, disagreement case는 최종 rank가 비어 있어 바로 gold로 적용되지 않는다
  - 검증: `verify_gold_review_workflow.sh`에서 consensus, disagreement, invalid label reject를 함께 검증한다

## Follow-up Checks

- 실제 대규모 저장소에서 `--profile real-repo` 제외 규칙이 과하거나 부족하지 않은지 확인한다.
- 실제 사용자 로그는 아직 익명화 샘플 TSV로만 검증했으므로, 실제 로그를 어떤 TSV 컬럼으로 투영할지 수집/전처리 계약을 추가한다.
- 공개 CRM silver dataset은 사람이 찍은 gold가 아니므로, 실서비스 성능 주장에는 쓰지 않고 하네스 확장 검증용으로만 쓴다.
- Olist는 실제 익명화 로그지만 gold label은 silver label이므로, 실제 사업기획팀 우선순위 검증으로 과장하지 않는다.
- 실제 gold label은 `datasets/gold_labels/`에 별도 파일로 받아야 하며, 현재는 단일 reviewer 적용과 복수 reviewer adjudication workflow 계약만 검증했다.
- 실제 저장소용 service lens 입력이 생기면 stage 4 rationale을 정적 문구에서 입력 기반 설명으로 확장한다.
