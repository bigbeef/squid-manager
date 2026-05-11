from fastapi import APIRouter

from src.app.interfaces.http.routers.auth import router as auth_router
from src.app.interfaces.http.routers.health import router as health_router
from src.app.interfaces.http.routers.pages import router as pages_router
from src.app.interfaces.http.routers.proxy_accounts import router as proxy_accounts_router


api_router = APIRouter()
api_router.include_router(auth_router)
api_router.include_router(health_router)
api_router.include_router(pages_router)
api_router.include_router(proxy_accounts_router)
