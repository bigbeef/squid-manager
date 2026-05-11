import hmac
from typing import Any

from itsdangerous import BadSignature, SignatureExpired, URLSafeTimedSerializer

from src.app.core.settings import Settings


SESSION_SALT = "squid-manager-session"


def constant_time_equals(left: str, right: str) -> bool:
    return hmac.compare_digest(left.encode("utf-8"), right.encode("utf-8"))


def create_session_token(settings: Settings, username: str) -> str:
    serializer = URLSafeTimedSerializer(settings.session_secret_key, salt=SESSION_SALT)
    return serializer.dumps({"authenticated": True, "username": username})


def load_session_token(settings: Settings, token: str | None) -> dict[str, Any] | None:
    if not token:
        return None
    serializer = URLSafeTimedSerializer(settings.session_secret_key, salt=SESSION_SALT)
    try:
        payload = serializer.loads(
            token,
            max_age=settings.session_cookie_max_age_seconds,
        )
    except (BadSignature, SignatureExpired):
        return None
    if not isinstance(payload, dict) or payload.get("authenticated") is not True:
        return None
    return payload
