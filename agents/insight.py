from agents.llm import ask_gemini


def insight_agent(state):

    topic = state.get("user_request", "")

    research = state.get("research", "")

    analysis = state.get("analysis", "")

    prompt = f"""

You are the Insight Agent in ResearchFlow AI.

RESEARCH TOPIC:

{topic}


RESEARCH FINDINGS:

{research[:14000]}


DATA ANALYSIS:

{analysis[:9000]}


Your task is to produce a detailed analytical interpretation.

Include the following sections:

1. Main Findings

Explain the most important discoveries from the research.

2. Important Patterns

Identify meaningful patterns and explain what they indicate.

3. Research Interpretation

Explain why the findings matter.

4. Real-World Implications

Explain how the findings affect industries, organisations,
governments and individuals where relevant.

5. Opportunities

Identify opportunities arising from the research topic.

6. Challenges and Risks

Explain important limitations, risks and difficulties.

7. Evidence Gaps

Identify information that is missing or uncertain.

8. Overall Assessment

Provide a balanced conclusion based on the available evidence.


RULES:

- Stay focused on the exact research topic.
- Never introduce unrelated datasets.
- Do not invent statistics.
- Do not create false correlations.
- Do not confuse correlation with causation.
- If no CSV was uploaded, clearly state that.
- Do not pretend that statistical analysis was performed
  when no structured dataset was provided.
- Explain the findings in simple but professional language.
- Do not merely repeat the Research Agent output.

"""

    try:

        state["insights"] = ask_gemini(prompt)

    except Exception as exc:

        state["insights"] = (

            "AI insight generation was unavailable.\n\n"
            f"Reason: {type(exc).__name__}: {exc}\n\n"
            "No additional conclusions have been fabricated."

        )

    return state