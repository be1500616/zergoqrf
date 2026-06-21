"""Tier A tests for ``Settings.database_url`` resolution.

No DB connection required. Uses ``monkeypatch`` to set/clear env vars and
construct a fresh ``Settings`` per test. Each test is self-contained —
no module-level state leaks between cases.
"""

import pytest
from sqlalchemy.engine.url import make_url

from app.core.config import Settings

# Env keys that ``app.core.config`` reads at module import (via
# ``load_dotenv`` and direct ``os.getenv``). Tests must clear these
# before constructing ``Settings`` so file-loaded values (e.g. from
# ``.env.local``) cannot leak in.
_CONFIG_ENV_KEYS = (
    "APP_PROFILE",
    "APP_ENV",
    "ENV",
    "DATABASE_URL",
    "DIRECT_URL",
    "SUPABASE_URL",
    "SUPABASE_ANON_KEY",
    "SUPABASE_SERVICE_ROLE_KEY",
    "SUPABASE_JWT_SECRET",
    "SUPABASE_LOCAL_URL",
    "SUPABASE_LOCAL_ANON_KEY",
    "SUPABASE_LOCAL_SERVICE_ROLE_KEY",
    "SUPABASE_LOCAL_JWT_SECRET",
    "SUPABASE_DEV_URL",
    "SUPABASE_DEV_ANON_KEY",
    "SUPABASE_DEV_SERVICE_ROLE_KEY",
    "SUPABASE_DEV_JWT_SECRET",
    "SUPABASE_DEV_DB_URL",
    "SUPABASE_TEST_DB_URL",
    "SUPABASE_PROD_DB_URL",
)


def _build_settings(monkeypatch, profile: str, db_env: dict | None = None) -> Settings:
    """Build a fresh ``Settings`` with a controlled env.

    No DB connection required. The returned ``Settings`` has not been
    touched by the module-level singleton, so tests are independent.
    """
    for key in _CONFIG_ENV_KEYS:
        monkeypatch.delenv(key, raising=False)
    monkeypatch.setenv("APP_PROFILE", profile)
    for k, v in (db_env or {}).items():
        monkeypatch.setenv(k, v)
    # Profile-specific Supabase creds: local uses SUPABASE_LOCAL_*; others
    # use the shared SUPABASE_* names.
    prefix = "SUPABASE_LOCAL" if profile == "local" else "SUPABASE"
    monkeypatch.setenv(f"{prefix}_URL", "http://localhost:54321")
    monkeypatch.setenv(f"{prefix}_ANON_KEY", "test-anon-key")
    monkeypatch.setenv(f"{prefix}_JWT_SECRET", "test-jwt-secret")
    return Settings()


@pytest.mark.parametrize(
    "profile,db_env,expected",
    [
        (
            "dev",
            {"SUPABASE_DEV_DB_URL": "postgresql+asyncpg://u:p@db.dev:6543/p"},
            "postgresql+asyncpg://u:p@db.dev:6543/p",
        ),
        (
            "test",
            {"SUPABASE_TEST_DB_URL": "postgresql+asyncpg://u:p@db.test:6543/p"},
            "postgresql+asyncpg://u:p@db.test:6543/p",
        ),
        (
            "prod",
            {"SUPABASE_PROD_DB_URL": "postgresql+asyncpg://u:p@db.prod:6543/p"},
            "postgresql+asyncpg://u:p@db.prod:6543/p",
        ),
        (
            "local",
            {"DATABASE_URL": "postgresql+asyncpg://postgres:postgres@localhost:5432/postgres"},
            "postgresql+asyncpg://postgres:postgres@localhost:5432/postgres",
        ),
    ],
)
def test_settings_database_url_populated_per_profile(monkeypatch, profile, db_env, expected):
    s = _build_settings(monkeypatch, profile, db_env)
    assert s.database_url == expected
    parsed = make_url(s.database_url)
    assert parsed.drivername in {"postgresql+asyncpg", "postgresql"}


def test_settings_database_url_missing_dev_profile_fails(monkeypatch):
    """Profile dev with no DB URL must fail fast at construction."""
    with pytest.raises(ValueError) as exc_info:
        _build_settings(
            monkeypatch,
            "dev",
            db_env={"SUPABASE_DEV_DB_URL": ""},
        )
    msg = str(exc_info.value)
    assert "dev" in msg
    assert "SUPABASE_DEV_DB_URL" in msg


def test_settings_database_url_unparseable_fails(monkeypatch):
    """Malformed URL must raise a single readable error."""
    with pytest.raises(ValueError) as exc_info:
        _build_settings(
            monkeypatch,
            "dev",
            db_env={"SUPABASE_DEV_DB_URL": "not a url"},
        )
    msg = str(exc_info.value)
    assert "dev" in msg


def test_settings_database_url_rejects_wrong_scheme(monkeypatch):
    """Schemes other than postgresql/postgresql+asyncpg are rejected."""
    with pytest.raises(ValueError) as exc_info:
        _build_settings(
            monkeypatch,
            "dev",
            db_env={"SUPABASE_DEV_DB_URL": "mysql+aiomysql://u:p@db/p"},
        )
    msg = str(exc_info.value)
    assert "scheme" in msg.lower() or "postgresql" in msg


def test_database_url_password_preserved_through_rewrite(monkeypatch):
    """postgresql:// URLs get rewritten to postgresql+asyncpg:// AND keep
    the real password (no `***` masking from str(URL))."""
    s = _build_settings(
        monkeypatch,
        "local",
        db_env={"DATABASE_URL": "postgresql://app:s3cret-pa$$@127.0.0.1:54322/p"},
    )
    assert "***" not in s.database_url
    assert s.database_url.startswith("postgresql+asyncpg://")
    parsed = make_url(s.database_url)
    assert parsed.password == "s3cret-pa$$"
