import re
import yfinance as yf
from dataclasses import dataclass


@dataclass
class StockData:
    ticker: str
    company_name: str
    current_price: float
    previous_close: float
    change_percent: float
    volume: int
    market_cap: int | None
    pe_ratio: float | None
    week_52_high: float
    week_52_low: float
    price_history: list[dict]  # [{date: str, close: float}, ...]
    currency: str


def get_stock_data(ticker: str) -> StockData:
    """
    Fetch real stock data from Yahoo Finance via yfinance.
    No API key required. Rate limit: be respectful with requests.
    """
    try:
        yf_ticker = yf.Ticker(ticker.upper())
        info = yf_ticker.info

        if not info or "regularMarketPrice" not in info:
            raise ValueError(f"Ticker '{ticker}' not found or no data available")

        # 1-year price history
        hist = yf_ticker.history(period="1y")
        price_history = []
        for date, row in hist.iterrows():
            price_history.append({
                "date": date.strftime("%Y-%m-%d"),
                "close": round(float(row["Close"]), 2)
            })

        current = info.get("regularMarketPrice") or info.get("currentPrice", 0)
        prev = info.get("previousClose", current)
        change_pct = ((current - prev) / prev * 100) if prev else 0

        return StockData(
            ticker=ticker.upper(),
            company_name=info.get("longName", ticker),
            current_price=round(current, 2),
            previous_close=round(prev, 2),
            change_percent=round(change_pct, 2),
            volume=info.get("regularMarketVolume", 0),
            market_cap=info.get("marketCap"),
            pe_ratio=info.get("trailingPE"),
            week_52_high=info.get("fiftyTwoWeekHigh", 0),
            week_52_low=info.get("fiftyTwoWeekLow", 0),
            price_history=price_history,
            currency=info.get("currency", "USD")
        )
    except Exception as e:
        raise ValueError(f"Failed to fetch data for {ticker}: {str(e)}")


def resolve_ticker(company_name: str, llm) -> str:
    """
    Use local LLM to resolve company name to ticker.
    "Apple" -> "AAPL", "Microsoft" -> "MSFT"
    """
    prompt = f"""Return ONLY the stock ticker symbol for this company.
No explanation. No punctuation. Just the ticker.

Company: {company_name}
Ticker:"""
    response = llm.invoke(prompt)
    ticker = response.content.strip().upper()

    match = re.match(r'^[A-Z]{1,5}$', ticker)
    if not match:
        fallbacks = {
            "apple": "AAPL", "microsoft": "MSFT",
            "google": "GOOGL", "alphabet": "GOOGL",
            "amazon": "AMZN", "tesla": "TSLA",
            "nvidia": "NVDA", "meta": "META",
        }
        return fallbacks.get(company_name.lower(), company_name.upper()[:4])
    return ticker
