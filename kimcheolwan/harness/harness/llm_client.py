"""
② LLMClient — Flutter 평가 하네스 2단계
역할: FlutterProblem을 받아 프롬프트를 구성하고 LLM API를 호출해 Dart 코드 생성

[widget] Flutter 위젯 구현 프롬프트 (StatelessWidget / StatefulWidget)
[logic]  Dart 순수 함수 구현 프롬프트
"""

import os
import re

from harness.loader import FlutterProblem


# ─── 프롬프트 빌더 ────────────────────────────────────────────────────────

def build_widget_prompt(problem: FlutterProblem) -> str:
    """Widget mode: Flutter 위젯 구현 프롬프트."""
    hint_section = f"\n코드 힌트:\n{problem.hint}" if problem.hint else ""

    return f"""다음 Flutter 위젯을 구현하세요.

요구사항:
- 위젯 이름: {problem.widget_name}
- 설명: {problem.description}
{hint_section}

구현 규칙:
1. import 'package:flutter/material.dart'; 를 포함하세요.
2. StatelessWidget 또는 StatefulWidget을 사용하세요.
3. 위젯 클래스 이름은 반드시 `{problem.widget_name}`이어야 합니다.
4. main() 함수는 포함하지 마세요 — 위젯 클래스만 구현하세요.
5. runApp() 등 앱 실행 코드는 포함하지 마세요.
6. import 문을 포함한 완전한 코드를 ```dart ... ``` 블록으로 출력하세요.
"""


def build_logic_prompt(problem: FlutterProblem) -> str:
    """Logic mode: Dart 순수 함수 구현 프롬프트."""
    hint_section = f"\n코드 힌트:\n{problem.hint}" if problem.hint else ""

    return f"""다음 Dart 함수를 구현하세요.

요구사항:
- 함수 이름: {problem.function_name}
- 설명: {problem.description}
{hint_section}

구현 규칙:
1. 함수 구현 코드만 출력하세요. main() 함수는 포함하지 마세요.
2. 필요한 import 문이 있으면 포함하세요.
3. ```dart ... ``` 블록으로 출력하세요.
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
        max_tokens=4096,
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
        max_tokens=4096,
    )
    return response.choices[0].message.content


# ─── 코드 추출 헬퍼 ───────────────────────────────────────────────────────

def _extract_dart_block(text: str) -> str:
    """LLM 응답에서 ```dart ... ``` 블록 추출. 없으면 전체 반환."""
    lines = text.splitlines()
    in_block = False
    code_lines = []
    for line in lines:
        if line.strip().startswith("```dart"):
            in_block = True
            continue
        if in_block and line.strip() == "```":
            break
        if in_block:
            code_lines.append(line)
    return "\n".join(code_lines) if code_lines else text


# ─── 퍼블릭 인터페이스 ────────────────────────────────────────────────────

def generate_flutter_code(problem: FlutterProblem, config: dict) -> str:
    """FlutterProblem → LLM 호출 → Dart 코드 생성."""
    if problem.mode == "widget":
        prompt = build_widget_prompt(problem)
    else:
        prompt = build_logic_prompt(problem)

    raw = call_llm(prompt, config)
    return _extract_dart_block(raw)
