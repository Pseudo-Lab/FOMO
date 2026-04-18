# FOMO Crew W2: fixture에서 실제 입력으로 확장하기

> 목표: 서비스 관점 프로젝트 이해와 서비스 가치 알고리즘 평가를, fixture에서 실제 저장소와 실제 로그로 확장 가능한 재현 실험 하네스로 만든다.

---

## 1. 이번 주 목표

- `project_scan`이 fixture/usecase 같은 실험 자산에 오염되지 않고 실제 저장소를 분석할 수 있게 만든다.
- 유즈케이스 실행 결과를 터미널 출력뿐 아니라 Markdown 보고서로 남긴다.
- `service_value_eval`이 고정 fixture뿐 아니라 외부 TSV dataset도 같은 metric으로 평가할 수 있게 만든다.
- 각 단계의 변경 이유, 완료 기준, 검증 결과를 문서에 남긴다.

---

## 2. 단계별 작업 계획

| 단계 | 작업 | 완료 기준 | 검증 |
|:---:|:---|:---|:---|
| 1 | `project_scan` 실제 저장소용 exclude/profile 모드 | `kimjungsu` 스캔 시 `fixtures/`와 `usecases/`가 stage 4 상위 추천을 오염시키지 않음 | `verify_project_scan.sh`에 profile 검증 추가 |
| 2 | Markdown 보고서 저장 모드 | 유즈케이스 실행 결과가 `reports/` 또는 지정 경로의 Markdown으로 저장됨 | 보고서에 stage 1~4와 service lens가 포함됨 |
| 3 | `service_value_eval` 외부 dataset 입력 계약 | `--dataset path.tsv`로 기존 fixture와 같은 metric 출력 가능 | 기존 fixture 결과 유지 + 외부 dataset fixture 검증 |
| 4 | 추천 이유의 서비스 언어 보강 | stage 4 또는 보고서가 왜 먼저 읽는지 서비스 관점으로 설명 | generic reason이 비어 있지 않고 usecase별 흐름을 유지 |
| 5 | 사업기획팀 현실 유즈케이스 추가 | `biz-planning` 프로젝트 이해와 우선순위 알고리즘 평가가 실제 하네스로 실행됨 | `verify_project_scan.sh`, `verify_service_value_eval.sh`에 사업기획팀 검증 추가 |
| 6 | 사업기획팀 유즈케이스 현실성 보강 | baseline도 일부 맞는 경계 사례와 로그 샘플을 추가해 toy dataset을 피함 | `biz-planning` fixture 5 cases + 외부 로그 샘플 검증 |
| 7 | 공개 CRM 데이터셋 준비 | Maven CRM Sales Opportunities를 `biz-planning` silver TSV로 변환 | `verify_dataset_preparation.sh` |
| 8 | Olist 실제 공개 로그 준비 | Olist funnel/e-commerce 실제 익명화 로그를 `biz-planning` silver TSV로 변환 | `verify_dataset_preparation.sh` |
| 9 | 실서비스 정답 검증 workflow | blind review pack과 단일 reviewer rank 적용 계약을 만든다 | `verify_gold_review_workflow.sh` |
| 10 | 복수 reviewer adjudication workflow | consensus와 disagreement를 분리하고 최종 adjudication 전 gold 적용을 막는다 | `verify_gold_review_workflow.sh` |

---

## 3. 진행 기록

### 1단계. 실제 저장소용 exclude/profile 모드

- 상태: 구현 및 검증 완료
- 변경:
  - `project_scan.sh`에 `--profile default|real-repo` 옵션을 추가했다.
  - `real-repo` profile은 `fixtures/`, `usecases/`, `reports/`, `__pycache__/`, `.venv/`, `node_modules/` 같은 실험 자산과 생성물을 제외한다.
  - `--exclude glob` 옵션으로 추가 제외 규칙을 직접 넘길 수 있게 했다.
  - scan header에 `profile`과 적용된 `excludes`를 출력해 재현 조건을 남긴다.
