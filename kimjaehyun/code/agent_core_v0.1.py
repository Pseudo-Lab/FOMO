"""
FOMO Crew W1 - Agent Core v0.1
Claude API를 활용한 기본 Task 분업 로직 구현

Author: kimjaehyun
Date: 2025-03-22
"""

import anthropic


def create_agent(role: str, system_prompt: str) -> dict:
    """에이전트 역할과 시스템 프롬프트를 정의"""
    return {
        "role": role,
        "system_prompt": system_prompt,
        "history": [],
    }


def run_agent(agent: dict, user_message: str) -> str:
    """단일 에이전트에게 태스크를 전달하고 응답을 받는다"""
    client = anthropic.Anthropic()

    agent["history"].append({"role": "user", "content": user_message})

    response = client.messages.create(
        model="claude-sonnet-4-20250514",
        max_tokens=1024,
        system=agent["system_prompt"],
        messages=agent["history"],
    )

    assistant_message = response.content[0].text
    agent["history"].append({"role": "assistant", "content": assistant_message})

    return assistant_message


def chain_agents(agents: list[dict], initial_input: str) -> list[str]:
    """에이전트들을 순차적으로 체이닝하여 태스크를 분업 처리"""
    results = []
    current_input = initial_input

    for agent in agents:
        output = run_agent(agent, current_input)
        results.append({"role": agent["role"], "output": output})
        current_input = f"이전 에이전트({agent['role']})의 결과:\n{output}\n\n이를 바탕으로 당신의 역할을 수행하세요."

    return results


# 사용 예시
if __name__ == "__main__":
    # 3개의 에이전트로 구성된 간단한 파이프라인
    researcher = create_agent(
        role="Researcher",
        system_prompt="당신은 리서치 에이전트입니다. 주어진 주제에 대해 핵심 포인트를 3가지로 정리하세요.",
    )

    analyzer = create_agent(
        role="Analyzer",
        system_prompt="당신은 분석 에이전트입니다. 리서치 결과를 받아 실무 적용 가능성을 평가하세요.",
    )

    writer = create_agent(
        role="Writer",
        system_prompt="당신은 작성 에이전트입니다. 분석 결과를 바탕으로 팀에 공유할 1페이지 요약문을 작성하세요.",
    )

    results = chain_agents(
        agents=[researcher, analyzer, writer],
        initial_input="Agent Harness 패턴이 현업 개발 워크플로우에 미치는 영향",
    )

    for result in results:
        print(f"\n{'='*50}")
        print(f"[{result['role']}]")
        print(f"{'='*50}")
        print(result["output"])
