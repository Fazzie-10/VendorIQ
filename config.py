import os
from pydantic_settings import BaseSettings
from typing import List


class Settings(BaseSettings):
    EVOLUTION_API_URL: str
    EVOLUTION_API_KEY: str
    EVOLUTION_INSTANCE: str = "vendoriq"
    GEMINI_API_KEY: str
    GEMINI_MODELS: List[str] = ["gemini-3.1-flash-lite", "gemini-3.5-flash", "gemini-3.5-pro"]
    SUPABASE_URL: str
    SUPABASE_ANON_KEY: str
    APP_HOST: str = "0.0.0.0"
    APP_PORT: int = int(os.getenv("PORT", 8000))
    VENDORIQ_PHONE: str
    DAILY_SUMMARY_HOUR: int = 20
    DAILY_SUMMARY_MINUTE: int = 0

    class Config:
        env_file = ".env"


settings = Settings()
