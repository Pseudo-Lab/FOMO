"""
② LLMClient — 파이프라인 2단계
역할: Problem / WebProblem을 받아 프롬프트를 구성하고 LLM API를 호출

[week1] 코드 생성 프롬프트 (함수 구현)
[week2] 웹 엔드포인트 생성 프롬프트 (FastAPI / Flask)
        실제 Anthropic / OpenAI API 연결
"""

import os
import re

from harness.loader import Problem, WebProblem


# ─── 프롬프트 빌더 ────────────────────────────────────────────────────────

def build_code_prompt(problem: Problem) -> str:
    """Week1: 코드 생성 평가용 프롬프트."""
    return f"""다음 문제를 파이썬으로 풀어주세요.

문제: {problem.description}

함수 뼈대:
{problem.function_signature}
    pass

주의: 함수 구현 코드만 출력하세요. 설명은 불필요합니다.
"""


def build_web_prompt(problem: WebProblem) -> str:
    """
    Week2: 웹/앱 서비스 평가용 프롬프트.
    LLM에게 FastAPI 엔드포인트 구현을 요청.
    ※ 평가 목적에 따라 프롬프트 템플릿 자유롭게 수정.
    """
    method = problem.method.upper()

    test_lines = []
    for i, tc in enumerate(problem.test_cases, 1):
        line = f"  테스트 {i}: {method} {problem.endpoint} → HTTP {tc.expected_status}"
        if tc.request_body:
            line += f"  (요청 body: {tc.request_body})"
        if tc.expected_schema:
            line += "  (응답 스키마 검증 있음)"
        test_lines.append(line)

    signature_hint = (
        f"\n코드 힌트:\n{problem.function_signature}" if problem.function_signature else ""
    )

    return f"""다음 웹 API 엔드포인트를 {problem.framework.capitalize()}로 구현하세요.

요구사항:
- 엔드포인트: {method} {problem.endpoint}
- 설명: {problem.description}

테스트 케이스:
{chr(10).join(test_lines)}
{signature_hint}

구현 규칙:
1. FastAPI app 객체를 반드시 `app` 변수에 할당하세요. (예: app = FastAPI())
2. 엔드포인트 함수만 구현하세요. 서버 실행 코드(uvicorn.run 등)는 포함하지 마세요.
3. 적절한 HTTP 상태 코드를 반환하세요.
4. Pydantic 모델로 입력 검증을 구현하세요.
5. import 문을 포함한 완전한 코드를 ```python ... ``` 블록으로 출력하세요.
"""


# ─── LLM API 호출 ─────────────────────────────────────────────────────────

def call_llm(prompt: str, config: dict) -> str:
    """
    실제 LLM API 호출.
    config["provider"]에 따라 Anthropic / OpenAI 분기.
    API 키는 config["api_key_env"] 환경변수에서 읽음 (직접 기입 금지).
    """
    model = config.get("model", "claude-sonnet-4-6")
    provider = config.get("provider", "anthropic")

    print(f"  [LLMClient] {provider} / {model} 호출 중...")

    if provider == "anthropic":
        return _call_anthropic(prompt, model, config.get("api_key_env", "ANTHROPIC_API_KEY"))
    elif provider == "openai":
        return _call_openai(prompt, model, config.get("api_key_env", "OPENAI_API_KEY"))
    else:
        raise ValueError(f"지원하지 않는 provider: {provider} (anthropic | openai)")


def _call_anthropic(prompt: str, model: str, api_key_env: str) -> str:
    try:
        import anthropic
    except ImportError:
        raise ImportError("anthropic 패키지가 필요합니다: pip install anthropic")

    api_key = os.environ.get(api_key_env)
    if not api_key:
        raise EnvironmentError(f"환경변수 '{api_key_env}'가 설정되지 않았습니다.")

    client = anthropic.Anthropic(api_key=api_key)
    message = client.messages.create(
        model=model,
        max_tokens=2048,
        messages=[{"role": "user", "content": prompt}],
    )
    return message.content[0].text


def _call_openai(prompt: str, model: str, api_key_env: str) -> str:
    try:
        import openai
    except ImportError:
        raise ImportError("openai 패키지가 필요합니다: pip install openai")

    api_key = os.environ.get(api_key_env)
    if not api_key:
        raise EnvironmentError(f"환경변수 '{api_key_env}'가 설정되지 않았습니다.")

    client = openai.OpenAI(api_key=api_key)
    response = client.chat.completions.create(
        model=model,
        messages=[{"role": "user", "content": prompt}],
        max_tokens=2048,
    )
    return response.choices[0].message.content


# ─── 코드 추출 헬퍼 ───────────────────────────────────────────────────────

def _extract_code_block(text: str) -> str:
    """LLM 응답에서 ```python ... ``` 블록 추출. 없으면 전체 반환."""
    lines = text.splitlines()
    in_block = False
    code_lines = []
    for line in lines:
        if line.strip().startswith("```python"):
            in_block = True
            continue
        if in_block and line.strip() == "```":
            break
        if in_block:
            code_lines.append(line)
    return "\n".join(code_lines) if code_lines else text


# ─── 퍼블릭 인터페이스 ────────────────────────────────────────────────────

def generate_code(problem: Problem, config: dict) -> str:
    """Week1: DataLoader → LLMClient 인터페이스 (코드 생성)."""
    prompt = build_code_prompt(problem)
    return call_llm(prompt, config)


def generate_web_code(problem: WebProblem, config: dict) -> str:
    """Week2: DataLoader → LLMClient 인터페이스 (웹 엔드포인트 생성)."""
    prompt = build_web_prompt(problem)
    raw = call_llm(prompt, config)
    return _extract_code_block(raw)
