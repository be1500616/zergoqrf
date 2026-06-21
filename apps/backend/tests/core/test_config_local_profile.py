"""Regression tests for app.core.config — local profile.

Specifically guards against the URL-masking bug where `str(URL)` replaces
the password with `***` and the value gets re-stored, breaking runtime
auth. If `settings.database_url` ever contains `***` again, these fail.
"""

import pytest

from app.core.config import Settings


def _make_settings(monkeypatch: pytest.MonkeyPatch, **env_overrides: str) -> Settings:
    """Build a Settings instance with a controlled env, no .env files."""
    # Clear keys that config.py reads at import time
    for k in [
        "APP_PROFILE", "APP_ENV", "ENV",
        "DATABASE_URL", "DIRECT_URL",
        "SUPABASE_URL", "SUPABASE_ANON_KEY",
        "SUPABASE_SERVICE_ROLE_KEY", "SUPABASE_JWT_SECRET",
        "SUPABASE_LOCAL_URL", "SUPABASE_LOCAL_ANON_KEY",
        "SUPABASE_LOCAL_SERVICE_ROLE_KEY", "SUPABASE_LOCAL_JWT_SECRET",
        "SUPABASE_DEV_URL", "SUPABASE_DEV_ANON_KEY",
        "SUPABASE_DEV_SERVICE_ROLE_KEY", "SUPABASE_DEV_JWT_SECRET",
        "SUPABASE_DEV_DB_URL",
    ]:
        monkeypatch.delenv(k, raising=False)
    for k, v in env_overrides.items():
        monkeypatch.setenv(k, v)
    return Settings()


def test_local_profile_resolves_to_docker_url(monkeypatch: pytest.MonkeyPatch) -> None:
    s = _make_settings(
        monkeypatch,
        APP_PROFILE="local",
        DATABASE_URL="postgresql://postgres:postgres@127.0.0.1:54322/postgres",
        SUPABASE_LOCAL_URL="http://127.0.0.1:54321",
        SUPABASE_LOCAL_ANON_KEY="anon-key",
        SUPABASE_LOCAL_SERVICE_ROLE_KEY="service-key",
        SUPABASE_LOCAL_JWT_SECRET="jwt-secret",
    )
    assert s.app_profile == "local"
    assert s.supabase_url == "http://127.0.0.1:54321"
    assert s.supabase_service_role_key == "service-key"
    assert s.supabase_jwt_secret == "jwt-secret"


def test_local_profile_ignores_cloud_base_env(monkeypatch: pytest.MonkeyPatch) -> None:
    """If a stale SUPABASE_URL from a shared .env leaks in, the local profile
    must NOT inherit it — it must use SUPABASE_LOCAL_URL exclusively."""
    s = _make_settings(
        monkeypatch,
        APP_PROFILE="local",
        SUPABASE_URL="https://stale-cloud.supabase.co",  # base env leak
        SUPABASE_ANON_KEY="stale-anon",
        SUPABASE_JWT_SECRET="stale-jwt",
        DATABASE_URL="postgresql://postgres:postgres@127.0.0.1:54322/postgres",
        SUPABASE_LOCAL_URL="http://127.0.0.1:54321",
        SUPABASE_LOCAL_ANON_KEY="local-anon",
        SUPABASE_LOCAL_JWT_SECRET="local-jwt",
    )
    assert s.supabase_url == "http://127.0.0.1:54321"
    assert s.supabase_anon_key == "local-anon"
    assert s.supabase_jwt_secret == "local-jwt"


def test_database_url_password_not_masked(monkeypatch: pytest.MonkeyPatch) -> None:
    """Regression: ensure `database_url` retains the real password after
    the post-init asyncpg driver rewrite. `str(URL)` would mask it as
    `***`; `render_as_string(hide_password=False)` is the correct path."""
    s = _make_settings(
        monkeypatch,
        APP_PROFILE="local",
        DATABASE_URL="postgresql://app_user:s3cret-pa$$@127.0.0.1:54322/postgres",
        SUPABASE_LOCAL_URL="http://127.0.0.1:54321",
        SUPABASE_LOCAL_ANON_KEY="anon",
        SUPABASE_LOCAL_JWT_SECRET="jwt",
    )
    assert "***" not in s.database_url, (
        f"database_url contains masked password: {s.database_url}"
    )
    # Password survives URL encoding (%24 = $). The real password must be
    # retrievable by the SQLAlchemy URL parser.
    from sqlalchemy.engine.url import make_url
    parsed = make_url(s.database_url)
    assert parsed.password == "s3cret-pa$$", (
        f"password was masked or corrupted: {parsed.password!r}"
    )
    assert s.database_url.startswith("postgresql+asyncpg://")


def test_database_url_rejects_unknown_scheme(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    with pytest.raises(ValueError, match="Invalid DATABASE_URL scheme"):
        _make_settings(
            monkeypatch,
            APP_PROFILE="local",
            DATABASE_URL="mysql://u:p@host:3306/db",
            SUPABASE_LOCAL_URL="http://127.0.0.1:54321",
            SUPABASE_LOCAL_ANON_KEY="anon",
            SUPABASE_LOCAL_JWT_SECRET="jwt",
        )
