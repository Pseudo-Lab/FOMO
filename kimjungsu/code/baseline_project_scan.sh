#!/usr/bin/env bash

set -euo pipefail

TARGET="${1:-.}"

if ! command -v rg >/dev/null 2>&1; then
  echo "error: ripgrep (rg) is required." >&2
  exit 1
fi

if [ ! -d "$TARGET" ]; then
  echo "error: target directory not found: $TARGET" >&2
  exit 1
fi

ROOT="$(cd "$TARGET" && pwd)"

echo "== Baseline Project Scan =="
echo "target=$ROOT"
echo
echo "[baseline]"
echo "goal=최소 정보만 출력하는 비교 기준"
echo "signal=file_list_only"
echo

{
  rg --files "$ROOT" || true
} | sed "s#^$ROOT/##" | sed 's#^/##' | sort
