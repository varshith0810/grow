from pydantic_settings import BaseSettings, SettingsConfigDict
class Settings(BaseSettings):
    app_env:str="development"
    cors_origins:list[str]=["http://localhost:3000"]
    api_port:int=8000
    market_data_provider:str="free"
    news_provider:str="free"
    aws_region:str="ap-south-1"
    bedrock_model_id:str="anthropic.claude-opus-5-20260724-v1:0"
    database_url:str="postgresql://market:market@localhost:5432/market"
    redis_url:str="redis://localhost:6379/0"
    model_config=SettingsConfigDict(env_file=".env",env_prefix="",extra="ignore")
settings=Settings()