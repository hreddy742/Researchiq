import asyncio
import time
from datetime import datetime, timezone

from backend.agents.state import AgentStep, ResearchState
from backend.tools.stock_data import get_stock_data


async def financial_agent(state: ResearchState) -> dict:
    """
    Fetches real stock data from Yahoo Finance via yfinance.
    Runs in a thread to avoid blocking the async event loop.
    """
    start = time.time()
    try:
        stock = await asyncio.to_thread(get_stock_data, state["ticker"])
        duration = int((time.time() - start) * 1000)

        sign = "+" if stock.change_percent >= 0 else ""
        if stock.market_cap:
            output = (
                f"${stock.current_price} ({sign}{stock.change_percent}%) | "
                f"MCap: ${stock.market_cap:,}"
            )
        else:
            output = f"${stock.current_price} ({sign}{stock.change_percent}%)"

        return {
            "stock_data": {
                "ticker": stock.ticker,
                "company_name": stock.company_name,
                "current_price": stock.current_price,
                "previous_close": stock.previous_close,
                "change_percent": stock.change_percent,
                "volume": stock.volume,
                "market_cap": stock.market_cap,
                "pe_ratio": stock.pe_ratio,
                "week_52_high": stock.week_52_high,
                "week_52_low": stock.week_52_low,
                "price_history": stock.price_history,
                "currency": stock.currency,
            },
            "agent_steps": [AgentStep(
                agent="financial",
                status="complete",
                output=output,
                duration_ms=duration,
                timestamp=datetime.now(timezone.utc).isoformat(),
            )],
        }
    except Exception as e:
        return {
            "stock_data": {},
            "agent_steps": [AgentStep(
                agent="financial",
                status="error",
                output=f"Failed to fetch stock data: {str(e)}",
                duration_ms=int((time.time() - start) * 1000),
                timestamp=datetime.now(timezone.utc).isoformat(),
            )],
        }
