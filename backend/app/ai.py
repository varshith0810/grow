import json
import boto3
from .settings import settings

class BedrockPredictor:
    def __init__(self):
        self.client = boto3.client("bedrock-runtime", region_name=settings.aws_region)

    def predict(self, symbol: str, timeframe: str):
        prompt = f"""You are a market-analysis assistant.
Stock: {symbol}
Timeframe: {timeframe}
Return JSON with signal (GREEN, RED, or NEUTRAL), confidence from 0 to 1, rationale (array of strings), and risk.
Do not claim certainty or provide personalized financial advice."""
        try:
            response = self.client.converse(
                modelId=settings.bedrock_model_id,
                messages=[{"role":"user","content":[{"text":prompt}]}],
                inferenceConfig={"maxTokens":500, "temperature":0.1},
            )
            raw = response["output"]["message"]["content"][0]["text"]
            data = json.loads(raw)
            return {"symbol": symbol, "timeframe": timeframe, **data}
        except Exception:
            return {
                "symbol": symbol, "timeframe": timeframe,
                "signal": "NEUTRAL", "confidence": 0,
                "rationale": ["Prediction service is not configured or market inputs are unavailable."],
                "risk": "Unavailable"
            }
