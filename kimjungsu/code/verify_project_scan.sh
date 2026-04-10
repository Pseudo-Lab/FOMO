#!/usr/bin/env bash

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
SCAN_SCRIPT="$SCRIPT_DIR/project_scan.sh"
BASELINE_SCRIPT="$SCRIPT_DIR/baseline_project_scan.sh"
FIXTURE_ROOT="$(cd "$SCRIPT_DIR/.." && pwd)/fixtures"
SAMPLE_FIXTURE="$FIXTURE_ROOT/sample_app"
DOCS_FIXTURE="$FIXTURE_ROOT/docs_only"
BRIEFING_FIXTURE="$FIXTURE_ROOT/briefing_app"
OPS_HANDOFF_FIXTURE="$FIXTURE_ROOT/ops_handoff"
SMOKE_TARGET="${1:-$(cd "$SCRIPT_DIR/../.." && pwd)}"

if ! command -v rg >/dev/null 2>&1; then
  echo "error: ripgrep (rg) is required." >&2
  exit 1
fi

if [ ! -x "$SCAN_SCRIPT" ]; then
  echo "error: scan script is not executable: $SCAN_SCRIPT" >&2
  exit 1
fi

if [ ! -x "$BASELINE_SCRIPT" ]; then
  echo "error: baseline script is not executable: $BASELINE_SCRIPT" >&2
  exit 1
fi

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

assert_not_contains() {
  local haystack="$1"
  local needle="$2"
  local message="$3"

  if printf '%s\n' "$haystack" | rg -Fq "$needle"; then
    echo "FAIL $message" >&2
    return 1
  else
    echo "PASS $message"
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
  printf '%s\n' "$output" | awk -F'=' -v key="$key" '$1 == key {print $2; exit}'
}

check_sample_fixture_stage_1() {
  local output total markdown python json toml typescript tracked
  output="$("$SCAN_SCRIPT" --stage 1 "$SAMPLE_FIXTURE")"

  total="$(extract_metric "$output" "total")"
  markdown="$(extract_metric "$output" "markdown")"
  python="$(extract_metric "$output" "python")"
  json="$(extract_metric "$output" "json")"
  toml="$(extract_metric "$output" "toml")"
  typescript="$(extract_metric "$output" "typescript")"
  tracked="$(extract_metric "$output" "tracked_subtotal")"

  assert_equals "$total" "10" "sample fixture stage 1 total"
  assert_equals "$markdown" "4" "sample fixture stage 1 markdown count"
  assert_equals "$python" "2" "sample fixture stage 1 python count"
  assert_equals "$json" "2" "sample fixture stage 1 json count"
  assert_equals "$toml" "1" "sample fixture stage 1 toml count"
  assert_equals "$typescript" "1" "sample fixture stage 1 typescript count"
  assert_equals "$tracked" "10" "sample fixture stage 1 tracked subtotal"
}

check_sample_fixture_stage_2() {
  local output
  output="$("$SCAN_SCRIPT" --stage 2 "$SAMPLE_FIXTURE")"

  assert_contains "$output" "docs=README.md,backend/README.md,frontend/README.md" "sample fixture stage 2 docs anchors"
  assert_contains "$output" "python=backend/pyproject.toml" "sample fixture stage 2 python anchors"
  assert_contains "$output" "node=frontend/package.json" "sample fixture stage 2 node anchors"
  assert_contains "$output" "typescript=frontend/tsconfig.json" "sample fixture stage 2 typescript anchors"
  assert_contains "$output" "ops=(none)" "sample fixture stage 2 ops anchors"
}

check_sample_fixture_stage_3() {
  local output
  output="$("$SCAN_SCRIPT" --stage 3 "$SAMPLE_FIXTURE")"

  assert_contains "$output" "1|frontend|score=23|reasons=files:4,anchors:3,source:1,readme,node,typescript" "sample fixture stage 3 rank 1"
  assert_contains "$output" "2|backend|score=20|reasons=files:4,anchors:2,source:2,readme,python" "sample fixture stage 3 rank 2"
  assert_contains "$output" "3|ROOT|score=8|reasons=files:1,anchors:1,readme" "sample fixture stage 3 rank 3"
  assert_contains "$output" "4|docs|score=1|reasons=files:1" "sample fixture stage 3 rank 4"
}

check_sample_fixture_stage_4() {
  local output
  output="$("$SCAN_SCRIPT" --stage 4 "$SAMPLE_FIXTURE")"

  assert_contains "$output" "1|README.md|score=400|why=area:ROOT,area_score:8,role:root-readme,file_bonus:320" "sample fixture stage 4 rank 1"
  assert_contains "$output" "2|frontend/README.md|score=390|why=area:frontend,area_score:23,role:area-readme,file_bonus:160" "sample fixture stage 4 rank 2"
  assert_contains "$output" "3|backend/README.md|score=360|why=area:backend,area_score:20,role:area-readme,file_bonus:160" "sample fixture stage 4 rank 3"
  assert_contains "$output" "4|frontend/package.json|score=320|why=area:frontend,area_score:23,role:manifest,file_bonus:90" "sample fixture stage 4 rank 4"
  assert_contains "$output" "5|frontend/tsconfig.json|score=300|why=area:frontend,area_score:23,role:tooling-config,file_bonus:70" "sample fixture stage 4 rank 5"
}

