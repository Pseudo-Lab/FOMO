#!/usr/bin/env bash

set -euo pipefail

export LC_ALL=C

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
ROOT_DIR="$(cd "$SCRIPT_DIR/.." && pwd)"
MODE="hypothesis"
USECASE="briefing"
DATASET_OVERRIDE=""

usage() {
  cat <<'EOF'
Usage:
  service_value_eval.sh [--mode hypothesis|baseline] [--dataset path.tsv] [briefing|ops-handoff|biz-planning]

Modes:
  hypothesis  Evaluate the service hypothesis algorithm
  baseline    Evaluate the naive baseline algorithm

Options:
  --dataset path.tsv  Use an external TSV dataset with the selected usecase schema
EOF
}

while [ $# -gt 0 ]; do
  case "$1" in
    --mode)
      if [ $# -lt 2 ]; then
        echo "error: --mode requires a value." >&2
        exit 1
      fi
      MODE="$2"
      shift 2
      ;;
    --dataset)
      if [ $# -lt 2 ]; then
        echo "error: --dataset requires a path." >&2
        exit 1
      fi
      DATASET_OVERRIDE="$2"
      shift 2
      ;;
    --help|-h)
      usage
      exit 0
      ;;
    *)
      USECASE="$1"
      shift
      ;;
  esac
done

case "$MODE" in
  hypothesis|baseline) ;;
  *)
    echo "error: invalid mode: $MODE" >&2
    usage >&2
    exit 1
    ;;
esac

case "$USECASE" in
  briefing|ops-handoff|biz-planning|business-planning) ;;
  *)
    echo "error: unsupported usecase: $USECASE" >&2
    usage >&2
    exit 1
    ;;
esac

dataset_for_usecase() {
  case "$1" in
    briefing)
      printf '%s\n' "$ROOT_DIR/fixtures/service_value/briefing_priority_cases.tsv"
      ;;
    ops-handoff)
      printf '%s\n' "$ROOT_DIR/fixtures/service_value/ops_handoff_priority_cases.tsv"
      ;;
    biz-planning|business-planning)
      printf '%s\n' "$ROOT_DIR/fixtures/service_value/biz_planning_priority_cases.tsv"
      ;;
    *)
      echo "error: unsupported usecase: $1" >&2
      exit 1
      ;;
  esac
}

expected_header_for_usecase() {
  case "$1" in
    briefing)
      printf '%s\n' "case_id	item_id	title	urgency	due_hours	prep_minutes	team_impact	user_visible	expected_rank"
      ;;
    ops-handoff)
      printf '%s\n' "case_id	item_id	title	severity	sla_minutes	vip_account	overnight_incident	revenue_risk	expected_rank"
      ;;
    biz-planning|business-planning)
      printf '%s\n' "case_id	item_id	title	forecast_gap_pct	board_deadline_hours	cross_team_dependency	exec_visibility	revenue_impact	expected_rank"
      ;;
  esac
}

validate_dataset_contract() {
  local dataset="$1"
  local expected_header header

  expected_header="$(expected_header_for_usecase "$USECASE")"

  if ! IFS= read -r header < "$dataset"; then
    echo "error: dataset is empty: $dataset" >&2
    exit 1
  fi

  header="${header%$'\r'}"
  if [ "$header" != "$expected_header" ]; then
    echo "error: dataset header does not match $USECASE schema: $dataset" >&2
    echo "expected: $expected_header" >&2
    echo "actual:   $header" >&2
    exit 1
  fi

  if ! awk -F'\t' '
    NR > 1 {
      rows += 1
      cases[$1] = 1
      if ($9 !~ /^[0-9]+$/) {
        bad_rank += 1
      }
      if (($9 + 0) == 1) {
        gold[$1] += 1
      }
    }
    END {
      if (rows == 0 || bad_rank > 0) {
        exit 1
      }
      for (case_id in cases) {
        if (gold[case_id] != 1) {
          exit 1
        }
      }
    }
  ' "$dataset"; then
    echo "error: dataset must have rows, numeric expected_rank, and exactly one gold rank per case: $dataset" >&2
    exit 1
  fi
}

print_stage_0() {
  case "$USECASE:$MODE" in
    briefing:hypothesis)
      cat <<'EOF'
