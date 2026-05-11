from contextlib import asynccontextmanager
from pathlib import Path

from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse, RedirectResponse, Response
from fastapi.staticfiles import StaticFiles

from src.app.application.services.expiration_scanner import ExpirationScanner
from src.app.bootstrap import bootstrap
from src.app.core.security import load_session_token
from src.app.core.settings import get_settings
from src.app.interfaces.http.routers import api_router


STATIC_DIR = Path(__file__).resolve().parent / "static"
PUBLIC_PATHS = {
    ("GET", "/health"),
    ("GET", "/login"),
    ("GET", "/api/auth/captcha"),
    ("POST", "/api/auth/login"),
}


def _is_public_path(method: str, path: str) -> bool:
    if path.startswith("/static/"):
        return True
    return (method.upper(), path.rstrip("/") or "/") in PUBLIC_PATHS


def _is_api_path(path: str) -> bool:
    return path.startswith("/api/") or path == "/health"


@asynccontextmanager
async def lifespan(app: FastAPI):
    app.state.context = bootstrap()
    settings = app.state.context.settings
    app.state.expiration_scanner = ExpirationScanner(
        settings.account_expiration_scan_interval_seconds
    )
    app.state.expiration_scanner.start()
    yield
    await app.state.expiration_scanner.stop()


def create_app() -> FastAPI:
    settings = get_settings()
    app = FastAPI(title="Squid管理系统", version=settings.app_version, lifespan=lifespan)

    @app.middleware("http")
    async def require_login(request: Request, call_next):
        path = request.url.path.rstrip("/") or "/"
        if _is_public_path(request.method, path):
            return await call_next(request)

        payload = load_session_token(settings, request.cookies.get(settings.session_cookie_name))
        if payload is None:
            if _is_api_path(path):
                return JSONResponse({"detail": "not authenticated"}, status_code=401)
            return RedirectResponse(url="/login", status_code=303)

        request.state.current_user = payload.get("username")
        return await call_next(request)

    app.mount("/static", StaticFiles(directory=str(STATIC_DIR)), name="static")
    app.include_router(api_router)

    @app.get("/favicon.ico", include_in_schema=False)
    def favicon() -> Response:
        return Response(status_code=204)

    return app


app = create_app()
