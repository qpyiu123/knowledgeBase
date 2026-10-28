---
title: "2023 数字网络安全人才挑战赛 WriteUp by Arr3stY0u"
category: web
tags: ["数字网络安全人才挑战赛 2023", "web", "SSRF", "proc_net_arp", "gopher协议", "SQL盲注绕过滤"]
signals: ["数字网络安全人才挑战赛 2023 2023", "SSRF", "proc_net_arp", "gopher协议", "SQL盲注绕过滤", "HNP格", "离散DH_CRT", "TEA变种", "pwn_起源", "ssrf", "gopher", "SQL", "HNP", "CRT"]
difficulty: medium
source: "https://www.ctfiot.com/105328.html"
tools: ["ROP", "Sage"]
origin: des-import
origin_kind: cards
updated: 2026-10-24
---
# 2023 数字网络安全人才挑战赛 WriteUp by Arr3stY0u

> 赛事：数字网络安全人才挑战赛 2023 2023 | 方向：web | 难度：medium | 工具：ROP、Sage

## 一句话总结

综合 6 题：SSRF+gopher+SQL 盲注绕过滤+HNP 格+DH CRT+TEA 变种+pwn 起源 ROP。

## 攻击链

1. easy_curl: file:///proc/net/arp 读内网 IP，绕过 127 关键字
2. gopher://127.1:80/ POST flag.php key=2730ea2fd4c40df0f8b7fdb6738221d6
3. 双重 URL 编码 gopher payload，hackbar 发包
4. Simple Message Board: 搜索 SQL 注入，禁 union 用 if 绕
5. 禁 substr/ascii 用 ord + left 绕，二分盲注
6. babysecret: 30 个 inputs 构造 HNP 格，sage LLL 求 x
7. factor(n-1) 多素数 p_i，discrete_log 各 p_i 模下解 ri，CRT 拼 x
8. game: 调试器改 dword_AEE880 = 0x280 改后续 XOR
9. easykernel: dev_write 函数，TEA 变种 -= 改 += 调顺序还原
10. pwn 起源: read 0x28 字节 + p32(0x100006F0) 大端跳转 ROP
11. one_gadget 配合 pwncli 一把梭

## 关键 payload

```
POST /flag.php HTTP/1.1\r\nHost: 10.252.47.1\r\nContent-Length: 36\r\n\r\nkey=2730ea2fd4c40df0f8b7fdb6738221d6
```

## 经验教训

proc/net/arp 替代 127 关键字查内网；SQL 注入禁 union 用 if + 禁 substr 用 ord/left；HNP 用格攻击 + 离散 DH 用 CRT 拼。

## 标签

SSRF、proc_net_arp、gopher协议、SQL盲注绕过滤、HNP格、离散DH_CRT、TEA变种、pwn_起源、山海关

## 参考来源

- https://www.ctfiot.com/105328.html
- 原文件：2023_数字网络安全人才挑战赛_writeup_by_Arr3stY0u.full.md
