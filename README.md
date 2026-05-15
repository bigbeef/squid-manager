# Squid代理管理系统

Squid代理管理系统是一个用于管理 Squid 代理账号的轻量后台。

如果你在使用 Squid 搭建代理服务，并且需要给不同用户分配账号、设置密码、控制启用状态或配置到期时间，这个项目可以帮你用网页后台完成这些操作，不需要手动维护 Squid 的认证文件。

## 项目能做什么

Squid代理管理系统主要解决 Squid 代理账号不好管理的问题。

你可以在后台创建代理账号，设置账号密码和过期时间，随时启用、禁用或删除账号。系统会自动把可用账号同步到 Squid 使用的 passwd 文件中，账号被禁用、删除或到期后，会自动从生效配置中移除。

## 适合场景

- 自建 Squid 代理服务
- 需要给多个用户分配代理账号
- 希望按时间控制代理账号有效期
- 不想手动编辑 Squid passwd 文件
- 需要一个简单的网页后台来管理代理账号

## 主要功能

- **代理账号管理**：支持新增、编辑、删除代理账号。
- **密码管理**：支持设置、修改和查看账号密码。
- **账号启停控制**：可以随时启用或禁用指定账号。
- **过期时间设置**：可以给账号设置到期时间，也可以设置为长期有效。
- **自动过期处理**：账号到期后会自动失效，不再允许继续使用代理。
- **自动同步 Squid**：账号变更后自动更新 Squid 使用的认证文件。
- **手动同步能力**：后台提供手动同步按钮，方便在需要时重新生成 passwd 文件。
- **分页账号列表**：账号较多时可以分页查看和管理。
- **管理员登录**：后台需要管理员登录后才能访问。
- **验证码保护**：登录页面带验证码，并使用独立的浅蓝科技风登录界面，减少后台被暴力尝试的风险。
- **Docker 部署**：支持通过 Docker 快速部署。

## 账号状态说明

- **启用**：账号正常生效，可以用于 Squid 代理认证。
- **已禁用**：账号被手动停用，不会写入 Squid 认证文件。
- **已过期**：账号超过设置的过期时间，系统会自动停用。

## 快速开始

### Docker Compose 部署

项目根目录已提供 `docker-compose.yml` 和 `squid.conf`，会同时启动 `squid-manager` 管理后台和 `squid` 代理服务。

```shell
cd ~
git clone https://gitee.com/winfed/squid-manager.git

cd ~/squid-manager
git pull
docker build -f docker/Dockerfile -t winfed/squid-manager .

docker compose up -d
```

首次启动时，Compose 会自动创建运行时目录和密码文件：

```text
squid-manager/          # 管理系统 SQLite 数据目录，不提交到 Git
squid/                  # Squid 运行时目录，不提交到 Git
```

访问后台：

```text
http://服务器IP:56688
```

Squid 代理地址：

```text
服务器IP:63128
```

默认管理员账号由 `docker-compose.yml` 配置：

```text
ADMIN_USERNAME=admin
ADMIN_PASSWORD=change-this-password
```

请在正式使用前修改 `ADMIN_PASSWORD`。

### Docker 镜像构建

构建镜像（非必须，可直接拉公共镜像）：

```shell
cd ~
git clone https://gitee.com/winfed/squid-manager.git

cd ~/squid-manager
git pull
docker build -f docker/Dockerfile -t winfed/squid-manager .
```

## 配置说明

| 配置项 | 说明 |
| --- | --- |
| `ADMIN_USERNAME` | 后台管理员用户名 |
| `ADMIN_PASSWORD` | 后台管理员密码 |
| `SESSION_SECRET_KEY` | 登录会话密钥，建议设置为随机字符串 |
| `SQUID_PASSWD_PATH` | 生成给 Squid 使用的 passwd 文件路径 |
| `SQLITE_DB_PATH` | 账号数据保存路径 |
| `ACCOUNT_EXPIRATION_SCAN_INTERVAL_SECONDS` | 账号过期检查间隔，默认 60 秒 |

常用目录说明：

| 路径 | 说明 |
| --- | --- |
| `./squid-manager` | 管理系统 SQLite 数据目录 |
| `./squid` | Squid 运行时目录，保存 passwd、cache、log 等文件 |
| `./squid.conf` | Squid 配置文件，提交到 Git |

## Squid 配套搭建教程

Compose 部署已包含 Squid 服务。如果你只想单独了解 Squid 容器配置，可以参考：

[README_SQUID.md](https://github.com/bigbeef/squid-manager/blob/master/README_SQUID.md)

Squid代理管理系统只负责管理 Squid 认证账号，代理流量仍由 Squid 服务处理。

## 本地运行

如果你想在本地开发或测试，可以使用：

```powershell
pip install -r requirements.txt
uvicorn src.app.web:app --reload
```

访问：

```text
http://127.0.0.1:8000/login
```

## 注意事项

- 为了支持在页面查看密码并生成 Squid 认证文件，代理账号密码会以可读取形式保存在管理系统中。
- 请将后台部署在可信环境中，并保护好管理员账号、管理员密码和数据目录。
- 正式使用时请务必修改默认密码。
- 删除、禁用或过期的账号会从 Squid 生效账号中移除。

## 系统截图

![登录页面](pic/login.png)

![账号管理](pic/account.png)

## 开源协议

本项目使用 [MIT License](LICENSE) 协议