- 검증:
  - `bash -n kimjungsu/code/project_scan.sh` 통과.
  - `bash kimjungsu/code/project_scan.sh --stage 4 --profile real-repo kimjungsu`에서 `fixtures/`와 `usecases/`가 상위 추천에서 제외되는 것을 확인했다.
  - `verify_project_scan.sh`에 `real-repo` profile 회귀 검증을 추가했다.
  - `./kimjungsu/code/verify_project_scan.sh` 통과.
- 남은 점검:
  - 실제 대규모 저장소에서 제외 기본값이 과하거나 부족하지 않은지 추가 사례로 확인한다.

### 2단계. Markdown 보고서 저장 모드

- 상태: 구현 및 검증 완료
- 변경:
  - `run_project_scan_usecase.sh`에 `--report path.md` 옵션을 추가했다.
  - 보고서에는 usecase, target, 재실행 명령, 전체 stage 출력이 Markdown 형식으로 저장된다.
  - 기본 터미널 출력은 유지해 기존 데모 흐름이 바뀌지 않게 했다.
- 검증:
  - `bash -n kimjungsu/code/run_project_scan_usecase.sh` 통과.
  - `/tmp`의 임시 Markdown 파일로 `docs-only` report 생성을 확인했다.
  - `verify_project_scan.sh`에 report title, usecase, service lens, stage 1, stage 4 포함 검증을 추가했다.
  - `./kimjungsu/code/verify_project_scan.sh` 통과.
- 남은 점검:
  - 실제 `reports/` 디렉토리를 만들지 여부는 산출물 관리 정책에 맞춰 결정한다.

### 3단계. 외부 dataset 입력 계약

- 상태: 구현 및 검증 완료
- 변경:
  - `service_value_eval.sh`에 `--dataset path.tsv` 옵션을 추가했다.
  - dataset header가 선택한 usecase schema와 맞는지 실행 전에 검증한다.
  - row 존재, numeric `expected_rank`, case별 gold rank 1개 존재를 검사한다.
  - `fixtures/service_value/log_sample_briefing_priority_cases.tsv`를 외부 로그 샘플 fixture로 추가했다.
  - `fixtures/service_value/log_sample_biz_planning_priority_cases.tsv`를 사업기획팀 외부 로그 샘플 fixture로 추가했다.
  - 출력에 `dataset_source=fixture|override`와 dataset schema 계약을 남긴다.
- 검증:
  - `bash -n kimjungsu/code/service_value_eval.sh` 통과.
  - `bash kimjungsu/code/service_value_eval.sh --dataset kimjungsu/fixtures/service_value/log_sample_briefing_priority_cases.tsv briefing`에서 `top1_accuracy=1.00`을 확인했다.
  - `bash kimjungsu/code/service_value_eval.sh --dataset kimjungsu/fixtures/service_value/log_sample_biz_planning_priority_cases.tsv biz-planning`에서 `top1_accuracy=1.00`을 확인했다.
  - briefing schema를 ops-handoff usecase에 넣으면 schema mismatch 에러가 나는 것을 확인했다.
  - `./kimjungsu/code/verify_service_value_eval.sh` 통과.
- 남은 점검:
  - 실제 사용자 로그를 어느 단위로 TSV에 투영할지 별도 수집/전처리 계약이 필요하다.

### 4단계. 추천 이유 서비스 언어 보강

- 상태: 구현 및 검증 완료
- 변경:
  - `run_project_scan_usecase.sh`의 stage 4 뒤에 `[read-first service rationale]` 섹션을 추가했다.
  - briefing-app은 web 가치 접점과 python service 품질 엔진을 구분해 설명한다.
  - ops-handoff는 `services/digest` 가치 엔진과 `apps/admin` 보조 접점을 구분해 설명한다.
  - 사용자 정의 유즈케이스는 service lens가 구체화되기 전까지 기술 스택 이름만으로 중요도를 확정하지 않는다는 fallback 설명을 남긴다.
- 검증:
  - `bash -n kimjungsu/code/run_project_scan_usecase.sh` 통과.
  - briefing-app과 ops-handoff 출력에서 service rationale 섹션을 확인했다.
  - `verify_project_scan.sh`에 report 포함 여부와 유즈케이스별 rationale 문구 검증을 추가했다.
