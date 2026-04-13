#!/usr/bin/env bash

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
ROOT_DIR="$(cd "$SCRIPT_DIR/.." && pwd)"
PREPARE_SCRIPT="$SCRIPT_DIR/prepare_biz_planning_crm_dataset.py"
EVAL_SCRIPT="$SCRIPT_DIR/service_value_eval.sh"
RAW_DIR="$ROOT_DIR/datasets/raw/maven_crm_sales_opportunities"
PREPARED_DATASET="$ROOT_DIR/datasets/prepared/maven_crm_biz_planning_silver.tsv"
OLIST_RAW_DIR="$ROOT_DIR/datasets/raw/olist"
OLIST_PREPARED_DATASET="$ROOT_DIR/datasets/prepared/olist_biz_planning_silver.tsv"

if ! command -v rg >/dev/null 2>&1; then
  echo "error: ripgrep (rg) is required." >&2
  exit 1
fi

assert_contains() {
  local haystack="$1"
  local needle="$2"
  local message="$3"

  if printf '%s\n' "$haystack" | rg -Fq -- "$needle"; then
    echo "PASS $message"
  else
    echo "FAIL $message" >&2
    return 1
  fi
}

assert_file() {
  local path="$1"
  local message="$2"

  if [ -f "$path" ]; then
    echo "PASS $message"
  else
    echo "FAIL $message (missing: $path)" >&2
    return 1
  fi
}

assert_equals() {
  local actual="$1"
  local expected="$2"
  local message="$3"

  if [ "$actual" = "$expected" ]; then
    echo "PASS $message"
  else
    echo "FAIL $message (expected=$expected actual=$actual)" >&2
    return 1
  fi
}

extract_metric() {
  local output="$1"
  local key="$2"
  printf '%s\n' "$output" | awk -F'=' -v key="$key" '$1 == key { print $2; exit }'
}

assert_file "$RAW_DIR/accounts.csv" "maven crm accounts raw file exists"
assert_file "$RAW_DIR/products.csv" "maven crm products raw file exists"
assert_file "$RAW_DIR/sales_pipeline.csv" "maven crm sales pipeline raw file exists"
assert_file "$RAW_DIR/sales_teams.csv" "maven crm sales teams raw file exists"
assert_file "$PREPARED_DATASET" "maven crm prepared silver dataset exists"
assert_file "$OLIST_RAW_DIR/olist_marketing_qualified_leads_dataset.csv" "olist mql raw file exists"
assert_file "$OLIST_RAW_DIR/olist_closed_deals_dataset.csv" "olist closed deals raw file exists"
assert_file "$OLIST_RAW_DIR/olist_orders_dataset.csv" "olist orders raw file exists"
assert_file "$OLIST_RAW_DIR/olist_order_items_dataset.csv" "olist order items raw file exists"
assert_file "$OLIST_RAW_DIR/olist_order_payments_dataset.csv" "olist order payments raw file exists"
assert_file "$OLIST_RAW_DIR/olist_order_reviews_dataset.csv" "olist order reviews raw file exists"
assert_file "$OLIST_RAW_DIR/olist_sellers_dataset.csv" "olist sellers raw file exists"
assert_file "$OLIST_PREPARED_DATASET" "olist prepared silver dataset exists"

tmp_output="$(mktemp /tmp/maven_crm_biz_planning.XXXXXX.tsv)"
tmp_olist_output="$(mktemp /tmp/olist_biz_planning.XXXXXX.tsv)"
trap 'rm -f "$tmp_output" "$tmp_olist_output"' EXIT

python3 "$PREPARE_SCRIPT" --crm-dir "$RAW_DIR" --output "$tmp_output" >/dev/null
python3 "$SCRIPT_DIR/prepare_biz_planning_olist_dataset.py" --olist-dir "$OLIST_RAW_DIR" --output "$tmp_olist_output" >/dev/null

if cmp -s "$tmp_output" "$PREPARED_DATASET"; then
  echo "PASS maven crm conversion is reproducible"
else
  echo "FAIL maven crm conversion drifted from prepared dataset" >&2
  exit 1
fi

if cmp -s "$tmp_olist_output" "$OLIST_PREPARED_DATASET"; then
  echo "PASS olist conversion is reproducible"
else
  echo "FAIL olist conversion drifted from prepared dataset" >&2
  exit 1
fi

hypothesis="$("$EVAL_SCRIPT" --dataset "$PREPARED_DATASET" biz-planning)"
baseline="$("$EVAL_SCRIPT" --mode baseline --dataset "$PREPARED_DATASET" biz-planning)"
olist_hypothesis="$("$EVAL_SCRIPT" --dataset "$OLIST_PREPARED_DATASET" biz-planning)"
olist_baseline="$("$EVAL_SCRIPT" --mode baseline --dataset "$OLIST_PREPARED_DATASET" biz-planning)"

assert_contains "$hypothesis" "dataset_source=override" "maven crm dataset source is override"
assert_contains "$hypothesis" "dataset_schema_matches_usecase" "maven crm dataset schema contract is reported"
assert_equals "$(extract_metric "$hypothesis" "cases")" "8" "maven crm hypothesis case count"
assert_equals "$(extract_metric "$hypothesis" "top1_accuracy")" "0.50" "maven crm hypothesis top1 accuracy"
assert_equals "$(extract_metric "$hypothesis" "mrr")" "0.69" "maven crm hypothesis mrr"
assert_equals "$(extract_metric "$hypothesis" "mean_gold_rank")" "1.88" "maven crm hypothesis mean gold rank"
assert_equals "$(extract_metric "$baseline" "cases")" "8" "maven crm baseline case count"
assert_equals "$(extract_metric "$baseline" "top1_accuracy")" "0.25" "maven crm baseline top1 accuracy"
assert_equals "$(extract_metric "$baseline" "mrr")" "0.53" "maven crm baseline mrr"
assert_equals "$(extract_metric "$baseline" "mean_gold_rank")" "2.38" "maven crm baseline mean gold rank"
assert_contains "$olist_hypothesis" "dataset_source=override" "olist dataset source is override"
assert_contains "$olist_hypothesis" "dataset_schema_matches_usecase" "olist dataset schema contract is reported"
assert_equals "$(extract_metric "$olist_hypothesis" "cases")" "12" "olist hypothesis case count"
assert_equals "$(extract_metric "$olist_hypothesis" "top1_accuracy")" "0.83" "olist hypothesis top1 accuracy"
assert_equals "$(extract_metric "$olist_hypothesis" "mrr")" "0.90" "olist hypothesis mrr"
assert_equals "$(extract_metric "$olist_hypothesis" "mean_gold_rank")" "1.25" "olist hypothesis mean gold rank"
assert_equals "$(extract_metric "$olist_baseline" "cases")" "12" "olist baseline case count"
assert_equals "$(extract_metric "$olist_baseline" "top1_accuracy")" "0.33" "olist baseline top1 accuracy"
assert_equals "$(extract_metric "$olist_baseline" "mrr")" "0.54" "olist baseline mrr"
assert_equals "$(extract_metric "$olist_baseline" "mean_gold_rank")" "2.58" "olist baseline mean gold rank"

echo "PASS overall: public dataset preparation is reproducible and evaluable"
