# SECURITY.md — Dart/Flutter 보안 규칙

> 하네스가 LLM 생성 Dart/Flutter 코드를 보안 관점에서 검사하는 규칙과 프로젝트 전반의 보안 원칙을 정의합니다.

## 1. API 키 및 시크릿 관리

| 규칙 | 설명 |
|:---|:---|
| 환경변수만 사용 | API 키는 `config.yaml`의 `api_key_env`에 환경변수 **이름**만 기재 |
| 코드 내 하드코딩 금지 | `apiKey = '...'`, `password = '...'` 패턴은 HIGH로 탐지 |
| --dart-define 활용 | Flutter 앱 빌드 시 `--dart-define=API_KEY=xxx`로 시크릿 전달 |
| .gitignore 필수 | `.env`, `*.key`, `credentials.*`, `*.jks` (키스토어) 등 gitignore |
| results/ 주의 | 결과 JSONL에 `generated_code`가 포함되므로 시크릿이 생성 코드에 있으면 로그에도 남음 |

## 2. 정적 보안 분석 규칙 (validators/security.py)

### HIGH 심각도 (감점 -0.4)

| 규칙 ID | 탐지 패턴 | 위험 | 대안 |
|:---|:---|:---|:---|
| `HARDCODED_SECRET` | `password/secret/apiKey/token = '...'` | 시크릿 유출 | 환경변수, `--dart-define`, 시크릿 매니저 |
| `PROCESS_RUN` | `Process.run(...)` | 커맨드 인젝션 | 사용자 입력을 직접 전달하지 않기 |
| `DART_MIRRORS` | `import 'dart:mirrors'` | 리플렉션 보안 위험 + Flutter 비호환 | 코드 생성 또는 직접 구현 |
| `HTTP_NOT_HTTPS` | `'http://...'` (localhost 제외) | 평문 통신, Android 9+ 차단 | HTTPS 사용 |
| `BLOCKING_SLEEP` | `sleep(Duration(...))` | UI 스레드 블로킹 → ANR | `Future.delayed()` 사용 |

### MEDIUM 심각도 (감점 -0.2)

| 규칙 ID | 탐지 패턴 | 위험 | 대안 |
|:---|:---|:---|:---|
| `DEBUG_PRINT` | `print()` / `debugPrint()` | 민감 정보 콘솔 출력 | `logger` 패키지 사용, 프로덕션에서 제거 |
| `ASYNC_SET_STATE` | `setState(() async { ... await ... })` | dispose 후 setState 호출 → crash | `mounted` 체크 또는 상태 관리 패턴 사용 |
| `CORS_WILDCARD` | `Access-Control-Allow-Origin: *` | 무제한 교차 출처 허용 | 허용 도메인 명시적 지정 |

### LOW 심각도 (감점 -0.05)

| 규칙 ID | 탐지 패턴 | 위험 | 대안 |
|:---|:---|:---|:---|
| `SSL_VERIFY_DISABLED` | `badCertificateCallback => true` | 중간자 공격 가능 | 프로덕션에서 인증서 검증 활성화 |
| `TODO_REMAINING` | `// TODO` | 미완성 구현 가능성 | 구현 완료 후 TODO 제거 |

## 3. Flutter/Android 특화 보안 고려사항

### 네트워크 보안

| 항목 | Android 기본 동작 | 권장 |
|:---|:---|:---|
| HTTP 평문 통신 | Android 9+ 기본 차단 | HTTPS만 사용 |
| 인증서 고정 | 미적용 | Certificate Pinning 적용 |
| 네트워크 보안 설정 | 기본값 | `network_security_config.xml` 설정 |

### 데이터 저장

| 저장소 | 보안 수준 | 용도 |
|:---|:---:|:---|
| SharedPreferences | 낮음 | 비민감 설정값만 |
| flutter_secure_storage | 높음 | 토큰, 인증 정보 |
| SQLite (sqflite) | 중간 | 암호화 옵션 사용 권장 |
| 파일 시스템 | 낮음 | getApplicationDocumentsDirectory() 사용 |

### 입력 검증

| 항목 | 위험 | 대안 |
|:---|:---|:---|
| 사용자 입력 미검증 | XSS, 인젝션 | TextField 입력값 검증/새니타이징 |
| Deep Link 파라미터 | 악의적 URL 주입 | 파라미터 화이트리스트 검증 |
| Intent 데이터 (Android) | 악성 앱의 데이터 전달 | 수신 데이터 타입/범위 검증 |

## 4. 샌드박스 보안 경계

### Python → Flutter CLI 호출

| 조치 | 설명 |
|:---|:---|
| 임시 디렉토리 격리 | `tempfile.mkdtemp()`로 생성, 실행 후 `shutil.rmtree()`로 삭제 |
| subprocess 타임아웃 | `timeout` 인자로 무한 실행 방어 |
| shell=False | 셸 인젝션 방지 (리스트 형태 인자 전달) |
| 결과만 파싱 | stdout/stderr 텍스트만 읽고 임의 코드 실행 없음 |

### exec() 미사용

이전 Python 하네스와 달리, Flutter 하네스는 `exec()`를 사용하지 않는다.
LLM 생성 코드는 `.dart` 파일로 저장되고 Flutter SDK를 통해 실행된다.
Python 프로세스 자체의 네임스페이스는 오염되지 않는다.

## 5. 보안 규칙 추가 방법

`harness/harness/validators/security.py`의 `_RULES` 리스트에 튜플을 추가:

```python
_RULES.append((
    r'패턴 정규식',       # 탐지할 Dart 코드 패턴
    "HIGH",              # 심각도: HIGH | MEDIUM | LOW
    "RULE_ID",           # 고유 규칙 ID
    "사람이 읽을 메시지",  # 탐지 시 출력할 메시지
))
```

## 6. 보안 체크리스트

코드 리뷰 또는 새 기능 추가 시 확인:

- [ ] API 키가 코드/config에 하드코딩되어 있지 않은가?
- [ ] HTTP 대신 HTTPS를 사용하고 있는가?
- [ ] 사용자 입력이 검증/새니타이징되고 있는가?
- [ ] 민감 데이터가 SharedPreferences가 아닌 secure_storage에 저장되는가?
- [ ] print()/debugPrint()에 민감 정보가 출력되지 않는가?
- [ ] setState() 호출 전 mounted 체크가 되어 있는가?
- [ ] 새 보안 규칙이 필요한 Dart 패턴이 발견되었는가?