- 남은 점검:
  - 실제 저장소용 service lens 입력 형식이 생기면 rationale을 정적 문구에서 입력 기반 설명으로 확장한다.

### 5단계. 사업기획팀 현실 유즈케이스 추가

- 상태: 구현 및 검증 완료
- 변경:
  - `biz-planning` 유즈케이스를 추가했다.
  - 현실 시나리오는 사업기획팀, FP&A, Revenue Operations 리드가 주간 운영 회의 전에 forecast gap, board deadline, cross-team dependency, revenue impact를 보고 첫 확인 항목을 결정하는 상황으로 잡았다.
  - `fixtures/biz_planning/`에 planning console, forecasting service, planning operating model, metrics, weekly review log 문서를 가진 샘플 저장소를 추가했다.
  - `usecases/project_scan_biz_planning.md`에 service lens와 stage별 기대 결과를 기록했다.
  - `fixtures/service_value/biz_planning_priority_cases.tsv`와 `usecases/service_value_biz_planning.md`를 추가했다.
  - `service_value_eval.sh`에 `biz-planning` scorer를 추가해 forecast-gap-only baseline과 서비스 가설 기반 hypothesis를 비교한다.
- 검증:
  - `bash kimjungsu/code/run_project_scan_usecase.sh biz-planning`에서 `services > apps > ROOT > docs` 순위를 확인했다.
  - `bash kimjungsu/code/service_value_eval.sh biz-planning`에서 hypothesis `top1_accuracy=1.00`을 확인했다.
  - `bash kimjungsu/code/service_value_eval.sh --mode baseline biz-planning`에서 baseline `top1_accuracy=0.20`, `mrr=0.53`, `mean_gold_rank=2.20`을 확인했다.
  - `verify_project_scan.sh`와 `verify_service_value_eval.sh`에 사업기획팀 회귀 검증을 추가했다.
- 남은 점검:
  - 실제 사업기획팀 로그가 들어오면 현재 fixture 컬럼이 충분한지 확인해야 한다.

### 6단계. 사업기획팀 유즈케이스 현실성 보강

- 상태: 구현 및 검증 완료
- 변경:
  - `biz_planning_priority_cases.tsv`를 3 cases에서 5 cases로 늘리고, 20개 row로 확장했다.
  - P4는 gap 자체도 크고 board-facing impact도 큰 케이스로 두어 forecast-gap-only baseline도 맞게 했다.
  - P1/P2/P3/P5는 gap만 보면 다른 항목이 먼저 올라오지만, 실제 사업기획팀 첫 확인 항목은 deadline, dependency, exec visibility, revenue impact 때문에 달라지는 경계 사례로 뒀다.
  - `fixtures/biz_planning/docs/metrics.md`와 `fixtures/biz_planning/docs/weekly_review_log.md`를 추가해 저장소 fixture가 실제 운영 회의 문맥을 갖게 했다.
  - `log_sample_biz_planning_priority_cases.tsv`를 외부 로그 샘플로 추가했다.
  - `usecases/service_value_biz_planning.md`에 baseline도 일부 맞아야 현실적인 평가라는 기준을 명시했다.
- 검증:
  - hypothesis는 `cases=5`, `top1_accuracy=1.00`, `mrr=1.00`, `mean_gold_rank=1.00`이다.
  - baseline은 `cases=5`, `top1_accuracy=0.20`, `mrr=0.53`, `mean_gold_rank=2.20`이다.
  - 외부 로그 샘플은 `cases=2`, `top1_accuracy=1.00`, `mrr=1.00`으로 평가된다.
- 남은 점검:
  - 실제 익명화 로그가 들어오면 현재 5개 feature가 충분한지, 또는 source/channel/owner 같은 운영 필드를 추가해야 하는지 확인한다.

### 7단계. 공개 CRM 데이터셋 준비