[stage 0] hypothesis lens
service=briefing
decision=아침에 무엇을 먼저 해야 하는지 2분 안에 결정하게 만든다
hypothesis=urgency만 보지 않고 due time, prep need, team impact, user visibility를 함께 반영하면 첫 행동 선택이 더 정확해진다
baseline=urgency만 보는 단순 정렬
primary_metric=top1_accuracy
secondary_metric=mrr,mean_gold_rank
EOF
      ;;
    briefing:baseline)
      cat <<'EOF'
[stage 0] hypothesis lens
service=briefing
decision=아침에 무엇을 먼저 해야 하는지 2분 안에 결정하게 만든다
hypothesis=baseline run
baseline=urgency만 보는 단순 정렬
primary_metric=top1_accuracy
secondary_metric=mrr,mean_gold_rank
EOF
      ;;
    ops-handoff:hypothesis)
      cat <<'EOF'
[stage 0] hypothesis lens
service=ops-handoff
decision=support ops lead가 오늘 가장 먼저 대응할 고객과 이슈를 빠르게 결정하게 만든다
hypothesis=severity만 보지 않고 SLA risk, VIP, overnight incident, revenue risk를 함께 반영하면 첫 대응 선택이 더 정확해진다
baseline=severity만 보는 단순 정렬
primary_metric=top1_accuracy
secondary_metric=mrr,mean_gold_rank
EOF
      ;;
    ops-handoff:baseline)
      cat <<'EOF'
[stage 0] hypothesis lens
service=ops-handoff
decision=support ops lead가 오늘 가장 먼저 대응할 고객과 이슈를 빠르게 결정하게 만든다
hypothesis=baseline run
baseline=severity만 보는 단순 정렬
primary_metric=top1_accuracy
secondary_metric=mrr,mean_gold_rank
EOF
      ;;
    biz-planning:hypothesis|business-planning:hypothesis)
      cat <<'EOF'
[stage 0] hypothesis lens
service=biz-planning
decision=사업기획팀이 주간 운영 회의 전에 어떤 매출 가정과 리스크를 먼저 확인할지 빠르게 결정하게 만든다
hypothesis=forecast gap만 보지 않고 board deadline, cross-team dependency, executive visibility, revenue impact를 함께 반영하면 첫 확인 항목 선택이 더 정확해진다
baseline=forecast gap만 보는 단순 정렬
primary_metric=top1_accuracy
secondary_metric=mrr,mean_gold_rank
EOF
      ;;
    biz-planning:baseline|business-planning:baseline)
      cat <<'EOF'
[stage 0] hypothesis lens
service=biz-planning
decision=사업기획팀이 주간 운영 회의 전에 어떤 매출 가정과 리스크를 먼저 확인할지 빠르게 결정하게 만든다
hypothesis=baseline run
baseline=forecast gap만 보는 단순 정렬
primary_metric=top1_accuracy
secondary_metric=mrr,mean_gold_rank
EOF
      ;;
  esac
  echo
}

