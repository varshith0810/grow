import asyncio
import json
from datetime import datetime, time
from zoneinfo import ZoneInfo

from fastapi import APIRouter, Query
from fastapi.responses import StreamingResponse

from ..market_stream import market_stream
from ..providers import MarketProviderRegistry

router = APIRouter()
providers = MarketProviderRegistry()
IST = ZoneInfo("Asia/Kolkata")


def _market_open() -> bool:
    now = datetime.now(IST)
    return now.weekday() < 5 and time(9, 15) <= now.time() <= time(15, 30)


def _fallback_quotes():
    return [q.model_dump() for q in providers.market.quotes()]


@router.get("/quotes")
def quotes():
    live = market_stream.snapshot()
    fallback = _fallback_quotes()
    by_symbol = {q["symbol"]: q for q in fallback}
    by_symbol.update({q["symbol"]: q for q in live})
    return list(by_symbol.values())


@router.get("/live/status")
def live_status():
    status = market_stream.status()
    status["market_open"] = _market_open()
    return status


@router.get("/stream")
async def stream(symbols: str = Query("", description="Comma-separated NSE symbols")):
    requested = [s.strip().upper() for s in symbols.split(",") if s.strip()]

    async def event_stream():
        last_payload = ""
        while True:
            live = market_stream.snapshot(requested or None)
            fallback = _fallback_quotes()
            by_symbol = {q["symbol"]: q for q in fallback}
            by_symbol.update({q["symbol"]: q for q in live})
            snapshot = list(by_symbol.values())
            payload = json.dumps(snapshot, separators=(",", ":"))
            if payload != last_payload:
                yield f"event: quotes\ndata: {payload}\n\n"
                last_payload = payload
            await asyncio.sleep(0.5)

    return StreamingResponse(
        event_stream(),
        media_type="text/event-stream",
        headers={"Cache-Control": "no-cache", "Connection": "keep-alive", "X-Accel-Buffering": "no"},
    )


@router.get("/rankings")
def rankings(period: str = Query("day", pattern="^(live|day|weekly|yearly)$")):
    quotes = quotes()
    ordered = sorted(quotes, key=lambda q: q["change_pct"], reverse=True)
    return {"period": period, "top": ordered[:10], "worst": ordered[-10:][::-1]}
