#!/usr/bin/env bash

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
ROOT_DIR="$(cd "$SCRIPT_DIR/.." && pwd)"
BUILD_REVIEW="$SCRIPT_DIR/build_gold_review_pack.py"
APPLY_LABELS="$SCRIPT_DIR/apply_gold_review_labels.py"
ADJUDICATE_REVIEWS="$SCRIPT_DIR/adjudicate_gold_reviews.py"
EVAL_SCRIPT="$SCRIPT_DIR/service_value_eval.sh"
SOURCE_DATASET="$ROOT_DIR/datasets/prepared/olist_biz_planning_silver.tsv"
REVIEW_PACK="$ROOT_DIR/datasets/review_packs/olist_biz_planning_review_pack.tsv"

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

tmp_review="$(mktemp /tmp/olist_review_pack.XXXXXX.tsv)"
tmp_completed="$(mktemp /tmp/olist_completed_review.XXXXXX.tsv)"
tmp_completed_b="$(mktemp /tmp/olist_completed_review_b.XXXXXX.tsv)"
tmp_conflict="$(mktemp /tmp/olist_conflict_review.XXXXXX.tsv)"
tmp_adjudicated="$(mktemp /tmp/olist_adjudicated_review.XXXXXX.tsv)"
tmp_disagreements="$(mktemp /tmp/olist_disagreements.XXXXXX.tsv)"
tmp_gold="$(mktemp /tmp/olist_gold_dataset.XXXXXX.tsv)"
tmp_bad_review="$(mktemp /tmp/olist_bad_review.XXXXXX.tsv)"
trap 'rm -f "$tmp_review" "$tmp_completed" "$tmp_completed_b" "$tmp_conflict" "$tmp_adjudicated" "$tmp_disagreements" "$tmp_gold" "$tmp_bad_review"' EXIT

python3 "$BUILD_REVIEW" --dataset "$SOURCE_DATASET" --output "$tmp_review" >/dev/null

if cmp -s "$tmp_review" "$REVIEW_PACK"; then
  echo "PASS olist review pack is reproducible"
else
  echo "FAIL olist review pack drifted from committed pack" >&2
  exit 1
fi

review_header="$(head -n 1 "$tmp_review")"
assert_contains "$review_header" "reviewer_rank" "review pack has reviewer rank column"
if printf '%s\n' "$review_header" | rg -Fq -- "expected_rank"; then
  echo "FAIL review pack leaks expected_rank in header" >&2
  exit 1
else
  echo "PASS review pack hides expected rank"
fi

python3 - "$SOURCE_DATASET" "$tmp_review" "$tmp_completed" <<'PY'
import csv
import sys

source_path, review_path, output_path = sys.argv[1:]
with open(source_path, newline="", encoding="utf-8-sig") as handle:
    source_rows = list(csv.DictReader(handle, delimiter="\t"))
rank_by_key = {(row["case_id"], row["item_id"]): row["expected_rank"] for row in source_rows}

with open(review_path, newline="", encoding="utf-8-sig") as handle:
    reader = csv.DictReader(handle, delimiter="\t")
    fieldnames = reader.fieldnames
    rows = list(reader)

with open(output_path, "w", newline="", encoding="utf-8") as handle:
    writer = csv.DictWriter(handle, fieldnames=fieldnames, delimiter="\t", lineterminator="\n")
    writer.writeheader()
    for row in rows:
        row["reviewer_rank"] = rank_by_key[(row["case_id"], row["item_id"])]
        row["reviewer_rationale"] = "contract test copied from existing silver label"
        writer.writerow(row)
PY

python3 "$APPLY_LABELS" --dataset "$SOURCE_DATASET" --review "$tmp_completed" --output "$tmp_gold" >/dev/null

if cmp -s "$tmp_gold" "$SOURCE_DATASET"; then
  echo "PASS applying completed review recreates eval dataset"
else
  echo "FAIL completed review did not recreate eval dataset" >&2
  exit 1
fi

gold_output="$("$EVAL_SCRIPT" --dataset "$tmp_gold" biz-planning)"
assert_equals "$(extract_metric "$gold_output" "cases")" "12" "gold workflow eval case count"
assert_equals "$(extract_metric "$gold_output" "top1_accuracy")" "0.83" "gold workflow eval top1 accuracy"
assert_equals "$(extract_metric "$gold_output" "mrr")" "0.90" "gold workflow eval mrr"

