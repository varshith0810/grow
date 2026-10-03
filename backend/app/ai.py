import json
import math
import boto3
import yfinance as yf
import feedparser
from urllib.parse import quote
from botocore.exceptions import BotoCoreError, ClientError
from .settings import settings

class BedrockPredictor:
    def __init__(self):
        self.client = None

    def _client(self):
        if not settings.bedrock_enabled:
            return None
        if self.client is None:
            self.client = boto3.client("bedrock-runtime", region_name=settings.aws_region)
        return self.client

    @staticmethod
    def _rsi(closes, period=14):
        if len(closes) <= period:
            return None
        gains, losses = [], []
        for a, b in zip(closes[-period-1:-1], closes[-period:]):
            delta = b - a
            gains.append(max(delta, 0))
            losses.append(max(-delta, 0))
        avg_gain = sum(gains) / period
        avg_loss = sum(losses) / period
        if avg_loss == 0:
            return 100.0
        return 100 - (100 / (1 + avg_gain / avg_loss))

    def _context(self, symbol: str):
        ticker = yf.Ticker(symbol + ".NS")
        hist = ticker.history(period="6mo", interval="1d", auto_adjust=False).dropna()
        if hist.empty:
            raise ValueError("No market data")
        closes = [float(x) for x in hist["Close"].tolist()]
        volumes = [float(x) for x in hist["Volume"].tolist()]
        last = closes[-1]
        prev = closes[-2] if len(closes) > 1 else last
        sma20 = sum(closes[-20:]) / min(20, len(closes))
        sma50 = sum(closes[-50:]) / min(50, len(closes))
        rsi = self._rsi(closes) or 50.0
        returns = [(b / a - 1) for a, b in zip(closes[-21:-1], closes[-20:]) if a]
        volatility = math.sqrt(sum((x - sum(returns)/len(returns))**2 for x in returns) / max(1, len(returns)-1)) if returns else 0
        avg_volume = sum(volumes[-20:]) / min(20, len(volumes))
        query = quote(f"{symbol} India stock")
        feed = feedparser.parse(f"https://news.google.com/rss/search?q={query}&hl=en-IN&gl=IN&ceid=IN:en")
        news = [entry.get("title", "") for entry in feed.entries[:10]]
        return {
            "symbol": symbol,
            "price": round(last, 2),
            "return_1d_pct": round((last / prev - 1) * 100, 2) if prev else 0,
            "return_20d_pct": round((last / closes[-21] - 1) * 100, 2) if len(closes) > 21 else 0,
            "sma20": round(sma20, 2),
            "sma50": round(sma50, 2),
            "rsi14": round(rsi, 2),
            "volatility_20d": round(volatility * 100, 2),
            "volume_vs_20d_avg_pct": round((volumes[-1] / avg_volume - 1) * 100, 2) if avg_volume else 0,
            "news": news,
        }

    @staticmethod
    def _local_prediction(context, timeframe):
        score = 50
        reasons = []
        risks = []
        if context["price"] > context["sma20"]:
            score += 12; reasons.append("Price is above the 20-day moving average.")
        else:
            score -= 12; reasons.append("Price is below the 20-day moving average.")
        if context["sma20"] > context["sma50"]:
            score += 12; reasons.append("The 20-day moving average is above the 50-day moving average.")
        else:
            score -= 12; reasons.append("The 20-day moving average is below the 50-day moving average.")
        if context["return_20d_pct"] > 0:
            score += 8; reasons.append("The 20-day return is positive.")
        else:
            score -= 8; reasons.append("The 20-day return is negative.")
        rsi = context["rsi14"]
        if rsi >= 70: score -= 8; risks.append("RSI is elevated; reversal risk is higher.")
        elif rsi <= 30: score += 4; risks.append("RSI is low; reversal risk is elevated.")
        if context["volatility_20d"] > 3: risks.append("Recent daily volatility is elevated.")
        score = max(0, min(100, score))
        signal = "GREEN" if score >= 62 else "RED" if score <= 38 else "NEUTRAL"
        confidence = max(0.35, min(0.85, 0.35 + abs(score - 50) / 50))
        if not risks: risks.append("Technical indicators do not guarantee future returns.")
        return {"symbol": context["symbol"], "timeframe": timeframe, "signal": signal, "confidence": round(confidence,2), "horizon": timeframe, "summary": "Zero-cost technical analysis using public historical data; this is not Claude.", "rationale": reasons, "risks": risks, "technical_score": round(score), "news_sentiment": "UNKNOWN", "context": context, "provider": "local-technical"}
    def predict(self, symbol: str, timeframe: str):
        try:
            context = self._context(symbol)
            client = self._client()
            if client is None:
                return self._local_prediction(context, timeframe)
            prompt = f"""You are a financial-market analysis assistant for an Indian stock analytics application.
Use the supplied quantitative market data and recent news as evidence. Do not invent prices, news, indicators, or facts.
Return ONLY valid JSON with this schema:
{{"signal":"GREEN|RED|NEUTRAL","confidence":0.0,"horizon":"...","summary":"...","rationale":["..."],"risks":["..."],"technical_score":0,"news_sentiment":"POSITIVE|NEGATIVE|MIXED|UNKNOWN"}}
The confidence must represent model confidence in the direction classification, not probability of profit.
Never claim certainty and never give personalized financial advice.
Timeframe: {timeframe}
Market context: {json.dumps(context, ensure_ascii=False)}
"""
            response = client.converse(
                modelId=settings.bedrock_model_id,
                messages=[{"role": "user", "content": [{"text": prompt}]}],
                inferenceConfig={"maxTokens": 700, "temperature": 0.1},
            )
            raw = response["output"]["message"]["content"][0]["text"].strip()
            if raw.startswith("```"):
                raw = raw.replace("```json", "").replace("```", "").strip()
            data = json.loads(raw)
            signal = data.get("signal", "NEUTRAL")
            if signal not in {"GREEN", "RED", "NEUTRAL"}:
                signal = "NEUTRAL"
            return {
                "symbol": symbol, "timeframe": timeframe, "signal": signal,
                "confidence": max(0, min(1, float(data.get("confidence", 0)))),
                "horizon": data.get("horizon", timeframe),
                "summary": data.get("summary", ""),
                "rationale": data.get("rationale", []),
                "risks": data.get("risks", []),
                "technical_score": max(0, min(100, int(data.get("technical_score", 0)))),
                "news_sentiment": data.get("news_sentiment", "UNKNOWN"),
                "context": context,
            }
        except (BotoCoreError, ClientError, ValueError, KeyError, json.JSONDecodeError, TypeError):
            return {
                "symbol": symbol, "timeframe": timeframe, "signal": "NEUTRAL",
                "confidence": 0, "horizon": timeframe,
                "summary": "Claude analysis is temporarily unavailable.",
                "rationale": [], "risks": ["AI service or market data unavailable."],
                "technical_score": 0, "news_sentiment": "UNKNOWN", "context": {},
            }
