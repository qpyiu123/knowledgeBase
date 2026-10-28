---
title: "ACTF 2025 writeup by Mini-Venom"
category: web
tags: ["ACTF", "web", "Flask任意文件读", "命令注入", "os.system", "sha256已知哈希爆破"]
signals: ["ACTF 2025", "Flask任意文件读", "命令注入", "os.system", "sha256已知哈希爆破", "backdoor密码", "AES-CBC cookie伪造", "用户登录绕过", "not so web 1", "web_unknown", "ACTF", "upload", "admin", "backdoor"]
difficulty: medium
source: "https://www.ctfiot.com/243984.html"
tools: ["Flask", "Python"]
origin: des-import
origin_kind: cards
updated: 2026-10-24
---
# ACTF 2025 writeup by Mini-Venom

> 赛事：ACTF 2025 | 方向：web | 难度：medium | 工具：Flask、Python

## 一句话总结

ACTF 2025 — upload 任意文件读 + admin backdoor 密码爆破 + os.system 命令注入 + not so web 1 AES-CBC cookie 用户态加密。

## 攻击链

1. ACTF upload: upload?file_path=../../../../app/app.py 任意文件读源码
2. 源码中 admin 密码 hash=32783cef... 是 backdoor (sha256)
3. admin 走 os.system(f'base64 {file_path} > /tmp/...') 命令注入
4. file_path=; ls / > /tmp/aaa # 列根目录得 Fl4g_is_H3r3
5. file_path=../../../../Fl4g_is_H3r3 读 flag
6. not so web 1: AES-CBC cookie 加密 (iv + padded)，validate_cookie 检查 json.loads 成功
7. 自定义 APPUser dataclass, 管理员 password_raw 在 ADMIN_PASSWORD
8. 加密逻辑 generate_cookie 走 AES-CBC，iv 随机，pad PKCS7

## 关键 payload

```
admin 密码 sha256=backdoor / os.system 命令注入 / file_path=; cmd > /tmp / AES-CBC(iv, KEY) cookie 伪造
```

## 经验教训

Flask app.py 任意文件读 + sha256 哈希爆破 = admin 入口;os.system 拼接 file_path 是经典命令注入;自定义 AES-CBC cookie 加密可用密钥重放+iv 控制伪造。

## 标签

Flask任意文件读、命令注入、os.system、sha256已知哈希爆破、backdoor密码、AES-CBC cookie伪造、用户登录绕过、not so web 1、pad-oracle、AES-CBC用户态

## 参考来源

- https://www.ctfiot.com/243984.html
- 原文件：ACTF_2025_writeup_by_Mini-Venom.full.md