- 상태: 구현 및 검증 완료
- 변경:
  - Maven Analytics의 `CRM Sales Opportunities` 공개 데이터셋을 1차 외부 후보로 선정했다.
  - 원본 CSV를 `datasets/raw/maven_crm_sales_opportunities/`에 준비했다.
  - `datasets/README.md`에 후보 리서치, 선정 이유, 라이선스, 필드 매핑, 한계를 기록했다.
  - `prepare_biz_planning_crm_dataset.py`를 추가해 CRM sales pipeline을 `biz-planning` TSV schema로 변환한다.
  - 변환 산출물 `datasets/prepared/maven_crm_biz_planning_silver.tsv`를 추가했다.
  - `verify_dataset_preparation.sh`를 추가해 raw 파일 존재, 변환 재현성, hypothesis/baseline 평가 metric을 검증한다.
- 원본 audit:
  - `sales_pipeline.csv` rows: 8,800
  - usable closed rows: 6,711
  - skipped open rows: 2,089
- 변환 결과:
  - rows: 32
  - cases: 8
  - case grain: quarter + regional office
- 검증:
  - hypothesis: `cases=8`, `top1_accuracy=0.50`, `mrr=0.69`, `mean_gold_rank=1.88`
  - baseline: `cases=8`, `top1_accuracy=0.25`, `mrr=0.53`, `mean_gold_rank=2.38`
  - `./kimjungsu/code/verify_dataset_preparation.sh` 통과.
- 남은 점검:
  - 이 dataset의 `expected_rank`는 사람이 찍은 gold가 아니라 deterministic silver label이다.
  - 실제 익명화 로그가 생기면 silver label 규칙이 아니라 사용자 선택/운영 판단 기반 gold label로 교체해야 한다.

### 8단계. Olist 실제 공개 로그 준비

- 상태: 구현 및 검증 완료
- 변경:
  - Olist Marketing Funnel과 Brazilian E-Commerce를 실제 공개 로그 후보로 선정했다.
  - 원본 CSV를 `datasets/raw/olist/`에 준비했다.
  - `datasets/README.md`에 실제 로그 후보군, Olist 선정 이유, 필드 매핑, 한계를 기록했다.
  - `prepare_biz_planning_olist_dataset.py`를 추가해 Olist funnel/order/review/payment/seller 로그를 `biz-planning` TSV schema로 변환한다.
  - 변환 산출물 `datasets/prepared/olist_biz_planning_silver.tsv`를 추가했다.
  - `verify_dataset_preparation.sh`에 Olist raw 파일 존재, 변환 재현성, hypothesis/baseline 평가 metric을 추가했다.
- 원본 audit:
  - MQL rows: 8,000
  - closed deal rows: 842
  - order rows: 99,441
  - order item rows: 112,650
  - seller-month rows after join: 1,030
- 변환 결과:
  - rows: 48
  - cases: 12
  - case grain: month + business segment
- 검증:
  - hypothesis: `cases=12`, `top1_accuracy=0.83`, `mrr=0.90`, `mean_gold_rank=1.25`
  - baseline: `cases=12`, `top1_accuracy=0.33`, `mrr=0.54`, `mean_gold_rank=2.58`
  - `./kimjungsu/code/verify_dataset_preparation.sh` 통과.
- 남은 점검:
  - Olist는 실제 익명화 로그지만, 우선순위 gold label은 deterministic silver label이다.
  - `forecast_gap_pct`가 높은 구간에 몰려 있어 다음 개선에서 segment별 gap bucket을 더 정교하게 다듬어야 한다.

### 9단계. 실서비스 정답 검증 workflow

- 상태: 구현 및 검증 완료
- 변경:
  - `build_gold_review_pack.py`를 추가해 `biz-planning` dataset에서 silver `expected_rank`를 숨긴 blind review pack을 만든다.
  - `apply_gold_review_labels.py`를 추가해 reviewer가 채운 `reviewer_rank`를 `service_value_eval.sh` 입력 dataset의 `expected_rank`로 적용한다.
  - `datasets/review_packs/olist_biz_planning_review_pack.tsv`를 생성했다.
  - `datasets/gold_labels/README.md`에 reviewer protocol과 gate를 기록했다.
  - `verify_gold_review_workflow.sh`를 추가해 review pack 재현성, `expected_rank` 비노출, label 적용, invalid label reject를 검증한다.
