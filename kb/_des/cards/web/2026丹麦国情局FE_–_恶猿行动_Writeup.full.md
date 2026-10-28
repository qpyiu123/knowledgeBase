---
title: "2026 丹麦国情局 FE – 恶猿行动 Writeup（OPERATION BAD PRIMATE 渗透）"
category: web
tags: ["2026 丹麦国情局 FE", "web", "丹麦国情局 FE 恶猿行动 2026", "MonkEZ/EDO 公司服务器", "OPERATION BAD PRIMATE", "vmdk 虚拟机"]
signals: ["2026 丹麦国情局 FE 2026", "丹麦国情局 FE 恶猿行动 2026", "MonkEZ/EDO 公司服务器", "OPERATION BAD PRIMATE", "vmdk 虚拟机", "仅主机模式", "nmap 三个 ssh + 一个 http", "sqlite 登录 SQLMap", "robots.txt 目录扫描", "sqli", "lfi", "pwn_unknown", "ssh", "MonkEZ"]
difficulty: hard
source: "https://www.ctfiot.com/298748.html"
tools: ["nmap", "sqlmap"]
origin: des-import
origin_kind: cards
updated: 2026-10-24
---
# 2026 丹麦国情局 FE – 恶猿行动 Writeup（OPERATION BAD PRIMATE 渗透）

> 赛事：2026 丹麦国情局 FE 2026 | 方向：web | 难度：hard | 工具：nmap、sqlmap

## 一句话总结

2026 丹麦国情局 FE 恶猿行动：MonkEZ/EDO 服务器渗透 - sqlmap + robots 路径穿越 + AES SSH 私钥 + docker 逃逸 + TLS 客户端证书恢复。

## 攻击链

1. 部署: 下载 vmdk → VM 仅主机模式（避免 NAT 暴露）
2. 外部侦察: nmap 三个 ssh + 一个 http
3. 初始访问: 登录框随便输 → sqlmap dump users → 拿 ssh 凭据
4. docker 登录 → html 注释提示至少 2 个漏洞
5. robots.txt 目录扫描 → 路径穿越
6. 路径穿越拿 AES 加密的 SSH 私钥
7. docker 逃逸: bash_history 查 docker 命令 → 需 TLS 客户端证书
8. 证书密钥已被删 → 需从备份/历史恢复
9. 最终: root@printserver

## 关键 payload

```
robots.txt → 路径穿越 → AES SSH 私钥
```

## 经验教训

丹麦国情局 FE 是面向计算机网络利用部 (CNE) 培训的高仿真 APT 渗透靶场，核心是 docker 逃逸 + TLS 客户端证书恢复；用 vmdk 部署 + 仅主机模式 防 VM 反弹。

## 标签

丹麦国情局 FE 恶猿行动 2026、MonkEZ/EDO 公司服务器、OPERATION BAD PRIMATE、vmdk 虚拟机、仅主机模式、nmap 三个 ssh + 一个 http、sqlite 登录 SQLMap、robots.txt 目录扫描、路径穿越 + AES 加密 SSH 私钥、docker 逃逸 bash_history、TLS 客户端证书密钥被删、root@printserver、root access

## 参考来源

- https://www.ctfiot.com/298748.html
- 原文件：2026丹麦国情局FE_–_恶猿行动_Writeup.full.md
