from fastapi import APIRouter, HTTPException, Query, status

from src.app.application.schemas.proxy_account import (
    ProxyAccountCreate,
    ProxyAccountEnabledUpdate,
    ProxyAccountPage,
    ProxyAccountPasswordUpdate,
    ProxyAccountRead,
    ProxyAccountUpdate,
)
from src.app.application.services.proxy_account_service import (
    AccountNotFoundError,
    DuplicateUsernameError,
    ProxyAccountService,
)
from src.app.infrastructure.db.session import get_session


router = APIRouter(prefix="/api/proxy-accounts", tags=["proxy-accounts"])


def _service_response(callback):
    session = get_session()
    try:
        return callback(ProxyAccountService(session))
    except AccountNotFoundError as exc:
        raise HTTPException(status_code=404, detail="account not found") from exc
    except DuplicateUsernameError as exc:
        raise HTTPException(status_code=409, detail="username already exists") from exc
    finally:
        session.close()


@router.get("", response_model=ProxyAccountPage)
def list_accounts(
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
) -> ProxyAccountPage:
    def action(service: ProxyAccountService) -> ProxyAccountPage:
        items, total = service.list_page(page, page_size)
        return ProxyAccountPage(page=page, page_size=page_size, total=total, items=items)

    return _service_response(action)


@router.post("", response_model=ProxyAccountRead, status_code=status.HTTP_201_CREATED)
def create_account(payload: ProxyAccountCreate) -> ProxyAccountRead:
    return _service_response(lambda service: service.create(payload))


@router.put("/{account_id}", response_model=ProxyAccountRead)
def update_account(account_id: int, payload: ProxyAccountUpdate) -> ProxyAccountRead:
    return _service_response(lambda service: service.update(account_id, payload))


@router.patch("/{account_id}/password", response_model=ProxyAccountRead)
def update_password(account_id: int, payload: ProxyAccountPasswordUpdate) -> ProxyAccountRead:
    return _service_response(lambda service: service.update_password(account_id, payload.password))


@router.patch("/{account_id}/enabled", response_model=ProxyAccountRead)
def set_enabled(account_id: int, payload: ProxyAccountEnabledUpdate) -> ProxyAccountRead:
    return _service_response(lambda service: service.set_enabled(account_id, payload.enabled))


@router.delete("/{account_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_account(account_id: int) -> None:
    _service_response(lambda service: service.delete(account_id))


@router.post("/sync-passwd")
def sync_passwd() -> dict[str, int]:
    return _service_response(lambda service: {"active_accounts": service.sync_passwd()})


@router.post("/scan-expired")
def scan_expired() -> dict[str, int]:
    return _service_response(lambda service: {"expired_accounts": service.scan_expired()})
