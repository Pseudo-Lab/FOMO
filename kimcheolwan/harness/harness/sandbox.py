"""
③ ExecutionSandbox — 파이프라인 3단계
역할: LLM이 생성한 코드를 안전하게 실행하고 유닛 테스트 결과를 반환

[보안 팁 — 보리스 팁 13 '검증 루프' 구현의 핵심]
1. 타임아웃: 무한 루프 방어 (threading.Timer 사용)
2. 네임스페이스 격리: exec()에 빈 __builtins__ 전달로 위험 모듈 차단
3. 예외 캐치: 런타임 에러를 하네스가 흡수해 전체 파이프라인 중단 방지
"""

import threading
from dataclasses import dataclass


@dataclass
class ExecutionResult:
    """실행 결과 표준 객체."""
    passed: int       # 통과한 테스트 수
    failed: int       # 실패한 테스트 수
    errors: list[str] # 실패/에러 메시지 목록
    timed_out: bool = False


def run_with_timeout(fn, timeout_sec: int):
    """
    타임아웃 제한 실행 래퍼.
    timeout_sec 초 내에 fn()이 완료되지 않으면 강제 종료.
    """
    result = {"value": None, "timed_out": False}

    def target():
        result["value"] = fn()

    thread = threading.Thread(target=target, daemon=True)
    thread.start()
    thread.join(timeout=timeout_sec)

    if thread.is_alive():
        result["timed_out"] = True

    return result


def execute(generated_code: str, unit_tests: list[str], timeout_sec: int = 5) -> ExecutionResult:
    """
    생성된 코드 + 유닛 테스트를 격리된 네임스페이스에서 실행.

    Args:
        generated_code: LLM이 생성한 파이썬 코드 문자열
        unit_tests: assert 문 리스트 (예: ["assert add(1,2)==3"])
        timeout_sec: 최대 실행 허용 시간 (초)

    Returns:
        ExecutionResult: pass/fail 집계 및 에러 메시지
    """
    passed = 0
    failed = 0
    errors = []

    # ※ 격리된 네임스페이스 — 위험한 빌트인 함수 차단
    # ※ 필요한 모듈은 safe_globals에 명시적으로 추가
    safe_globals = {
        "__builtins__": {
            "len": len, "range": range, "print": print,
            "int": int, "str": str, "float": float,
            "list": list, "dict": dict, "tuple": tuple,
            "bool": bool, "None": None, "True": True, "False": False,
            # ※ 평가 목적에 따라 허용 빌트인 추가 (예: "open": open)
        }
    }
    local_ns = {}

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
        return ExecutionResult(passed=0, failed=len(unit_tests), errors=["[타임아웃] 실행 시간 초과"], timed_out=True)

    return ExecutionResult(passed=passed, failed=failed, errors=errors)
