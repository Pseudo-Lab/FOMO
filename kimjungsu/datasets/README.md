# Biz Planning Dataset Research

## 목표

`biz-planning` 유즈케이스를 고정 fixture에서 더 큰 공개 데이터셋 기반 검증으로 확장한다.
현재 하네스가 요구하는 입력은 아래 TSV schema다.

```text
case_id	item_id	title	forecast_gap_pct	board_deadline_hours	cross_team_dependency	exec_visibility	revenue_impact	expected_rank
```

## 1차 선택: Maven CRM Sales Opportunities

- source page: https://mavenanalytics.io/data-playground/crm-sales-opportunities
- direct download: https://maven-datasets.s3.amazonaws.com/CRM+Sales+Opportunities/CRM+Sales+Opportunities.zip
- source noted by Maven: data.world
- license noted by Maven: Public Domain
- local raw path: `kimjungsu/datasets/raw/maven_crm_sales_opportunities/`
- local prepared path: `kimjungsu/datasets/prepared/maven_crm_biz_planning_silver.tsv`

선정 이유:

- B2B sales pipeline 데이터라 사업기획팀/FP&A/Revenue Ops 유즈케이스에 가장 가깝다.
- `sales_pipeline.csv`에 opportunity, product, account, stage, close date, close value가 있다.
- `accounts.csv`, `products.csv`, `sales_teams.csv`가 있어 account size, product price, regional office를 함께 쓸 수 있다.
- Public Domain으로 명시되어 있어 실험 fixture로 보관하기 쉽다.
- 원본 ZIP은 작고 CSV 기반이라 네트워크가 없어도 재현할 수 있다.

다운로드한 원본 구조:

```text
accounts.csv
data_dictionary.csv
products.csv
sales_pipeline.csv
sales_teams.csv
```

원본 audit:

- `sales_pipeline.csv` rows: 8,800
- closed rows with `close_date` and `close_value`: 6,711
- open rows skipped for this silver-label conversion: 2,089
- `sales_pipeline.csv` sha256: `825ce8f6c32d4009548b468df3173d55a46fd73f2531f532c5459371dc52adf2`

## 변환 방식

변환 스크립트:

```bash
python3 kimjungsu/code/prepare_biz_planning_crm_dataset.py \
  --crm-dir kimjungsu/datasets/raw/maven_crm_sales_opportunities \
  --output kimjungsu/datasets/prepared/maven_crm_biz_planning_silver.tsv
```

변환 결과:

- output rows: 32
- cases: 8
- case grain: quarter + regional office
- items per case: 4
- output sha256: `ea678d5a5098ad26ffc08c359fbbb7850bb2e92bcf784d1bba4eee830ec392ce`

필드 매핑:

| harness field | public CRM proxy |
|:---|:---|
| `case_id` | `close_date` quarter + `regional_office` |
| `item_id` | `opportunity_id` |
| `title` | account + product + deal stage + regional office |
| `forecast_gap_pct` | `close_value`와 product `sales_price` 차이를 1~10 bucket으로 변환 |
| `board_deadline_hours` | quarter 시작일에서 close date까지의 시간, 12~720 hours cap |
| `cross_team_dependency` | deal stage, account employee size, product complexity proxy |
| `exec_visibility` | high close value, high account revenue, or enterprise product proxy |
| `revenue_impact` | `close_value` 1~5 bucket |
| `expected_rank` | outcome/stage, revenue impact, deadline, dependency, exec visibility를 섞은 deterministic silver score 순위 |

중요한 한계:

- 이 데이터셋에는 실제 board deadline, cross-team dependency, exec visibility, 사람이 찍은 gold rank가 없다.
- 따라서 `expected_rank`는 실서비스 정답이 아니라 공개 CRM 데이터에서 만든 deterministic silver label이다.
- 이 데이터셋의 역할은 "실제 회사 로그 검증 완료"가 아니라 "fixture보다 큰 pipeline-shaped 공개 데이터로 하네스를 흔들어보기"다.

## 현재 평가 결과

```bash
bash kimjungsu/code/service_value_eval.sh \
  --dataset kimjungsu/datasets/prepared/maven_crm_biz_planning_silver.tsv \
  biz-planning

bash kimjungsu/code/service_value_eval.sh \
  --mode baseline \
  --dataset kimjungsu/datasets/prepared/maven_crm_biz_planning_silver.tsv \
  biz-planning
```

현재 metric:

| mode | cases | top1_accuracy | mrr | mean_gold_rank |
|:---|---:|---:|---:|---:|
| hypothesis | 8 | 0.50 | 0.69 | 1.88 |
| baseline | 8 | 0.25 | 0.53 | 2.38 |

