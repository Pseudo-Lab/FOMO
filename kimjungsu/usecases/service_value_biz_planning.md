# Use Case: Business Planning Priority Algorithm

## 서비스 가설

이 서비스의 핵심 가치는 사업기획팀이
주간 운영 회의 전에 어떤 매출 가정과 리스크를 먼저 확인해야 하는지 빠르게 고르게 만드는 것이다.

현실적인 status quo는 forecast gap만 보는 것이 완전히 틀렸다는 뜻이 아니다.
gap이 매우 크고 board-facing인 경우에는 gap-only baseline도 맞을 수 있다.
다만 실제 사업기획팀의 첫 확인 항목은 아래 신호가 같이 붙을 때 바뀐다.

- board pack 또는 CEO/COO 보고 마감이 가까운가
- 영업, 마케팅, CS, Finance가 같이 맞춰야 하는 dependency인가
- 이번 주 운영 회의에서 바로 결정을 막는가
- ARR/bookings 영향이 큰 고객, 가격, 갱신, partner launch와 연결되는가

그래서 알고리즘 가설도 아래처럼 서비스 판단 기준으로 적는다.

- baseline: forecast gap만 보면 된다
- hypothesis: forecast gap만으로는 부족하고, `board deadline`, `cross-team dependency`, `executive visibility`, `revenue impact`를 함께 반영해야 첫 확인 항목 선택이 더 정확해진다

즉 이 실험은
"gap이 큰 항목이 항상 1순위인가"가 아니라
**"사업기획팀의 첫 확인 항목 선택이 더 정확해지는가"**를 검증한다.

## 객관적 실험 설계

- fixture: `fixtures/service_value/biz_planning_priority_cases.tsv`
- external log sample: `fixtures/service_value/log_sample_biz_planning_priority_cases.tsv`
- public CRM silver dataset: `datasets/prepared/maven_crm_biz_planning_silver.tsv`
- public real-log silver dataset: `datasets/prepared/olist_biz_planning_silver.tsv`
- 평가 단위: case별 gold 1위 항목
- baseline 비교: forecast-gap-only
- hypothesis 비교: deadline/dependency/exec-visible/revenue-impact 반영
- metric:
  - `top1_accuracy`
  - `MRR`
  - `mean_gold_rank`

fixture는 5개 case, 20개 row로 구성한다.

- P1/P2/P3/P5: gap-only baseline이 큰 gap 항목을 먼저 올리지만, 실제 첫 확인 항목은 board deadline, cross-team dependency, exec visibility, revenue impact 때문에 달라진다.
- P4: `strategic_enterprise_slip`처럼 gap 자체도 크고 business impact도 큰 케이스다. 이 case는 baseline도 맞아야 한다. 그래야 실험이 "baseline을 무조건 틀리게 만든 toy dataset"이 되지 않는다.

현재 기대 metric은 아래와 같다.

- hypothesis: `cases=5`, `top1_accuracy=1.00`, `mrr=1.00`, `mean_gold_rank=1.00`
- baseline: `cases=5`, `top1_accuracy=0.20`, `mrr=0.53`, `mean_gold_rank=2.20`

## 재현성 계약

- 고정 TSV fixture를 쓴다
- scorer는 결정론적이다
- tie-break는 `item_id` 사전순이다
- 같은 명령을 두 번 실행했을 때 완전히 같은 출력이 나와야 한다
- 외부 로그 샘플도 같은 schema와 metric으로 평가해야 한다
- 공개 CRM dataset은 silver label임을 명시하고, 실서비스 gold label처럼 해석하지 않는다
- Olist dataset은 실제 익명화 로그지만 silver label임을 명시하고, 실서비스 gold label처럼 해석하지 않는다
- human gold label 검증은 blind review pack의 `reviewer_rank`를 적용한 별도 dataset으로 수행한다

## Human Gold Label 준비

- review pack: `datasets/review_packs/olist_biz_planning_review_pack.tsv`
- protocol: `datasets/gold_labels/README.md`
- reviewer에게는 silver `expected_rank`를 보여주지 않는다
- reviewer는 case별로 1부터 N까지 중복 없이 `reviewer_rank`를 채운다
- reviewer 2명 이상이 독립적으로 채운 경우 `adjudicate_gold_reviews.py`로 consensus/disagreement를 분리한다
- consensus case는 자동으로 rank를 채우고, disagreement case는 최종 adjudicator가 빈 `reviewer_rank`를 채우기 전까지 gold dataset으로 적용하지 않는다
- 적용 후 산출물은 `datasets/gold_labels/olist_biz_planning_gold.tsv` 같은 별도 파일로 저장한다
- 현재 실제 human gold label 파일은 아직 없다

## 실행

```bash
bash kimjungsu/code/service_value_eval.sh biz-planning
bash kimjungsu/code/service_value_eval.sh --mode baseline biz-planning
bash kimjungsu/code/service_value_eval.sh --dataset kimjungsu/fixtures/service_value/log_sample_biz_planning_priority_cases.tsv biz-planning
bash kimjungsu/code/service_value_eval.sh --dataset kimjungsu/datasets/prepared/maven_crm_biz_planning_silver.tsv biz-planning
bash kimjungsu/code/service_value_eval.sh --mode baseline --dataset kimjungsu/datasets/prepared/maven_crm_biz_planning_silver.tsv biz-planning
bash kimjungsu/code/service_value_eval.sh --dataset kimjungsu/datasets/prepared/olist_biz_planning_silver.tsv biz-planning
bash kimjungsu/code/service_value_eval.sh --mode baseline --dataset kimjungsu/datasets/prepared/olist_biz_planning_silver.tsv biz-planning
python3 kimjungsu/code/build_gold_review_pack.py --dataset kimjungsu/datasets/prepared/olist_biz_planning_silver.tsv --output kimjungsu/datasets/review_packs/olist_biz_planning_review_pack.tsv
python3 kimjungsu/code/adjudicate_gold_reviews.py --dataset kimjungsu/datasets/prepared/olist_biz_planning_silver.tsv --review fpna_a=path/to/reviewer_a_completed.tsv --review revops_b=path/to/reviewer_b_completed.tsv --output kimjungsu/datasets/gold_labels/olist_biz_planning_adjudicated_review.tsv --disagreements kimjungsu/datasets/gold_labels/olist_biz_planning_disagreements.tsv
bash kimjungsu/code/verify_service_value_eval.sh
bash kimjungsu/code/verify_dataset_preparation.sh
bash kimjungsu/code/verify_gold_review_workflow.sh
```
