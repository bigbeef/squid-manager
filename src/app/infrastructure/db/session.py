from collections.abc import Generator

from sqlalchemy import create_engine
from sqlalchemy.orm import Session, sessionmaker

from src.app.core.settings import get_settings
from src.app.infrastructure.db.base import Base


def _build_database_url() -> str:
    sqlite_path = get_settings().sqlite_db_path
    sqlite_path.parent.mkdir(parents=True, exist_ok=True)
    return "sqlite:///{}".format(sqlite_path.as_posix())


engine = create_engine(_build_database_url(), connect_args={"check_same_thread": False}, future=True)
SessionLocal = sessionmaker(bind=engine, autoflush=False, autocommit=False, future=True)


def get_session() -> Session:
    return SessionLocal()


def session_scope() -> Generator[Session, None, None]:
    session = SessionLocal()
    try:
        yield session
        session.commit()
    except Exception:
        session.rollback()
        raise
    finally:
        session.close()


def init_db() -> None:
    import src.app.infrastructure.db.models  # noqa: F401

    Base.metadata.create_all(bind=engine)
