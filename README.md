# Indian Market Analytics

Groww-inspired Indian market research terminal with live market streaming and Claude-powered stock analysis.

## Live market data

The production live-feed path uses the Upstox V3 MarketDataStreamer over WebSocket. Upstox provides real-time LTPC updates and maintains an instrument master containing NSE/BSE contracts. The app loads NSE equity instrument keys automatically when `UPSTOX_INSTRUMENT_KEYS` is empty.

Set these server-side secrets/environment variables:

- `UPSTOX_ACCESS_TOKEN` — required to enable the live stream.
- `UPSTOX_INSTRUMENT_KEYS` — optional comma-separated instrument keys; leave empty for automatic NSE equity discovery.
- `UPSTOX_MAX_INSTRUMENTS` — maximum subscription count; the code caps this at the provider's documented limit.

The backend keeps the latest ticks in memory and exposes them through `/api/market/stream` as Server-Sent Events. The frontend consumes the stream without polling once per second.

**Important:** a live exchange/broker feed is different from the old free yfinance/public-feed fallback. Data access, subscription limits, display rights and commercial terms are controlled by the provider. Do not publish or expose your Upstox access token.

## Free-data fallback

Without `UPSTOX_ACCESS_TOKEN`, the app falls back to the existing public market provider for development and yfinance for historical data. Free public feeds may be delayed, rate-limited, incomplete, or temporarily unavailable.

## AI

Amazon Bedrock is optional. The prediction service uses Claude for on-demand analysis of recent price behaviour, technical indicators and news. AI output is informational and does not guarantee future returns.

## Run

Copy `.env.example` to `.env`, then start backend/frontend. For Railway, add the live-feed variables to the backend service as secrets and redeploy.
