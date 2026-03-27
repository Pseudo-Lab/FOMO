"""
run.py — 공용 평가 하네스 엔트리포인트

실행 방법:
    python run.py

파이프라인 흐름:
    ① DataLoader → ② LLMClient → ③ ExecutionSandbox → ④ Scorer/Logger
"""

import yaml
from datetime import datetime
from pathlib import Path

from harness.loader import load_problems
from harness.llm_client import generate_code
from harness.sandbox import execute
from harness.scorer import score, log_result, print_summary


def main():
    # 설정 로드
    with open("config.yaml", "r", encoding="utf-8") as f:
        config = yaml.safe_load(f)

    # 결과 파일 경로 (실행 시각 기준 자동 생성)
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    output_path = Path(config["results"]["output_dir"]) / f"run_{timestamp}.jsonl"

    # ① 문제 로드
    problems = load_problems(config["data"]["problems_path"])
    print(f"[하네스 시작] 문제 수: {len(problems)}")

    all_scores = []

    for problem in problems:
        print(f"\n▶ [{problem.id}] {problem.description[:40]}...")

        # ② LLM 호출 → 코드 생성
        generated_code = generate_code(problem, config["llm"])

        # ③ 샌드박스 실행
        exec_result = execute(
            generated_code=generated_code,
            unit_tests=problem.unit_tests,
            timeout_sec=config["sandbox"]["timeout_sec"],
        )

        # ④ 채점 + 로깅
        score_data = score(exec_result)
        log_result(problem.id, generated_code, score_data, str(output_path))

        all_scores.append(score_data)
        print(f"  점수: {score_data['score']:.0%} ({score_data['passed']}/{score_data['total']} 통과)")

    # 전체 요약 출력 (보리스 팁 13 — 피드백 루프)
    print_summary(all_scores)
    print(f"\n결과 저장 위치: {output_path}")


if __name__ == "__main__":
    main()
