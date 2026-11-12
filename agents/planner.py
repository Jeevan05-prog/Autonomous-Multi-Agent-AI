from models.state import AgentState
from agents.llm import ask_gemini


def create_fallback_plan(user_request: str):
    """
    Creates a useful research plan when Gemini is unavailable.
    Works with different research topics.
    """

    return [
        f"Find recent statistics and historical trends related to {user_request}.",

        f"Research the major developments and important factors influencing {user_request}.",

        f"Collect relevant numerical data, reports, and supporting evidence about {user_request}.",

        f"Identify the major opportunities, challenges, and limitations related to {user_request}.",

        f"Compare available findings and identify important patterns and trends in {user_request}.",

        f"Verify important facts using reliable sources and identify any conflicting information.",

        f"Summarize the findings and prepare conclusions about {user_request}.",
    ]


def planner_agent(state: AgentState) -> AgentState:

    user_request = state["user_request"]

    print("\n========== PLANNER AGENT ==========")
    print(f"User Request: {user_request}")

    prompt = f"""
You are the Planner Agent in an autonomous multi-agent AI research system.

Research topic:
{user_request}

Create a detailed research plan containing 5 to 7 tasks.

The tasks must cover:
1. Historical trends and recent developments.
2. Important statistics and numerical data.
3. Major factors influencing the topic.
4. Opportunities and challenges.
5. Comparisons and important patterns.
6. Verification using reliable sources.
7. Conclusions and future outlook.

IMPORTANT:
- Make every task specific to the research topic.
- Write tasks that can be used directly as web search queries.
- Avoid generic tasks such as "collect information".
- Return only a numbered list.
"""

    try:
        generated_plan = ask_gemini(prompt)

        plan = [
            line.strip()
            for line in generated_plan.splitlines()
            if line.strip()
        ]

        if not plan:
            raise ValueError("Gemini returned an empty research plan.")

        state["plan"] = plan

        print("\nGenerated Plan using Gemini:")

    except Exception as error:

        print("\nGemini is unavailable.")
        print("Using the built-in research planning system.")
        print(f"Reason: {error}")

        state["plan"] = create_fallback_plan(user_request)

        print("\nGenerated Fallback Research Plan:")

    for task in state["plan"]:
        print(task)

    return state