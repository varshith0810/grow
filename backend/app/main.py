from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from .settings import settings
from .routes import market, stocks, news, predictions

app = FastAPI(title="Indian Market Analytics API", version="1.2.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins_list,
    allow_credentials=False,
    allow_methods=["GET", "POST"],
    allow_headers=["*"],
)

app.include_router(market.router, prefix="/api/market", tags=["market"])
app.include_router(stocks.router, prefix="/api/stocks", tags=["stocks"])
app.include_router(news.router, prefix="/api/news", tags=["news"])
app.include_router(predictions.router, prefix="/api/predictions", tags=["predictions"])


@app.get("/health")
def health():
    from .market_stream import market_stream
    return {
        "status": "ok",
        "environment": settings.app_env,
        "market_provider": settings.market_data_provider,
        "live_feed": market_stream.status(),
        "ai_provider": "amazon-bedrock" if settings.bedrock_enabled else "disabled",
    }


@app.get("/")
def root():
    return {"service": "grow-api", "status": "ok"}
