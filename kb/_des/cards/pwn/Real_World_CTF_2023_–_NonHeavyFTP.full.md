---
title: "Real World CTF 2023 - NonHeavyFTP Writeup"
category: pwn
tags: ["Real World CTF 2023", "pwn", "ftp", "lightftp", "race-condition", "strcpy"]
signals: ["Real World CTF 2023 2023", "ftp", "lightftp", "race-condition", "strcpy", "ftp-list", "ftp-retr", "file-read", "anonymous", "pwn_unknown", "Real", "World", "CTF", "NonHeavyFTP"]
difficulty: medium
source: "https://www.ctfiot.com/90436.html"
tools: []
origin: des-import
origin_kind: cards
updated: 2026-10-24
---
# Real World CTF 2023 - NonHeavyFTP Writeup

> 赛事：Real World CTF 2023 2023 | 方向：pwn | 难度：medium

## 一句话总结

Real World CTF 2023 NonHeavyFTP: LightFTP 2.2 源码审计发现 ftpUSER 共享 context->FileName 触发 list_thread race condition，列目录/读 flag 任意文件。

## 攻击链

1. LightFTP 2.2 (最新) 源码 + 编译 binary + config readonly
2. fuzz (boofuzz) 500 exec/s 跑 32k session 无果 → 转向源码审计
3. 漏洞点: ftpUSER (ftpserv.c#L265) strcpy(context->FileName, params) - 看似可溢出但实际不能
4. 真实漏洞: ftpLIST + stor_thread 共享 context->FileName
5. 攻击: LIST ''random'' 触发 list_thread 阻塞 (无 client 连 data port)
6. 此时 USER '/etc' 覆盖 context->FileName 为任意路径
7. 连接 data port 让 list_thread 解阻塞, 走 open(context->FileName) 任意读
8. 步骤 1: LIST 触发 list_thread + 立即 USER / 列根目录
9. 步骤 2: RETR hello.txt + USER /flag.deb10154-8cb2-11ed-be49-0242ac110002 读 flag
10. 同理可读任意文件

## 关键 payload

```
p.sendline(b"LIST ") + p.sendline(b"USER /") + connect(data_port)
```

## 经验教训

FTP USER/LIST 等命令共享 context->FileName 缓冲区是经典 race condition；strcpy 看似漏洞但实际 buffer 不够大；线程共享变量的 race 是 read-only bypass 关键。

## 标签

ftp、lightftp、race-condition、strcpy、ftp-list、ftp-retr、file-read、anonymous、source-review

## 参考来源

- https://www.ctfiot.com/90436.html
- 原文件：Real_World_CTF_2023_–_NonHeavyFTP.full.md
