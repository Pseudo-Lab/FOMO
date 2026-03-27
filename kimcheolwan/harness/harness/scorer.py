"""
④ Scorer / Logger — 파이프라인 4단계
역할: 실행 결과를 채점하고 JSONL 파일로 저장
"""

import json
from datetime import datetime
from pathlib import Path

from harness.sandbox import ExecutionResult


def score(result: ExecutionResult) -> dict:
    """
    ExecutionResult를 채점해 점수 딕셔너리 반환.
    ※ 현재는 단순 pass/fail 비율 — 부분 점수나 가중치 등 확장 가능.
    """
    total = result.passed + result.failed
    score_value = result.passed / total if total > 0 else 0.0
    return {
        "passed": result.passed,
        "failed": result.failed,
        "total": total,
        "score": round(score_value, 4),   # 0.0 ~ 1.0
        "timed_out": result.timed_out,
        "errors": result.errors,
    }


def log_result(problem_id: str, generated_code: str, score_data: dict, output_path: str):
    """
    채점 결과를 JSONL 파일에 한 줄 추가.
    파일이 없으면 자동 생성.
    """
    record = {
        "id": problem_id,
        "timestamp": datetime.now().isoformat(),
        "generated_code": generated_code,
        **score_data,
    }
    Path(output_path).parent.mkdir(parents=True, exist_ok=True)
    with open(output_path, "a", encoding="utf-8") as f:
        f.write(json.dumps(record, ensure_ascii=False) + "\n")


def print_summary(results: list[dict]):
    """
    전체 실행 후 콘솔 요약 출력.
    ※ 보리스 팁 13: 피드백 루프 — 파이프라인 종료 시 결과를 즉시 확인 가능하게.
    """
    total = len(results)
    perfect = sum(1 for r in results if r["score"] == 1.0)
    avg_score = sum(r["score"] for r in results) / total if total > 0 else 0.0

    print("\n" + "=" * 40)
    print(f"[결과 요약] 총 {total}문제")
    print(f"  완벽 통과: {perfect} / {total}")
    print(f"  평균 점수: {avg_score:.2%}")
    print("=" * 40)
