---
title: "All You Need Is MCP – LLMs Solving a DEF CON CTF Finals Challenge"
category: reverse
tags: ["DEF CON CTF", "reverse", "ico二进制", "byte协议", "0x10 enable", "0x22 build default"]
signals: ["DEF CON CTF 2025", "ico二进制", "byte协议", "0x10 enable", "0x22 build default", "0x32 metadata bundle", "/flag 加载", "g_FlagString全局", "tEXt Author chunk", "reverse", "DEF", "CON", "CTF", "Finals"]
difficulty: hard
source: "https://www.ctfiot.com/257948.html"
tools: ["IDA"]
origin: des-import
origin_kind: cards
updated: 2026-10-24
---
# All You Need Is MCP – LLMs Solving a DEF CON CTF Finals Challenge

> 赛事：DEF CON CTF 2025 | 方向：reverse | 难度：hard | 工具：IDA

## 一句话总结

DEF CON CTF Finals 2025 — ico 二进制 byte 协议 (0x10/0x22/0x32) + 服务端 fork + /flag → tEXt Author chunk + MCP LLM 自动化 + IDA 改名 (g_FlagString, server_main)。

## 攻击链

1. 服务端 ico 二进制: amd64-64-little, Partial RELRO, No canary, NX, No PIE
2. 协议: 0x10 enable session, 0x22 build default entry 复制 /flag → Author, 0x32\x01 request bundle
3. 服务端 init_flag_from_file: open /flag + read → g_FlagString 全局
4. cmd_send_metadata_bundle 返回 PNG 格式含 tEXt Author chunk = flag
5. MCP 自动化: LLM 调 send_cmd(0x10) → 0x22 → 0x32 + parse_kv_payload
6. 解析 0x32 payload 找 "Author" 后下一 printable token 即 flag
7. IDA 改名: server_main / accept_fork_loop / handle_connection / dispatch_loop / init_flag_from_file / parse_ncif_container / g_FlagString
8. 服务端 fork + drop_privileges + set_alarm(16) 后处理

## 关键 payload

```
0x10 enable + 0x22 build default + 0x32\x01 metadata bundle / g_FlagString = /flag / tEXt Author chunk / MCP 自动化 parse_kv_payload
```

## 经验教训

服务端常用 byte 协议 (tag+length+payload) 替代 HTTP;flag 通常藏在 metadata chunk (PNG tEXt) 中;MCP 让 LLM 直接调工具打 CTF Finals 是新趋势。

## 标签

ico二进制、byte协议、0x10 enable、0x22 build default、0x32 metadata bundle、/flag 加载、g_FlagString全局、tEXt Author chunk、PNG IDAT、MCP LLM、IDA renaming、server_main fork、accept_fork_loop、drop_privileges_to_user

## 参考来源

- https://www.ctfiot.com/257948.html
- 原文件：All_You_Need_Is_MCP_–_LLMs_Solving_a_DEF_CON_CTF_Finals_Challenge.full.md
