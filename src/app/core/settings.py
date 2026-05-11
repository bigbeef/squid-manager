import os
from dataclasses import dataclass
from functools import lru_cache
from pathlib import Path

from dotenv import load_dotenv


BASE_DIR = Path(__file__).resolve().parents[3]
DEFAULT_SQLITE_DB_PATH = BASE_DIR / "data" / "squid_manager.db"
DEFAULT_SQUID_PASSWD_PATH = BASE_DIR / "squid" / "squid_passwd"

load_dotenv(BASE_DIR / ".env")


@dataclass(frozen=True)
class Settings:
    app_version: str
    log_level: str
    admin_username: str
    admin_password: str
    session_secret_key: str
    session_cookie_name: str
    session_cookie_max_age_seconds: int
    session_cookie_secure: bool
    sqlite_db_path: Path
    squid_passwd_path: Path
    account_expiration_scan_interval_seconds: int


def _parse_bool_env(name: str, default: bool = False) -> bool:
    value = os.getenv(name)
    if value is None:
        return default
    normalized_value = value.strip().lower()
    if normalized_value in {"1", "true", "yes", "on"}:
        return True
    if normalized_value in {"0", "false", "no", "off"}:
        return False
    raise ValueError(f"environment variable {name} must be a boolean value")


def _resolve_path_env(name: str, default: Path) -> Path:
    configured_path = os.getenv(name)
    if not configured_path:
        return default
    candidate = Path(configured_path)
    if not candidate.is_absolute():
        candidate = BASE_DIR / candidate
    return candidate.resolve()


@lru_cache(maxsize=1)
def get_settings() -> Settings:
    return Settings(
        app_version=os.getenv("APP_VERSION", "1.0.0"),
        log_level=os.getenv("LOG_LEVEL", "INFO").upper(),
        admin_username=os.getenv("ADMIN_USERNAME", "admin"),
        admin_password=os.getenv("ADMIN_PASSWORD", "change-me"),
        session_secret_key=os.getenv("SESSION_SECRET_KEY", "change-this-secret-key"),
        session_cookie_name=os.getenv("SESSION_COOKIE_NAME", "squid_manager_session"),
        session_cookie_max_age_seconds=int(
            os.getenv("SESSION_COOKIE_MAX_AGE_SECONDS", "28800")
        ),
        session_cookie_secure=_parse_bool_env("SESSION_COOKIE_SECURE", False),
        sqlite_db_path=_resolve_path_env("SQLITE_DB_PATH", DEFAULT_SQLITE_DB_PATH),
        squid_passwd_path=_resolve_path_env("SQUID_PASSWD_PATH", DEFAULT_SQUID_PASSWD_PATH),
        account_expiration_scan_interval_seconds=int(
            os.getenv("ACCOUNT_EXPIRATION_SCAN_INTERVAL_SECONDS", "60")
        ),
    )
