# Indian Market Analytics

Zero-budget Indian stock analytics dashboard.

## Free-data mode
The default market provider is a public no-key NSE/BSE API. Its project documents free REST access to NSE/BSE prices and symbols under MIT licensing. This is a community/public service, so availability, latency, coverage and rate limits are not guaranteed.

Historical/chart data can use Yahoo Finance through yfinance. News can be sourced from public RSS feeds. No paid market-data subscription is required for development.

The app intentionally does not scrape NSE/BSE HTML pages.

## Zero-budget caveat
Free public feeds may be delayed, rate-limited, incomplete, or temporarily unavailable. This is not an exchange-certified tick feed and should not be used for trade execution.

## AI
Amazon Bedrock is optional. Bedrock itself is not guaranteed to be zero-cost; keep it disabled until your AWS account has an applicable free/credit allowance. The prediction service falls back to NEUTRAL when unavailable.

## Run
Copy .env.example to .env, then start backend/frontend. Set NEXT_PUBLIC_API_URL for a deployed frontend.
