import asyncio
import json
import uuid
from datetime import datetime, timezone
from typing import AsyncGenerator

from fastapi import APIRouter, HTTPException
from sse_starlette.sse import EventSourceResponse

from backend.agents.orchestrator import run_research
from backend.api.schemas import ResearchRequest, ResearchResponse
from backend.db.database import get_db_session
from backend.db.models import ResearchSession

router = APIRouter(prefix="/research", tags=["research"])

# In-memory store for active SSE queues: session_id -> asyncio.Queue
_active_sessions: dict[str, asyncio.Queue] = {}


@router.post("", response_model=ResearchResponse)
async def start_research(request: ResearchRequest):
    """
    Kick off a research pipeline and return a session_id.
    The client immediately opens a GET /{session_id}/stream SSE connection.
    """
    if not request.query.strip():
        raise HTTPException(status_code=400, detail="Query cannot be empty")

    session_id = str(uuid.uuid4())
    event_queue: asyncio.Queue = asyncio.Queue()
    _active_sessions[session_id] = event_queue

    # Fire the pipeline in the background — the SSE route drains the queue
    asyncio.create_task(
        _run_and_persist(request.query.strip(), session_id, event_queue)
    )

    return ResearchResponse(session_id=session_id)


async def _run_and_persist(query: str, session_id: str, queue: asyncio.Queue):
    """Run pipeline, then persist the final result to the DB."""
    await run_research(query, session_id, queue)


@router.get("/{session_id}/stream")
async def stream_research(session_id: str):
    """
    SSE endpoint. Streams agent_step, complete, and error events.
    """
    queue = _active_sessions.get(session_id)
    if queue is None:
        raise HTTPException(status_code=404, detail="Session not found")

    async def event_generator() -> AsyncGenerator[dict, None]:
        try:
            while True:
                try:
                    event = await asyncio.wait_for(queue.get(), timeout=120.0)
                except asyncio.TimeoutError:
                    yield {"event": "heartbeat", "data": "{}"}
                    continue

                yield {
                    "event": event["type"],
                    "data": json.dumps(event["data"]),
                }

                if event["type"] in ("complete", "error"):
                    break
        finally:
            _active_sessions.pop(session_id, None)

    return EventSourceResponse(event_generator())


@router.get("/{session_id}")
async def get_research(session_id: str):
    """
    Return a completed research session from the DB.
    """
    async with get_db_session() as session:
        result = await session.get(ResearchSession, session_id)
        if not result:
            raise HTTPException(status_code=404, detail="Session not found")
        return result.to_dict()
