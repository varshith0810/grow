from __future__ import annotations

import logging
import threading
import time
from dataclasses import dataclass, asdict
from typing import Any

import yfinance as yf

from .settings import settings

log = logging.getLogger(__name__)

DEFAULT_SYMBOLS = [
    "RELIANCE.NS","TCS.NS","HDFCBANK.NS","INFY.NS","ICICIBANK.NS","ITC.NS","SBIN.NS",
    "ADANIENT.NS","TATAMOTORS.NS","WIPRO.NS","BHARTIARTL.NS","LT.NS","KOTAKBANK.NS",
    "AXISBANK.NS","MARUTI.NS","SUNPHARMA.NS","HCLTECH.NS","TITAN.NS","NTPC.NS",
    "POWERGRID.NS","ONGC.NS","COALINDIA.NS","BEL.NS","TECHM.NS","M&M.NS",
    "BAJFINANCE.NS","BAJAJFINSV.NS","INDUSINDBK.NS","HINDUNILVR.NS","ASIANPAINT.NS",
    "ULTRACEMCO.NS","NESTLEIND.NS","TATASTEEL.NS","JSWSTEEL.NS","ADANIPORTS.NS",
    "HINDALCO.NS","CIPLA.NS","DRREDDY.NS","EICHERMOT.NS","GRASIM.NS","DIVISLAB.NS",
    "APOLLOHOSP.NS","BRITANNIA.NS","HEROMOTOCO.NS","TATACONSUM.NS","SBILIFE.NS",
    "HDFCLIFE.NS","TRENT.NS","SHRIRAMFIN.NS",
]

@dataclass
class LiveQuote:
    symbol: str
    name: str
    exchange: str
    price: float
    change_pct: float
    volume: int = 0
    updated_at: int = 0

class MarketStreamManager:
    """Simple public Yahoo Finance WebSocket cache for the dashboard.

    This is market-data display only; it is not a broker or trading API.
    """

    def __init__(self) -> None:
        self._lock = threading.RLock()
        self._quotes: dict[str, LiveQuote] = {}
        self._thread: threading.Thread | None = None
        self._started = False
        self._connected = False
        self._last_error: str | None = None

    @property
    def symbols(self) -> list[str]:
        return settings.live_symbols_list or DEFAULT_SYMBOLS

    def status(self) -> dict[str, Any]:
        with self._lock:
            return {"provider":"yahoo-finance","enabled":True,"connected":self._connected,
                    "instruments":len(self.symbols),"quotes":len(self._quotes),
                    "last_error":self._last_error}

    def start(self) -> None:
        if self._started:
            return
        self._started = True
        self._thread = threading.Thread(target=self._run, name="yahoo-market-stream", daemon=True)
        self._thread.start()

    def _run(self) -> None:
        while True:
            try:
                self._connected = False
                with yf.WebSocket(verbose=False) as ws:
                    ws.subscribe(self.symbols)
                    self._connected = True
                    ws.listen(self._on_message)
            except Exception as exc:
                self._connected = False
                self._last_error = str(exc)
                log.warning("Yahoo live stream reconnecting: %s", exc)
                time.sleep(3)

    def _on_message(self, message: dict[str, Any]) -> None:
        try:
            symbol = str(message.get("id") or message.get("symbol") or "").upper()
            price = float(message.get("price") or 0)
            if not symbol or price <= 0:
                return
            change_pct = message.get("changePercent")
            if change_pct is None:
                change = message.get("change")
                previous = message.get("previousClose")
                change_pct = float(change) / float(previous) * 100 if change is not None and previous else 0.0
            clean = symbol.removesuffix(".NS")
            with self._lock:
                self._quotes[clean] = LiveQuote(clean, clean, "NSE", price, float(change_pct or 0),
                                                int(message.get("dayVolume") or 0),
                                                int(message.get("time") or time.time()*1000))
        except (TypeError, ValueError):
            return

    def snapshot(self, symbols: list[str] | None = None) -> list[dict[str, Any]]:
        with self._lock:
            values = list(self._quotes.values())
        if symbols:
            wanted = {s.upper().removesuffix(".NS") for s in symbols}
            values = [q for q in values if q.symbol in wanted]
        return [asdict(q) for q in values]

    def get(self, symbol: str) -> dict[str, Any] | None:
        with self._lock:
            quote = self._quotes.get(symbol.upper().removesuffix(".NS"))
            return asdict(quote) if quote else None

market_stream = MarketStreamManager()
