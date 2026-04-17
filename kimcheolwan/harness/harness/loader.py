"""
① DataLoader — Flutter 평가 하네스 1단계
역할: 문제 데이터(JSONL)를 읽어서 FlutterProblem 객체 리스트로 변환

[widget] FlutterProblem (mode="widget") — Flutter 위젯 테스트 평가
[logic]  FlutterProblem (mode="logic")  — Dart 순수 로직 테스트 평가
"""

import json
from dataclasses import dataclass, field


@dataclass
class FlutterProblem:
    """
    Flutter/Dart 평가용 표준 문제 객체.

    mode:
      - "widget" → Flutter 위젯 구현 + testWidgets()로 검증
      - "logic"  → Dart 순수 함수 구현 + test()로 검증

    test_code:
      flutter test에 사용할 완전한 Dart 테스트 코드.
      import 'package:harness_eval/solution.dart'; 포함 필수.
    """
    id: str
    description: str
    mode: str                                          # "widget" | "logic"
    test_code: str                                     # 완전한 Dart 테스트 코드
    widget_name: str = ""                              # widget mode: 구현할 위젯 이름
    function_name: str = ""                            # logic mode: 구현할 함수 이름
    dependencies: list[str] = field(default_factory=list)   # 추가 pubspec 의존성
    hint: str = ""                                     # 코드 힌트 (선택)
    tags: list[str] = field(default_factory=list)


def load_flutter_problems(path: str) -> list[FlutterProblem]:
    """JSONL 파일에서 Flutter 평가 문제 로드."""
    problems = []
    with open(path, "r", encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if not line or line.startswith("#"):
                continue
            data = json.loads(line)
            problems.append(FlutterProblem(**data))
    return problems
