# Gold Label Review Protocol

## 목적

`biz-planning` 평가는 지금까지 fixture와 silver label로 검증했다.
실서비스 정답 검증으로 넘어가려면 사업기획/FP&A/Revenue Ops 관점의 사람이 case별 첫 확인 항목을 직접 정해야 한다.

이 디렉토리는 그 reviewer label을 받을 위치다.
아직 실제 human gold label 파일은 없다.

## Workflow

1. Blind review pack을 만든다.

```bash
python3 kimjungsu/code/build_gold_review_pack.py \
  --dataset kimjungsu/datasets/prepared/olist_biz_planning_silver.tsv \
  --output kimjungsu/datasets/review_packs/olist_biz_planning_review_pack.tsv
```

2. Reviewer가 `reviewer_rank`와 `reviewer_rationale`을 채운다.

Reviewer에게 보이는 schema:

```text
case_id	item_id	title	forecast_gap_pct	board_deadline_hours	cross_team_dependency	exec_visibility	revenue_impact	reviewer_rank	reviewer_rationale
```

중요한 점:

- `expected_rank`는 review pack에 포함하지 않는다.
- reviewer는 case별로 1부터 N까지 중복 없이 rank를 채운다.
- rank 1은 "주간 운영 회의 전에 사업기획팀이 가장 먼저 확인해야 할 항목"이다.
- `reviewer_rationale`에는 why를 짧게 남긴다.

3. Review label을 평가 dataset으로 적용한다.

```bash
python3 kimjungsu/code/apply_gold_review_labels.py \
  --dataset kimjungsu/datasets/prepared/olist_biz_planning_silver.tsv \
  --review path/to/completed_review.tsv \
  --output kimjungsu/datasets/gold_labels/olist_biz_planning_gold.tsv
```

4. 같은 평가 하네스로 baseline/hypothesis를 비교한다.

```bash
bash kimjungsu/code/service_value_eval.sh \
  --dataset kimjungsu/datasets/gold_labels/olist_biz_planning_gold.tsv \
  biz-planning

bash kimjungsu/code/service_value_eval.sh \
  --mode baseline \
  --dataset kimjungsu/datasets/gold_labels/olist_biz_planning_gold.tsv \
  biz-planning
```

## Multi Reviewer Adjudication

실서비스 정답 검증으로 더 엄격하게 보려면 reviewer 2명 이상이 독립적으로 같은 review pack을 채운다.
그 다음 복수 reviewer 결과를 합쳐 consensus case와 disagreement case를 분리한다.

```bash
python3 kimjungsu/code/adjudicate_gold_reviews.py \
  --dataset kimjungsu/datasets/prepared/olist_biz_planning_silver.tsv \
  --review fpna_a=path/to/reviewer_a_completed.tsv \
  --review revops_b=path/to/reviewer_b_completed.tsv \
  --output kimjungsu/datasets/gold_labels/olist_biz_planning_adjudicated_review.tsv \
  --disagreements kimjungsu/datasets/gold_labels/olist_biz_planning_disagreements.tsv
```

동작 방식:

- reviewer별 TSV schema와 case/item set이 원본 dataset과 일치해야 한다.
- 각 reviewer의 case별 rank는 1..N으로 이어져야 한다.
- reviewer들이 같은 case에서 모든 item rank에 합의하면 `reviewer_rank`를 자동으로 채운다.
- reviewer들이 한 case라도 다르게 rank하면 해당 case 전체의 `reviewer_rank`를 비워 둔다.
- disagreement detail 파일에도 `expected_rank`는 넣지 않는다.
- 최종 adjudicator가 빈 `reviewer_rank`와 rationale을 채운 뒤 `apply_gold_review_labels.py`로 gold TSV를 만든다.

스크립트 출력에서 볼 metric:

```text
reviewers=2
cases=12
consensus_cases=...
disagreement_cases=...
top1_agreement_rate=...
full_rank_agreement_rate=...
```

## Review Gate

실서비스 정답 검증으로 인정하려면 아래 조건을 충족해야 한다.

- reviewer가 silver label 생성 로직을 보지 않은 상태에서 review해야 한다.
- case별 모든 item에 rank가 있어야 한다.
- case별 rank는 1부터 N까지 중복 없이 이어져야 한다.
- reviewer 2명 이상이 독립적으로 label을 찍고, disagreement case를 별도 adjudication한다.
- label 파일에는 reviewer 이름 대신 reviewer id와 review date만 남긴다.

## 현재 상태

- [olist_biz_planning_review_pack.tsv](../review_packs/olist_biz_planning_review_pack.tsv)는 생성되어 있다.
- 실제 human gold label은 아직 없다.
- `verify_gold_review_workflow.sh`는 기존 silver label을 임시 reviewer rank로 복사해 workflow 계약만 테스트한다. 이 결과는 human gold 검증이 아니다.
- 같은 검증 안에서 consensus adjudication, disagreement adjudication, invalid label reject도 확인한다.
