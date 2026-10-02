# Indian Market Analytics

Simple Indian stock-market analytics platform with live-ready rankings, charts, news and Amazon Bedrock AI forecasts.

## Stack
- Frontend: Next.js + TypeScript
- Backend: FastAPI + Python
- AI: Amazon Bedrock / Claude Opus 5
- Storage: PostgreSQL-ready
- Cache: Redis-ready

## Safety
Use a licensed market-data provider for production. AI forecasts are informational and not guaranteed investment outcomes.

## Structure
`frontend/` dashboard UI
`backend/` API and domain services
`backend/tests/` API tests
`docker-compose.yml` local stack

## Production data
The repository does not scrape NSE/BSE pages. NSE provides real-time data directly and through authorized vendors. TrueData currently advertises authorized NSE/BSE real-time WebSocket and historical REST market-data APIs. Configure MARKET_DATA_PROVIDER=truedata only after subscribing to the appropriate service and storing credentials as deployment secrets.

## AI
Set AWS_REGION and BEDROCK_MODEL_ID and grant the runtime role only the required Amazon Bedrock permissions. Forecasts are informational and do not execute trades or guarantee outcomes.

## Frontend deployment
Set NEXT_PUBLIC_API_URL to the public backend URL; never hard-code localhost in production.
