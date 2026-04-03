"""
① DataLoader — 파이프라인 1단계
역할: 문제 데이터(JSONL)를 읽어서 표준 Problem / WebProblem 객체 리스트로 변환

[week1] Problem       — 코드 생성 평가용 (function_signature + unit_tests)
[week2] WebProblem    — 웹/앱 서비스 평가용 (endpoint + method + test_cases)
"""

import json
from dataclasses import dataclass, field
from pathlib import Path


# ─── Week1: 코드 평가용 ──────────────────────────────────────────────────

@dataclass
class Problem:
    """
    코드 생성 평가용 표준 문제 객체 (week1 호환).
    ※ SQL 평가라면 'schema' 필드 추가, 파일 처리라면 'input_files' 필드 추가.
    """
    id: str
    description: str
    function_signature: str
    unit_tests: list[str]
    tags: list[str] = field(default_factory=list)


# ─── Week2: 웹/앱 평가용 ─────────────────────────────────────────────────

@dataclass
class TestCase:
    """
    웹 평가용 단일 테스트 케이스.
    하나의 HTTP 요청 → 예상 응답을 정의.
    """
    expected_status: int = 200
    request_params: dict = field(default_factory=dict)   # query string
    request_body: dict | None = None                      # JSON body (POST/PUT)
    request_headers: dict = field(default_factory=dict)   # 요청 헤더
    expected_schema: dict | None = None                   # JSON Schema 검증 대상
    expected_response: dict | None = None                 # 완전 일치 검사 (선택)


@dataclass
class WebProblem:
    """
    웹/앱 서비스 평가용 표준 문제 객체.
    ※ REST API 엔드포인트 구현을 평가 대상으로 함.
    ※ framework 필드로 FastAPI / Flask 분기 가능.
    """
    id: str
    description: str
    endpoint: str               # 예: "/users/{user_id}"
    method: str                 # "GET" | "POST" | "PUT" | "DELETE" | "PATCH"
    framework: str              # "fastapi" | "flask"
    test_cases: list[TestCase]
    function_signature: str = ""   # 코드 힌트 (선택)
    tags: list[str] = field(default_factory=list)


# ─── 로더 함수 ────────────────────────────────────────────────────────────

def load_problems(path: str) -> list[Problem]:
    """JSONL 파일에서 코드 평가 문제 로드 (week1 호환)."""
    problems = []
    with open(path, "r", encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if not line or line.startswith("#"):
                continue
            data = json.loads(line)
            problems.append(Problem(**data))
    return problems


def load_web_problems(path: str) -> list[WebProblem]:
    """
    JSONL 파일에서 웹/앱 평가 문제 로드.
    test_cases 배열을 TestCase 객체로 자동 변환.
    """
    problems = []
    with open(path, "r", encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if not line or line.startswith("#"):
                continue
            data = json.loads(line)
            test_cases = [TestCase(**tc) for tc in data.pop("test_cases", [])]
            problems.append(WebProblem(test_cases=test_cases, **data))
    return problems
