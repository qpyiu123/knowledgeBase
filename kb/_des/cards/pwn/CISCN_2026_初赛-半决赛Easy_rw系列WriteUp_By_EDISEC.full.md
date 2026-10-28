---
title: "CISCN 2026 初赛-半决赛 Easy_rw 系列 WriteUp By EDISEC"
category: pwn
tags: ["CISCN", "pwn", "Easy_rw", "自定义packet协议", "header+packet_len+payload", "struct.pack!II"]
signals: ["CISCN 2026", "Easy_rw", "自定义packet协议", "header+packet_len+payload", "struct.pack!II", "Easy_rw_revenge", "RC4 KSA", "libc.srand(time()) 32字节key", "0xFFFF2525 AUTH_MAGIC", "forensic_traffic", "CISCN", "packet", "header", "len"]
difficulty: hard
source: "https://www.ctfiot.com/306898.html"
tools: ["ROP"]
origin: des-import
origin_kind: cards
updated: 2026-10-24
---
# CISCN 2026 初赛-半决赛 Easy_rw 系列 WriteUp By EDISEC

> 赛事：CISCN 2026 | 方向：pwn | 难度：hard | 工具：ROP

## 一句话总结

CISCN 2026 Easy_rw 系列 — 自定义 packet 协议 (header+len+payload) + Easy_rw_revenge proxy RC4 转发 + rtsp:// 命令注入 + libc leak + ORW ROP + AES-ECB 0123456789ABCDEF 解密。

## 攻击链

1. Easy_rw: 自定义 packet 协议 header(4) + packet_len(4) + payload
2. Easy_rw_revenge: proxy 192.168.18.137:9999 → server 127.0.0.1:7777
3. RC4: libc.srand(time()) 生成 32 字节 key, KSA 初始化
4. AUTH_MAGIC=0xFFFF2525 认证, FORWARD_MAGIC=0x7F687985 转发
5. rtsp:// 协议 + XOR 0x41*8 + 转发到 server
6. server: add/delete/show/edit 命令, cookie 认证
7. libc leak: large=u64(pack[0:6].ljust(8,b''\x00'')), libc_base=large-0x21b110
8. ORW ROP: open /flag + read + write stdout
9. 加密数据 AES-ECB 0123456789ABCDEF 解密

## 关键 payload

```
struct.pack!II / RC4 KSA / libc.srand(time()) / AUTH_MAGIC 0xFFFF2525 / FORWARD_MAGIC 0x7F687985 / rtsp:// proxy / libc 0x21b110 / ORW ROP / AES-ECB 0123456789ABCDEF
```

## 经验教训

自定义二进制协议 reverse: header+length+payload 模板;RC4 + libc.srand(time()) 是经典 PRNG 漏洞;rtsp:// 是 rfc 协议伪装;ORW 是无 system 时的标准解法。

## 标签

Easy_rw、自定义packet协议、header+packet_len+payload、struct.pack!II、Easy_rw_revenge、RC4 KSA、libc.srand(time()) 32字节key、0xFFFF2525 AUTH_MAGIC、0x7F687985 FORWARD_MAGIC、rtsp:// proxy转发、libc 0x21b110、libc leak、_IO_list_all、ORW ROP、/flag 0123456789ABCDEF ECB

## 参考来源

- https://www.ctfiot.com/306898.html
- 原文件：CISCN_2026_初赛-半决赛Easy_rw系列WriteUp_By_EDISEC.full.md
