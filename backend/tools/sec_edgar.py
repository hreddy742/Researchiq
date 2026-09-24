import httpx
import time
from dataclasses import dataclass

EDGAR_BASE = "https://data.sec.gov"


@dataclass
class FilingData:
    ticker: str
    company_name: str
    cik: str
    latest_10k_date: str | None
    latest_10k_url: str | None
    found: bool
    error: str | None


def get_filings(ticker: str, user_agent: str) -> FilingData:
    """
    Fetch SEC filing data from EDGAR API.
    Free, no API key. Official US SEC public API.
    Required: User-Agent header identifying your application.
    Rate limit: 10 requests/second max.
    """
    headers = {"User-Agent": user_agent, "Accept": "application/json"}

    try:
        # Step 1: Get CIK from ticker via company tickers endpoint
        time.sleep(0.1)
        tickers_resp = httpx.get(
            "https://www.sec.gov/files/company_tickers.json",
            headers=headers,
            timeout=15,
        )
        tickers_data = tickers_resp.json()

        cik = None
        company_name = ticker
        for entry in tickers_data.values():
            if entry.get("ticker", "").upper() == ticker.upper():
                cik = str(entry["cik_str"]).zfill(10)
                company_name = entry.get("title", ticker)
                break

        if not cik:
            return FilingData(
                ticker=ticker, company_name=ticker, cik="",
                latest_10k_date=None, latest_10k_url=None,
                found=False, error="CIK not found for ticker"
            )

        # Step 2: Fetch submissions
        time.sleep(0.1)
        subs_resp = httpx.get(
            f"{EDGAR_BASE}/submissions/CIK{cik}.json",
            headers=headers,
            timeout=15,
        )
        subs = subs_resp.json()

        # Step 3: Find latest 10-K
        filings = subs.get("filings", {}).get("recent", {})
        forms = filings.get("form", [])
        dates = filings.get("filingDate", [])
        accessions = filings.get("accessionNumber", [])

        latest_10k_date = None
        latest_10k_url = None

        for form, date, accession in zip(forms, dates, accessions):
            if form == "10-K":
                latest_10k_date = date
                acc_clean = accession.replace("-", "")
                latest_10k_url = (
                    f"https://www.sec.gov/Archives/edgar/data/"
                    f"{int(cik)}/{acc_clean}/{accession}-index.htm"
                )
                break

        return FilingData(
            ticker=ticker,
            company_name=company_name,
            cik=cik,
            latest_10k_date=latest_10k_date,
            latest_10k_url=latest_10k_url,
            found=True,
            error=None,
        )

    except Exception as e:
        return FilingData(
            ticker=ticker, company_name=ticker, cik="",
            latest_10k_date=None, latest_10k_url=None,
            found=False, error=str(e)
        )
