## 创建目录
```
mkdir -p /app/docker/squid/cache
mkdir -p /app/docker/squid/errors
mkdir -p /app/docker/squid/log
chown -R 13:13 /app/docker/squid/cache
chown -R 13:13 /app/docker/squid/log
```

### 创建密码文件
```
touch /app/docker/squid/passwd
chmod 777 /app/docker/squid/passwd
```

### 配置文件
```
cat << EOF > /app/docker/squid/squid.conf
auth_param basic children 5 startup=2 idle=1
auth_param basic casesensitive off
auth_param basic log credential on
#################################################################################
# **重点**，这里/app/docker/squid/passwd要挂载到宿主机，暴露给squid-manager管理
#################################################################################
auth_param basic program /usr/lib/squid/basic_ncsa_auth /app/docker/squid/passwd
acl auth_user proxy_auth REQUIRED
http_access allow auth_user

# 禁止所有日志
access_log none
cache_log /dev/null
logfile_rotate 0
cache_store_log none
# 完全隐藏版本信息
httpd_suppress_version_string on
via off
forwarded_for delete
# 移除所有标识性头部
reply_header_access Server deny all
reply_header_access X-Cache deny all
reply_header_access X-Squid-Error deny all
reply_header_access Via deny all
reply_header_access X-Forwarded-For deny all

#以下是高匿的设置
request_header_access Via deny all
request_header_access X-Forwarded-For deny all

http_port 3128

EOF
chmod 777 /app/docker/squid/squid.conf
```


## 启动容器
```
docker rm -f squid
docker run --name squid \
--restart=always \
--ulimit nofile=65535:65535 \
--log-driver=none \
-p 63128:3128 \
-v /app/docker/squid:/app/docker/squid \
-v /app/docker/squid/squid.conf:/etc/squid/squid.conf \
-v /app/docker/squid/errors:/usr/share/squid/errors \
-v /app/docker/squid/log:/var/log/squid \
-d ubuntu/squid:6.13-25.04_beta

docker logs -tf --tail=100 squid
```