from fastapi import APIRouter, HTTPException
from ..providers import MarketProviderRegistry

router = APIRouter()
providers = MarketProviderRegistry()

@router.get("/{symbol}")
def stock(symbol: str):
    symbol = symbol.upper()
    quote = next((q for q in providers.market.quotes() if q.symbol == symbol), None)
    if not quote:
        raise HTTPException(status_code=404, detail="Stock not found")
    return {
        "quote": quote,
        "chart": {"timeframes": ["live","1m","15m","1h","1d","1w","1yr"], "candles": []}
    }
