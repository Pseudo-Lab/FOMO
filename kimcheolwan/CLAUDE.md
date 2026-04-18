# CLAUDE.md — Flutter 평가 하네스 진입점

> 이 파일은 Claude Code가 프로젝트를 빠르게 파악하기 위한 진입 가이드입니다.
> 상세 문서는 `docs/` 하위 폴더에 있습니다.

## 먼저 읽을 것

1. **ARCHITECTURE.md** — 전체 구조와 모듈 간 관계
2. **harness/config.yaml** — 실행 설정 (mode, LLM provider, 가중치)
3. **harness/run.py** — 엔트리포인트, 파이프라인 흐름 파악

## 핵심 파이프라인

```
config.yaml → run.py → ① loader.py → ② llm_client.py → ③ sandbox.py → ④ scorer.py
```

- `mode: "widget"` → Flutter 위젯 테스트 평가 (testWidgets)
- `mode: "logic"` → Dart 순수 함수 테스트 평가 (test)

## 실행 방법

```bash
cd harness
pip install -r requirements.txt
python run.py
```

### 전제 조건

- **Flutter SDK** 설치 필수 (`flutter`, `dart` 명령어가 PATH에 있어야 함)
- API 키는 환경변수로 설정 (`ANTHROPIC_API_KEY` 또는 `OPENAI_API_KEY`)
- config.yaml의 `llm.api_key_env`에 환경변수 이름만 기입

## 피해야 할 것

- **API 키를 코드나 config에 직접 기입하지 말 것** — 반드시 환경변수 사용
- **template_project/pubspec.yaml의 패키지 이름을 변경하지 말 것** — 테스트 코드의 import 경로(`package:harness_eval/solution.dart`)와 일치해야 함
- **LLM 생성 코드에 main() 또는 runApp()을 포함시키지 말 것** — 테스트 실행을 방해함
- **results/ 디렉토리의 기존 결과 파일을 덮어쓰지 말 것** — 실행별 비교를 위해 타임스탬프 기반 자동 생성
- **sandbox timeout을 30초 미만으로 설정하지 말 것** — Flutter 빌드에 시간이 필요함

## 품질 및 보안 기준

- **QUALITY_SCORE.md** — 채점 루브릭과 품질 기준 (test/lint/security 3축)
- **SECURITY.md** — Dart/Flutter 보안 규칙과 정적 분석 탐지 항목

## 상세 문서

```
docs/
├── design-docs/      # 설계 문서 (아키텍처 결정, 기술 선택 이유)
├── product-specs/    # 제품 명세 (기능 요구사항, 평가 기준)
├── references/       # 참고 자료 (외부 링크, 논문, 가이드)
└── exec-plans/       # 실행 계획 (주차별 목표, 마일스톤)
```

## 코드 수정 시 주의사항

- 새 문제 추가 시: `data/flutter_problems.jsonl`에 JSONL 한 줄 추가 (test_code에 완전한 Dart 테스트 포함)
- 새 보안 규칙 추가 시: `validators/security.py`의 `_RULES` 리스트에 `(pattern, severity, rule_id, message)` 튜플 추가
- 새 LLM provider 추가 시: `llm_client.py`에 `_call_<provider>()` 함수 + `call_llm()` 분기
- 의존성 패키지 추가 시: `template_project/pubspec.yaml`에 추가 또는 문제 JSONL의 `dependencies` 필드 활용
