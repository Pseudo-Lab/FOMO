#!/usr/bin/env bash

set -euo pipefail

STAGE="all"
TARGET="."

usage() {
  cat <<'EOF'
Usage:
  project_scan.sh [--stage 1|2|3|4|all] [target]

Stages:
  1    Inventory: count files with minimal assumptions
  2    Anchor detection: find entry/config files by ecosystem rules
  3    Area priority: rank top-level areas to inspect first
  4    Read-first files: recommend concrete files to open first
  all  Run every stage in order
EOF
}

while [ $# -gt 0 ]; do
  case "$1" in
    --stage)
      if [ $# -lt 2 ]; then
        echo "error: --stage requires a value." >&2
        exit 1
      fi
      STAGE="$2"
      shift 2
      ;;
    --help|-h)
      usage
      exit 0
      ;;
    *)
      TARGET="$1"
      shift
      ;;
  esac
done

case "$STAGE" in
  1|2|3|4|all) ;;
  *)
    echo "error: invalid stage: $STAGE" >&2
    usage >&2
    exit 1
    ;;
esac

if ! command -v rg >/dev/null 2>&1; then
  echo "error: ripgrep (rg) is required." >&2
  exit 1
fi

if [ ! -d "$TARGET" ]; then
  echo "error: target directory not found: $TARGET" >&2
  exit 1
fi

ROOT="$(cd "$TARGET" && pwd)"

rg_files() {
  rg --files --hidden -g '!.git' "$ROOT" || true
}

rg_files_glob() {
  local glob="$1"
  rg --files --hidden -g '!.git' -g "$glob" "$ROOT" || true
}

list_rel_files() {
  rg_files | sed "s#^$ROOT/##" | sed 's#^/##' | sort
}

count_matches() {
  local glob="$1"
  ({ rg_files_glob "$glob"; } | wc -l | tr -d ' ')
}

join_comma_or_none() {
  if [ $# -eq 0 ]; then
    echo "(none)"
  else
    local joined
    joined=$(printf '%s\n' "$@" | sort | paste -sd, -)
    echo "${joined:-"(none)"}"
  fi
}

print_common_header() {
  echo "== Project Scan =="
  echo "target=$ROOT"
  echo
}

run_stage_1() {
  local total markdown python shell json yaml yml toml typescript tsx tracked_subtotal

  total=$(list_rel_files | wc -l | tr -d ' ')
  markdown=$(count_matches '*.md')
  python=$(count_matches '*.py')
  shell=$(count_matches '*.sh')
  json=$(count_matches '*.json')
  yaml=$(count_matches '*.yaml')
  yml=$(count_matches '*.yml')
  toml=$(count_matches '*.toml')
  typescript=$(count_matches '*.ts')
  tsx=$(count_matches '*.tsx')
  tracked_subtotal=$((markdown + python + shell + json + yaml + yml + toml + typescript + tsx))

  echo "[stage 1] inventory"
  echo "goal=저장소를 추측 없이 계수한다"
  echo "assumption_level=low"
  echo "new_signal=overall_size,file_type_mix"
  echo "validation_contract=total>=1,metrics_are_numeric,tracked_subtotal<=total"
  echo
  echo "[metrics]"
  echo "total=$total"
  echo "markdown=$markdown"
  echo "python=$python"
  echo "shell=$shell"
  echo "json=$json"
  echo "yaml=$yaml"
  echo "yml=$yml"
  echo "toml=$toml"
  echo "typescript=$typescript"
  echo "tsx=$tsx"
  echo "tracked_subtotal=$tracked_subtotal"
  echo
}

run_stage_2() {
  local -a docs python node typescript ops go rust env
  local file

  docs=()
  python=()
  node=()
  typescript=()
  ops=()
  go=()
  rust=()
  env=()

  while IFS= read -r file; do
    [ -n "$file" ] || continue
    case "$file" in
      README*|*/README*)
        docs+=("$file")
        ;;
      *requirements.txt|*pyproject.toml)
        python+=("$file")
        ;;
      *package.json|*pnpm-lock.yaml|*yarn.lock|*package-lock.json)
        node+=("$file")
        ;;
      *tsconfig.json|*vite.config.*|*next.config.*)
        typescript+=("$file")
        ;;
      *Dockerfile|*docker-compose*)
        ops+=("$file")
        ;;
      *go.mod)
        go+=("$file")
        ;;
      *Cargo.toml)
        rust+=("$file")
        ;;
      *.env.example)
        env+=("$file")
        ;;
    esac
  done < <(
    {
      rg --files --hidden -g '!.git' -g 'README*' -g 'package.json' -g 'pnpm-lock.yaml' -g 'yarn.lock' \
        -g 'package-lock.json' -g 'tsconfig.json' -g 'vite.config.*' -g 'next.config.*' \
        -g 'pyproject.toml' -g 'requirements.txt' -g 'Cargo.toml' -g 'go.mod' \
        -g 'Dockerfile' -g 'docker-compose*' -g '.env.example' "$ROOT" || true
    } | sed "s#^$ROOT/##" | sed 's#^/##' | sort -u
  )

  echo "[stage 2] anchor detection"
  echo "goal=진입점과 ecosystem anchor를 찾는다"
  echo "assumption_level=medium"
  echo "new_signal=entry_points,config_files,ecosystem_groups"
  echo "validation_contract=deterministic_groups,no_duplicates,each_anchor_has_one_group"
  echo
  echo "[anchors]"
  echo "docs=$(join_comma_or_none "${docs[@]}")"
  echo "python=$(join_comma_or_none "${python[@]}")"
  echo "node=$(join_comma_or_none "${node[@]}")"
  echo "typescript=$(join_comma_or_none "${typescript[@]}")"
  echo "ops=$(join_comma_or_none "${ops[@]}")"
  echo "go=$(join_comma_or_none "${go[@]}")"
  echo "rust=$(join_comma_or_none "${rust[@]}")"
  echo "env=$(join_comma_or_none "${env[@]}")"
  echo
}

