import asyncio
import json
import time
from datetime import datetime, timezone

from langchain_ollama import ChatOllama

from backend.agents.state import AgentStep, ResearchState
from backend.core.config import get_settings
from backend.tools.news_fetcher import get_news


async def news_agent(state: ResearchState) -> dict:
    """
    Fetches real news from Yahoo Finance RSS and Google News.
    Uses local LLM to score overall sentiment from headlines.
    """
    start = time.time()
    settings = get_settings()
    try:
        news = await asyncio.to_thread(
            get_news, state["ticker"], state["company_name"]
        )

        if not news.headlines:
            sentiment = {
                "score": 0.0,
                "label": "neutral",
                "summary": "No recent news found",
            }
        else:
            llm = ChatOllama(
                model=settings.OLLAMA_MODEL,
                base_url=settings.OLLAMA_URL,
                temperature=0.0,
                format="json",
            )
            headlines_text = "\n".join(
                f"- {h.title}" for h in news.headlines[:8]
            )
            prompt = f"""Analyze the sentiment of these news headlines about {state['company_name']}.

Headlines:
{headlines_text}

Return a JSON object with exactly these fields:
{{
  "score": <float from -1.0 (very negative) to 1.0 (very positive)>,
  "label": <"positive" or "neutral" or "negative">,
  "summary": <one sentence summarizing the overall news sentiment>
}}"""
            response = llm.invoke(prompt)
            try:
                sentiment = json.loads(response.content)
            except Exception:
                sentiment = {
                    "score": 0.0,
                    "label": "neutral",
                    "summary": "Unable to parse sentiment",
                }

        duration = int((time.time() - start) * 1000)
        return {
            "news_data": {
                "headlines": [
                    {
                        "title": h.title,
                        "link": h.link,
                        "published": h.published,
                        "source": h.source,
                    }
                    for h in news.headlines
                ],
                "fetched_at": news.fetched_at,
            },
            "sentiment": sentiment,
            "agent_steps": [AgentStep(
                agent="news",
                status="complete",
                output=(
                    f"{len(news.headlines)} headlines · "
                    f"Sentiment: {sentiment.get('label', 'unknown')} "
                    f"({sentiment.get('score', 0):.2f})"
                ),
                duration_ms=duration,
                timestamp=datetime.now(timezone.utc).isoformat(),
            )],
        }
    except Exception as e:
        return {
            "news_data": {"headlines": []},
            "sentiment": {"score": 0.0, "label": "neutral", "summary": str(e)},
            "agent_steps": [AgentStep(
                agent="news",
                status="error",
                output=f"News fetch failed: {str(e)}",
                duration_ms=int((time.time() - start) * 1000),
                timestamp=datetime.now(timezone.utc).isoformat(),
            )],
        }
