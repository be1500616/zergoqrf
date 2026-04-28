from typing import List
import os

from dotenv import load_dotenv
from pydantic_settings import BaseSettings, SettingsConfigDict

PROFILE_ALIASES = {
    "development": "dev",
    "dev": "dev",
    "testing": "test",
    "test": "test",
    "production": "prod",
    "prod": "prod",
    "local": "local",
}


def _resolve_profile(raw_value: str | None) -> str:
    value = (raw_value or "dev").strip().lower()
    return PROFILE_ALIASES.get(value, value)


def _profile_env_key(profile: str, base_key: str) -> str:
    return f"SUPABASE_{profile.upper()}_{base_key}"


# Load base and profile-specific env files.
load_dotenv(".env")
ACTIVE_PROFILE = _resolve_profile(
    os.getenv("APP_PROFILE") or os.getenv("APP_ENV") or os.getenv("ENV")
)
os.environ["APP_PROFILE"] = ACTIVE_PROFILE
load_dotenv(f".env.{ACTIVE_PROFILE}", override=True)


class Settings(BaseSettings):
    env: str = "development"
    app_profile: str = ACTIVE_PROFILE
    api_host: str = "0.0.0.0"
    api_port: int = 8000
    log_level: str = "INFO"
    # Comma-separated list in env: ALLOWED_ORIGINS
    allowed_origins_csv: str = ""

    supabase_url: str = ""
    supabase_anon_key: str = ""
    supabase_service_role_key: str | None = None
    supabase_jwt_secret: str = ""

    model_config = SettingsConfigDict(extra="ignore")

    def model_post_init(self, __context: object) -> None:
        profile = _resolve_profile(self.app_profile)
        self.app_profile = profile
        self.env = {
            "dev": "development",
            "test": "test",
            "prod": "production",
            "local": "development",
        }.get(profile, self.env)

        self.supabase_url = self.supabase_url or os.getenv(
            _profile_env_key(profile, "URL"), ""
        )
        self.supabase_anon_key = self.supabase_anon_key or os.getenv(
            _profile_env_key(profile, "ANON_KEY"), ""
        )
        if not self.supabase_service_role_key:
            self.supabase_service_role_key = os.getenv(
                _profile_env_key(profile, "SERVICE_ROLE_KEY")
            )
        self.supabase_jwt_secret = self.supabase_jwt_secret or os.getenv(
            _profile_env_key(profile, "JWT_SECRET"), ""
        )

        # Supabase credentials are required for shared profiles.
        if profile in {"dev", "test", "prod"}:
            missing = []
            if not self.supabase_url:
                missing.append("SUPABASE_URL")
            if not self.supabase_anon_key:
                missing.append("SUPABASE_ANON_KEY")
            if not self.supabase_jwt_secret:
                missing.append("SUPABASE_JWT_SECRET")
            if missing:
                joined = ", ".join(missing)
                raise ValueError(
                    f"Missing required Supabase config for profile '{profile}': {joined}"
                )

    @property
    def allowed_origins(self) -> List[str]:
        return [
            o.strip() for o in (self.allowed_origins_csv or "").split(",") if o.strip()
        ]


settings = Settings()
