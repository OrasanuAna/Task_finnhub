import os
import asyncio
from typing import Any, Dict, List, Literal, Optional

import httpx
from dotenv import load_dotenv
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, Field

load_dotenv()
FINNHUB_TOKEN = os.getenv("FINNHUB_TOKEN")
if not FINNHUB_TOKEN:
    raise RuntimeError("FINNHUB_TOKEN is missing. Put it in your .env file.")

FINNHUB_METRIC_URL = "https://finnhub.io/api/v1/stock/metric"

app = FastAPI(title="Company Ranker")


class SortSpec(BaseModel):
    by: Literal["pricePerEarnings", "pricePerBook", "pricePerBookValue", "pe_then_pb"] = "pricePerEarnings"
    direction: Literal["asc", "desc"] = "asc"


class RankRequest(BaseModel):
    symbols: List[str] = Field(..., min_length=1, max_length=15)
    sort: SortSpec = SortSpec()


def to_float_or_none(v: Any) -> Optional[float]:
    try:
        n = float(v)
        if n != n:  # NaN
            return None
        return n
    except Exception:
        return None


async def fetch_metrics(client: httpx.AsyncClient, symbol: str) -> Dict[str, Any]:
    """
    Calls Finnhub Company Basic Financials endpoint and extracts:
    - P/E TTM -> metric.peTTM
    - Price-to-Book -> metric.pb
    """
    params = {"symbol": symbol, "metric": "all", "token": FINNHUB_TOKEN}
    r = await client.get(FINNHUB_METRIC_URL, params=params, timeout=15.0)
    r.raise_for_status()
    data = r.json()

    m = data.get("metric", {}) or {}

    pe = to_float_or_none(m.get("peTTM"))
    pb = to_float_or_none(m.get("pb"))

    return {
        "symbol": symbol,
        "pricePerEarnings": pe,
        "pricePerBook": pb,
        "pricePerBookValue": pb,
    }


def sort_rows(rows: List[Dict[str, Any]], by: str, direction: str) -> List[Dict[str, Any]]:
    reverse = direction == "desc"

    def one_field_key(x: Dict[str, Any]):
        v = x.get(by)
        return (v is None, v)

    def two_field_key(x: Dict[str, Any]):
        pe = x.get("pricePerEarnings")
        pb = x.get("pricePerBook")
        return (
            pe is None, pe,
            pb is None, pb
        )

    key_fn = two_field_key if by == "pe_then_pb" else one_field_key
    return sorted(rows, key=key_fn, reverse=reverse)


@app.post("/rank")
async def rank_companies(payload: RankRequest):
    if len(payload.symbols) > 15:
        raise HTTPException(status_code=400, detail="Max 15 symbols allowed.")

    symbols = [s.strip().upper() for s in payload.symbols if s and s.strip()]
    if not symbols:
        raise HTTPException(status_code=400, detail="symbols must contain at least 1 valid symbol.")

    sem = asyncio.Semaphore(5)

    async def safe_fetch(sym: str, client: httpx.AsyncClient):
        async with sem:
            try:
                return await fetch_metrics(client, sym)
            except Exception:
                return {
                    "symbol": sym,
                    "pricePerEarnings": None,
                    "pricePerBook": None,
                    "pricePerBookValue": None,
                    "error": "failed_to_fetch",
                }

    async with httpx.AsyncClient() as client:
        rows = await asyncio.gather(*[safe_fetch(sym, client) for sym in symbols])

    sorted_rows = sort_rows(rows, payload.sort.by, payload.sort.direction)

    return {
        "inputCount": len(symbols),
        "sort": payload.sort.model_dump(),
        "data": sorted_rows,
    }