check_docs_only_fixture() {
  local stage2 stage3 stage4
  stage2="$("$SCAN_SCRIPT" --stage 2 "$DOCS_FIXTURE")"
  stage3="$("$SCAN_SCRIPT" --stage 3 "$DOCS_FIXTURE")"
  stage4="$("$SCAN_SCRIPT" --stage 4 "$DOCS_FIXTURE")"

  assert_contains "$stage2" "docs=README.md" "docs-only fixture docs anchor"
  assert_contains "$stage2" "python=(none)" "docs-only fixture python anchor is empty"
  assert_contains "$stage2" "node=(none)" "docs-only fixture node anchor is empty"
  assert_contains "$stage3" "1|ROOT|score=8|reasons=files:1,anchors:1,readme" "docs-only fixture rank 1"
  assert_contains "$stage3" "2|notes|score=2|reasons=files:2" "docs-only fixture rank 2"
  assert_contains "$stage4" "1|README.md|score=400|why=area:ROOT,area_score:8,role:root-readme,file_bonus:320" "docs-only fixture stage 4 rank 1"
  assert_contains "$stage4" "2|notes/week1.md|score=30|why=area:notes,area_score:2,role:doc,file_bonus:10" "docs-only fixture stage 4 rank 2"
  assert_contains "$stage4" "3|notes/week2.md|score=30|why=area:notes,area_score:2,role:doc,file_bonus:10" "docs-only fixture stage 4 rank 3"
}

check_briefing_usecase() {
  local stage1 stage2 stage3 stage4
  stage1="$("$SCAN_SCRIPT" --stage 1 "$BRIEFING_FIXTURE")"
  stage2="$("$SCAN_SCRIPT" --stage 2 "$BRIEFING_FIXTURE")"
  stage3="$("$SCAN_SCRIPT" --stage 3 "$BRIEFING_FIXTURE")"
  stage4="$("$SCAN_SCRIPT" --stage 4 "$BRIEFING_FIXTURE")"

  assert_contains "$stage1" "markdown=5" "briefing usecase stage 1 markdown count"
  assert_contains "$stage1" "python=1" "briefing usecase stage 1 python count"
  assert_contains "$stage1" "typescript=1" "briefing usecase stage 1 typescript count"
  assert_contains "$stage2" "docs=README.md,apps/web/README.md,services/briefing/README.md" "briefing usecase stage 2 docs anchors"
  assert_contains "$stage2" "python=services/briefing/pyproject.toml" "briefing usecase stage 2 python anchor"
  assert_contains "$stage2" "node=apps/web/package.json" "briefing usecase stage 2 node anchor"
  assert_contains "$stage3" "1|apps|score=23|reasons=files:4,anchors:3,source:1,readme,node,typescript" "briefing usecase stage 3 apps rank"
  assert_contains "$stage3" "2|services|score=17|reasons=files:3,anchors:2,source:1,readme,python" "briefing usecase stage 3 services rank"
  assert_contains "$stage4" "1|README.md|score=400|why=area:ROOT,area_score:8,role:root-readme,file_bonus:320" "briefing usecase stage 4 rank 1"
  assert_contains "$stage4" "2|apps/web/README.md|score=390|why=area:apps,area_score:23,role:area-readme,file_bonus:160" "briefing usecase stage 4 rank 2"
  assert_contains "$stage4" "3|services/briefing/README.md|score=330|why=area:services,area_score:17,role:area-readme,file_bonus:160" "briefing usecase stage 4 rank 3"
}

