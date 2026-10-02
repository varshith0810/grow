from __future__ import annotations

import gzip
import json
import logging
import threading
import time
from dataclasses import dataclass, asdict
from typing import Any

import httpx
import upstox_client

from .settings import settings

log = logging.getLogger(__name__)

INSTRUMENT_URL = "https://assets.upstox.com/market-quote/instruments/exchange/NSE.json.gz"


@dataclass
class LiveQuote:
    symbol: str
    name: str
    exchange: str
    price: float
    change_pct: float
    volume: int = 0
    instrument_key: str = ""
    updated_at: int = 0


class MarketStreamManager:
    """Process-local live market cache backed by Upstox MarketDataStreamerV3."""

    def __init__(self) -> None:
        self._lock = threading.RLock()
        self._quotes: dict[str, LiveQuote] = {}
        self._symbol_to_key: dict[str, str] = {}
        self._key_to_meta: dict[str, dict[str, Any]] = {}
        self._streamer: Any = None
        self._thread: threading.Thread | None = None
        self._started = False
        self._last_error: str | None = None

    @property
    def enabled(self) -> bool:
        return bool(settings.upstox_analytics_token)

    def status(self) -> dict[str, Any]:
        with self._lock:
            return {
                "provider": "upstox",
                "enabled": self.enabled,
                "connected": self._streamer is not None,
                "instruments": len(self._symbol_to_key),
                "quotes": len(self._quotes),
                "last_error": self._last_error,
            }

    def start(self) -> None:
        if not self.enabled or self._started:
            return
        self._started = True
        self._thread = threading.Thread(target=self._run, name="upstox-market-stream", daemon=True)
        self._thread.start()

    def _load_instruments(self) -> list[str]:
        requested = [x.strip().upper() for x in settings.upstox_instrument_keys.split(",") if x.strip()]
        if requested:
            return requested

        with httpx.Client(timeout=30.0) as client:
            response = client.get(INSTRUMENT_URL)
            response.raise_for_status()
            raw = gzip.decompress(response.content)

        data = json.loads(raw)
        keys: list[str] = []
        for item in data:
            if item.get("segment") != "NSE_EQ":
                continue
            if item.get("instrument_type") not in {"EQ", "BE", "SM"}:
                continue
            key = item.get("instrument_key")
            symbol = item.get("trading_symbol")
            if not key or not symbol:
                continue
            keys.append(key)
            self._key_to_meta[key] = item
            self._symbol_to_key[symbol.upper()] = key

        limit = max(1, min(settings.upstox_max_instruments, 5000))
        return keys[:limit]

    def _run(self) -> None:
        try:
            keys = self._load_instruments()
            if not keys:
                raise RuntimeError("No Upstox instrument keys were loaded")

            configuration = upstox_client.Configuration()
            configuration.access_token = settings.upstox_access_token
            api_client = upstox_client.ApiClient(configuration)

            self._streamer = upstox_client.MarketDataStreamerV3(
                api_client,
                keys,
                "ltpc",
            )
            self._streamer.on("open", lambda: log.info("Upstox live market stream connected: %s instruments", len(keys)))
            self._streamer.on("message", self._on_message)
            self._streamer.on("error", self._on_error)
            self._streamer.on("close", self._on_close)
            self._streamer.auto_reconnect(True, 5, 10)
            self._streamer.connect()
        except Exception as exc:
            self._last_error = str(exc)
            log.exception("Unable to start Upstox live market stream")
            self._streamer = None

    def _on_error(self, error: Any) -> None:
        self._last_error = str(error)
        log.error("Upstox market stream error: %s", error)

    def _on_close(self, *args: Any) -> None:
        log.warning("Upstox market stream closed")

    def _on_message(self, message: dict[str, Any]) -> None:
        feeds = message.get("feeds", {})
        now = int(time.time() * 1000)
        with self._lock:
            for key, payload in feeds.items():
                ltpc = payload.get("ltpc")
                if not ltpc:
                    # Some SDK versions wrap LTPC one level deeper.
                    ltpc = self._find_ltpc(payload)
                if not ltpc:
                    continue

                price = self._number(ltpc.get("ltp"))
                previous = self._number(ltpc.get("cp"))
                if price is None:
                    continue

                meta = self._key_to_meta.get(key, {})
                symbol = str(meta.get("trading_symbol") or key.split("|")[-1]).upper()
                name = str(meta.get("name") or symbol)
                change = ((price / previous) - 1) * 100 if previous else 0.0
                self._quotes[symbol] = LiveQuote(
                    symbol=symbol,
                    name=name,
                    exchange="NSE",
                    price=price,
                    change_pct=change,
                    volume=int(self._number(ltpc.get("ltq")) or 0),
                    instrument_key=key,
                    updated_at=int(self._number(ltpc.get("ltt")) or now),
                )

    @staticmethod
    def _find_ltpc(value: Any) -> dict[str, Any] | None:
        if isinstance(value, dict):
            if isinstance(value.get("ltpc"), dict):
                return value["ltpc"]
            for child in value.values():
                found = MarketStreamManager._find_ltpc(child)
                if found:
                    return found
        return None

    @staticmethod
    def _number(value: Any) -> float | None:
        try:
            return float(value)
        except (TypeError, ValueError):
            return None

    def snapshot(self, symbols: list[str] | None = None) -> list[dict[str, Any]]:
        with self._lock:
            values = list(self._quotes.values())
        if symbols:
            wanted = {s.upper() for s in symbols}
            values = [q for q in values if q.symbol in wanted]
        return [asdict(q) for q in values]

    def get(self, symbol: str) -> dict[str, Any] | None:
        with self._lock:
            quote = self._quotes.get(symbol.upper())
            return asdict(quote) if quote else None


market_stream = MarketStreamManager()
