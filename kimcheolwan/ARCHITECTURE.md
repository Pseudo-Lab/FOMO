# ARCHITECTURE.md — Flutter 평가 하네스 구조

## 디렉토리 맵

```
kimcheolwan/
├── CLAUDE.md                          # 진입 가이드 (먼저 읽을 것)
├── ARCHITECTURE.md                    # ← 이 파일 (구조 설명)
├── QUALITY_SCORE.md                   # 품질 루브릭
├── SECURITY.md                        # Dart/Flutter 보안 규칙
├── README.md                          # 개인 KMS 소개
├── harness_guide.md                   # 하네스 상세 해설 (참고용)
│
├── harness/                           # 평가 하네스 루트
│   ├── config.yaml                    # 전체 설정 (mode, llm, sandbox, flutter)
│   ├── run.py                         # 엔트리포인트
│   ├── requirements.txt               # Python 의존성
│   ├── data/
│   │   └── flutter_problems.jsonl     # Flutter/Dart 평가 문제
│   ├── results/                       # 채점 결과 (자동 생성)
│   ├── template_project/              # Flutter 테스트용 템플릿 프로젝트
│   │   ├── pubspec.yaml               # package: harness_eval
│   │   ├── lib/                       # solution.dart가 여기에 저장됨
│   │   └── test/                      # solution_test.dart가 여기에 저장됨
│   └── harness/                       # 파이프라인 패키지
│       ├── __init__.py
│       ├── loader.py                  # ① DataLoader
│       ├── llm_client.py              # ② LLMClient
│       ├── sandbox.py                 # ③ FlutterSandbox
│       ├── scorer.py                  # ④ Scorer / Logger
│       └── validators/
│           ├── __init__.py
│           └── security.py            # Dart/Flutter 정적 보안 검사
│
├── docs/                              # 상세 지식 저장소
│   ├── design-docs/
│   ├── product-specs/
│   ├── references/
│   └── exec-plans/
│
└── weekly/                            # 주차별 학습 기록
    ├── week1.md
    └── week2.md
```

## 파이프라인 흐름

widget / logic 두 모드 모두 동일한 4단계 파이프라인을 따른다.

```
┌─────────────────────────────────────────────────────────────────┐
│  config.yaml                                                     │
│  ┌────────────────┐                                              │
│  │ mode           │──→ "widget" 또는 "logic"                    │
│  │ llm            │──→ provider, model, api_key_env             │
│  │ sandbox        │──→ timeout_sec, pub_get_timeout_sec         │
│  │ flutter        │──→ sdk_path, template_project, score_weights│
│  └────────────────┘                                              │
└──────────┬──────────────────────────────────────────────────────┘
           │
           ▼
┌──── run.py (엔트리포인트) ────┐
│  main() → run_flutter()      │
│  mode로 문제 필터링           │
└──────────┬───────────────────┘
           │
           ▼
① loader.py ─── load_flutter_problems()
   FlutterProblem (id, description, mode, test_code, widget_name/function_name)
           │
           ▼
② llm_client.py ─── generate_flutter_code()
   ├── [widget] build_widget_prompt() → Dart 위젯 코드
   └── [logic]  build_logic_prompt()  → Dart 함수 코드
   → call_llm() → _extract_dart_block()
           │
           ▼
③ sandbox.py ─── execute_flutter()
   ┌─────────────────────────────────────────────┐
   │ 1. template_project/ → 임시 디렉토리 복사    │
   │ 2. lib/solution.dart ← LLM 생성 코드 저장    │
   │ 3. test/solution_test.dart ← 테스트 코드 저장 │
   │ 4. flutter pub get                            │
   │ 5. flutter test --machine → 결과 JSON 파싱    │
   │ 6. dart analyze → 린트 이슈 파싱              │
   │ 7. 임시 디렉토리 정리                          │
   └─────────────────────────────────────────────┘
   → FlutterExecutionResult (test_results + lint_issues)
           │
           ▼
④ scorer.py ─── score_flutter()
   ├── test_score     (0.4) ← flutter test 통과율
   ├── lint_score     (0.3) ← dart analyze 감점
   └── security_score (0.3) ← validators/security.py 정적 분석
   → log_result() → results/run_YYYYMMDD_HHMMSS.jsonl
   → print_summary()
```

