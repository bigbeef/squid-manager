from dataclasses import dataclass

from src.app.core.logging import configure_logging, get_logger
from src.app.core.settings import Settings, get_settings
from src.app.infrastructure.db.session import init_db


@dataclass(frozen=True)
class ApplicationContext:
    settings: Settings


def bootstrap() -> ApplicationContext:
    settings = get_settings()
    configure_logging(settings.log_level)
    init_db()
    get_logger(__name__).info("Application bootstrap completed")
    return ApplicationContext(settings=settings)
