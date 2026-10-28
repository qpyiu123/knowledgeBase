---
title: "The Art of PHP – My CTF Journey and Untold Stories! (Orange Tsai)"
category: web
tags: ["多个", "web", "orange-tsai", "php-internals", "fsop", "csp-bypass"]
signals: ["多个 2024", "orange-tsai", "php-internals", "fsop", "csp-bypass", "max_input_vars", "lfi2rce", "phar", "laravel-mpdf", "rce", "Orange", "Tsai", "PHP", "CTF"]
difficulty: hard
source: "https://www.ctfiot.com/257942.html"
tools: ["Laravel", "PHP", "Wireshark"]
origin: des-import
origin_kind: cards
updated: 2026-10-24
---
# The Art of PHP – My CTF Journey and Untold Stories! (Orange Tsai)

> 赛事：多个 2024 | 方向：web | 难度：hard | 工具：Laravel、PHP、Wireshark

## 一句话总结

Orange Tsai 大佬回忆录：PHP 内核 + CTF 二十年 + 真实 CVE + FSOP + LFI 进化 + PHAR 反序列化 + Scoreboard 0day。

## 攻击链

1. PHP 7.0 Throwable 格式串 bug #71105 配合 new $model() 触发 RCE
2. max_input_vars 触发 warning 破坏 header 输出 → CSP 失效
3. WordPress maybe_unserialize 自动反序列化 DB 字符串 (Column Truncation 攻击)
4. LFI to RCE 二十年进化史 (filter chain → AFR → base64)
5. PHAR 反序列化 (Laravel + mPDF 链)
6. Hack the Scoreboard: 0day 改 CTF 排行榜
7. 多个真实 CVE 复盘 (Microsoft Exchange / SSL VPN / Apache HTTP)
8. XCTF / SECCON / DEFCON / cLEMENCy middle-endian 9-bit byte
9. One-Gadget / Return-to-CSU / House of Orange / FreeBSD 0day "God Mode
10. Wireshark bug / ELF parser bug 干扰对手

## 关键 payload

```
new $model() + Throwable $name
```

## 经验教训

CTF 不只是比赛，是研究交流的社区；Orange Tsai 真实 0day 经验 (Exchange/SSL VPN/Apache) 与 CTF 一脉相承。

## 标签

orange-tsai、php-internals、fsop、csp-bypass、max_input_vars、lfi2rce、phar、laravel-mpdf、scoreboard-hack、real-world-cve

## 参考来源

- https://www.ctfiot.com/257942.html
- 原文件：The_Art_of_PHP_–_My_CTF_Journey_and_Untold_Stories!.full.md