build_area_priority_rows() {
  list_rel_files | awk '
    function top_area(path, n, parts) {
      n = split(path, parts, "/")
      if (n == 1) {
        return "ROOT"
      }
      return parts[1]
    }
    function mark_reason(area, token) {
      if (token == "") {
        return
      }
      reason_flag[area, token] = 1
    }
    function append_reason(detail, area, token) {
      if (reason_flag[area, token]) {
        detail = detail "," token
      }
      return detail
    }
    {
      area = top_area($0)
      files[area] += 1

      if ($0 ~ /(^|\/)README[^/]*$/) {
        anchors[area] += 1
        readmes[area] += 1
        mark_reason(area, "readme")
      }
      if ($0 ~ /(requirements\.txt|pyproject\.toml)$/) {
        anchors[area] += 1
        mark_reason(area, "python")
      }
      if ($0 ~ /(package\.json|pnpm-lock\.yaml|yarn\.lock|package-lock\.json)$/) {
        anchors[area] += 1
        mark_reason(area, "node")
      }
      if ($0 ~ /(tsconfig\.json|vite\.config\.[^/]+|next\.config\.[^/]+)$/) {
        anchors[area] += 1
        mark_reason(area, "typescript")
      }
      if ($0 ~ /(Dockerfile|docker-compose[^/]*)$/) {
        anchors[area] += 1
        mark_reason(area, "ops")
      }
      if ($0 ~ /(go\.mod)$/) {
        anchors[area] += 1
        mark_reason(area, "go")
      }
      if ($0 ~ /(Cargo\.toml)$/) {
        anchors[area] += 1
        mark_reason(area, "rust")
      }
      if ($0 ~ /(\.env\.example)$/) {
        anchors[area] += 1
        mark_reason(area, "env")
      }
      if ($0 ~ /\.(py|ts|tsx|js|sh)$/) {
        source[area] += 1
      }
    }
    END {
      for (area in files) {
        score = files[area] + (anchors[area] * 5) + (readmes[area] * 2) + (source[area] * 2)

        detail = "files:" files[area]
        if (anchors[area] > 0) {
          detail = detail ",anchors:" anchors[area]
        }
        if (source[area] > 0) {
          detail = detail ",source:" source[area]
        }
        detail = append_reason(detail, area, "readme")
        detail = append_reason(detail, area, "python")
        detail = append_reason(detail, area, "node")
        detail = append_reason(detail, area, "typescript")
        detail = append_reason(detail, area, "ops")
        detail = append_reason(detail, area, "go")
        detail = append_reason(detail, area, "rust")
        detail = append_reason(detail, area, "env")

        printf "%s\t%s\t%s\n", score, area, detail
      }
    }
  ' | sort -t $'\t' -k1,1nr -k2,2
}

