# QUALITY_SCORE.md — Flutter 하네스 품질 루브릭

> 하네스가 LLM 생성 Dart/Flutter 코드를 평가하는 기준과 점수 체계를 정의합니다.

## 채점 구조 — 3축 가중 평균

| 축 | 기본 가중치 | 측정 대상 | 산출 방식 |
|:---|:---:|:---|:---|
| **test_score** | 0.4 | flutter test 통과율 | `통과한 테스트 수 / 전체 테스트 수` |
| **lint_score** | 0.3 | dart analyze 정적 분석 | `1.0 - (심각도별 감점 합)` |
| **security_score** | 0.3 | Dart/Flutter 보안 정적 검사 | `1.0 - (심각도별 감점 합)` |

**총점 공식**:
```
총점 = (0.4 × test_score) + (0.3 × lint_score) + (0.3 × security_score)
```

가중치는 `config.yaml` > `flutter.score_weights`에서 조정 가능.

## 각 축의 세부 기준

### 1. Test Score — 기능 정확성 (가중치 0.4)

`flutter test --machine`의 JSON 결과를 파싱하여 산출.

#### Widget Mode 테스트 유형

| 테스트 패턴 | 검증 대상 | 예시 |
|:---|:---|:---|
| 초기 렌더링 | 위젯이 올바르게 그려지는가 | `expect(find.text('0'), findsOneWidget)` |
| 사용자 상호작용 | 탭/입력 후 상태가 바뀌는가 | `tester.tap()` → `expect(find.text('1'))` |
| 위젯 트리 구조 | 필요한 위젯이 존재하는가 | `expect(find.byType(TextField), findsOneWidget)` |

#### Logic Mode 테스트 유형

| 테스트 패턴 | 검증 대상 | 예시 |
|:---|:---|:---|
| 정상 입력 | 올바른 반환값 | `expect(findLongest(['a', 'bb']), equals('bb'))` |
| 경계 입력 | 빈 리스트, 단일 원소 | `expect(findLongest([]), equals(''))` |
| 동점 처리 | 동일 조건 시 우선순위 | `expect(findLongest(['abc', 'def']), equals('abc'))` |

### 2. Lint Score — 코드 품질 (가중치 0.3)

`dart analyze`의 출력을 파싱하여 감점 방식으로 산출.

| 심각도 | 감점 | 의미 | 예시 |
|:---:|:---:|:---|:---|
| **error** | -0.3 | 컴파일 오류 수준 | 미정의 변수, 타입 불일치 |
| **warning** | -0.1 | 잠재적 문제 | 미사용 import, null 안전성 위반 |
| **info** | -0.02 | 스타일 권고 | const 생성자 미사용, 명명 규칙 |

- 이슈 없음 = 1.0점
- error 1개 = 0.7점, error 2개 = 0.4점
- warning 3개 = 0.7점
- 최소 0.0점

### 3. Security Score — 보안 (가중치 0.3)

Dart/Flutter 코드에 대한 정규식 기반 정적 분석.

| 심각도 | 감점 | 예시 |
|:---:|:---:|:---|
| **HIGH** | -0.4 | 하드코딩 시크릿, Process.run, HTTP URL, sleep() |
| **MEDIUM** | -0.2 | print() 남용, async setState |
| **LOW** | -0.05 | SSL 검증 비활성화, TODO 잔존 |

- 이슈 없음 = 1.0점
- HIGH 1개 = 0.6점, HIGH 2개 = 0.2점, HIGH 3개 이상 = 0.0점
- 최소 0.0점

상세 규칙은 **SECURITY.md** 참조.

## 0점 처리 조건

| 상황 | 처리 |
|:---|:---|
| Flutter SDK를 찾을 수 없음 | setup_error → 전체 0점 |
| template_project 디렉토리 없음 | setup_error → 전체 0점 |
| flutter pub get 실패 | setup_error → 전체 0점 |
| 코드 컴파일 오류 (빌드 실패) | build_error → 전체 0점 |
| 타임아웃 (기본 120초 초과) | timed_out → 전체 0점 |

## 결과 저장 형식

채점 결과는 `results/run_YYYYMMDD_HHMMSS.jsonl`에 JSONL로 저장된다.

각 줄의 필드:
```json
{
  "id": "flutter_001",
  "timestamp": "2026-04-16T14:30:00",
  "generated_code": "import 'package:flutter/material.dart'; ...",
  "score": 0.85,
  "test_score": 1.0,
  "lint_score": 0.8,
  "security_score": 0.7,
  "total_tests": 3,
  "passed_tests": 3,
  "lint_errors": 0,
  "lint_warnings": 2,
  "timed_out": false,
  "setup_error": null,
  "build_error": null,
  "security_issues": [{"severity": "MEDIUM", "rule": "DEBUG_PRINT", "message": "...", "line": 5}],
  "lint_details": [{"severity": "warning", "rule": "unused_import", "message": "...", "line": 2}]
}
```

## 품질 등급 해석 가이드

| 총점 범위 | 등급 | 의미 |
|:---:|:---:|:---|
| 0.95 ~ 1.00 | A | 완벽 — 테스트 전통과, 린트 깨끗, 보안 이슈 없음 |
| 0.80 ~ 0.94 | B | 양호 — 경미한 린트 이슈 또는 보안 권고 존재 |
| 0.60 ~ 0.79 | C | 보통 — 일부 테스트 실패 또는 보안 이슈 |
| 0.40 ~ 0.59 | D | 미흡 — 다수 테스트 실패 또는 HIGH 보안 이슈 |
| 0.00 ~ 0.39 | F | 실패 — 빌드 오류, 타임아웃, 또는 심각한 결함 |
