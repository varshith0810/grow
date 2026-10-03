import asyncio
import json

from fastapi import APIRouter, Query
from fastapi.responses import StreamingResponse

from ..market_stream import market_stream
from ..providers import MarketProviderRegistry

router = APIRouter()
providers = MarketProviderRegistry()


@router.get("/quotes")
def quotes():
    live = market_stream.snapshot()
    return live if live else [q.model_dump() for q in providers.market.quotes()]


@router.get("/live/status")
def live_status():
    return market_stream.status()


@router.get("/stream")
async def stream(symbols: str = Query("", description="Comma-separated NSE symbols")):
    requested = [s.strip().upper() for s in symbols.split(",") if s.strip()]

    async def event_stream():
        last_payload = ""
        while True:
            snapshot = market_stream.snapshot(requested or None)
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
    quotes = market_stream.snapshot() or [q.model_dump() for q in providers.market.quotes()]
    ordered = sorted(quotes, key=lambda q: q["change_pct"], reverse=True)
    return {"period": period, "top": ordered[:10], "worst": ordered[-10:][::-1]}
