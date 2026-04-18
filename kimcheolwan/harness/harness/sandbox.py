"""
③ ExecutionSandbox — Flutter 평가 하네스 3단계
역할: LLM이 생성한 Dart 코드를 Flutter 프로젝트로 조립하고 테스트 실행

실행 전략:
  1. 템플릿 프로젝트를 임시 디렉토리에 복사
  2. 생성된 코드를 lib/solution.dart에 저장
  3. 테스트 코드를 test/solution_test.dart에 저장
  4. flutter pub get → flutter test --machine 실행
  5. dart analyze 실행
  6. 결과 파싱 후 임시 디렉토리 정리

[보안 고려사항]
- 타임아웃: subprocess에 timeout 인자로 무한 실행 방어
- 임시 디렉토리 격리: 원본 프로젝트에 영향 없음
- 자동 정리: finally 블록에서 임시 디렉토리 삭제
"""

import json
import os
import shutil
import subprocess
import sys
import tempfile
from dataclasses import dataclass, field
from pathlib import Path


# ─── 실행 결과 데이터 클래스 ──────────────────────────────────────────────

@dataclass
class FlutterTestResult:
    """단일 테스트 케이스 결과."""
    test_id: int
    test_name: str
    passed: bool
    error: str | None = None


@dataclass
class LintIssue:
    """dart analyze 단일 이슈."""
    severity: str          # "info" | "warning" | "error"
    message: str
    file: str
    line: int
    rule: str = ""


@dataclass
class FlutterExecutionResult:
    """전체 실행 결과."""
    test_results: list[FlutterTestResult] = field(default_factory=list)
    lint_issues: list[LintIssue] = field(default_factory=list)
    setup_error: str | None = None
    build_error: str | None = None
    timed_out: bool = False


# ─── 커맨드 유틸리티 ─────────────────────────────────────────────────────

def _find_command(name: str, sdk_path: str = "") -> str:
    """Flutter/Dart 커맨드 경로를 찾는다. Windows에서는 .bat 확장자를 고려."""
    if sdk_path:
        bin_dir = os.path.join(sdk_path, "bin")
        if sys.platform == "win32":
            bat_path = os.path.join(bin_dir, f"{name}.bat")
            if os.path.exists(bat_path):
                return bat_path
        return os.path.join(bin_dir, name)

    found = shutil.which(name)
    if found:
        return found

    # Windows: .bat 확장자로 재시도
    if sys.platform == "win32":
        found = shutil.which(f"{name}.bat")
        if found:
            return found

    return name


# ─── 메인 실행 함수 ──────────────────────────────────────────────────────

def execute_flutter(
    generated_code: str,
    test_code: str,
    template_dir: str,
    timeout_sec: int = 120,
    pub_get_timeout_sec: int = 60,
    sdk_path: str = "",
    cleanup: bool = True,
) -> FlutterExecutionResult:
    """
    Flutter 테스트 실행 파이프라인.

    1. 템플릿 프로젝트 복사 → 임시 디렉토리
    2. solution.dart + solution_test.dart 저장
    3. flutter pub get
    4. flutter test --machine → 테스트 결과 파싱
    5. dart analyze → 린트 결과 파싱
    6. 임시 디렉토리 정리
    """
    flutter_cmd = _find_command("flutter", sdk_path)
    dart_cmd = _find_command("dart", sdk_path)

    # Flutter SDK 존재 확인
    if not shutil.which(flutter_cmd) and not os.path.exists(flutter_cmd):
        return FlutterExecutionResult(
            setup_error="[환경 오류] Flutter SDK를 찾을 수 없습니다. "
                        "PATH에 Flutter를 추가하거나 config.yaml의 flutter.sdk_path를 설정하세요.",
        )

    # 템플릿 프로젝트 존재 확인
    if not os.path.isdir(template_dir):
        return FlutterExecutionResult(
            setup_error=f"[환경 오류] 템플릿 프로젝트가 없습니다: {template_dir}",
        )

    temp_dir = tempfile.mkdtemp(prefix="harness_flutter_")
    try:
        # 1. 프로젝트 복사
        shutil.copytree(template_dir, temp_dir, dirs_exist_ok=True)

        lib_dir = Path(temp_dir) / "lib"
        test_dir = Path(temp_dir) / "test"
        lib_dir.mkdir(exist_ok=True)
        test_dir.mkdir(exist_ok=True)

        # 2. 코드 저장
        (lib_dir / "solution.dart").write_text(generated_code, encoding="utf-8")
        (test_dir / "solution_test.dart").write_text(test_code, encoding="utf-8")

        # .gitkeep 정리
        for gk in [lib_dir / ".gitkeep", test_dir / ".gitkeep"]:
            if gk.exists():
                gk.unlink()

        # 3. flutter pub get
        pub_result = _run_pub_get(flutter_cmd, temp_dir, pub_get_timeout_sec)
        if pub_result is not None:
            return FlutterExecutionResult(setup_error=pub_result)

        # 4. flutter test --machine
        test_results, timed_out, build_error = _run_flutter_test(
            flutter_cmd, temp_dir, timeout_sec,
        )
        if timed_out:
            return FlutterExecutionResult(timed_out=True)
        if build_error:
            return FlutterExecutionResult(build_error=build_error)

        # 5. dart analyze
        lint_issues = _run_dart_analyze(dart_cmd, temp_dir)

        return FlutterExecutionResult(
            test_results=test_results,
            lint_issues=lint_issues,
        )

    except Exception as e:
        return FlutterExecutionResult(
            setup_error=f"[실행 오류] {type(e).__name__}: {e}",
        )
    finally:
        if cleanup:
            shutil.rmtree(temp_dir, ignore_errors=True)


