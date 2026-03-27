"""
② LLMClient — 파이프라인 2단계
역할: Problem을 받아 프롬프트를 구성하고, LLM API를 호출해 생성 코드를 반환
"""

from harness.loader import Problem


def build_prompt(problem: Problem) -> str:
    """
    Problem 객체를 LLM에게 보낼 프롬프트 문자열로 변환.
    ※ 이 함수가 하네스의 '문제 제시 방식'을 결정하는 핵심.
    ※ 평가 목적에 따라 프롬프트 템플릿을 자유롭게 수정.
    """
    # ※ 아래는 코딩 문제용 예시 프롬프트 템플릿
    prompt = f"""다음 문제를 파이썬으로 풀어주세요.

문제: {problem.description}

함수 뼈대:
{problem.function_signature}
    pass

주의: 함수 구현 코드만 출력하세요. 설명은 불필요합니다.
"""
    return prompt


def call_llm(prompt: str, config: dict) -> str:
    """
    LLM API를 호출해 생성된 코드 문자열을 반환.
    ※ 현재는 더미(dummy) 구현 — 실제 사용 시 아래 중 하나로 교체:
        - Anthropic Claude API
        - OpenAI GPT API
        - 로컬 모델 (Ollama 등)
    """
    # TODO: 실제 API 호출 코드로 교체
    # 예시) anthropic.Anthropic().messages.create(...)
    model = config.get("model", "claude-sonnet-4-6")
    print(f"  [LLMClient] 모델: {model} 호출 중...")

    # ※ 더미 응답 — 실제 API 연결 전 파이프라인 동작 확인용
    dummy_response = f"""
{problem_signature_from_prompt(prompt)}
    # ※ 더미 응답 — LLM API 연결 후 실제 코드로 대체됨
    pass
"""
    return dummy_response


def problem_signature_from_prompt(prompt: str) -> str:
    """프롬프트에서 함수 시그니처 줄만 추출 (더미용 헬퍼)."""
    for line in prompt.splitlines():
        if line.strip().startswith("def "):
            return line.strip()
    return "def unknown():"


def generate_code(problem: Problem, config: dict) -> str:
    """
    DataLoader → LLMClient 인터페이스.
    Problem을 받아 생성된 코드 문자열을 반환.
    """
    prompt = build_prompt(problem)
    return call_llm(prompt, config)
