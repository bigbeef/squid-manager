from datetime import datetime

from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from src.app.application.schemas.proxy_account import (
    ProxyAccountCreate,
    ProxyAccountRead,
    ProxyAccountUpdate,
)
from src.app.core.settings import get_settings
from src.app.infrastructure.db.models import ProxyAccount
from src.app.infrastructure.db.repositories.proxy_account_repository import ProxyAccountRepository
from src.app.infrastructure.squid.passwd_file import write_passwd_file


class AccountNotFoundError(Exception):
    pass


class DuplicateUsernameError(Exception):
    pass


def local_now() -> datetime:
    return datetime.now().replace(microsecond=0)


def account_status(account: ProxyAccount, now: datetime | None = None) -> str:
    current_time = now or local_now()
    if account.expired_at is not None:
        return "expired"
    if account.expires_at is not None and account.expires_at <= current_time:
        return "expired"
    if not account.enabled:
        return "disabled"
    return "enabled"


def to_read_model(account: ProxyAccount, now: datetime | None = None) -> ProxyAccountRead:
    return ProxyAccountRead(
        id=account.id,
        username=account.username,
        password=account.password,
        enabled=account.enabled,
        expires_at=account.expires_at,
        expired_at=account.expired_at,
        created_at=account.created_at,
        updated_at=account.updated_at,
        status=account_status(account, now),
    )


class ProxyAccountService:
    def __init__(self, session: Session) -> None:
        self._session = session
        self._repository = ProxyAccountRepository(session)

    def list_page(
        self,
        page: int,
        page_size: int,
        username: str | None = None,
        status: str | None = None,
    ) -> tuple[list[ProxyAccountRead], int]:
        now = local_now()
        accounts, total = self._repository.list_page(
            page, page_size, username, status, now
        )
        return [to_read_model(account, now) for account in accounts], total

    def create(self, payload: ProxyAccountCreate) -> ProxyAccountRead:
        now = local_now()
        account = ProxyAccount(
            username=payload.username,
            password=payload.password,
            enabled=payload.enabled,
            expires_at=payload.expires_at,
            expired_at=(
                now if payload.expires_at is not None and payload.expires_at <= now else None
            ),
            created_at=now,
            updated_at=now,
        )
        if account.expired_at is not None:
            account.enabled = False
        try:
            self._repository.add(account)
            self._session.commit()
        except IntegrityError as exc:
            self._session.rollback()
            raise DuplicateUsernameError(payload.username) from exc
        self.sync_passwd()
        return to_read_model(account)

    def update(self, account_id: int, payload: ProxyAccountUpdate) -> ProxyAccountRead:
        account = self._get_required(account_id)
        now = local_now()
        account.username = payload.username
        account.password = payload.password
        account.enabled = payload.enabled
        account.expires_at = payload.expires_at
        account.updated_at = now
        if payload.expires_at is not None and payload.expires_at <= now:
            account.enabled = False
            account.expired_at = now
        else:
            account.expired_at = None
        try:
            self._session.commit()
        except IntegrityError as exc:
            self._session.rollback()
            raise DuplicateUsernameError(payload.username) from exc
        self.sync_passwd()
        return to_read_model(account)

    def update_password(self, account_id: int, password: str) -> ProxyAccountRead:
        account = self._get_required(account_id)
        account.password = password
        account.updated_at = local_now()
        self._session.commit()
        self.sync_passwd()
        return to_read_model(account)

    def set_enabled(self, account_id: int, enabled: bool) -> ProxyAccountRead:
        account = self._get_required(account_id)
        now = local_now()
        account.enabled = enabled
        account.updated_at = now
        if enabled and (account.expires_at is None or account.expires_at > now):
            account.expired_at = None
        if enabled and account.expires_at is not None and account.expires_at <= now:
            account.enabled = False
            account.expired_at = now
        self._session.commit()
        self.sync_passwd()
        return to_read_model(account)

    def delete(self, account_id: int) -> None:
        account = self._get_required(account_id)
        self._repository.delete(account)
        self._session.commit()
        self.sync_passwd()

    def scan_expired(self) -> int:
        now = local_now()
        expired_accounts = self._repository.list_expired_enabled(now)
        for account in expired_accounts:
            account.enabled = False
            account.expired_at = now
            account.updated_at = now
        if expired_accounts:
            self._session.commit()
            self.sync_passwd()
        return len(expired_accounts)

    def sync_passwd(self) -> int:
        now = local_now()
        active_accounts = self._repository.list_active_for_passwd(now)
        write_passwd_file(get_settings().squid_passwd_path, active_accounts)
        return len(active_accounts)

    def _get_required(self, account_id: int) -> ProxyAccount:
        account = self._repository.get_by_id(account_id)
        if account is None:
            raise AccountNotFoundError(str(account_id))
        return account
