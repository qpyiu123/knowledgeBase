---
title: "HGAME2025杭州电子科技大学网络攻防大赛 PWN writeup"
category: pwn
tags: ["HGAME 2025 杭电", "pwn", "pwn", "format-string", "vuln-negative-bypass", "libc-leak"]
signals: ["HGAME 2025 杭电 2025", "pwn", "format-string", "vuln-negative-bypass", "libc-leak", "ae64", "rop", "glibc-all-in-one", "fmt_string", "HGAME", "PWN", "format", "diary", "keeper"]
difficulty: medium
source: "https://www.ctfiot.com/228151.html"
tools: ["C", "ROP"]
origin: des-import
origin_kind: cards
updated: 2026-10-24
---
# HGAME2025杭州电子科技大学网络攻防大赛 PWN writeup

> 赛事：HGAME 2025 杭电 2025 | 方向：pwn | 难度：medium | 工具：C、ROP

## 一句话总结

HGAME 2025 PWN：format字符串+diary keeper off-by-null合并

## 攻击链

1. 3字节格式化字符串漏洞
2. vuln=-1绕过
3. %*d+%s 泄露libc地址
4. AE64编码system ROP链
5. week1 format系列
6. week2 diary keeper: PROTECT_PTR 指针保护
7. patchelf替换libc 2.35
8. 申请chunkA/B/C/D
9. off by null合并A+B+C
10. 读写合并大chunk操作B内容

## 关键 payload

```
%*d+%s leak libc; AE64(system ROP)
```

## 经验教训

负索引vuln可绕过；PROTECT_PTR指针保护可用低12位异或绕过

## 标签

pwn、format-string、vuln-negative-bypass、libc-leak、ae64、rop、glibc-all-in-one

## 参考来源

- https://www.ctfiot.com/228151.html
- 原文件：HGAME2025杭州电子科技大学网络攻防大赛_PWN_writeup.full.md
