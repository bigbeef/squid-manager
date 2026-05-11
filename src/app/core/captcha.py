import html
import hmac
import secrets
import time
from dataclasses import dataclass
from threading import Lock

from src.app.core.settings import Settings


CAPTCHA_TTL_SECONDS = 300
CAPTCHA_ALPHABET = "ABCDEFGHJKLMNPQRSTUVWXYZ23456789"
CAPTCHA_LENGTH = 4


@dataclass(frozen=True)
class CaptchaChallenge:
    token: str
    answer: str
    svg: str


@dataclass(frozen=True)
class _CaptchaEntry:
    answer: str
    expires_at: float


_captcha_store: dict[str, _CaptchaEntry] = {}
_captcha_lock = Lock()


def get_captcha_cookie_name(settings: Settings) -> str:
    return f"{settings.session_cookie_name}_captcha"


def create_captcha_challenge() -> CaptchaChallenge:
    answer = "".join(secrets.choice(CAPTCHA_ALPHABET) for _ in range(CAPTCHA_LENGTH))
    token = secrets.token_urlsafe(32)
    challenge = CaptchaChallenge(token=token, answer=answer, svg=_build_svg(answer))
    now = time.time()

    with _captcha_lock:
        _clear_expired_locked(now)
        _captcha_store[token] = _CaptchaEntry(
            answer=answer,
            expires_at=now + CAPTCHA_TTL_SECONDS,
        )

    return challenge


def discard_captcha(token: str | None) -> None:
    if not token:
        return
    with _captcha_lock:
        _captcha_store.pop(token, None)


def consume_captcha(token: str | None, submitted_answer: str) -> bool:
    if not token:
        return False

    normalized_answer = submitted_answer.strip().upper()
    now = time.time()

    with _captcha_lock:
        entry = _captcha_store.pop(token, None)

    if entry is None or entry.expires_at < now or not normalized_answer:
        return False
    return hmac.compare_digest(normalized_answer, entry.answer)


def _clear_expired_locked(now: float) -> None:
    expired_tokens = [
        token for token, entry in _captcha_store.items() if entry.expires_at < now
    ]
    for token in expired_tokens:
        _captcha_store.pop(token, None)


def _build_svg(answer: str) -> str:
    letter_spans = []
    for index, letter in enumerate(answer):
        x = 22 + index * 26 + secrets.randbelow(7)
        y = 31 + secrets.randbelow(9)
        rotation = secrets.randbelow(31) - 15
        letter_spans.append(
            f'<text x="{x}" y="{y}" transform="rotate({rotation} {x} {y})">'
            f"{html.escape(letter)}</text>"
        )

    noise_lines = []
    for _ in range(5):
        x1 = secrets.randbelow(132)
        y1 = secrets.randbelow(44)
        x2 = secrets.randbelow(132)
        y2 = secrets.randbelow(44)
        opacity = 0.18 + secrets.randbelow(20) / 100
        noise_lines.append(
            f'<line x1="{x1}" y1="{y1}" x2="{x2}" y2="{y2}" '
            f'opacity="{opacity:.2f}" />'
        )

    return (
        '<svg xmlns="http://www.w3.org/2000/svg" width="132" height="44" '
        'viewBox="0 0 132 44" role="img" aria-label="验证码">'
        "<defs>"
        '<pattern id="dots" width="6" height="6" patternUnits="userSpaceOnUse">'
        '<circle cx="1" cy="1" r="1" fill="#cbd5e1" opacity="0.65" />'
        "</pattern>"
        "</defs>"
        '<rect width="132" height="44" rx="9" fill="#f6f7fb" />'
        '<rect width="132" height="44" rx="9" fill="url(#dots)" />'
        '<g stroke="#7c3aed" stroke-width="1.4" stroke-linecap="round">'
        f'{"".join(noise_lines)}'
        "</g>"
        '<g fill="#42197c" font-family="Georgia, Times New Roman, serif" '
        'font-size="24" font-style="italic" font-weight="700">'
        f'{"".join(letter_spans)}'
        "</g>"
        "</svg>"
    )
