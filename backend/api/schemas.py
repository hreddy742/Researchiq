from pydantic import BaseModel
from typing import Optional


class ResearchRequest(BaseModel):
    query: str


class ResearchResponse(BaseModel):
    session_id: str
    status: str = "started"


class AgentStepSchema(BaseModel):
    agent: str
    status: str
    output: str
    duration_ms: int


class StockDataSchema(BaseModel):
    ticker: str
    company_name: str
    current_price: float
    previous_close: float
    change_percent: float
    volume: int
    market_cap: Optional[int] = None
    pe_ratio: Optional[float] = None
    week_52_high: float
    week_52_low: float
    price_history: list[dict]
    currency: str


class SentimentSchema(BaseModel):
    score: float
    label: str
    summary: str


class ResearchResultSchema(BaseModel):
    session_id: str
    query: str
    ticker: str
    company_name: str
    stock_data: Optional[dict] = None
    news_data: Optional[dict] = None
    filing_data: Optional[dict] = None
    sentiment: Optional[dict] = None
    report: str = ""
    agent_steps: list[AgentStepSchema] = []
    status: str
    created_at: str