해석:

- 기존 fixture처럼 `1.00`이 나오지 않는다.
- 그래도 forecast-gap-only baseline보다 hypothesis가 더 낫다.
- 따라서 다음 단계에서 실제 익명화 로그가 들어오기 전, 공개 CRM 데이터로 하네스의 ranking/metric 흐름을 점검하는 중간 실험으로 쓸 수 있다.

## 2차 선택: Olist 실제 공개 로그

- marketing funnel source page: https://www.kaggle.com/datasets/olistbr/marketing-funnel-olist
- e-commerce source page: https://www.kaggle.com/datasets/olistbr/brazilian-ecommerce
- local raw path: `kimjungsu/datasets/raw/olist/`
- local prepared path: `kimjungsu/datasets/prepared/olist_biz_planning_silver.tsv`
- actualness: real data, anonymized and sampled
- license note: Kaggle dataset pages list non-commercial Creative Commons terms; use as research/demo data, not commercial benchmark

다운로드한 원본 구조:

```text
olist_closed_deals_dataset.csv
olist_marketing_qualified_leads_dataset.csv
olist_order_items_dataset.csv
olist_order_payments_dataset.csv
olist_order_reviews_dataset.csv
olist_orders_dataset.csv
olist_products_dataset.csv
olist_sellers_dataset.csv
```

원본 audit:

- MQL rows: 8,000
- closed deal rows: 842
- order rows: 99,441
- order item rows: 112,650
- order payment rows: 103,886
- order review rows: 104,719
- seller rows: 3,095
- closed-deal sellers with order history: 380
- seller-month rows after join: 1,030

변환 방식:

```bash
python3 kimjungsu/code/prepare_biz_planning_olist_dataset.py \
  --olist-dir kimjungsu/datasets/raw/olist \
  --output kimjungsu/datasets/prepared/olist_biz_planning_silver.tsv
```

변환 결과:

- output rows: 48
- cases: 12
- case grain: month + business segment
- items per case: 4
- output sha256: `caa042bd797c2a90a3c37f587e766ca6daeb0e667fd478d0288c2121845ee38b`

필드 매핑:

| harness field | Olist real-log proxy |
|:---|:---|
| `case_id` | seller order month + closed deal `business_segment` |
| `item_id` | seller_id + month |
| `title` | business segment + seller prefix + month + revenue + lead origin + seller state |
| `forecast_gap_pct` | seller-month revenue vs declared monthly revenue or segment-month median, distribution-bucketed |
| `board_deadline_hours` | time from first seller order in month to month-end planning deadline |
| `cross_team_dependency` | review risk, late delivery, catalog size, installments, product variety proxy |
| `exec_visibility` | high revenue/order impact or manufacturer business type proxy |
| `revenue_impact` | seller-month revenue bucket |
| `expected_rank` | deterministic silver score from revenue, gap, dependency, exec visibility, delivery/review risk, deadline |

현재 metric:

| mode | cases | top1_accuracy | mrr | mean_gold_rank |
|:---|---:|---:|---:|---:|
| hypothesis | 12 | 0.83 | 0.90 | 1.25 |
| baseline | 12 | 0.33 | 0.54 | 2.58 |

해석:

- Maven CRM과 달리 Olist는 실제 익명화 로그다.
- 다만 공개 데이터에는 사업기획팀이 직접 찍은 우선순위 gold label이 없으므로 여전히 silver label이다.
- 현재 결과는 실제 로그 proxy에서도 forecast-gap-only보다 service-feature hypothesis가 더 낫다는 하네스 검증이다.
- `forecast_gap_pct`가 높은 값에 많이 몰려 있어, 다음 개선에서는 segment별 declared revenue quality와 gap bucket을 더 정교하게 조정해야 한다.

## 후보 데이터셋 리뷰

| 후보 | 장점 | 한계 | 판단 |
|:---|:---|:---|:---|
| Maven CRM Sales Opportunities | B2B pipeline, accounts/products/teams/opportunities, Public Domain | 실제 회사 로그는 아니고 gold rank 없음 | 1차 채택 |
| Olist Brazilian E-Commerce / Marketing Funnel | 실제 익명화 상거래/마케팅 funnel 성격, 주문/리뷰/결제/배송 분석 가능 | board-facing planning, dependency, gold rank 없음 | 매출/마케팅 보조 검증 후보 |
| M5 Forecasting Accuracy | Walmart 계층형 time-series sales forecast benchmark | CRM/account/team/회의 의사결정 맥락 없음 | forecast model 평가 후보 |
| UCI Online Retail II | 실제 온라인 리테일 거래, 수요/매출 시계열 구성 가능 | sales pipeline과 운영 priority label 없음 | forecast-gap 보조 후보 |

