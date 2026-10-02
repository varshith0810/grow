from fastapi import APIRouter, Query
from ..providers import MarketProviderRegistry

router = APIRouter()
providers = MarketProviderRegistry()

@router.get("/quotes")
def quotes():
    return providers.market.quotes()

@router.get("/rankings")
def rankings(period: str = Query("day", pattern="^(live|day|weekly|yearly)$")):
    quotes = providers.market.quotes()
    ordered = sorted(quotes, key=lambda q: q.change_pct, reverse=True)
    return {"period": period, "top": ordered[:10], "worst": ordered[-10:][::-1]}
