---
title: "UTCTF 2024 WriteUp by Min-Venom"
category: web
tags: ["UTCTF", "web", "http-range", "proc-mem", "file-listing", "ssrf-localhost"]
signals: ["UTCTF 2024", "http-range", "proc-mem", "file-listing", "ssrf-localhost", "click-counter", "baby-rsa", "lfsr-mid-square", "bleach-sql", "file_read", "UTCTF", "Min-Venom", "HTTP", "Range"]
difficulty: medium
source: "https://www.ctfiot.com/171127.html"
tools: []
origin: des-import
origin_kind: cards
updated: 2026-10-24
---
# UTCTF 2024 WriteUp by Min-Venom

> 赛事：UTCTF 2024 | 方向：web | 难度：medium

## 一句话总结

UTCTF 2024 Min-Venom：HTTP Range /proc/self/mem 爆破 + 整数溢出 count + baby RSA + LFSR 爆破。

## 攻击链

1. Home on the Range: HTTP Range 请求 + 目录穿越 → /proc/self/mem 爆破
2. 读 flag.txt 后删除，从 /proc/self/maps 找内存段
3. utflag' 字符串扫描爆破内存区域
4. 起子 0x1CE2C00C2000-0x1CE2D0296000 找到 flag
5. Basic Reversing: 117 116 102 108 97 103 123 105 95 99 52 110 95 114 51 118 33 125 = "utflag{i_c4n_r3v!}
6. click-counter: POST /api/absorbCompany/2 count=10000000000 整数溢出
7. guppy/click 路由 SSRF localhost
8. baby-rsa: p, q 已知直接解 d
9. c1: 1025252665848145091840062845209085931, 75575216771551332467177108987001026743883
10. 5 字符 Permutation hmsuu 等 120 种组合 - middle-square PRNG 爆破
11. get_random_number = int(str(seed*seed).zfill(12)[3:9])
12. submit_signature: 给 (n, e) + signature service, 输入 m=0 触发 m^s mod n, sig=1
13. server 误判 m=0 sig=1 接受 → flag{just_send_plaintext}
14. signal_signature_quirk: 之前 sig=1 是对 m=1 的合法 sig
15. input m=0 sig=1 → (0 * sha256 + 1) 等某些操作后通过校验

## 关键 payload

```
count=10000000000 (整数溢出 → 获得 10000)
```

## 经验教训

HTTP Range + 目录穿越 + 内存段爆破 是绕过 flag.txt 删除的经典手法。

## 标签

http-range、proc-mem、file-listing、ssrf-localhost、click-counter、baby-rsa、lfsr-mid-square、bleach-sql

## 参考来源

- https://www.ctfiot.com/171127.html
- 原文件：UTCTF2024_WriteUp_By_Mini-Venom.full.md
