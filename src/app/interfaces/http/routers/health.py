from datetime import datetime

from fastapi import APIRouter

from src.app.core.settings import get_settings


router = APIRouter(prefix="/health", tags=["system"])


@router.get("")
def health_check() -> dict[str, str]:
    return {
        "status": "UP",
        "service": "Squid代理管理系统",
        "version": get_settings().app_version,
        "timestamp": datetime.now().isoformat(),
    }
