import feedparser
import time
from dataclasses import dataclass
from datetime import datetime, timedelta, timezone


@dataclass
class NewsHeadline:
    title: str
    link: str
    published: str
    source: str


@dataclass
class NewsData:
    headlines: list[NewsHeadline]
    fetched_at: str
    ticker: str


def get_news(ticker: str, company_name: str) -> NewsData:
    """
    Fetch news headlines from public RSS feeds.
    Uses Yahoo Finance RSS and Google News RSS.
    Free, no API key required.
    """
    headlines = []

    # Yahoo Finance RSS
    yahoo_url = (
        f"https://feeds.finance.yahoo.com/rss/2.0/headline"
        f"?s={ticker}&region=US&lang=en-US"
    )
    try:
        feed = feedparser.parse(yahoo_url)
        for entry in feed.entries[:8]:
            pub = entry.get("published", "")
            headlines.append(NewsHeadline(
                title=entry.get("title", ""),
                link=entry.get("link", ""),
                published=pub[:10] if pub else "",
                source="Yahoo Finance",
            ))
    except Exception:
        pass

    # Google News RSS fallback
    if len(headlines) < 5:
        query = f"{company_name}+stock+earnings"
        google_url = (
            f"https://news.google.com/rss/search"
            f"?q={query}&hl=en-US&gl=US&ceid=US:en"
        )
        try:
            time.sleep(0.5)
            feed = feedparser.parse(google_url)
            for entry in feed.entries[:5]:
                headlines.append(NewsHeadline(
                    title=entry.get("title", ""),
                    link=entry.get("link", ""),
                    published=entry.get("published", "")[:10],
                    source="Google News",
                ))
        except Exception:
            pass

    return NewsData(
        headlines=headlines[:10],
        fetched_at=datetime.now(timezone.utc).isoformat(),
        ticker=ticker,
    )
