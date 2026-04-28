from typing import List
import os

from dotenv import load_dotenv
from pydantic_settings import BaseSettings, SettingsConfigDict

# Load base .env file first
load_dotenv(".env")

# Determine environment from loaded .env or default to 'development'
ENV = os.getenv("ENV", "development")
load_dotenv(f".env.{ENV}", override=True)  # Load env-specific file, overriding base


class Settings(BaseSettings):
    env: str = "development"
    api_host: str = "0.0.0.0"
    api_port: int = 8000
    log_level: str = "INFO"
    # Comma-separated list in env: ALLOWED_ORIGINS
    allowed_origins_csv: str = ""

    supabase_url: str
    supabase_anon_key: str
    supabase_service_role_key: str | None = None
    supabase_jwt_secret: str

    model_config = SettingsConfigDict(extra="ignore")

    @property
    def allowed_origins(self) -> List[str]:
        return [
            o.strip() for o in (self.allowed_origins_csv or "").split(",") if o.strip()
        ]


settings = Settings()
