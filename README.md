# Squid管理系统

一个 Python 3.11 + FastAPI + SQLite 的 Squid 代理账号管理后台。

## 功能

- 管理员登录，账号密码从 `.env` 读取。
- 所有接口默认必须登录，只有 `/health`、登录页、登录接口和静态资源免登录。
- 代理账号分页列表、创建、编辑、修改密码、启用/禁用、删除。
- 数据库保存代理账号明文密码，页面支持查看密码。
- 账号可设置本地时间过期时间。
- 后台任务每分钟扫描过期账号，把账号改为禁用并标记已过期。
- 自动生成 Squid htpasswd 兼容 passwd 文件；保存为禁用或过期时会立即从 passwd 文件中移除。

## 初始化

```powershell
python -m venv .venv
.\.venv\Scripts\activate
pip install -r requirements.txt
Copy-Item .env.example .env
```

修改 `.env` 中的 `ADMIN_PASSWORD` 和 `SESSION_SECRET_KEY`。

## 启动

```powershell
uvicorn src.app.web:app --reload
```

访问：

```text
http://127.0.0.1:8000/login
```

## 配置

```env
SQLITE_DB_PATH=data/squid_manager.db
SQUID_PASSWD_PATH=data/squid_passwd
ACCOUNT_EXPIRATION_SCAN_INTERVAL_SECONDS=60
```

`SQUID_PASSWD_PATH` 是生成给 Squid 使用的 passwd 文件路径。应用会把启用且未过期账号写入该文件。

## 安全说明

本项目按需求明文保存代理账号密码，并在登录后的页面/API 中返回明文密码。请确保：

- 不要把 SQLite 数据库文件暴露给非授权用户。
- 不要在日志中记录请求体和密码。
- 开放到公网时必须放在 HTTPS 后面，并设置 `SESSION_COOKIE_SECURE=true`。
- 生产环境必须修改默认管理员密码和 `SESSION_SECRET_KEY`。

## 验证

```powershell
python -m compileall src
python -m src.app.main
```