score_dataset() {
  local dataset="$1"

  case "$USECASE:$MODE" in
    briefing:hypothesis)
      awk -F'\t' '
        BEGIN { OFS = "\t" }
        NR == 1 { next }
        {
          urgency = $4 + 0
          due_hours = $5 + 0
          prep_minutes = $6 + 0
          team_impact = $7 + 0
          user_visible = $8 + 0
          gold_rank = $9 + 0

          due_component = (due_hours <= 2 ? 35 : (due_hours <= 6 ? 20 : (due_hours <= 24 ? 10 : 0)))
          prep_component = (prep_minutes >= 45 ? 20 : (prep_minutes >= 15 ? 10 : 0))
          score = (urgency * 20) + due_component + prep_component + (team_impact * 18) + (user_visible * 20)

          reason = "urgency:" urgency ",due:" due_component ",prep:" prep_component ",team:" (team_impact * 18) ",visible:" (user_visible * 20)
          print $1, $2, $3, gold_rank, score, reason
        }
      ' "$dataset"
      ;;
    briefing:baseline)
      awk -F'\t' '
        BEGIN { OFS = "\t" }
        NR == 1 { next }
        {
          urgency = $4 + 0
          gold_rank = $9 + 0
          score = urgency
          reason = "urgency_only:" urgency
          print $1, $2, $3, gold_rank, score, reason
        }
      ' "$dataset"
      ;;
    ops-handoff:hypothesis)
      awk -F'\t' '
        BEGIN { OFS = "\t" }
        NR == 1 { next }
        {
          severity = $4 + 0
          sla_minutes = $5 + 0
          vip_account = $6 + 0
          overnight_incident = $7 + 0
          revenue_risk = $8 + 0
          gold_rank = $9 + 0

          sla_component = (sla_minutes <= 30 ? 25 : (sla_minutes <= 120 ? 15 : (sla_minutes <= 480 ? 8 : 0)))
          score = (severity * 25) + sla_component + (vip_account * 20) + (overnight_incident * 15) + (revenue_risk * 20)

          reason = "severity:" (severity * 25) ",sla:" sla_component ",vip:" (vip_account * 20) ",overnight:" (overnight_incident * 15) ",revenue:" (revenue_risk * 20)
          print $1, $2, $3, gold_rank, score, reason
        }
      ' "$dataset"
      ;;
    ops-handoff:baseline)
      awk -F'\t' '
        BEGIN { OFS = "\t" }
        NR == 1 { next }
        {
          severity = $4 + 0
          gold_rank = $9 + 0
          score = severity
          reason = "severity_only:" severity
          print $1, $2, $3, gold_rank, score, reason
        }
      ' "$dataset"
      ;;
    biz-planning:hypothesis|business-planning:hypothesis)
      awk -F'\t' '
        BEGIN { OFS = "\t" }
        NR == 1 { next }
        {
          forecast_gap_pct = $4 + 0
          board_deadline_hours = $5 + 0
          cross_team_dependency = $6 + 0
          exec_visibility = $7 + 0
          revenue_impact = $8 + 0
          gold_rank = $9 + 0

          deadline_component = (board_deadline_hours <= 24 ? 35 : (board_deadline_hours <= 72 ? 20 : (board_deadline_hours <= 168 ? 10 : 0)))
          score = (forecast_gap_pct * 10) + deadline_component + (cross_team_dependency * 18) + (exec_visibility * 20) + (revenue_impact * 20)

          reason = "gap:" (forecast_gap_pct * 10) ",deadline:" deadline_component ",dependency:" (cross_team_dependency * 18) ",exec:" (exec_visibility * 20) ",revenue:" (revenue_impact * 20)
          print $1, $2, $3, gold_rank, score, reason
        }
      ' "$dataset"
      ;;
    biz-planning:baseline|business-planning:baseline)
      awk -F'\t' '
        BEGIN { OFS = "\t" }
        NR == 1 { next }
        {
          forecast_gap_pct = $4 + 0
          gold_rank = $9 + 0
          score = forecast_gap_pct
          reason = "forecast_gap_only:" forecast_gap_pct
          print $1, $2, $3, gold_rank, score, reason
        }
      ' "$dataset"
      ;;
  esac
}

rank_scored_rows() {
  local dataset="$1"
  local score_tmp rank_tmp

  score_tmp="$(mktemp)"
  rank_tmp="$(mktemp)"

  trap 'rm -f "$score_tmp" "$rank_tmp"' RETURN

  score_dataset "$dataset" > "$score_tmp"
  sort -t $'\t' -k1,1 -k5,5nr -k2,2 "$score_tmp" | awk -F'\t' '
    BEGIN { OFS = "\t" }
    {
      if ($1 != current_case) {
        current_case = $1
        predicted_rank = 0
      }
      predicted_rank += 1
      print $1, predicted_rank, $2, $3, $4, $5, $6
    }
  ' > "$rank_tmp"

  cat "$rank_tmp"
}

print_stage_1() {
  local dataset="$1"
  local rows cases mean_items

  rows="$(awk 'NR > 1 { rows += 1 } END { print rows + 0 }' "$dataset")"
  cases="$(awk -F'\t' 'NR > 1 { seen[$1] = 1 } END { print length(seen) + 0 }' "$dataset")"
  mean_items="$(awk -F'\t' '
    NR > 1 {
      count[$1] += 1
    }
    END {
      for (case_id in count) {
        total += count[case_id]
        cases += 1
      }
      if (cases == 0) {
        printf "0.00"
      } else {
        printf "%.2f", total / cases
      }
    }
  ' "$dataset")"

  echo "[stage 1] case audit"
  echo "dataset=$dataset"
  if [ -n "$DATASET_OVERRIDE" ]; then
    echo "dataset_source=override"
  else
    echo "dataset_source=fixture"
  fi
  echo "mode=$MODE"
  echo "rows=$rows"
  echo "cases=$cases"
  echo "mean_items_per_case=$mean_items"
  echo "validation_contract=dataset_schema_matches_usecase,explicit_gold_labels,case_count>=1"
  echo
}

