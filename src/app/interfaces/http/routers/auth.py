from fastapi import APIRouter, Form, Request, Response, status
from fastapi.responses import JSONResponse

from src.app.core.captcha import (
    CAPTCHA_TTL_SECONDS,
    consume_captcha,
    create_captcha_challenge,
    discard_captcha,
    get_captcha_cookie_name,
)
from src.app.core.security import constant_time_equals, create_session_token
from src.app.core.settings import get_settings


router = APIRouter(prefix="/api/auth", tags=["auth"])


@router.get("/captcha")
def captcha(request: Request) -> Response:
    settings = get_settings()
    captcha_cookie_name = get_captcha_cookie_name(settings)
    discard_captcha(request.cookies.get(captcha_cookie_name))

    challenge = create_captcha_challenge()
    response = Response(
        content=challenge.svg,
        media_type="image/svg+xml",
        headers={"Cache-Control": "no-store, max-age=0"},
    )
    response.set_cookie(
        key=captcha_cookie_name,
        value=challenge.token,
        max_age=CAPTCHA_TTL_SECONDS,
        httponly=True,
        secure=settings.session_cookie_secure,
        samesite="lax",
    )
    return response


@router.post("/login")
def login(
    request: Request,
    response: Response,
    username: str = Form(...),
    password: str = Form(...),
    captcha: str = Form(""),
) -> dict[str, str]:
    settings = get_settings()
    captcha_cookie_name = get_captcha_cookie_name(settings)
    captcha_token = request.cookies.get(captcha_cookie_name)
    captcha_ok = consume_captcha(captcha_token, captcha)
    if not captcha_ok:
        error_response = JSONResponse(
            {"detail": "invalid captcha"},
            status_code=status.HTTP_400_BAD_REQUEST,
        )
        error_response.delete_cookie(captcha_cookie_name)
        return error_response

    username_ok = constant_time_equals(username, settings.admin_username)
    password_ok = constant_time_equals(password, settings.admin_password)
    if not username_ok or not password_ok:
        error_response = JSONResponse(
            {"detail": "invalid credentials"},
            status_code=status.HTTP_401_UNAUTHORIZED,
        )
        error_response.delete_cookie(captcha_cookie_name)
        return error_response

    token = create_session_token(settings, username)
    response.delete_cookie(captcha_cookie_name)
    response.set_cookie(
        key=settings.session_cookie_name,
        value=token,
        max_age=settings.session_cookie_max_age_seconds,
        httponly=True,
        secure=settings.session_cookie_secure,
        samesite="lax",
    )
    return {"status": "ok"}


@router.post("/logout")
def logout(response: Response) -> dict[str, str]:
    settings = get_settings()
    response.delete_cookie(settings.session_cookie_name)
    return {"status": "ok"}


@router.get("/me")
def me(request: Request) -> dict[str, str | None]:
    return {"username": getattr(request.state, "current_user", None)}