run_stage_3() {
  local row rank=0 score area detail

  echo "[stage 3] area priority"
  echo "goal=stage1과 stage2 결과를 상위 디렉토리 우선순위로 바꾼다"
  echo "assumption_level=high"
  echo "new_signal=ranked_area_order,score,reasons"
  echo "validation_contract=at_least_one_item,sorted_by_score_desc,each_item_has_reason"
  echo
  echo "[priority]"

  while IFS=$'\t' read -r score area detail; do
    [ -n "$area" ] || continue
    rank=$((rank + 1))
    printf '%d|%s|score=%s|reasons=%s\n' "$rank" "$area" "$score" "$detail"
  done < <(build_area_priority_rows)
  echo
}

build_file_priority_rows() {
  awk -F'\t' '
    NR == FNR {
      area_score[$2] = $1
      next
    }
    function top_area(path, n, parts) {
      n = split(path, parts, "/")
      if (n == 1) {
        return "ROOT"
      }
      return parts[1]
    }
    function role_bonus(path) {
      if (path == "README.md") {
        return 320
      }
      if (path ~ /(^|\/)README[^/]*$/) {
        return 160
      }
      if (path ~ /(package\.json|pyproject\.toml|requirements\.txt)$/) {
        return 90
      }
      if (path ~ /(tsconfig\.json|vite\.config\.[^/]+|next\.config\.[^/]+)$/) {
        return 70
      }
      if (path ~ /(^|\/)(ARCHITECTURE|architecture)\.md$/) {
        return 50
      }
      if (path ~ /(^|\/)(main|app|server|index)\.(py|ts|tsx|js)$/) {
        return 45
      }
      if (path ~ /\.(py|ts|tsx|js|md)$/) {
        return 10
      }
      return 0
    }
    function role_name(path) {
      if (path == "README.md") {
        return "root-readme"
      }
      if (path ~ /(^|\/)README[^/]*$/) {
        return "area-readme"
      }
      if (path ~ /(package\.json|pyproject\.toml|requirements\.txt)$/) {
        return "manifest"
      }
      if (path ~ /(tsconfig\.json|vite\.config\.[^/]+|next\.config\.[^/]+)$/) {
        return "tooling-config"
      }
      if (path ~ /(^|\/)(ARCHITECTURE|architecture)\.md$/) {
        return "architecture-doc"
      }
      if (path ~ /(^|\/)(main|app|server|index)\.(py|ts|tsx|js)$/) {
        return "entry-source"
      }
      if (path ~ /\.(py|ts|tsx|js)$/) {
        return "source"
      }
      if (path ~ /\.md$/) {
        return "doc"
      }
      return "other"
    }
    {
      path = $0
      area = top_area(path)
      area_component = (area_score[area] + 0) * 10
      file_component = role_bonus(path)
      score = area_component + file_component
      reason = "area:" area ",area_score:" area_score[area] ",role:" role_name(path) ",file_bonus:" file_component
      printf "%s\t%s\t%s\n", score, path, reason
    }
  ' <(build_area_priority_rows) <(list_rel_files) | sort -t $'\t' -k1,1nr -k2,2
}

run_stage_4() {
  local rank=0 score path reason

  echo "[stage 4] read-first files"
  echo "goal=stage2와 stage3 산출물을 바탕으로 서비스 이해에 필요한 파일을 먼저 추천한다"
  echo "assumption_level=high"
  echo "new_signal=ranked_file_order,service_first_read_path"
  echo "validation_contract=uses_existing_files_only,top_items_have_reasons,rank_is_stable"
  echo
  echo "[read-first]"

  while IFS=$'\t' read -r score path reason; do
    [ -n "$path" ] || continue
    rank=$((rank + 1))
    if [ "$rank" -le 5 ]; then
      printf '%d|%s|score=%s|why=%s\n' "$rank" "$path" "$score" "$reason"
    fi
  done < <(build_file_priority_rows)
  echo
}

print_common_header

case "$STAGE" in
  1)
    run_stage_1
    ;;
  2)
    run_stage_2
    ;;
  3)
    run_stage_3
    ;;
  4)
    run_stage_4
    ;;
  all)
    run_stage_1
    run_stage_2
    run_stage_3
    run_stage_4
    ;;
esac

echo "[summary]"
echo "completed_stage=$STAGE"