## 공개 실제 로그 추가 리서치

질문: "공개용으로 된 실제 로그가 있는가?"

결론:

- 완전한 B2B CRM opportunity + 회의 우선순위 + 사람이 찍은 gold rank를 모두 가진 공개 로그는 찾기 어렵다.
- 대신 실제 익명화 로그는 marketing funnel, e-commerce transactions, ITSM incident event log, helpdesk tickets, clickstream 영역에 존재한다.
- `biz-planning`에 가장 가까운 실제 공개 로그는 Olist Marketing Funnel + Brazilian E-Commerce 조합이다.
- `ops-handoff`에 가장 가까운 실제 공개 로그는 UCI Incident Management / BPI Challenge 2013 / Mendeley Help Desk Tickets다.

### 실제 로그 후보

| 우선순위 | dataset | 실제성 | 쓸 수 있는 신호 | 현재 유즈케이스 적합도 | 라이선스/주의 |
|:---:|:---|:---|:---|:---|:---|
| 1 | Olist Marketing Funnel | 실제 데이터, 익명화, 샘플링 | 8k MQL, seller lead, lead category, catalog size, behaviour profile, closed deal 연결 | `biz-planning`에서 marketing/sales funnel priority 검증에 가장 가까움 | CC BY-NC-SA 4.0, 상업 사용 주의 |
| 2 | Olist Brazilian E-Commerce | 실제 상거래 주문 로그, 익명화 | 100k orders, order status, price, payment, freight, reviews, seller/customer/product | revenue impact, seller segment, fulfillment risk로 확장 가능 | CC BY-NC-SA 4.0 |
| 3 | UCI Incident Management enriched event log | 실제 ServiceNow incident event log, 익명화 | 141,712 events, 24,918 incidents, SLA, reassignment, impact, urgency, priority, resolved/closed time | `ops-handoff` 실제 로그 검증에 매우 적합 | CC BY 4.0 |
| 4 | BPI Challenge 2013 Incidents | Volvo IT incident management real-life event log | 7,554 cases, 65,533 events, XES event log | process/incident handoff 검증에 적합 | 4TU General Terms of Use |
| 5 | Mendeley Help Desk Tickets | 국제 소프트웨어 회사 helpdesk DB에서 추출/익명화 | issues, change history, snapshots, sample utterances, manager-scored issue snapshot | support priority/gold label 실험에 강함 | CC BY 4.0 |
| 6 | RetailRocket e-commerce events | real-world ecommerce website raw event logs | 2,756,101 events, views/addtocart/transactions, item properties | product/revenue signal에는 좋지만 사업기획 회의 맥락은 약함 | Kaggle license 확인 필요 |
| 7 | Instacart Market Basket | 실제 주문 기반 익명화 데이터 | 3M+ grocery orders, 200k+ users, reorder behavior | demand/reorder forecast에는 좋지만 B2B planning과는 거리 있음 | CC0 mirror도 있으나 원출처 조건 확인 필요 |
| 8 | UCI Online Retail II | 실제 UK online retail transactions | 1,067,371 transactions, invoice, item, quantity, price, customer, country | revenue/forecast 보조 검증 가능 | CC BY 4.0 |
| 제외 | Kaggle synthetic support tickets류 | synthetic으로 명시됨 | priority/SLA/sentiment 등 필드는 좋음 | 현실성 보강 목적에는 부적합 | 실제 로그 아님 |
| 제외 | Maven CRM Sales Opportunities | B2B sales pipeline 형태는 좋음 | opportunities/accounts/products/teams | 현재 하네스 smoke에는 유용 | fictitious company 데이터라 실제 로그 아님 |

주요 출처:

- Olist Marketing Funnel: https://www.kaggle.com/datasets/olistbr/marketing-funnel-olist
- Olist Brazilian E-Commerce: https://www.kaggle.com/datasets/olistbr/brazilian-ecommerce
- UCI Incident Management Process enriched event log: https://archive.ics.uci.edu/dataset/498/incident%2Bmanagement%2Bprocess%2Benriched%2Bevent%2Blog
- BPI Challenge 2013 Incidents: https://data.4tu.nl/articles/dataset/BPI_Challenge_2013_incidents/12693914
- Mendeley Help Desk Tickets: https://data.mendeley.com/datasets/btm76zndnt/1
- Mendeley Helpdesk process log: https://data.mendeley.com/datasets/39bp3vv62t/1
- RetailRocket recommender system dataset: https://www.kaggle.com/datasets/retailrocket/ecommerce-dataset
- Instacart Market Basket Analysis: https://www.kaggle.com/c/instacart-market-basket-analysis/data
- UCI Online Retail II: https://archive.ics.uci.edu/dataset/502/online%2Bretail%2Bii

