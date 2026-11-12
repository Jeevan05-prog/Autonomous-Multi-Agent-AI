from typing import TypedDict, List


class AgentState(TypedDict):

    user_request: str

    plan: List[str]

    research: str

    dataset_path: str

    analysis: str

    insights: str

    critique: str

    final_report: str

    research_round: int