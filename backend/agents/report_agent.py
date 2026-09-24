import time
from datetime import datetime, timezone

from langchain_core.messages import HumanMessage, SystemMessage
from langchain_ollama import ChatOllama

from backend.agents.state import AgentStep, ResearchState
from backend.core.config import get_settings

REPORT_SYSTEM = """You are a senior financial analyst writing a concise investment brief.
Rules:
- Use only the data provided. Never fabricate numbers.
- Be specific — use exact figures from the data.
- If data is missing, say "data unavailable" rather than guessing.
- Keep the total response under 600 words."""


def build_report_prompt(state: ResearchState) -> str:
    stock = state.get("stock_data", {})
    news = state.get("news_data", {})
    filing = state.get("filing_data", {})
    sentiment = state.get("sentiment", {})

    headlines = "\n".join(
        f"  - {h['title']} ({h['published']})"
        for h in news.get("headlines", [])[:5]
    )

    market_cap = stock.get("market_cap")
    market_cap_str = f"${market_cap:,}" if market_cap else "N/A"

    return f"""Write a structured investment brief for {state['company_name']} ({state['ticker']}).

=== DATA PROVIDED ===

Financial Data:
  Current Price: ${stock.get('current_price', 'N/A')}
  Change: {stock.get('change_percent', 'N/A')}%
  Market Cap: {market_cap_str}
  P/E Ratio: {stock.get('pe_ratio', 'N/A')}
  52-Week High: ${stock.get('week_52_high', 'N/A')}
  52-Week Low: ${stock.get('week_52_low', 'N/A')}

SEC Filings:
  Latest 10-K: {filing.get('latest_10k_date', 'Not found')}
  SEC URL: {filing.get('latest_10k_url', 'N/A')}

Recent News Headlines:
{headlines if headlines else '  No recent headlines found'}

News Sentiment:
  Score: {sentiment.get('score', 0):.2f} ({sentiment.get('label', 'unknown')})
  Summary: {sentiment.get('summary', 'N/A')}

=== REQUIRED FORMAT ===

## Executive Summary
[2-3 sentences: current position and key highlights]

## Financial Snapshot
[Price, valuation metrics, 52-week range with specific numbers]

## Recent Developments
[Based on news headlines above — summarize key themes]

## Risk Factors
[2-3 risks based on available data and sector knowledge]

## Sentiment Analysis
[Interpret the {sentiment.get('score', 0):.2f} sentiment score in context]

Write the brief now:"""


async def report_agent(state: ResearchState) -> dict:
    """
    Synthesizes all collected data into a structured research report.
    Uses local llama3.2:3b via Ollama. No cloud LLM API needed.
    """
    start = time.time()
    settings = get_settings()
    llm = ChatOllama(
        model=settings.OLLAMA_MODEL,
        base_url=settings.OLLAMA_URL,
        temperature=0.2,
        num_predict=800,
    )

    try:
        prompt = build_report_prompt(state)
        messages = [
            SystemMessage(content=REPORT_SYSTEM),
            HumanMessage(content=prompt),
        ]
        response = llm.invoke(messages)
        report = response.content
        duration = int((time.time() - start) * 1000)

        return {
            "report": report,
            "agent_steps": [AgentStep(
                agent="report",
                status="complete",
                output=f"Report generated ({len(report.split())} words)",
                duration_ms=duration,
                timestamp=datetime.now(timezone.utc).isoformat(),
            )],
        }
    except Exception as e:
        return {
            "report": f"Report generation failed: {str(e)}",
            "agent_steps": [AgentStep(
                agent="report",
                status="error",
                output=str(e),
                duration_ms=int((time.time() - start) * 1000),
                timestamp=datetime.now(timezone.utc).isoformat(),
            )],
        }
