# Indian Market Analytics

Groww-inspired Indian market research terminal with a simple public market-data dashboard and Claude-powered stock analysis.

## Architecture

- **Frontend:** Next.js
- **Backend:** FastAPI
- **Market data:** Yahoo Finance public data + WebSocket stream
- **AI analysis:** Amazon Bedrock / Claude
- **Transport:** REST + Server-Sent Events
- **Deployment:** Railway-compatible Docker services

## Live market dashboard

The dashboard uses Yahoo Finance's public WebSocket support for live price updates and yfinance for historical OHLCV data. No Upstox, Zerodha, Angel One, Groww or other broker API is required.

The backend exposes:

- `GET /api/market/quotes`
- `GET /api/market/live/status`
- `GET /api/market/stream`
- `GET /api/market/rankings`
- `GET /api/stocks/{symbol}`
- `GET /api/stocks/{symbol}/history`

The frontend receives live updates through SSE instead of repeatedly polling the dashboard.

**Data note:** Yahoo Finance/yfinance is a public-data solution intended for research/personal use. It is not an exchange-direct feed and should not be represented as guaranteed exchange tick data.

## Claude stock analysis

Stock analysis is handled by Amazon Bedrock's runtime Converse API. The backend collects public historical market data and recent news, builds a quantitative context, and sends that context to Claude. Claude returns structured JSON containing:

- signal classification
- confidence
- time horizon
- summary
- rationale
- risks
- technical score
- news sentiment

Bedrock is created lazily only when an analysis request is made. AWS credentials never belong in the frontend or GitHub repository.

## Railway variables

### Backend

```text
MARKET_DATA_PROVIDER=yahoo
AWS_REGION=us-east-1
BEDROCK_ENABLED=true
BEDROCK_MODEL_ID=global.anthropic.claude-opus-5
CORS_ORIGINS=https://YOUR-FRONTEND-DOMAIN
```

Configure AWS credentials as Railway secrets. Never commit them.

### Frontend

Keep the existing backend URL/proxy configuration. No market-data token is required in the frontend.

## Zero-broker design

There are intentionally **no Upstox credentials, broker SDKs, trading APIs, or order-placement APIs** in this project.

This project is a market research/analytics dashboard. It does not execute trades.

## Run locally

```bash
cd backend
pip install -r requirements.txt
uvicorn app.main:app --reload --port 8000
```

Then start the Next.js frontend.

## Security

- Secrets are server-side only.
- AWS credentials must be Railway secrets.
- No market-data credentials are shipped to the browser.
- No trading/order endpoint is exposed.
- Claude receives computed market context rather than direct browser access.
