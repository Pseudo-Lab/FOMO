"""
정적 보안 검사기
역할: LLM이 생성한 웹 코드의 기본 보안 취약점을 정적 분석으로 탐지

[탐지 항목]
- HIGH  : 하드코딩된 시크릿, SQL Injection, eval(), os.system(), shell=True
- MEDIUM: debug=True, CORS 와일드카드
- LOW   : SSL 검증 비활성화
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


# ─── 탐지 규칙 ────────────────────────────────────────────────────────────
# (pattern, severity, rule_id, message)
_RULES: list[tuple[str, str, str, str]] = [
    # 하드코딩된 시크릿
    (
        r'(?i)(password|secret|api_key|token|passwd)\s*=\s*["\'][^"\']{4,}["\']',
        "HIGH", "HARDCODED_SECRET",
        "하드코딩된 시크릿/패스워드 감지 — 환경변수로 분리하세요",
    ),
    # SQL Injection: f-string SQL
    (
        r'f["\'].*(?i)(SELECT|INSERT|UPDATE|DELETE|DROP).*\{',
        "HIGH", "SQL_INJECTION_FSTRING",
        "f-string SQL 쿼리 — SQL Injection 위험, 파라미터 바인딩을 사용하세요",
    ),
    # SQL Injection: 문자열 연결 SQL
    (
        r'["\'][\s\w]*(?i)(SELECT|INSERT|UPDATE|DELETE)[\s\w]*["\']\s*\+',
        "HIGH", "SQL_INJECTION_CONCAT",
        "문자열 연결 SQL 쿼리 — SQL Injection 위험, ORM 또는 파라미터 바인딩을 사용하세요",
    ),
    # 위험 함수
    (
        r'\beval\s*\(',
        "HIGH", "DANGEROUS_EVAL",
        "eval() 사용 — 코드 인젝션 위험",
    ),
    (
        r'\bos\.system\s*\(',
        "HIGH", "OS_COMMAND_INJECTION",
        "os.system() 사용 — 커맨드 인젝션 위험, subprocess를 사용하세요",
    ),
    (
        r'\bsubprocess\.(call|run|Popen)\s*\(.*shell\s*=\s*True',
        "HIGH", "SHELL_INJECTION",
        "shell=True subprocess — 셸 인젝션 위험, 리스트 형태 인자를 사용하세요",
    ),
    # 보안 설정 미흡
    (
        r'(?i)\bdebug\s*=\s*True',
        "MEDIUM", "DEBUG_ENABLED",
        "debug=True 감지 — 프로덕션에서 비활성화하세요",
    ),
    (
        r'(?i)allow_origins\s*=\s*\[\s*["\*]',
        "MEDIUM", "CORS_WILDCARD",
        "CORS allow_origins='*' — 와일드카드 허용은 보안 위험입니다",
    ),
    (
        r'(?i)verify\s*=\s*False',
        "LOW", "SSL_VERIFY_DISABLED",
        "SSL 인증서 검증 비활성화 — 프로덕션에서 활성화하세요",
    ),
]


def check_security(code: str) -> SecurityReport:
    """
    생성된 코드에 대해 정적 보안 분석 수행.
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