### 추천 다음 단계

1. `biz-planning` 실제 로그 확장:
   - Olist Marketing Funnel과 Brazilian E-Commerce를 같이 내려받는다.
   - `seller_id`로 funnel과 주문 로그를 join한다.
   - case grain을 `month + lead_origin/business_segment` 또는 `month + seller_segment`로 둔다.
   - `forecast_gap_pct`는 seller/month revenue variance proxy로 만든다.
   - `board_deadline_hours`는 월말/분기말까지 남은 시간 proxy로 만든다.
   - `cross_team_dependency`는 payment/logistics/review/fulfillment signal 조합으로 만든다.
   - `revenue_impact`는 seller/order value bucket으로 만든다.
   - gold는 실제 사람이 찍은 것이 아니므로 먼저 silver label로만 둔다.

2. `ops-handoff` 실제 로그 확장:
   - UCI Incident Management enriched event log를 우선 사용한다.
   - case grain은 incident number, item은 incident state update 또는 incident summary row로 잡는다.
   - severity baseline은 priority/impact만 보는 기준으로 잡는다.
   - hypothesis는 SLA, reassignment_count, reopen_count, urgency, vendor/problem/rfc association을 같이 본다.

3. 실제 gold label이 필요할 때:
   - 공개 데이터만으로는 부족하다.
   - 내부 익명화 로그 또는 domain reviewer가 case별 1순위 gold item을 찍는 review protocol이 필요하다.

## Human Gold Label Workflow

Olist는 실제 익명화 로그지만 `expected_rank`는 silver label이다.
실서비스 정답 검증으로 인정하려면 사람이 직접 rank를 찍은 label 파일이 필요하다.

현재 준비된 workflow:

```bash
python3 kimjungsu/code/build_gold_review_pack.py \
  --dataset kimjungsu/datasets/prepared/olist_biz_planning_silver.tsv \
  --output kimjungsu/datasets/review_packs/olist_biz_planning_review_pack.tsv

python3 kimjungsu/code/apply_gold_review_labels.py \
  --dataset kimjungsu/datasets/prepared/olist_biz_planning_silver.tsv \
  --review path/to/completed_review.tsv \
  --output kimjungsu/datasets/gold_labels/olist_biz_planning_gold.tsv

python3 kimjungsu/code/adjudicate_gold_reviews.py \
  --dataset kimjungsu/datasets/prepared/olist_biz_planning_silver.tsv \
  --review fpna_a=path/to/reviewer_a_completed.tsv \
  --review revops_b=path/to/reviewer_b_completed.tsv \
  --output kimjungsu/datasets/gold_labels/olist_biz_planning_adjudicated_review.tsv \
  --disagreements kimjungsu/datasets/gold_labels/olist_biz_planning_disagreements.tsv

./kimjungsu/code/verify_gold_review_workflow.sh
```

Review pack:

- path: `kimjungsu/datasets/review_packs/olist_biz_planning_review_pack.tsv`
- rows: 48
- cases: 12
- `expected_rank` column: hidden
- reviewer input columns: `reviewer_rank`, `reviewer_rationale`

검증 내용:

- review pack 재생성이 committed pack과 일치해야 한다.
- review pack header에 `expected_rank`가 없어야 한다.
- reviewer rank를 적용하면 `service_value_eval.sh --dataset`으로 평가 가능해야 한다.
- case별 rank가 비어 있거나 1..N 연속 순위가 아니면 거부해야 한다.
- 2명 이상 reviewer가 완전 합의한 case는 adjudication review에 자동 rank가 채워져야 한다.
- reviewer rank가 갈린 case는 final adjudicator가 채우기 전까지 `apply_gold_review_labels.py`가 거부해야 한다.
- disagreement detail 파일에도 `expected_rank`가 노출되지 않아야 한다.

현재 상태:

- 실제 human gold label은 아직 없다.
- `verify_gold_review_workflow.sh`는 기존 silver label을 임시 reviewer rank로 복사해 workflow 계약만 테스트한다.
- consensus/disagreement adjudication도 workflow 계약으로 검증한다.
- 실제 gold 검증을 시작하려면 reviewer가 `olist_biz_planning_review_pack.tsv`를 채운 뒤 `datasets/gold_labels/` 아래에 별도 파일로 저장해야 한다.
