from typing import TypedDict, Annotated
from dataclasses import dataclass
import operator


@dataclass
class AgentStep:
    agent: str
    status: str  # pending | running | complete | error
    output: str
    duration_ms: int
    timestamp: str


class ResearchState(TypedDict):
    query: str
    ticker: str
    company_name: str
    stock_data: dict
    news_data: dict
    filing_data: dict
    sentiment: dict
    report: str
    agent_steps: Annotated[list[AgentStep], operator.add]
    error: str | None
    session_id: str
