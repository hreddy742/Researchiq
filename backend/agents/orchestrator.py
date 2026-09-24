import asyncio
from datetime import datetime, timezone

from langchain_ollama import ChatOllama
from langgraph.checkpoint.memory import MemorySaver
from langgraph.graph import END, StateGraph

from backend.agents.filing_agent import filing_agent
from backend.agents.financial_agent import financial_agent
from backend.agents.news_agent import news_agent
from backend.agents.report_agent import report_agent
from backend.agents.state import ResearchState
from backend.core.config import get_settings
from backend.tools.stock_data import resolve_ticker


async def extract_ticker_node(state: ResearchState) -> dict:
    """Extract stock ticker from natural language query using local LLM."""
    settings = get_settings()
    llm = ChatOllama(
        model=settings.OLLAMA_MODEL,
        base_url=settings.OLLAMA_URL,
        temperature=0.0,
    )
    ticker = resolve_ticker(state["query"], llm)
    return {"ticker": ticker, "company_name": state["query"]}


async def parallel_research_node(state: ResearchState) -> dict:
    """Run all 3 data agents in parallel for speed."""
    results = await asyncio.gather(
        financial_agent(state),
        news_agent(state),
        filing_agent(state),
        return_exceptions=True,
    )
    merged: dict = {}
    for r in results:
        if isinstance(r, dict):
            merged.update(r)
    return merged


def build_graph():
    graph = StateGraph(ResearchState)
    graph.add_node("extract_ticker", extract_ticker_node)
    graph.add_node("parallel_research", parallel_research_node)
    graph.add_node("generate_report", report_agent)

    graph.set_entry_point("extract_ticker")
    graph.add_edge("extract_ticker", "parallel_research")
    graph.add_edge("parallel_research", "generate_report")
    graph.add_edge("generate_report", END)

    memory = MemorySaver()
    return graph.compile(checkpointer=memory)


_graph = None


def get_graph():
    global _graph
    if _graph is None:
        _graph = build_graph()
    return _graph


async def run_research(
    query: str, session_id: str, event_queue: asyncio.Queue
):
    """
    Run the full research pipeline and push events to queue.
    Events are consumed by the SSE route and streamed to the browser.
    """
    graph = get_graph()
    initial_state: ResearchState = {
        "query": query,
        "ticker": "",
        "company_name": query,
        "stock_data": {},
        "news_data": {},
        "filing_data": {},
        "sentiment": {},
        "report": "",
        "agent_steps": [],
        "error": None,
        "session_id": session_id,
    }

    config = {"configurable": {"thread_id": session_id}}

    try:
        async for event in graph.astream_events(initial_state, config, version="v1"):
            kind = event.get("event")
            name = event.get("name", "")

            if kind == "on_chain_end" and name in (
                "extract_ticker",
                "parallel_research",
                "generate_report",
            ):
                output = event.get("data", {}).get("output", {})
                steps = output.get("agent_steps", [])
                for step in steps:
                    await event_queue.put({
                        "type": "agent_step",
                        "data": {
                            "agent": step.agent,
                            "status": step.status,
                            "output": step.output,
                            "duration_ms": step.duration_ms,
                        },
                    })

        # Get final state
        final_state = graph.get_state(config).values
        await event_queue.put({
            "type": "complete",
            "data": {
                "stock_data": final_state.get("stock_data", {}),
                "news_data": final_state.get("news_data", {}),
                "sentiment": final_state.get("sentiment", {}),
                "report": final_state.get("report", ""),
                "agent_steps": [
                    {
                        "agent": s.agent,
                        "status": s.status,
                        "output": s.output,
                        "duration_ms": s.duration_ms,
                    }
                    for s in final_state.get("agent_steps", [])
                ],
            },
        })
    except Exception as e:
        await event_queue.put({
            "type": "error",
            "data": {"message": str(e)},
        })
