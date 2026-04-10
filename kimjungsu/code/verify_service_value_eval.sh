#!/usr/bin/env bash

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
EVAL_SCRIPT="$SCRIPT_DIR/service_value_eval.sh"

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

  if printf '%s\n' "$haystack" | rg -Fq "$needle"; then
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

check_reproducibility briefing
check_reproducibility ops-handoff
check_briefing
check_ops_handoff

echo "PASS overall: service value algorithm evaluation is objective, baseline-comparable, and reproducible"
