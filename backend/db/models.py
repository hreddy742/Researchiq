import json
from datetime import datetime, timezone

from sqlalchemy import JSON, Column, DateTime, String, Text
from sqlalchemy.orm import DeclarativeBase


class Base(DeclarativeBase):
    pass


class ResearchSession(Base):
    __tablename__ = "research_sessions"

    id = Column(String, primary_key=True)
    query = Column(String, nullable=False)
    ticker = Column(String, nullable=True)
    company_name = Column(String, nullable=True)
    stock_data = Column(JSON, nullable=True)
    news_data = Column(JSON, nullable=True)
    filing_data = Column(JSON, nullable=True)
    sentiment = Column(JSON, nullable=True)
    report = Column(Text, nullable=True)
    agent_steps = Column(JSON, nullable=True)
    status = Column(String, default="pending")
    created_at = Column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
    )

    def to_dict(self) -> dict:
        return {
            "session_id": self.id,
            "query": self.query,
            "ticker": self.ticker,
            "company_name": self.company_name,
            "stock_data": self.stock_data,
            "news_data": self.news_data,
            "filing_data": self.filing_data,
            "sentiment": self.sentiment,
            "report": self.report,
            "agent_steps": self.agent_steps,
            "status": self.status,
            "created_at": self.created_at.isoformat() if self.created_at else None,
        }
