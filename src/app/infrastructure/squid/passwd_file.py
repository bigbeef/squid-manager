from pathlib import Path

from passlib.hash import apr_md5_crypt

from src.app.infrastructure.db.models import ProxyAccount


def render_passwd_lines(accounts: list[ProxyAccount]) -> list[str]:
    lines: list[str] = []
    for account in accounts:
        password_hash = apr_md5_crypt.hash(account.password)
        lines.append(f"{account.username}:{password_hash}")
    return lines


def write_passwd_file(path: Path, accounts: list[ProxyAccount]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    tmp_path = path.with_name(f"{path.name}.tmp")
    content = "\n".join(render_passwd_lines(accounts))
    if content:
        content += "\n"
    tmp_path.write_text(content, encoding="utf-8")
    tmp_path.replace(path)
