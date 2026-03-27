#!/bin/bash
# SubagentStart Hook — 서브에이전트 스폰 시 추적
# stdin JSON에서 agent_id를 읽어 teammates.json에 등록
#
# 핵심: agent_name은 stdin에 포함되지 않으므로 agent_id를 키로 등록.
#       오케스트레이터가 스폰 후 이름을 매핑해야 한다.
#
# Author: kimjaehyun
# Date: 2026-03-28

set -euo pipefail

INPUT=$(cat)

AGENT_ID=$(echo "$INPUT" | python3 -c "import sys,json; print(json.load(sys.stdin).get('agent_id',''))" 2>/dev/null || echo "")
AGENT_TYPE=$(echo "$INPUT" | python3 -c "import sys,json; print(json.load(sys.stdin).get('agent_type',''))" 2>/dev/null || echo "")
CWD=$(echo "$INPUT" | python3 -c "import sys,json; print(json.load(sys.stdin).get('cwd',''))" 2>/dev/null || echo "$(pwd)")
TIMESTAMP=$(date -u +"%Y-%m-%dT%H:%M:%S")

# AUDIT.log 기록
AUDIT_LOG="${CWD}/AUDIT.log"
if [ -f "$AUDIT_LOG" ]; then
  echo "[$TIMESTAMP] system SUBAGENT_START ${AGENT_ID} (${AGENT_TYPE})" >> "$AUDIT_LOG"
fi

# 활성 에이전트 추적
TRACKER="${CWD}/.active-agents"
echo "${AGENT_ID}:${AGENT_TYPE}:${TIMESTAMP}" >> "$TRACKER" 2>/dev/null || true
ACTIVE_COUNT=$(wc -l < "$TRACKER" 2>/dev/null | tr -d ' ' || echo "0")
if [ "$ACTIVE_COUNT" -ge 5 ]; then
  echo "⚠️ 활성 에이전트 ${ACTIVE_COUNT}개 — 리소스 과부하 주의" >&2
fi

# teammates.json에 등록 (flock으로 동시 쓰기 보호)
RALPH_DIR="${CWD}/.ralph-loop"
TEAMMATES_FILE="${RALPH_DIR}/teammates.json"

if [ -d "$RALPH_DIR" ]; then
  (
    flock -w 5 200 || exit 0
    RALPH_AGENT_ID="${AGENT_ID}" RALPH_AGENT_TYPE="${AGENT_TYPE}" RALPH_TEAMMATES="${TEAMMATES_FILE}" python3 -c "
import json, os, datetime

agent_id = os.environ.get('RALPH_AGENT_ID', '')
agent_type = os.environ.get('RALPH_AGENT_TYPE', '')
timestamp = datetime.datetime.utcnow().strftime('%Y-%m-%dT%H:%M:%S')
f = os.environ['RALPH_TEAMMATES']

if os.path.exists(f):
    try: data = json.load(open(f))
    except (json.JSONDecodeError, FileNotFoundError): data = {'teammates': {}}
else:
    data = {'teammates': {}}

data['teammates'][agent_id] = {
    'id': agent_id, 'type': agent_type, 'status': 'running',
    'started_at': timestamp, 'last_seen': timestamp
}
json.dump(data, open(f, 'w'), indent=2, ensure_ascii=False)
" 2>/dev/null || true
  ) 200>"${TEAMMATES_FILE}.lock"
fi

exit 0
