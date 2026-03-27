# L2 품질 계층 가이드 (Hooks + Sandbox)

## settings.json이 하는 일

이 파일은 Claude Code의 **물리적 안전장치**입니다.
프롬프트로 "하지 마"라고 하는 건 소프트 가이드(무시 가능)이고,
settings.json은 하드 차단(무시 불가능)입니다.

---

## 설치 위치

```
~/.claude/settings.json    ← 이 위치에 복사
```

---

## 구성 요소

### 1. Sandbox (permissions)

**Allow 리스트** — Claude가 확인 없이 실행할 수 있는 명령어:
- 테스트 실행 (npm test, pytest)
- 린팅 (npm run lint, ruff check)
- Git 기본 명령 (add, commit, push, log, diff, status)
- 파일 읽기/탐색 (ls, cat, grep, find)
- 파일 생성/수정 (Read, Write, Edit)

**Deny 리스트** — 절대 실행 불가능한 명령어:
- rm -rf (재귀적 파일 삭제)
- sudo (관리자 권한 실행)
- chmod 777 (모든 권한 개방)
- curl | bash (원격 스크립트 실행)
- git push --force (강제 푸시)
- git reset --hard (하드 리셋)
- DROP TABLE / DROP DATABASE (DB 삭제)
- 포크 폭탄, 디스크 직접 접근 등

### 2. PreToolUse Hook (도구 실행 직전)

**작동**: Claude가 Bash 명령어를 실행하려 할 때마다 자동 검사.
**차단 대상**: rm -rf, sudo, chmod 777, git push --force, 
  git reset --hard, DROP TABLE, DROP DATABASE.
**결과**: 
- 안전한 명령어 → exit 0 → 실행 허용
- 위험한 명령어 → exit 2 → 물리적 차단 + 경고 메시지

예시:
```
Claude: git push --force origin main
Hook:   BLOCKED: Dangerous command detected — git push --force origin main
→ 실행 안 됨
```

### 3. PreCommit Hook (커밋 직전)

**작동**: git commit 직전에 스테이지된 파일에서 시크릿 스캔.
**탐지 대상**: api_key, api_secret, secret_key, password, token, 
  credential, private_key 패턴이 값과 함께 있는 경우.
**결과**:
- 시크릿 없음 → exit 0 → 커밋 허용
- 시크릿 발견 → exit 2 → 커밋 차단 + 경고

예시:
```
코드에: API_KEY = "sk-abc123..."
Hook:   BLOCKED: Potential secret detected in staged files
→ 커밋 안 됨
```

### 4. PostToolUse Hook (도구 실행 직후)

**작동**: Claude가 파일을 Write/Edit한 후 자동으로 린터 실행.
**동작**:
- .py 파일 수정 시 → ruff check 실행 (설치되어 있으면)
- .ts/.tsx 파일 수정 시 → tsc --noEmit 실행 (설치되어 있으면)
**결과**: exit 0 (항상 통과, 힌트만 제공). 차단하지 않고 피드백만.

---

## 주의사항

- settings.json은 Claude Code 재시작 후 적용됩니다.
- hooks는 OS에 해당 도구가 설치되어 있어야 작동합니다:
  - Python 린팅: `pip install ruff`
  - TypeScript 체크: `npm install -g typescript`
- Windows에서는 bash 명령어가 Git Bash 또는 WSL에서 실행됩니다.
- hooks가 없어도 하네스의 나머지 기능(커맨드, rules)은 정상 작동합니다.

---

## 커스터마이징

### 더 많은 명령어를 허용하려면
settings.json의 `permissions.allow`에 추가:
```json
"Bash(docker *)",
"Bash(pip install*)"
```

### 더 많은 명령어를 차단하려면
settings.json의 `permissions.deny`에 추가:
```json
"Bash(npm publish*)",
"Bash(heroku *)"
```

### Hook을 비활성화하려면
해당 hook 항목을 settings.json에서 삭제하면 됩니다.
