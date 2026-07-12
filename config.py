import os
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    GREEN_API_INSTANCE_ID: str
    GREEN_API_TOKEN: str
    GEMINI_API_KEY: str
    GEMINI_MODELS: str = "gemini-3.1-flash-lite,gemini-3.5-flash"
    SUPABASE_URL: str = ""
    SUPABASE_ANON_KEY: str = ""
    APP_HOST: str = "0.0.0.0"
    APP_PORT: int = int(os.getenv("PORT", 8000))
    APP_PUBLIC_URL: str = ""
    VENDORIQ_PHONE: str
    DAILY_SUMMARY_HOUR: int = 20
    DAILY_SUMMARY_MINUTE: int = 0

    class Config:
        env_file = ".env"


settings = Settings()
