from pathlib import Path

from fastapi import APIRouter
from fastapi.responses import FileResponse, RedirectResponse


STATIC_DIR = Path(__file__).resolve().parents[1] / "static"
router = APIRouter(tags=["pages"])


@router.get("/")
def index() -> RedirectResponse:
    return RedirectResponse(url="/admin#/accounts", status_code=303)


@router.get("/login")
def login_page() -> FileResponse:
    return FileResponse(STATIC_DIR / "login.html")


@router.get("/accounts")
def accounts_page() -> RedirectResponse:
    return RedirectResponse(url="/admin#/accounts", status_code=303)


@router.get("/admin")
def admin_page() -> FileResponse:
    return FileResponse(STATIC_DIR / "admin.html")