# ─── 내부 실행 함수 ──────────────────────────────────────────────────────

def _run_pub_get(flutter_cmd: str, project_dir: str, timeout_sec: int) -> str | None:
    """flutter pub get 실행. 성공 시 None, 실패 시 에러 메시지 반환."""
    try:
        result = subprocess.run(
            [flutter_cmd, "pub", "get"],
            cwd=project_dir,
            capture_output=True,
            text=True,
            timeout=timeout_sec,
        )
        if result.returncode != 0:
            return f"[pub get 실패] {result.stderr.strip()}"
        return None
    except subprocess.TimeoutExpired:
        return "[pub get 타임아웃] flutter pub get 시간 초과"
    except FileNotFoundError:
        return f"[환경 오류] 커맨드를 실행할 수 없습니다: {flutter_cmd}"


def _run_flutter_test(
    flutter_cmd: str,
    project_dir: str,
    timeout_sec: int,
) -> tuple[list[FlutterTestResult], bool, str | None]:
    """
    flutter test --machine 실행 후 결과 파싱.
    반환: (test_results, timed_out, build_error)
    """
    try:
        result = subprocess.run(
            [flutter_cmd, "test", "--machine", "--no-pub"],
            cwd=project_dir,
            capture_output=True,
            text=True,
            timeout=timeout_sec,
        )
    except subprocess.TimeoutExpired:
        return [], True, None

    # 컴파일 에러 등 빌드 실패 감지
    if result.returncode != 0 and not result.stdout.strip():
        return [], False, f"[빌드 오류] {result.stderr.strip()[:500]}"

    return _parse_machine_output(result.stdout), False, None


def _parse_machine_output(output: str) -> list[FlutterTestResult]:
    """flutter test --machine의 JSON 이벤트 스트림을 파싱."""
    tests: dict[int, str] = {}       # id → name
    results: list[FlutterTestResult] = []

    for line in output.splitlines():
        line = line.strip()
        if not line:
            continue
        try:
            event = json.loads(line)
        except json.JSONDecodeError:
            continue

        event_type = event.get("type")

        if event_type == "testStart":
            test_info = event.get("test", {})
            tid = test_info.get("id")
            name = test_info.get("name", "")
            # hidden 테스트 (loading 등) 건너뛰기
            if tid is not None and not name.startswith("loading"):
                tests[tid] = name

        elif event_type == "testDone":
            tid = event.get("testID")
            if tid in tests:
                passed = event.get("result") == "success"
                hidden = event.get("hidden", False)
                if not hidden:
                    results.append(FlutterTestResult(
                        test_id=tid,
                        test_name=tests[tid],
                        passed=passed,
                    ))

        elif event_type == "error":
            tid = event.get("testID")
            if tid in tests:
                error_msg = event.get("error", "알 수 없는 에러")
                # 이미 추가된 결과에 에러 메시지 병합
                for r in results:
                    if r.test_id == tid:
                        r.error = error_msg[:300]
                        break
                else:
                    results.append(FlutterTestResult(
                        test_id=tid,
                        test_name=tests.get(tid, f"test_{tid}"),
                        passed=False,
                        error=error_msg[:300],
                    ))

    return results


def _run_dart_analyze(dart_cmd: str, project_dir: str) -> list[LintIssue]:
    """
    dart analyze 실행 후 이슈 파싱.
    lib/solution.dart에 대한 린트 결과만 수집.
    """
    try:
        result = subprocess.run(
            [dart_cmd, "analyze", "lib/solution.dart"],
            cwd=project_dir,
            capture_output=True,
            text=True,
            timeout=30,
        )
    except (subprocess.TimeoutExpired, FileNotFoundError):
        return []

    return _parse_analyze_output(result.stdout + "\n" + result.stderr)


def _parse_analyze_output(output: str) -> list[LintIssue]:
    """
    dart analyze 출력 파싱.
    형식: '  severity - file:line:col - message - rule_name'
    """
    import re
    issues: list[LintIssue] = []

    pattern = re.compile(
        r"\s*(info|warning|error)\s*-\s*(.+?):(\d+):\d+\s*-\s*(.+?)\s*-\s*(\S+)"
    )
    for line in output.splitlines():
        match = pattern.match(line.strip())
        if match:
            severity, filepath, line_no, message, rule = match.groups()
            issues.append(LintIssue(
                severity=severity,
                message=message.strip(),
                file=filepath,
                line=int(line_no),
                rule=rule,
            ))

    return issues
