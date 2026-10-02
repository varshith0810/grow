from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    app_env: str = "development"
    cors_origins: str = "http://localhost:3000"
    api_port: int = 8000
    market_data_provider: str = "upstox"
    news_provider: str = "free"
    aws_region: str = "ap-south-1"
    bedrock_model_id: str = "anthropic.claude-opus-5-20260724-v1:0"
    bedrock_enabled: bool = False
    bedrock_enabled: bool = False
    database_url: str = "postgresql://market:market@localhost:5432/market"
    redis_url: str = "redis://localhost:6379/0"

    # Live market feed. Never commit the access token; set it as a Railway secret.
    upstox_analytics_token: str = ""
    upstox_instrument_keys: str = ""
    upstox_max_instruments: int = 2000

    @property
    def cors_origins_list(self) -> list[str]:
        return [origin.strip() for origin in self.cors_origins.split(",") if origin.strip()]

    model_config = SettingsConfigDict(
        env_file=".env",
        env_prefix="",
        extra="ignore",
    )


settings = Settings()
