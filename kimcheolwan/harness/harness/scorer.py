"""
④ Scorer / Logger — Flutter 평가 하네스 4단계
역할: 실행 결과를 채점하고 JSONL 파일로 저장

다차원 점수:
  - test_score     (기본 0.4): flutter test 통과율
  - lint_score     (기본 0.3): dart analyze 정적 분석
  - security_score (기본 0.3): 보안 정적 검사
"""

import json
from datetime import datetime
from pathlib import Path

from harness.sandbox import FlutterExecutionResult


# ─── Flutter 채점 ────────────────────────────────────────────────────────

def score_flutter(
    exec_result: FlutterExecutionResult,
    generated_code: str,
    weights: dict | None = None,
) -> dict:
    """
    Flutter 실행 결과를 다차원 채점.

    weights 예시: {"test": 0.4, "lint": 0.3, "security": 0.3}
    """
    from harness.validators.security import check_security

    if weights is None:
        weights = {"test": 0.4, "lint": 0.3, "security": 0.3}

    # 설정/타임아웃/빌드 오류 → 0점 처리
    if exec_result.setup_error or exec_result.timed_out or exec_result.build_error:
        return {
            "score": 0.0,
            "test_score": 0.0,
            "lint_score": 0.0,
            "security_score": 0.0,
            "total_tests": 0,
            "passed_tests": 0,
            "lint_errors": 0,
            "lint_warnings": 0,
            "timed_out": exec_result.timed_out,
            "setup_error": exec_result.setup_error,
            "build_error": exec_result.build_error,
            "security_issues": [],
        }

    # ── test_score: flutter test 통과율 ──
    total_tests = len(exec_result.test_results)
    passed_tests = sum(1 for r in exec_result.test_results if r.passed)
    test_score = passed_tests / total_tests if total_tests > 0 else 0.0

    # ── lint_score: dart analyze 결과 ──
    lint_errors = sum(1 for i in exec_result.lint_issues if i.severity == "error")
    lint_warnings = sum(1 for i in exec_result.lint_issues if i.severity == "warning")
    lint_infos = sum(1 for i in exec_result.lint_issues if i.severity == "info")

    # 감점: error -0.3, warning -0.1, info -0.02
    lint_penalty = (lint_errors * 0.3) + (lint_warnings * 0.1) + (lint_infos * 0.02)
    lint_score = max(0.0, 1.0 - lint_penalty)

    # ── security_score: 보안 정적 분석 ──
    sec_report = check_security(generated_code)
    security_score = sec_report.score

    # ── 가중 합산 ──
    total_score = (
        weights["test"] * test_score
        + weights["lint"] * lint_score
        + weights["security"] * security_score
    )

    return {
        "score": round(total_score, 4),
        "test_score": round(test_score, 4),
        "lint_score": round(lint_score, 4),
        "security_score": round(security_score, 4),
        "total_tests": total_tests,
        "passed_tests": passed_tests,
        "lint_errors": lint_errors,
        "lint_warnings": lint_warnings,
        "timed_out": exec_result.timed_out,
        "setup_error": None,
        "build_error": None,
        "security_issues": [
            {
                "severity": i.severity,
                "rule": i.rule,
                "message": i.message,
                "line": i.line,
            }
            for i in sec_report.issues
        ],
        "lint_details": [
            {
                "severity": i.severity,
                "rule": i.rule,
                "message": i.message,
                "line": i.line,
            }
            for i in exec_result.lint_issues
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


def print_summary(results: list[dict]) -> None:
    """전체 실행 후 콘솔 요약 출력."""
    total = len(results)
    if total == 0:
        print("\n[결과 없음]")
        return

    avg_score = sum(r["score"] for r in results) / total
    perfect = sum(1 for r in results if r["score"] >= 0.99)

    avg_test = sum(r.get("test_score", 0) for r in results) / total
    avg_lint = sum(r.get("lint_score", 0) for r in results) / total
    avg_sec = sum(r.get("security_score", 0) for r in results) / total

    print("\n" + "=" * 50)
    print(f"[결과 요약 — Flutter 하네스] 총 {total}문제")
    print(f"  완벽 통과 (≥99%): {perfect} / {total}")
    print(f"  평균 점수:        {avg_score:.2%}")
    print(f"  ─ 테스트 점수:    {avg_test:.2%}")
    print(f"  ─ 린트 점수:      {avg_lint:.2%}")
    print(f"  ─ 보안 점수:      {avg_sec:.2%}")

    # HIGH 보안 이슈 경고
    high_issues = sum(
        sum(1 for i in r.get("security_issues", []) if i["severity"] == "HIGH")
        for r in results
    )
    if high_issues > 0:
        print(f"  ⚠ HIGH 보안 이슈: {high_issues}건 — 코드 검토 필요")

    # 빌드/설정 오류 경고
    error_count = sum(
        1 for r in results if r.get("setup_error") or r.get("build_error")
    )
    if error_count > 0:
        print(f"  ⚠ 빌드/설정 오류: {error_count}건")

    print("=" * 50)
