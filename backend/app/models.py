from pydantic import BaseModel
from typing import Literal

class Quote(BaseModel):
    symbol: str
    name: str
    exchange: Literal["NSE", "BSE"]
    price: float
    change_pct: float
    volume: int = 0

class NewsArticle(BaseModel):
    title: str
    source: str
    url: str
    published_at: str

class Prediction(BaseModel):
    symbol: str
    timeframe: str
    signal: Literal["GREEN", "RED", "NEUTRAL"]
    confidence: float
    rationale: list[str]
    risk: str
