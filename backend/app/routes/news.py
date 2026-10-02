from fastapi import APIRouter
from ..providers import MarketProviderRegistry

router = APIRouter()
providers = MarketProviderRegistry()

@router.get("/{symbol}")
def news(symbol: str):
    return providers.news.news(symbol.upper())[:10]
