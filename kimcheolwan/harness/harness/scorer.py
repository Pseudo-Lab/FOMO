"""
④ Scorer / Logger — 파이프라인 4단계
역할: 실행 결과를 채점하고 JSONL 파일로 저장

[week1] 단일 점수: pass/fail 비율
[week2] 다차원 점수:
        - status_score  (기본 0.3): HTTP 상태 코드 일치율
        - schema_score  (기본 0.4): 응답 JSON Schema 적합도
        - security_score(기본 0.3): 정적 보안 검사 점수
"""

import json
from datetime import datetime
from pathlib import Path

from harness.sandbox import ExecutionResult, WebExecutionResult


# ─── Week1: 코드 채점 ────────────────────────────────────────────────────

def score(result: ExecutionResult) -> dict:
    """ExecutionResult → 점수 딕셔너리 (week1 호환)."""
    total = result.passed + result.failed
    score_value = result.passed / total if total > 0 else 0.0
    return {
        "passed": result.passed,
        "failed": result.failed,
        "total": total,
        "score": round(score_value, 4),
        "timed_out": result.timed_out,
        "errors": result.errors,
    }


# ─── Week2: 웹 채점 ──────────────────────────────────────────────────────

def score_web(
    exec_result: WebExecutionResult,
    generated_code: str,
    weights: dict | None = None,
) -> dict:
    """
    웹 실행 결과를 다차원 채점.

    weights 예시: {"status": 0.3, "schema": 0.4, "security": 0.3}
    ※ 가중치 합이 1.0이 되도록 설정. 기본값은 위와 동일.
    """
    from harness.validators.security import check_security

    if weights is None:
        weights = {"status": 0.3, "schema": 0.4, "security": 0.3}

    # 설정/타임아웃 오류 → 0점 처리
    if exec_result.setup_error or exec_result.timed_out:
        return {
            "score": 0.0,
            "status_score": 0.0,
            "schema_score": 0.0,
            "security_score": 0.0,
            "total_tests": 0,
            "passed_status": 0,
            "passed_schema": 0,
            "timed_out": exec_result.timed_out,
            "setup_error": exec_result.setup_error,
            "security_issues": [],
        }

    total = len(exec_result.test_results)

    # 상태 코드 점수
    passed_status = sum(1 for r in exec_result.test_results if r.status_matched)
    status_score = passed_status / total if total > 0 else 0.0

    # 스키마 점수
    passed_schema = sum(1 for r in exec_result.test_results if r.schema_valid)
    schema_score = passed_schema / total if total > 0 else 0.0

    # 보안 점수 (정적 분석)
    sec_report = check_security(generated_code)
    security_score = sec_report.score

    # 가중 합산
    total_score = (
        weights["status"] * status_score
        + weights["schema"] * schema_score
        + weights["security"] * security_score
    )

    return {
        "score": round(total_score, 4),
        "status_score": round(status_score, 4),
        "schema_score": round(schema_score, 4),
        "security_score": round(security_score, 4),
        "total_tests": total,
        "passed_status": passed_status,
        "passed_schema": passed_schema,
        "timed_out": exec_result.timed_out,
        "setup_error": None,
        "security_issues": [
            {
                "severity": i.severity,
                "rule": i.rule,
                "message": i.message,
                "line": i.line,
            }
            for i in sec_report.issues
        ],
    }


# ─── 공통: 로깅 + 요약 ───────────────────────────────────────────────────

def log_result(
    problem_id: str,
    generated_code: str,
    score_data: dict,
    output_path: str,
) -> None:
    """채점 결과를 JSONL 파일에 한 줄 추가. 파일/디렉토리 없으면 자동 생성."""
    record = {
        "id": problem_id,
        "timestamp": datetime.now().isoformat(),
        "generated_code": generated_code,
        **score_data,
    }
    Path(output_path).parent.mkdir(parents=True, exist_ok=True)
    with open(output_path, "a", encoding="utf-8") as f:
        f.write(json.dumps(record, ensure_ascii=False) + "\n")


def print_summary(results: list[dict], mode: str = "code") -> None:
    """
    전체 실행 후 콘솔 요약 출력.
    ※ 보리스 팁 13 — 피드백 루프: 파이프라인 종료 시 결과를 즉시 확인 가능하게.
    """
    total = len(results)
    if total == 0:
        print("\n[결과 없음]")
        return

    avg_score = sum(r["score"] for r in results) / total
    perfect = sum(1 for r in results if r["score"] >= 0.99)

    print("\n" + "=" * 50)
    print(f"[결과 요약 — {mode} mode] 총 {total}문제")
    print(f"  완벽 통과 (≥99%): {perfect} / {total}")
    print(f"  평균 점수:        {avg_score:.2%}")

    if mode == "web":
        avg_status = sum(r.get("status_score", 0) for r in results) / total
        avg_schema = sum(r.get("schema_score", 0) for r in results) / total
        avg_sec    = sum(r.get("security_score", 0) for r in results) / total
        print(f"  ─ 상태코드 점수:  {avg_status:.2%}")
        print(f"  ─ 스키마 점수:    {avg_schema:.2%}")
        print(f"  ─ 보안 점수:      {avg_sec:.2%}")

        high_issues = sum(
            sum(1 for i in r.get("security_issues", []) if i["severity"] == "HIGH")
            for r in results
        )
        if high_issues > 0:
            print(f"  ⚠ HIGH 보안 이슈: {high_issues}건 — 코드 검토 필요")

    print("=" * 50)
