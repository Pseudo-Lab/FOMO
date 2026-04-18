"""
정적 보안 검사기 — Dart/Flutter 전용
역할: LLM이 생성한 Dart 코드의 기본 보안 취약점을 정적 분석으로 탐지

[탐지 항목]
- HIGH  : 하드코딩된 시크릿, Process.run, dart:mirrors, HTTP URL
- MEDIUM: debugPrint 남용, 전역 상태 변경
- LOW   : badCertificateCallback 비활성화
"""

import re
from dataclasses import dataclass, field


@dataclass
class SecurityIssue:
    severity: str       # "HIGH" | "MEDIUM" | "LOW"
    rule: str           # 규칙 ID
    message: str        # 사람이 읽을 수 있는 설명
    line: int | None = None


@dataclass
class SecurityReport:
    issues: list[SecurityIssue] = field(default_factory=list)

    @property
    def score(self) -> float:
        """
        보안 점수 0.0 ~ 1.0.
        이슈가 없으면 1.0, HIGH 이슈마다 -0.4, MEDIUM -0.2, LOW -0.05.
        """
        if not self.issues:
            return 1.0
        _penalty_map = {"HIGH": 0.4, "MEDIUM": 0.2, "LOW": 0.05}
        penalty = sum(_penalty_map.get(i.severity, 0.1) for i in self.issues)
        return max(0.0, round(1.0 - penalty, 4))

    @property
    def high_count(self) -> int:
        return sum(1 for i in self.issues if i.severity == "HIGH")


# ─── Dart/Flutter 탐지 규칙 ──────────────────────────────────────────────
# (pattern, severity, rule_id, message)
_RULES: list[tuple[str, str, str, str]] = [
    # ── HIGH ──
    # 하드코딩된 시크릿
    (
        r"""(?i)(password|secret|apiKey|api_key|token|passwd)\s*[=:]\s*['"][^'"]{4,}['"]""",
        "HIGH", "HARDCODED_SECRET",
        "하드코딩된 시크릿/패스워드 감지 — 환경변수 또는 --dart-define으로 분리하세요",
    ),
    # Process.run (커맨드 인젝션 위험)
    (
        r'\bProcess\.run\s*\(',
        "HIGH", "PROCESS_RUN",
        "Process.run() 사용 — 커맨드 인젝션 위험, 사용자 입력을 직접 전달하지 마세요",
    ),
    # dart:mirrors (리플렉션 보안 위험 + Flutter 비호환)
    (
        r"import\s+['\"]dart:mirrors['\"]",
        "HIGH", "DART_MIRRORS",
        "dart:mirrors 사용 — Flutter에서 지원하지 않으며 보안 위험이 있습니다",
    ),
    # HTTP URL (HTTPS 미사용)
    (
        r"""['"]http://(?!localhost|127\.0\.0\.1|10\.|192\.168\.)""",
        "HIGH", "HTTP_NOT_HTTPS",
        "HTTP URL 사용 — HTTPS를 사용하세요 (Android 9+ 기본 차단)",
    ),
    # dart:io의 sleep (UI 스레드 블로킹)
    (
        r'\bsleep\s*\(\s*Duration',
        "HIGH", "BLOCKING_SLEEP",
        "sleep() 사용 — UI 스레드를 블로킹합니다. Future.delayed를 사용하세요",
    ),
    # ── MEDIUM ──
    # print() / debugPrint() 남용
    (
        r'\b(?:print|debugPrint)\s*\(',
        "MEDIUM", "DEBUG_PRINT",
        "print()/debugPrint() 감지 — 프로덕션에서는 로거를 사용하세요",
    ),
    # setState() 내 비동기 호출
    (
        r'setState\s*\(\s*\(\s*\)\s*(?:async|\{[^}]*await)',
        "MEDIUM", "ASYNC_SET_STATE",
        "setState() 내 비동기 작업 — 위젯이 dispose된 후 setState 호출 위험",
    ),
    # CORS/네트워크 와일드카드
    (
        r"""Access-Control-Allow-Origin['":\s]*\*""",
        "MEDIUM", "CORS_WILDCARD",
        "CORS 와일드카드 허용 — 허용 도메인을 명시적으로 지정하세요",
    ),
    # ── LOW ──
    # SSL 인증서 검증 비활성화
    (
        r'badCertificateCallback.*(?:=>|return)\s*true',
        "LOW", "SSL_VERIFY_DISABLED",
        "SSL 인증서 검증 비활성화 — 프로덕션에서 활성화하세요",
    ),
    # TODO 주석 잔존
    (
        r'//\s*TODO',
        "LOW", "TODO_REMAINING",
        "TODO 주석 잔존 — 구현이 완료되지 않았을 수 있습니다",
    ),
]


def check_security(code: str) -> SecurityReport:
    """
    생성된 Dart 코드에 대해 정적 보안 분석 수행.
    각 라인에 대해 규칙 패턴 매칭 → SecurityIssue 수집.
    """
    issues: list[SecurityIssue] = []
    lines = code.splitlines()

    for pattern, severity, rule_id, message in _RULES:
        compiled = re.compile(pattern)
        for line_no, line in enumerate(lines, 1):
            if compiled.search(line):
                issues.append(SecurityIssue(
                    severity=severity,
                    rule=rule_id,
                    message=message,
                    line=line_no,
                ))

    return SecurityReport(issues=issues)
