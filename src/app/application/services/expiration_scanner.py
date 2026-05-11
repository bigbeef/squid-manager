import asyncio

from src.app.application.services.proxy_account_service import ProxyAccountService
from src.app.core.logging import get_logger
from src.app.infrastructure.db.session import get_session


logger = get_logger(__name__)


class ExpirationScanner:
    def __init__(self, interval_seconds: int) -> None:
        self._interval_seconds = max(1, interval_seconds)
        self._task: asyncio.Task[None] | None = None

    def start(self) -> None:
        if self._task is None or self._task.done():
            self._task = asyncio.create_task(self._run(), name="account-expiration-scanner")

    async def stop(self) -> None:
        if self._task is None:
            return
        self._task.cancel()
        try:
            await self._task
        except asyncio.CancelledError:
            pass

    async def _run(self) -> None:
        while True:
            await asyncio.sleep(self._interval_seconds)
            try:
                session = get_session()
                try:
                    expired_count = ProxyAccountService(session).scan_expired()
                finally:
                    session.close()
                if expired_count:
                    logger.info("Expired proxy accounts disabled: %s", expired_count)
            except Exception:
                logger.exception("Failed to scan expired proxy accounts")