## 모듈 의존 관계

```
run.py
 ├── loader.py         (FlutterProblem, load_flutter_problems)
 ├── llm_client.py     (generate_flutter_code)
 │    └── loader.py    (FlutterProblem 타입 참조)
 ├── sandbox.py        (execute_flutter)
 │    [외부] flutter CLI, dart CLI — subprocess로 호출
 └── scorer.py         (score_flutter, log_result, print_summary)
      └── sandbox.py              (FlutterExecutionResult 타입 참조)
      └── validators/security.py  (check_security)
```

## 데이터 흐름 요약

| 단계 | 입력 | 출력 | 핵심 로직 |
|:---:|:---:|:---:|:---|
| ① Loader | JSONL 파일 | `FlutterProblem` 리스트 | JSON 파싱 + dataclass 변환 |
| ② LLMClient | FlutterProblem + config | Dart 코드 문자열 | 프롬프트 구성 → API 호출 → ```dart``` 블록 추출 |
| ③ Sandbox | 코드 + 테스트 | `FlutterExecutionResult` | 임시 프로젝트 생성 → flutter test → dart analyze |
| ④ Scorer | 실행 결과 + 코드 | 점수 dict + JSONL 로그 | 3축 가중 평균 + 보안 분석 |

## Python ↔ Flutter SDK 경계

```
┌─ Python 프로세스 (하네스) ──────────┐     ┌─ Flutter SDK (외부) ─────────┐
│                                      │     │                              │
│  loader.py   → 문제 로드             │     │                              │
│  llm_client.py → LLM API 호출       │     │                              │
│  sandbox.py  → 임시 프로젝트 조립    │────→│  flutter pub get             │
│              → subprocess 호출       │────→│  flutter test --machine      │
│              → 결과 JSON 파싱       │←────│  (JSON 이벤트 스트림 출력)    │
│              → subprocess 호출       │────→│  dart analyze                │
│              → 린트 출력 파싱        │←────│  (텍스트 출력)               │
│  scorer.py   → 채점 + 로깅          │     │                              │
│                                      │     │                              │
└──────────────────────────────────────┘     └──────────────────────────────┘
```

## 설계 결정 사항

| 결정 | 이유 |
|:---|:---|
| subprocess로 Flutter CLI 호출 | Python에서 Dart를 직접 실행할 수 없음 — CLI가 유일한 인터페이스 |
| 임시 디렉토리에 프로젝트 복사 | 원본 template_project를 오염시키지 않기 위해 |
| `flutter test --machine` 사용 | JSON 이벤트 스트림으로 테스트 결과를 정확하게 파싱 가능 |
| `dart analyze` 사용 | Flutter 공식 정적 분석 도구, lint 규칙 자동 적용 |
| 보안 검사를 별도 정규식으로 수행 | dart analyze는 보안 취약점을 직접 탐지하지 않음 |
| timeout 기본 120초 | Flutter 빌드(첫 실행 시 컴파일) + 테스트 실행 시간 필요 |
| package 이름 `harness_eval` 고정 | 테스트 코드의 import 경로와 일치해야 함 |
| Widget 테스트만 지원 (에뮬레이터 불필요) | testWidgets()는 인메모리 실행, 통합 테스트는 환경 의존성이 너무 큼 |

## 확장 포인트

- **새 문제 추가**: `data/flutter_problems.jsonl`에 JSONL 한 줄 추가
- **새 보안 규칙 추가**: `validators/security.py`의 `_RULES` 리스트에 튜플 추가
- **새 LLM provider 추가**: `llm_client.py`에 `_call_<provider>()` 함수 + `call_llm()` 분기
- **패키지 의존성 추가**: `template_project/pubspec.yaml`에 추가 (전체) 또는 문제별 `dependencies` 필드 사용
- **통합 테스트 지원**: `sandbox.py`에 `flutter test integration_test/` 실행 경로 추가 (에뮬레이터 필요)
