"""
① DataLoader — 파이프라인 1단계
역할: 문제 데이터(JSONL)를 읽어서 표준 Problem 객체 리스트로 변환
"""

import json
from dataclasses import dataclass, field
from pathlib import Path


@dataclass
class Problem:
    """
    표준 문제 객체.
    ※ 필드는 평가 목적에 따라 자유롭게 확장 가능.
    예) SQL 평가라면 'schema' 필드 추가, 파일 처리라면 'input_files' 필드 추가.
    """
    id: str
    description: str
    function_signature: str        # ※ 예시 필드 — 코딩 외 평가 시 다른 필드로 교체
    unit_tests: list[str]          # ※ 예시 필드 — 자동 채점 방식에 따라 교체
    tags: list[str] = field(default_factory=list)


def load_problems(path: str) -> list[Problem]:
    """
    JSONL 파일을 읽어 Problem 객체 리스트를 반환.
    한 줄 = 한 문제.
    """
    problems = []
    with open(path, "r", encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            # 주석 줄 또는 빈 줄 건너뜀
            if not line or line.startswith("#"):
                continue
            data = json.loads(line)
            problems.append(Problem(**data))
    return problems