cp "$tmp_completed" "$tmp_completed_b"
adjudication_output="$(
  python3 "$ADJUDICATE_REVIEWS" \
    --dataset "$SOURCE_DATASET" \
    --review fpna_a="$tmp_completed" \
    --review revops_b="$tmp_completed_b" \
    --output "$tmp_adjudicated" \
    --disagreements "$tmp_disagreements"
)"
assert_equals "$(extract_metric "$adjudication_output" "reviewers")" "2" "adjudication reviewer count"
assert_equals "$(extract_metric "$adjudication_output" "consensus_cases")" "12" "adjudication consensus case count"
assert_equals "$(extract_metric "$adjudication_output" "disagreement_cases")" "0" "adjudication no-disagreement case count"
assert_equals "$(extract_metric "$adjudication_output" "full_rank_agreement_rate")" "1.00" "adjudication full rank agreement"
python3 "$APPLY_LABELS" --dataset "$SOURCE_DATASET" --review "$tmp_adjudicated" --output "$tmp_gold" >/dev/null

if cmp -s "$tmp_gold" "$SOURCE_DATASET"; then
  echo "PASS consensus adjudication recreates eval dataset"
else
  echo "FAIL consensus adjudication did not recreate eval dataset" >&2
  exit 1
fi

python3 - "$tmp_completed" "$tmp_conflict" <<'PY'
import csv
import sys

source_path, output_path = sys.argv[1:]
with open(source_path, newline="", encoding="utf-8-sig") as handle:
    reader = csv.DictReader(handle, delimiter="\t")
    fieldnames = reader.fieldnames
    rows = list(reader)

case_id = rows[0]["case_id"]
case_rows = [row for row in rows if row["case_id"] == case_id]
rank_one = next(row for row in case_rows if row["reviewer_rank"] == "1")
rank_two = next(row for row in case_rows if row["reviewer_rank"] == "2")
rank_one["reviewer_rank"], rank_two["reviewer_rank"] = (
    rank_two["reviewer_rank"],
    rank_one["reviewer_rank"],
)
rank_one["reviewer_rationale"] = "contract test top1 disagreement"
rank_two["reviewer_rationale"] = "contract test top1 disagreement"

with open(output_path, "w", newline="", encoding="utf-8") as handle:
    writer = csv.DictWriter(handle, fieldnames=fieldnames, delimiter="\t", lineterminator="\n")
    writer.writeheader()
    writer.writerows(rows)
PY

adjudication_output="$(
  python3 "$ADJUDICATE_REVIEWS" \
    --dataset "$SOURCE_DATASET" \
    --review fpna_a="$tmp_completed" \
    --review revops_b="$tmp_conflict" \
    --output "$tmp_adjudicated" \
    --disagreements "$tmp_disagreements"
)"
assert_equals "$(extract_metric "$adjudication_output" "consensus_cases")" "11" "adjudication partial consensus count"
assert_equals "$(extract_metric "$adjudication_output" "disagreement_cases")" "1" "adjudication disagreement case count"
assert_equals "$(extract_metric "$adjudication_output" "needs_adjudication_rows")" "4" "adjudication rows needing final review"
assert_equals "$(extract_metric "$adjudication_output" "top1_agreement_rate")" "0.92" "adjudication top1 agreement rate"
assert_equals "$(extract_metric "$adjudication_output" "full_rank_agreement_rate")" "0.92" "adjudication full agreement rate"

disagreement_header="$(head -n 1 "$tmp_disagreements")"
if printf '%s\n' "$disagreement_header" | rg -Fq -- "expected_rank"; then
  echo "FAIL disagreement pack leaks expected_rank in header" >&2
  exit 1
else
  echo "PASS disagreement pack hides expected rank"
fi

if python3 "$APPLY_LABELS" --dataset "$SOURCE_DATASET" --review "$tmp_adjudicated" --output "$tmp_gold" >/dev/null 2>&1; then
  echo "FAIL disagreement adjudication template was accepted before final ranks" >&2
  exit 1
else
  echo "PASS disagreement adjudication template requires final ranks"
fi

python3 - "$tmp_completed" "$tmp_bad_review" <<'PY'
import csv
import sys

source_path, output_path = sys.argv[1:]
with open(source_path, newline="", encoding="utf-8-sig") as handle:
    reader = csv.DictReader(handle, delimiter="\t")
    fieldnames = reader.fieldnames
    rows = list(reader)
rows[0]["reviewer_rank"] = ""
with open(output_path, "w", newline="", encoding="utf-8") as handle:
    writer = csv.DictWriter(handle, fieldnames=fieldnames, delimiter="\t", lineterminator="\n")
    writer.writeheader()
    writer.writerows(rows)
PY

if python3 "$APPLY_LABELS" --dataset "$SOURCE_DATASET" --review "$tmp_bad_review" --output "$tmp_gold" >/dev/null 2>&1; then
  echo "FAIL invalid review labels were accepted" >&2
  exit 1
else
  echo "PASS invalid review labels are rejected"
fi

echo "PASS overall: gold review workflow is reproducible and enforceable"
