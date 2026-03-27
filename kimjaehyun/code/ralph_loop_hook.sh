#!/bin/bash
# Ralph Loop — Stop Hook Handler
# Claude Code 세션 종료 시 자동으로 다음 반복을 시작하는 Stop Hook
#
# 동작 원리:
#   1. .ralph-loop/state.json이 존재하고 active=true이면 루프 계속
#   2. 완료 프로미스(<promise>DONE</promise>)가 트랜스크립트에 있으면 종료
#   3. max_iterations 초과 시 종료
#   4. 그 외: inject_prompt로 다음 반복 시작
#
# Author: kimjaehyun
# Date: 2026-03-28

set -uo pipefail

# stdin에서 hook input 읽기
INPUT=$(cat)

HOOK_VARS=$(echo "$INPUT" | python3 -c "
import sys,json
d=json.load(sys.stdin)
print(d.get('session_id',''))
print(d.get('transcript_path',''))
print(d.get('cwd',''))
" 2>/dev/null) || HOOK_VARS=""
SESSION_ID=$(echo "$HOOK_VARS" | sed -n '1p')
TRANSCRIPT_PATH=$(echo "$HOOK_VARS" | sed -n '2p')
CWD=$(echo "$HOOK_VARS" | sed -n '3p')
CWD="${CWD:-$(pwd)}"

STATE_DIR="${CWD}/.ralph-loop"
STATE_FILE="${STATE_DIR}/state.json"

# 상태 파일이 없으면 루프 비활성 — 정상 종료
if [ ! -f "$STATE_FILE" ]; then
  echo '{"decision":"approve"}'
  exit 0
fi

# 상태 읽기 (환경변수로 경로 전달 — 경로 인젝션 방지)
STATE_VARS=$(RALPH_STATE_FILE="$STATE_FILE" python3 -c "
import json, os
f = os.environ['RALPH_STATE_FILE']
s = json.load(open(f))
print(s.get('active', False))
print(s.get('iteration', 0))
print(s.get('max_iterations', 100))
print(s.get('prompt', ''))
print(s.get('completion_promise', 'DONE'))
" 2>/dev/null) || {
  echo '{"decision":"approve"}'
  exit 0
}

ACTIVE=$(echo "$STATE_VARS" | sed -n '1p')
ITERATION=$(echo "$STATE_VARS" | sed -n '2p')
MAX_ITER=$(echo "$STATE_VARS" | sed -n '3p')
PROMPT=$(echo "$STATE_VARS" | sed -n '4p')
COMPLETION=$(echo "$STATE_VARS" | sed -n '5p')

if [ "$ACTIVE" != "True" ]; then
  echo '{"decision":"approve"}'
  exit 0
fi

# 완료 프로미스 감지
PROMISE_FOUND=false
if [ -n "$TRANSCRIPT_PATH" ] && [ -f "$TRANSCRIPT_PATH" ]; then
  if grep -q "<promise>${COMPLETION}</promise>" "$TRANSCRIPT_PATH" 2>/dev/null; then
    PROMISE_FOUND=true
  fi
fi

# 종료 조건
if [ "$PROMISE_FOUND" = "true" ]; then
  RALPH_STATE_FILE="$STATE_FILE" python3 -c "
import json, os, datetime
f = os.environ['RALPH_STATE_FILE']
s = json.load(open(f))
s['active'] = False
s['completed_at'] = datetime.datetime.now().isoformat()
s['status'] = 'completed'
json.dump(s, open(f, 'w'), indent=2, ensure_ascii=False)
" 2>/dev/null
  echo '{"decision":"approve"}'
  exit 0
fi

if [ "$ITERATION" -ge "$MAX_ITER" ]; then
  RALPH_STATE_FILE="$STATE_FILE" python3 -c "
import json, os, datetime
f = os.environ['RALPH_STATE_FILE']
s = json.load(open(f))
s['active'] = False
s['completed_at'] = datetime.datetime.now().isoformat()
s['status'] = 'max_iterations_reached'
json.dump(s, open(f, 'w'), indent=2, ensure_ascii=False)
" 2>/dev/null
  echo '{"decision":"approve"}'
  exit 0
fi

# 반복 증가
NEW_ITER=$((ITERATION + 1))
RALPH_STATE_FILE="$STATE_FILE" RALPH_NEW_ITER="$NEW_ITER" python3 -c "
import json, os, datetime
f = os.environ['RALPH_STATE_FILE']
s = json.load(open(f))
s['iteration'] = int(os.environ['RALPH_NEW_ITER'])
s['last_iteration_at'] = datetime.datetime.now().isoformat()
json.dump(s, open(f, 'w'), indent=2, ensure_ascii=False)
" 2>/dev/null

# 팀원 정보 수집
TEAMMATES_FILE="${STATE_DIR}/teammates.json"
TEAMMATE_INSTRUCTION=""
if [ -f "$TEAMMATES_FILE" ]; then
  TEAMMATE_INFO=$(RALPH_TEAMMATES="$TEAMMATES_FILE" python3 -c "
import json, os
try:
    f = os.environ['RALPH_TEAMMATES']
    data = json.load(open(f))
    running = {k: v for k,v in data.get('teammates',{}).items() if v.get('status')=='running'}
    if running:
        labels = [v.get('name', k) for k,v in running.items()]
        names = ', '.join(labels)
        print(f'\n⚡ 활성 팀원: {names} — SendMessage(to=이름)로 재사용. 새 Agent() 금지.')
    else:
        print('')
except (json.JSONDecodeError, OSError, KeyError):
    print('')
" 2>/dev/null || echo "")
  TEAMMATE_INSTRUCTION="$TEAMMATE_INFO"
fi

# 연속 프롬프트 주입
CONTINUATION="[Ralph Loop ${NEW_ITER}/${MAX_ITER}] ${PROMPT}${TEAMMATE_INSTRUCTION}
완료 시 <promise>${COMPLETION}</promise> 출력."

PROMPT_TMP="${STATE_DIR}/.inject_prompt.tmp"
printf '%s' "$CONTINUATION" > "$PROMPT_TMP"
ESCAPED_PROMPT=$(RALPH_TMP="$PROMPT_TMP" python3 -c "
import json, os
with open(os.environ['RALPH_TMP']) as f:
    print(json.dumps(f.read()))
" 2>/dev/null || echo "\"Continue\"")
rm -f "$PROMPT_TMP"

echo "{\"decision\":\"block\",\"reason\":\"Ralph Loop 계속\",\"inject_prompt\":${ESCAPED_PROMPT}}"
