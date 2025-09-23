from typing import List

from dotenv import find_dotenv, load_dotenv
from pydantic_settings import BaseSettings, SettingsConfigDict

# Load .env from project root automatically
load_dotenv(find_dotenv(usecwd=True))


class Settings(BaseSettings):
    model_config = SettingsConfigDict(extra="ignore")

    env: str = "development"
    api_host: str = "0.0.0.0"
    api_port: int = 8000
    log_level: str = "INFO"
    # Comma-separated list in env: ALLOWED_ORIGINS
    allowed_origins_csv: str = (
        "http://localhost:5173,http://localhost:3000,"
        "http://localhost:8080,http://localhost:5555"
    )

    supabase_url: str
    supabase_anon_key: str | None = None
    supabase_service_role_key: str | None = None
    supabase_jwt_secret: str | None = None

    @property
    def allowed_origins(self) -> List[str]:
        return [
            o.strip() for o in (self.allowed_origins_csv or "").split(",") if o.strip()
        ]


settings = Settings()
