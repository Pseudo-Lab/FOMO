"""
③ ExecutionSandbox — 파이프라인 3단계
역할: LLM이 생성한 코드를 안전하게 실행하고 테스트 결과를 반환

[week1] CodeSandbox  — exec() + namespace isolation + timeout
[week2] WebSandbox   — FastAPI TestClient + HTTP 수준 요청/응답 검증

[보안 고려사항]
- 타임아웃: threading.Timer로 무한 루프 방어
- 네임스페이스 격리 (코드 모드): exec()에 제한된 __builtins__ 전달
- 예외 흡수: 런타임 에러가 전체 파이프라인을 중단시키지 않도록 처리
"""

import threading
from dataclasses import dataclass, field

from harness.loader import TestCase


# ─── 공통: 타임아웃 래퍼 ─────────────────────────────────────────────────

def run_with_timeout(fn, timeout_sec: int) -> dict:
    """timeout_sec 초 내에 fn()이 완료되지 않으면 timed_out=True 반환."""
    result: dict = {"value": None, "timed_out": False}

    def target():
        result["value"] = fn()

    thread = threading.Thread(target=target, daemon=True)
    thread.start()
    thread.join(timeout=timeout_sec)

    if thread.is_alive():
        result["timed_out"] = True

    return result


# ─── Week1: 코드 실행 결과 ────────────────────────────────────────────────

@dataclass
class ExecutionResult:
    """코드 유닛 테스트 실행 결과."""
    passed: int
    failed: int
    errors: list[str]
    timed_out: bool = False


# ─── Week2: 웹 실행 결과 ──────────────────────────────────────────────────

@dataclass
class WebTestResult:
    """단일 HTTP 테스트 케이스 실행 결과."""
    test_index: int
    expected_status: int
    actual_status: int | None
    status_matched: bool
    schema_valid: bool
    response_body: dict | None = None
    error: str | None = None


@dataclass
class WebExecutionResult:
    """전체 웹 실행 결과 (n개 테스트 케이스 집합)."""
    test_results: list[WebTestResult] = field(default_factory=list)
    setup_error: str | None = None
    timed_out: bool = False


# ─── Week1: 코드 실행 샌드박스 ───────────────────────────────────────────

def execute(
    generated_code: str,
    unit_tests: list[str],
    timeout_sec: int = 5,
) -> ExecutionResult:
    """
    생성된 파이썬 코드 + 유닛 테스트를 격리된 네임스페이스에서 실행.

    ※ safe_globals의 __builtins__는 허용 목록 방식 — 위험한 빌트인 차단.
    ※ 평가 목적에 따라 허용 빌트인 추가 가능 (예: "open": open).
    """
    passed = 0
    failed = 0
    errors: list[str] = []

    safe_globals = {
        "__builtins__": {
            "len": len, "range": range, "print": print,
            "int": int, "str": str, "float": float,
            "list": list, "dict": dict, "tuple": tuple,
            "bool": bool, "None": None, "True": True, "False": False,
            "enumerate": enumerate, "zip": zip, "map": map,
            "min": min, "max": max, "sum": sum, "sorted": sorted,
        }
    }
    local_ns: dict = {}

    def _run():
        nonlocal passed, failed, errors

        # 1. 생성된 코드 실행 (함수 정의)
        try:
            exec(generated_code, safe_globals, local_ns)
        except Exception as e:
            errors.append(f"[코드 실행 오류] {type(e).__name__}: {e}")
            return

        # 2. 유닛 테스트 순차 실행
        for test in unit_tests:
            try:
                exec(test, safe_globals, local_ns)
                passed += 1
            except AssertionError:
                failed += 1
                errors.append(f"[실패] {test}")
            except Exception as e:
                failed += 1
                errors.append(f"[에러] {test} → {type(e).__name__}: {e}")

    result = run_with_timeout(_run, timeout_sec)
    if result["timed_out"]:
        return ExecutionResult(
            passed=0, failed=len(unit_tests),
            errors=["[타임아웃] 실행 시간 초과"], timed_out=True,
        )
    return ExecutionResult(passed=passed, failed=failed, errors=errors)


# ─── Week2: 웹 실행 샌드박스 ─────────────────────────────────────────────

def execute_web(
    generated_code: str,
    test_cases: list[TestCase],
    endpoint: str,
    method: str,
    timeout_sec: int = 5,
) -> WebExecutionResult:
    """
    FastAPI TestClient를 이용해 생성된 웹 코드를 HTTP 수준으로 테스트.

    실행 전략:
    1. 생성된 코드를 exec()로 실행 → `app` 변수(FastAPI 인스턴스) 추출
    2. TestClient(app)로 각 test_case를 요청
    3. 상태 코드 일치 + 응답 JSON Schema 검증
    """
    from harness.validators.schema import validate_schema

    def _run() -> WebExecutionResult:
        # 1. 코드 실행 → app 객체 추출
        namespace: dict = {}
        try:
            exec(generated_code, namespace)
        except Exception as e:
            return WebExecutionResult(
                setup_error=f"[코드 실행 오류] {type(e).__name__}: {e}",
            )

        app = namespace.get("app")
        if app is None:
            return WebExecutionResult(
                setup_error="[설정 오류] 생성된 코드에 `app` 변수가 없습니다. "
                            "(예: app = FastAPI())",
            )

        # 2. TestClient 생성
        try:
            from fastapi.testclient import TestClient
            client = TestClient(app, raise_server_exceptions=False)
        except ImportError:
            return WebExecutionResult(
                setup_error="[환경 오류] fastapi / httpx 패키지가 필요합니다: "
                            "pip install fastapi httpx",
            )

        # 3. 테스트 케이스 순차 실행
        results: list[WebTestResult] = []
        for i, tc in enumerate(test_cases):
            try:
                response = _make_request(client, method, endpoint, tc)
                actual_status = response.status_code
                status_matched = actual_status == tc.expected_status

                response_body = None
                schema_valid = True
                try:
                    response_body = response.json()
                    if tc.expected_schema:
                        schema_valid = validate_schema(response_body, tc.expected_schema)
                except Exception:
                    schema_valid = False

                results.append(WebTestResult(
                    test_index=i,
                    expected_status=tc.expected_status,
                    actual_status=actual_status,
                    status_matched=status_matched,
                    schema_valid=schema_valid,
                    response_body=response_body,
                ))
            except Exception as e:
                results.append(WebTestResult(
                    test_index=i,
                    expected_status=tc.expected_status,
                    actual_status=None,
                    status_matched=False,
                    schema_valid=False,
                    error=f"{type(e).__name__}: {e}",
                ))

        return WebExecutionResult(test_results=results)

    timeout_result = run_with_timeout(_run, timeout_sec)
    if timeout_result["timed_out"]:
        return WebExecutionResult(timed_out=True)

    return timeout_result["value"] or WebExecutionResult(
        setup_error="알 수 없는 실행 오류",
    )


def _make_request(client, method: str, endpoint: str, tc: TestCase):
    """TestCase 기반 HTTP 요청 수행."""
    kwargs: dict = {}
    if tc.request_params:
        kwargs["params"] = tc.request_params
    if tc.request_headers:
        kwargs["headers"] = tc.request_headers
    if tc.request_body is not None:
        kwargs["json"] = tc.request_body

    method_fn = {
        "GET":    client.get,
        "POST":   client.post,
        "PUT":    client.put,
        "DELETE": client.delete,
        "PATCH":  client.patch,
    }.get(method.upper(), client.get)

    return method_fn(endpoint, **kwargs)
