import asyncio
import time
from datetime import datetime, timezone

from backend.agents.state import AgentStep, ResearchState
from backend.core.config import get_settings
from backend.tools.sec_edgar import get_filings


async def filing_agent(state: ResearchState) -> dict:
    """
    Fetches SEC filing data from EDGAR public API.
    No API key required. Official US government data source.
    """
    start = time.time()
    settings = get_settings()
    try:
        filing = await asyncio.to_thread(
            get_filings, state["ticker"], settings.SEC_USER_AGENT
        )
        duration = int((time.time() - start) * 1000)

        if filing.found and filing.latest_10k_date:
            output = f"Latest 10-K: {filing.latest_10k_date} | CIK: {filing.cik}"
        else:
            output = filing.error or "No 10-K filing found"

        return {
            "filing_data": {
                "cik": filing.cik,
                "company_name": filing.company_name,
                "latest_10k_date": filing.latest_10k_date,
                "latest_10k_url": filing.latest_10k_url,
                "found": filing.found,
            },
            "agent_steps": [AgentStep(
                agent="filings",
                status="complete" if filing.found else "error",
                output=output,
                duration_ms=duration,
                timestamp=datetime.now(timezone.utc).isoformat(),
            )],
        }
    except Exception as e:
        return {
            "filing_data": {"found": False, "error": str(e)},
            "agent_steps": [AgentStep(
                agent="filings",
                status="error",
                output=str(e),
                duration_ms=int((time.time() - start) * 1000),
                timestamp=datetime.now(timezone.utc).isoformat(),
            )],
        }
