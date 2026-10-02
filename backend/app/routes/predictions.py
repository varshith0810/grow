from fastapi import APIRouter, Query
from ..ai import BedrockPredictor

router = APIRouter()
predictor = BedrockPredictor()

@router.get("/{symbol}")
def predict(symbol: str, timeframe: str = Query("15m", pattern="^(live|1m|15m|1h|1d|1w|1yr)$")):
    return predictor.predict(symbol.upper(), timeframe)