- 검증:
  - review pack rows: 48
  - review pack cases: 12
  - `expected_rank`는 review pack header에서 제외된다.
  - completed review를 적용하면 `service_value_eval.sh --dataset`으로 평가 가능하다.
  - 빈 reviewer rank는 거부된다.
  - `./kimjungsu/code/verify_gold_review_workflow.sh` 통과.
- 남은 점검:
  - 실제 human gold label 파일은 아직 없다.
  - 이 단계에서는 단일 reviewer label 적용까지만 다뤘고, 복수 reviewer disagreement 처리는 10단계에서 보강했다.

### 10단계. 복수 reviewer adjudication workflow

- 상태: 구현 및 검증 완료
- 변경:
  - `adjudicate_gold_reviews.py`를 추가해 reviewer 2명 이상의 completed review TSV를 병합한다.
  - reviewer별 TSV schema, case/item set, feature value, case별 1..N rank 연속성을 검증한다.
  - 모든 item rank가 같은 consensus case는 `reviewer_rank`를 자동으로 채운다.
  - rank가 다른 disagreement case는 해당 case 전체의 `reviewer_rank`를 비워 최종 adjudicator가 판단하게 한다.
  - disagreement detail TSV에는 reviewer별 rank/rationale과 adjudication 입력 칸을 남기되 `expected_rank`는 노출하지 않는다.
  - `datasets/gold_labels/README.md`, `datasets/README.md`, `usecases/service_value_biz_planning.md`에 복수 reviewer 절차를 기록했다.
- 검증:
  - reviewer count: 2
  - 완전 합의 contract test: `consensus_cases=12`, `disagreement_cases=0`, `full_rank_agreement_rate=1.00`
  - 불일치 contract test: `consensus_cases=11`, `disagreement_cases=1`, `needs_adjudication_rows=4`
  - disagreement pack header에서 `expected_rank`는 제외된다.
  - disagreement template은 final rank가 비어 있어 `apply_gold_review_labels.py`에서 거부된다.
  - `./kimjungsu/code/verify_gold_review_workflow.sh` 통과.
- 남은 점검:
  - 실제 reviewer 파일이 들어오면 reviewer id/date naming 규칙과 final adjudicator 책임자를 별도로 고정해야 한다.

---

## 4. 최종 점검

- 상태: 구현 및 검증 완료
- 실행한 검증:
  - `bash -n kimjungsu/code/project_scan.sh`
  - `bash -n kimjungsu/code/run_project_scan_usecase.sh`
  - `bash -n kimjungsu/code/service_value_eval.sh`
  - `bash -n kimjungsu/code/verify_project_scan.sh`
  - `bash -n kimjungsu/code/verify_service_value_eval.sh`
  - `./kimjungsu/code/verify_project_scan.sh`
  - `./kimjungsu/code/verify_service_value_eval.sh`
  - `./kimjungsu/code/verify_dataset_preparation.sh`
  - `./kimjungsu/code/verify_gold_review_workflow.sh`
  - `git diff --check`
  - `biz-planning` 프로젝트 이해 검증 포함
  - `biz-planning` 서비스 가치 알고리즘 baseline/hypothesis 검증 포함
  - `biz-planning` 외부 로그 샘플 dataset 검증 포함
  - Maven CRM 공개 dataset 변환/평가 검증 포함
  - Olist 실제 공개 로그 변환/평가 검증 포함
  - Olist human gold review workflow 계약 검증 포함
- 남은 리스크:
  - 실제 대규모 저장소에서는 `real-repo` profile의 제외 규칙이 너무 넓거나 좁을 수 있다.
  - Olist는 실제 공개 로그지만 실제 사업기획팀이 찍은 우선순위 gold label은 아니다.
  - 실서비스 gold label 검증을 위해서는 reviewer가 채운 별도 gold label 파일이 필요하다.
  - Maven CRM dataset은 공개 sales pipeline 기반 silver label이므로 실서비스 gold label 검증을 대체하지 않는다.
  - 실제 저장소용 service lens 입력 형식이 없어서 service rationale은 usecase별 정적 문구로 남아 있다.
