"""
run.py — Flutter 평가 하네스 엔트리포인트

실행 방법:
    cd harness
    python run.py

파이프라인 흐름:
    config.yaml → ① DataLoader → ② LLMClient → ③ FlutterSandbox → ④ Scorer/Logger

config.yaml의 mode 값으로 평가 유형을 선택합니다:
    "widget" — Flutter 위젯 테스트 평가
    "logic"  — Dart 순수 로직 테스트 평가
"""

import yaml
from datetime import datetime
from pathlib import Path

from harness.loader import load_flutter_problems
from harness.llm_client import generate_flutter_code
from harness.sandbox import execute_flutter
from harness.scorer import score_flutter, log_result, print_summary


def main():
    # 설정 로드
    with open("config.yaml", "r", encoding="utf-8") as f:
        config = yaml.safe_load(f)

    mode = config.get("mode", "widget")
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    output_path = Path(config["results"]["output_dir"]) / f"run_{timestamp}.jsonl"

    run_flutter(config, output_path, mode)


def run_flutter(config: dict, output_path: Path, mode: str) -> None:
    """Flutter 평가 파이프라인 (widget / logic 공통)."""
    problems = load_flutter_problems(config["data"]["problems_path"])

    # mode에 맞는 문제만 필터링 (문제 자체에 mode 필드가 있음)
    filtered = [p for p in problems if p.mode == mode]
    if not filtered:
        print(f"[경고] mode='{mode}'에 해당하는 문제가 없습니다. 전체 문제를 실행합니다.")
        filtered = problems

    print(f"[하네스 시작 — Flutter {mode} mode] 문제 수: {len(filtered)}")

    flutter_cfg = config.get("flutter", {})
    weights = flutter_cfg.get("score_weights", {"test": 0.4, "lint": 0.3, "security": 0.3})
    template_dir = flutter_cfg.get("template_project", "template_project/")
    sdk_path = flutter_cfg.get("sdk_path", "")

    sandbox_cfg = config.get("sandbox", {})
    timeout_sec = sandbox_cfg.get("timeout_sec", 120)
    pub_get_timeout = sandbox_cfg.get("pub_get_timeout_sec", 60)
    cleanup = sandbox_cfg.get("cleanup", True)

    all_scores = []
    for problem in filtered:
        label = problem.widget_name or problem.function_name or problem.id
        print(f"\n▶ [{problem.id}] {label} — {problem.description[:40]}...")

        # ② LLM 코드 생성
        generated_code = generate_flutter_code(problem, config["llm"])

        # ③ Flutter 테스트 실행
        exec_result = execute_flutter(
            generated_code=generated_code,
            test_code=problem.test_code,
            template_dir=template_dir,
            timeout_sec=timeout_sec,
            pub_get_timeout_sec=pub_get_timeout,
            sdk_path=sdk_path,
            cleanup=cleanup,
        )

        # ④ 채점
        score_data = score_flutter(exec_result, generated_code, weights)
        log_result(problem.id, generated_code, score_data, str(output_path))
        all_scores.append(score_data)

        # 결과 출력
        if exec_result.setup_error:
            print(f"  ✗ 설정 오류: {exec_result.setup_error}")
        elif exec_result.build_error:
            print(f"  ✗ 빌드 오류: {exec_result.build_error[:100]}")
        elif exec_result.timed_out:
            print(f"  ✗ 타임아웃")
        else:
            print(f"  점수: {score_data['score']:.0%}  "
                  f"(테스트:{score_data['test_score']:.0%} "
                  f"린트:{score_data['lint_score']:.0%} "
                  f"보안:{score_data['security_score']:.0%})")

            for tr in exec_result.test_results:
                status = "✓" if tr.passed else "✗"
                print(f"    {status} {tr.test_name}")
                if tr.error:
                    print(f"      → {tr.error[:80]}")

            for issue in score_data.get("security_issues", []):
                print(f"    [{issue['severity']}] {issue['message']} (line {issue['line']})")

    print_summary(all_scores)
    print(f"\n결과 저장 위치: {output_path}")


if __name__ == "__main__":
    main()