check_ops_handoff_usecase() {
  local stage1 stage2 stage3 stage4
  stage1="$("$SCAN_SCRIPT" --stage 1 "$OPS_HANDOFF_FIXTURE")"
  stage2="$("$SCAN_SCRIPT" --stage 2 "$OPS_HANDOFF_FIXTURE")"
  stage3="$("$SCAN_SCRIPT" --stage 3 "$OPS_HANDOFF_FIXTURE")"
  stage4="$("$SCAN_SCRIPT" --stage 4 "$OPS_HANDOFF_FIXTURE")"

  assert_contains "$stage1" "markdown=4" "ops handoff stage 1 markdown count"
  assert_contains "$stage1" "python=1" "ops handoff stage 1 python count"
  assert_contains "$stage1" "json=1" "ops handoff stage 1 json count"
  assert_contains "$stage2" "docs=README.md,apps/admin/README.md,services/digest/README.md" "ops handoff stage 2 docs anchors"
  assert_contains "$stage2" "python=services/digest/pyproject.toml" "ops handoff stage 2 python anchor"
  assert_contains "$stage2" "node=apps/admin/package.json" "ops handoff stage 2 node anchor"
  assert_contains "$stage3" "1|services|score=23|reasons=files:4,anchors:3,source:1,readme,python,env" "ops handoff stage 3 services rank"
  assert_contains "$stage3" "2|apps|score=17|reasons=files:3,anchors:2,source:1,readme,node" "ops handoff stage 3 apps rank"
  assert_contains "$stage4" "1|README.md|score=400|why=area:ROOT,area_score:8,role:root-readme,file_bonus:320" "ops handoff stage 4 rank 1"
  assert_contains "$stage4" "2|services/digest/README.md|score=390|why=area:services,area_score:23,role:area-readme,file_bonus:160" "ops handoff stage 4 rank 2"
  assert_contains "$stage4" "3|apps/admin/README.md|score=330|why=area:apps,area_score:17,role:area-readme,file_bonus:160" "ops handoff stage 4 rank 3"
}

check_boundary_separation() {
  local stage1 stage2 stage3 stage4
  stage1="$("$SCAN_SCRIPT" --stage 1 "$SAMPLE_FIXTURE")"
  stage2="$("$SCAN_SCRIPT" --stage 2 "$SAMPLE_FIXTURE")"
  stage3="$("$SCAN_SCRIPT" --stage 3 "$SAMPLE_FIXTURE")"
  stage4="$("$SCAN_SCRIPT" --stage 4 "$SAMPLE_FIXTURE")"

  assert_not_contains "$stage1" "[anchors]" "stage 1 excludes stage 2 data"
  assert_not_contains "$stage1" "[priority]" "stage 1 excludes stage 3 data"
  assert_not_contains "$stage1" "[read-first]" "stage 1 excludes stage 4 data"
  assert_not_contains "$stage2" "[metrics]" "stage 2 excludes stage 1 metrics"
  assert_not_contains "$stage2" "[priority]" "stage 2 excludes stage 3 data"
  assert_not_contains "$stage2" "[read-first]" "stage 2 excludes stage 4 data"
  assert_not_contains "$stage3" "[metrics]" "stage 3 excludes stage 1 metrics"
  assert_not_contains "$stage3" "[anchors]" "stage 3 excludes stage 2 data"
  assert_not_contains "$stage3" "[read-first]" "stage 3 excludes stage 4 data"
  assert_not_contains "$stage4" "[metrics]" "stage 4 excludes stage 1 metrics"
  assert_not_contains "$stage4" "[anchors]" "stage 4 excludes stage 2 data"
  assert_not_contains "$stage4" "[priority]" "stage 4 excludes stage 3 data"
}

check_baseline_comparison() {
  local baseline structured_stage2 structured_stage3 structured_stage4
  baseline="$("$BASELINE_SCRIPT" "$SAMPLE_FIXTURE")"
  structured_stage2="$("$SCAN_SCRIPT" --stage 2 "$SAMPLE_FIXTURE")"
  structured_stage3="$("$SCAN_SCRIPT" --stage 3 "$SAMPLE_FIXTURE")"
  structured_stage4="$("$SCAN_SCRIPT" --stage 4 "$SAMPLE_FIXTURE")"

  assert_not_contains "$baseline" "[anchors]" "baseline excludes anchor structure"
  assert_not_contains "$baseline" "[priority]" "baseline excludes priority structure"
  assert_not_contains "$baseline" "[read-first]" "baseline excludes read-first structure"
  assert_contains "$structured_stage2" "[anchors]" "structured stage 2 adds anchor structure"
  assert_contains "$structured_stage3" "[priority]" "structured stage 3 adds priority structure"
  assert_contains "$structured_stage4" "[read-first]" "structured stage 4 adds read-first structure"
}

check_smoke_target() {
  local output
  output="$("$SCAN_SCRIPT" --stage all "$SMOKE_TARGET")"

  assert_contains "$output" "[stage 1] inventory" "smoke target includes stage 1"
  assert_contains "$output" "[stage 2] anchor detection" "smoke target includes stage 2"
  assert_contains "$output" "[stage 3] area priority" "smoke target includes stage 3"
  assert_contains "$output" "[stage 4] read-first files" "smoke target includes stage 4"
}

check_sample_fixture_stage_1
check_sample_fixture_stage_2
check_sample_fixture_stage_3
check_sample_fixture_stage_4
check_docs_only_fixture
check_briefing_usecase
check_ops_handoff_usecase
check_boundary_separation
check_baseline_comparison
check_smoke_target

echo "PASS overall: project_scan satisfies fixture, usecase, boundary, baseline, and smoke validation"
