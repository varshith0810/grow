from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    app_env: str = "development"
    cors_origins: str = "http://localhost:3000"
    api_port: int = 8000
    market_data_provider: str = "yahoo"
    news_provider: str = "free"
    aws_region: str = "us-east-1"
    bedrock_model_id: str = "global.anthropic.claude-opus-5"
    bedrock_enabled: bool = True
    database_url: str = "postgresql://market:market@localhost:5432/market"
    redis_url: str = "redis://localhost:6379/0"

    # Yahoo Finance public WebSocket market stream. No broker token is required.
    live_symbols: str = ""

    @property
    def cors_origins_list(self) -> list[str]:
        return [origin.strip() for origin in self.cors_origins.split(",") if origin.strip()]

    @property
    def live_symbols_list(self) -> list[str]:
        return [s.strip().upper() for s in self.live_symbols.split(",") if s.strip()]

    model_config = SettingsConfigDict(
        env_file=".env",
        env_prefix="",
        extra="ignore",
    )


settings = Settings()
