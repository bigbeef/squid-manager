from datetime import datetime

from sqlalchemy import func, or_, select
from sqlalchemy.orm import Session

from src.app.infrastructure.db.models import ProxyAccount


class ProxyAccountRepository:
    def __init__(self, session: Session) -> None:
        self._session = session

    def get_by_id(self, account_id: int) -> ProxyAccount | None:
        return self._session.get(ProxyAccount, account_id)

    def get_by_username(self, username: str) -> ProxyAccount | None:
        statement = select(ProxyAccount).where(ProxyAccount.username == username)
        return self._session.execute(statement).scalar_one_or_none()

    def list_page(
        self,
        page: int,
        page_size: int,
        username: str | None = None,
        status: str | None = None,
        now: datetime | None = None,
    ) -> tuple[list[ProxyAccount], int]:
        offset = (page - 1) * page_size
        filters = []
        if username:
            filters.append(ProxyAccount.username.ilike(f"%{username}%"))

        if status:
            current_time = now or datetime.now().replace(microsecond=0)
            active_expiration = or_(
                ProxyAccount.expires_at.is_(None),
                ProxyAccount.expires_at > current_time,
            )
            expired_condition = or_(
                ProxyAccount.expired_at.is_not(None),
                ProxyAccount.expires_at <= current_time,
            )
            if status == "enabled":
                filters.extend([
                    ProxyAccount.enabled.is_(True),
                    ProxyAccount.expired_at.is_(None),
                    active_expiration,
                ])
            elif status == "disabled":
                filters.extend([
                    ProxyAccount.enabled.is_(False),
                    ProxyAccount.expired_at.is_(None),
                    active_expiration,
                ])
            elif status == "expired":
                filters.append(expired_condition)

        base_statement = select(ProxyAccount).where(*filters)
        total = self._session.execute(
            select(func.count()).select_from(ProxyAccount).where(*filters)
        ).scalar_one()
        rows = self._session.execute(
            base_statement.order_by(ProxyAccount.id.desc())
            .offset(offset)
            .limit(page_size)
        ).scalars().all()
        return list(rows), total

    def list_active_for_passwd(self, now: datetime) -> list[ProxyAccount]:
        rows = self._session.execute(
            select(ProxyAccount)
            .where(ProxyAccount.enabled.is_(True))
            .where(or_(ProxyAccount.expires_at.is_(None), ProxyAccount.expires_at > now))
            .order_by(ProxyAccount.username.asc())
        ).scalars().all()
        return list(rows)

    def list_expired_enabled(self, now: datetime) -> list[ProxyAccount]:
        rows = self._session.execute(
            select(ProxyAccount)
            .where(ProxyAccount.enabled.is_(True))
            .where(ProxyAccount.expires_at.is_not(None))
            .where(ProxyAccount.expires_at <= now)
        ).scalars().all()
        return list(rows)

    def add(self, account: ProxyAccount) -> ProxyAccount:
        self._session.add(account)
        self._session.flush()
        self._session.refresh(account)
        return account

    def delete(self, account: ProxyAccount) -> None:
        self._session.delete(account)