print_stage_2() {
  local ranked="$1"

  echo "[stage 2] deterministic scoring"
  echo "goal=고정 fixture 위에서 case별 우선순위를 결정론적으로 계산한다"
  echo "validation_contract=stable_sort,stable_tie_break,item_id_lexical_order"
  echo
  echo "[ranking]"
  printf '%s\n' "$ranked" | awk -F'\t' '
    BEGIN { OFS = "|" }
    {
      if (count[$1] < 3) {
        count[$1] += 1
        print $1, "pred_rank=" $2, "item=" $3, "gold_rank=" $5, "score=" $6, "why=" $7
      }
    }
  '
  echo
}

print_stage_3() {
  local ranked="$1"
  local cases top1_accuracy mrr mean_gold_rank

  cases="$(printf '%s\n' "$ranked" | awk -F'\t' '$5 == 1 { cases += 1 } END { print cases + 0 }')"
  top1_accuracy="$(printf '%s\n' "$ranked" | awk -F'\t' '
    $5 == 1 {
      cases += 1
      if ($2 == 1) {
        top1 += 1
      }
    }
    END {
      if (cases == 0) {
        printf "0.00"
      } else {
        printf "%.2f", top1 / cases
      }
    }
  ')"
  mrr="$(printf '%s\n' "$ranked" | awk -F'\t' '
    $5 == 1 {
      cases += 1
      reciprocal += 1 / $2
    }
    END {
      if (cases == 0) {
        printf "0.00"
      } else {
        printf "%.2f", reciprocal / cases
      }
    }
  ')"
  mean_gold_rank="$(printf '%s\n' "$ranked" | awk -F'\t' '
    $5 == 1 {
      cases += 1
      rank_sum += $2
    }
    END {
      if (cases == 0) {
        printf "0.00"
      } else {
        printf "%.2f", rank_sum / cases
      }
    }
  ')"

  echo "[stage 3] objective quality"
  echo "goal=서비스 가설이 실제 결정 품질을 얼마나 올리는지 본다"
  echo "validation_contract=top1_accuracy_is_numeric,mrr_is_numeric,mean_gold_rank_is_numeric"
  echo
  echo "[per-case]"
  printf '%s\n' "$ranked" | awk -F'\t' '
    BEGIN { OFS = "|" }
    $5 == 1 {
      print $1, "gold_item=" $3, "pred_rank=" $2, "score=" $6
    }
  '
  echo
  echo "[metrics]"
  echo "cases=$cases"
  echo "top1_accuracy=$top1_accuracy"
  echo "mrr=$mrr"
  echo "mean_gold_rank=$mean_gold_rank"
  echo
}

print_stage_4() {
  local dataset="$1"
  local rerun_command

  rerun_command="bash kimjungsu/code/service_value_eval.sh --mode $MODE"
  if [ -n "$DATASET_OVERRIDE" ]; then
    rerun_command="$rerun_command --dataset $DATASET_OVERRIDE"
  fi
  rerun_command="$rerun_command $USECASE"

  echo "[stage 4] reproducibility contract"
  echo "goal=같은 입력과 같은 규칙이면 같은 출력이 반복돼야 한다"
  echo "dataset_path=$dataset"
  echo "scorer_version=v1"
  echo "mode=$MODE"
  echo "randomness=none"
  echo "tie_break=item_id_lexical_order"
  echo "rerun_command=$rerun_command"
  echo
}

if [ -n "$DATASET_OVERRIDE" ]; then
  DATASET="$DATASET_OVERRIDE"
else
  DATASET="$(dataset_for_usecase "$USECASE")"
fi

if [ ! -f "$DATASET" ]; then
  echo "error: dataset not found: $DATASET" >&2
  exit 1
fi

validate_dataset_contract "$DATASET"

RANKED_ROWS="$(rank_scored_rows "$DATASET")"

echo "== Service Value Eval =="
echo "usecase=$USECASE"
echo "mode=$MODE"
echo

print_stage_0
print_stage_1 "$DATASET"
print_stage_2 "$RANKED_ROWS"
print_stage_3 "$RANKED_ROWS"
print_stage_4 "$DATASET"

echo "[summary]"
echo "completed=service_value_eval"
