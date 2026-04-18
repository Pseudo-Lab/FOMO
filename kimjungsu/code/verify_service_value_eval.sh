#!/usr/bin/env bash

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
EVAL_SCRIPT="$SCRIPT_DIR/service_value_eval.sh"
ROOT_DIR="$(cd "$SCRIPT_DIR/.." && pwd)"
BRIEFING_LOG_SAMPLE="$ROOT_DIR/fixtures/service_value/log_sample_briefing_priority_cases.tsv"
BIZ_PLANNING_LOG_SAMPLE="$ROOT_DIR/fixtures/service_value/log_sample_biz_planning_priority_cases.tsv"

if ! command -v rg >/dev/null 2>&1; then
  echo "error: ripgrep (rg) is required." >&2
  exit 1
fi

if [ ! -x "$EVAL_SCRIPT" ]; then
  echo "error: eval script is not executable: $EVAL_SCRIPT" >&2
  exit 1
fi

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

extract_metric() {
  local output="$1"
  local key="$2"
  printf '%s\n' "$output" | awk -F'=' -v key="$key" '$1 == key { print $2; exit }'
}

check_reproducibility() {
  local usecase="$1"
  local run_a run_b

  run_a="$("$EVAL_SCRIPT" "$usecase")"
  run_b="$("$EVAL_SCRIPT" "$usecase")"

  assert_equals "$run_a" "$run_b" "$usecase reproducibility"
}

check_briefing() {
  local hypothesis baseline

  hypothesis="$("$EVAL_SCRIPT" briefing)"
  baseline="$("$EVAL_SCRIPT" --mode baseline briefing)"

  assert_contains "$hypothesis" "[stage 0] hypothesis lens" "briefing includes stage 0"
  assert_contains "$hypothesis" "[stage 3] objective quality" "briefing includes stage 3"
  assert_contains "$hypothesis" "B2|gold_item=board_demo_prep|pred_rank=1|score=171" "briefing hypothesis fixes due-prep case"
  assert_equals "$(extract_metric "$hypothesis" "top1_accuracy")" "1.00" "briefing hypothesis top1 accuracy"
  assert_equals "$(extract_metric "$hypothesis" "mrr")" "1.00" "briefing hypothesis mrr"
  assert_equals "$(extract_metric "$hypothesis" "mean_gold_rank")" "1.00" "briefing hypothesis mean gold rank"
  assert_equals "$(extract_metric "$baseline" "top1_accuracy")" "0.33" "briefing baseline top1 accuracy"
  assert_equals "$(extract_metric "$baseline" "mrr")" "0.61" "briefing baseline mrr"
  assert_equals "$(extract_metric "$baseline" "mean_gold_rank")" "2.00" "briefing baseline mean gold rank"
}

check_ops_handoff() {
  local hypothesis baseline

  hypothesis="$("$EVAL_SCRIPT" ops-handoff)"
  baseline="$("$EVAL_SCRIPT" --mode baseline ops-handoff)"

  assert_contains "$hypothesis" "[stage 0] hypothesis lens" "ops handoff includes stage 0"
  assert_contains "$hypothesis" "[stage 3] objective quality" "ops handoff includes stage 3"
  assert_contains "$hypothesis" "O1|gold_item=vip_outage|pred_rank=1|score=240" "ops handoff hypothesis fixes vip outage case"
  assert_equals "$(extract_metric "$hypothesis" "top1_accuracy")" "1.00" "ops handoff hypothesis top1 accuracy"
  assert_equals "$(extract_metric "$hypothesis" "mrr")" "1.00" "ops handoff hypothesis mrr"
  assert_equals "$(extract_metric "$hypothesis" "mean_gold_rank")" "1.00" "ops handoff hypothesis mean gold rank"
  assert_equals "$(extract_metric "$baseline" "top1_accuracy")" "0.00" "ops handoff baseline top1 accuracy"
  assert_equals "$(extract_metric "$baseline" "mrr")" "0.50" "ops handoff baseline mrr"
  assert_equals "$(extract_metric "$baseline" "mean_gold_rank")" "2.00" "ops handoff baseline mean gold rank"
}

check_biz_planning() {
  local hypothesis baseline

  hypothesis="$("$EVAL_SCRIPT" biz-planning)"
  baseline="$("$EVAL_SCRIPT" --mode baseline biz-planning)"

  assert_contains "$hypothesis" "[stage 0] hypothesis lens" "biz planning includes stage 0"
  assert_contains "$hypothesis" "[stage 3] objective quality" "biz planning includes stage 3"
  assert_contains "$hypothesis" "P2|gold_item=pricing_guardrail_decision|pred_rank=1|score=275" "biz planning hypothesis fixes pricing guardrail case"
  assert_equals "$(extract_metric "$hypothesis" "cases")" "5" "biz planning hypothesis case count"
  assert_equals "$(extract_metric "$hypothesis" "top1_accuracy")" "1.00" "biz planning hypothesis top1 accuracy"
  assert_equals "$(extract_metric "$hypothesis" "mrr")" "1.00" "biz planning hypothesis mrr"
  assert_equals "$(extract_metric "$hypothesis" "mean_gold_rank")" "1.00" "biz planning hypothesis mean gold rank"
  assert_equals "$(extract_metric "$baseline" "top1_accuracy")" "0.20" "biz planning baseline top1 accuracy"
  assert_equals "$(extract_metric "$baseline" "mrr")" "0.53" "biz planning baseline mrr"
  assert_equals "$(extract_metric "$baseline" "mean_gold_rank")" "2.20" "biz planning baseline mean gold rank"
}

check_external_dataset() {
  local output biz_output

  output="$("$EVAL_SCRIPT" --dataset "$BRIEFING_LOG_SAMPLE" briefing)"

  assert_contains "$output" "dataset_source=override" "external dataset source is reported"
  assert_contains "$output" "dataset_schema_matches_usecase" "external dataset schema contract is reported"
  assert_contains "$output" "L1|gold_item=customer_escalation_prep|pred_rank=1|score=217" "external dataset ranks gold item first"
  assert_equals "$(extract_metric "$output" "cases")" "1" "external dataset case count"
  assert_equals "$(extract_metric "$output" "top1_accuracy")" "1.00" "external dataset top1 accuracy"
  assert_equals "$(extract_metric "$output" "mrr")" "1.00" "external dataset mrr"

  biz_output="$("$EVAL_SCRIPT" --dataset "$BIZ_PLANNING_LOG_SAMPLE" biz-planning)"

  assert_contains "$biz_output" "dataset_source=override" "biz planning external dataset source is reported"
  assert_contains "$biz_output" "dataset_schema_matches_usecase" "biz planning external dataset schema contract is reported"
  assert_contains "$biz_output" "BL2|gold_item=strategic_renewal_pullin|pred_rank=1|score=285" "biz planning external dataset ranks gold item first"
  assert_equals "$(extract_metric "$biz_output" "cases")" "2" "biz planning external dataset case count"
  assert_equals "$(extract_metric "$biz_output" "top1_accuracy")" "1.00" "biz planning external dataset top1 accuracy"
  assert_equals "$(extract_metric "$biz_output" "mrr")" "1.00" "biz planning external dataset mrr"
}

check_reproducibility briefing
check_reproducibility ops-handoff
check_reproducibility biz-planning
check_briefing
check_ops_handoff
check_biz_planning
check_external_dataset

echo "PASS overall: service value algorithm evaluation is objective, baseline-comparable, and reproducible"
