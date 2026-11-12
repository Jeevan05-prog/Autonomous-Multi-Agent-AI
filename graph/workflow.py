from langgraph.graph import StateGraph, START, END

from models.state import AgentState

from agents.planner import planner_agent
from agents.researcher import researcher_agent
from agents.data_analyst import data_analyst_agent
from agents.insight import insight_agent
from agents.critic import critic_agent, route_after_critique
from agents.report import report_agent


def run_researcher(state):

    state["research_round"] = (
        state.get("research_round", 0) + 1
    )

    print(
        f"\nResearch Attempt: {state['research_round']}"
    )

    return researcher_agent(state)


def create_workflow():

    builder = StateGraph(AgentState)

    # Register agents
    builder.add_node("planner", planner_agent)

    builder.add_node("researcher", run_researcher)

    builder.add_node("data_analyst", data_analyst_agent)

    builder.add_node("insight", insight_agent)

    builder.add_node("critic", critic_agent)

    builder.add_node("report", report_agent)

    # Main workflow
    builder.add_edge(START, "planner")

    builder.add_edge("planner", "researcher")

    builder.add_edge("researcher", "data_analyst")

    builder.add_edge("data_analyst", "insight")

    builder.add_edge("insight", "critic")

    # Conditional workflow
    builder.add_conditional_edges(
        "critic",
        route_after_critique,
        {
            "research": "researcher",
            "report": "report"
        }
    )

    builder.add_edge("report", END)

    return builder.compile()