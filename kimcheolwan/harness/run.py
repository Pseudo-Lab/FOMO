"""
run.py — 공용 평가 하네스 엔트리포인트

실행 방법:
    python run.py

파이프라인 흐름:
    [code mode] ① DataLoader → ② LLMClient → ③ CodeSandbox → ④ Scorer/Logger
    [web  mode] ① DataLoader → ② LLMClient → ③ WebSandbox  → ④ Scorer/Logger

config.yaml의 mode 값으로 평가 유형을 선택합니다.
"""

import yaml
from datetime import datetime
from pathlib import Path

from harness.loader import load_problems, load_web_problems
from harness.llm_client import generate_code, generate_web_code
from harness.sandbox import execute, execute_web
from harness.scorer import score, score_web, log_result, print_summary


def main():
    # 설정 로드
    with open("config.yaml", "r", encoding="utf-8") as f:
        config = yaml.safe_load(f)

    mode = config.get("mode", "code")
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    output_path = Path(config["results"]["output_dir"]) / f"run_{timestamp}.jsonl"

    if mode == "web":
        run_web(config, output_path)
    else:
        run_code(config, output_path)


# ─── Week1: 코드 평가 모드 ────────────────────────────────────────────────

def run_code(config: dict, output_path: Path) -> None:
    """코드 생성 평가 파이프라인."""
    problems = load_problems(config["data"]["problems_path"])
    print(f"[하네스 시작 — code mode] 문제 수: {len(problems)}")

    all_scores = []
    for problem in problems:
        print(f"\n▶ [{problem.id}] {problem.description[:40]}...")

        generated_code = generate_code(problem, config["llm"])

        exec_result = execute(
            generated_code=generated_code,
            unit_tests=problem.unit_tests,
            timeout_sec=config["sandbox"]["timeout_sec"],
        )

        score_data = score(exec_result)
        log_result(problem.id, generated_code, score_data, str(output_path))
        all_scores.append(score_data)

        print(f"  점수: {score_data['score']:.0%} "
              f"({score_data['passed']}/{score_data['total']} 통과)")

    print_summary(all_scores, mode="code")
    print(f"\n결과 저장 위치: {output_path}")


# ─── Week2: 웹/앱 평가 모드 ──────────────────────────────────────────────

def run_web(config: dict, output_path: Path) -> None:
    """웹/앱 서비스 평가 파이프라인."""
    problems = load_web_problems(config["data"]["problems_path"])
    print(f"[하네스 시작 — web mode] 문제 수: {len(problems)}")

    web_cfg = config.get("web", {})
    weights = web_cfg.get("score_weights", {"status": 0.3, "schema": 0.4, "security": 0.3})

    all_scores = []
    for problem in problems:
        print(f"\n▶ [{problem.id}] {problem.method} {problem.endpoint}"
              f" — {problem.description[:30]}...")

        generated_code = generate_web_code(problem, config["llm"])

        exec_result = execute_web(
            generated_code=generated_code,
            test_cases=problem.test_cases,
            endpoint=problem.endpoint,
            method=problem.method,
            timeout_sec=config["sandbox"]["timeout_sec"],
        )

        score_data = score_web(exec_result, generated_code, weights)
        log_result(problem.id, generated_code, score_data, str(output_path))
        all_scores.append(score_data)

        # 결과 출력
        if exec_result.setup_error:
            print(f"  ✗ 설정 오류: {exec_result.setup_error}")
        elif exec_result.timed_out:
            print(f"  ✗ 타임아웃")
        else:
            print(f"  점수: {score_data['score']:.0%}  "
                  f"(상태:{score_data['status_score']:.0%} "
                  f"스키마:{score_data['schema_score']:.0%} "
                  f"보안:{score_data['security_score']:.0%})")
            for issue in score_data.get("security_issues", []):
                print(f"    [{issue['severity']}] {issue['message']} (line {issue['line']})")

    print_summary(all_scores, mode="web")
    print(f"\n결과 저장 위치: {output_path}")


if __name__ == "__main__":
    main()
