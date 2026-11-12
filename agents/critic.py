def critic_agent(state):

    print("\n========== CRITIC AGENT ==========")

    research = state.get("research", "")
    analysis = state.get("analysis", "")
    round_number = state.get("research_round", 0)

    issues = []

    # Check research
    if not research.strip():

        issues.append(
            "Research findings are missing."
        )

    source_count = research.count("SOURCE ")

    if research.strip() and source_count == 0:

        issues.append(
            "Research sources could not be identified."
        )

    # Check analysis
    if "failed" in analysis.lower():

        issues.append(
            "Data analysis encountered an error."
        )

    # Decide whether more research is needed
    if issues and round_number < 2:

        decision = "RESEARCH_REQUIRED"

        result = "\n".join(issues)

        result += (
            "\n\nThe system should attempt additional research."
        )

    else:

        decision = "APPROVED"

        if issues:

            result = (
                "Research review completed with limitations. "
                "The workflow reached its maximum research attempts. "
                + " ".join(issues)
            )

        else:

            result = (
                "Research and analysis passed the basic quality checks. "
                "The available findings can be used to prepare the report."
            )

    state["critique"] = (
        decision + "\n" + result
    )

    print("\nCritic Decision:", decision)
    print(result)

    return state


def route_after_critique(state):

    if state["critique"].startswith(
        "RESEARCH_REQUIRED"
    ):

        if state.get("research_round", 0) < 2:

            return "research"

    return "report"