---
title: "AlpacaHack Round 1 (Pwn) Writeup"
category: pwn
tags: ["AlpacaHack", "pwn", "abs(INT_MIN)", "整数溢出", "scanf %d%*c", "BUF_SIZE 0x100"]
signals: ["AlpacaHack 2024", "abs(INT_MIN)", "整数溢出", "scanf %d%*c", "BUF_SIZE 0x100", "栈溢出 No canary", "No PIE", "win函数", "/bin/cat /flag.txt", "pwn_unknown", "AlpacaHack", "Round", "Pwn", "abs"]
difficulty: easy
source: "https://www.ctfiot.com/200153.html"
tools: []
origin: des-import
origin_kind: cards
updated: 2026-10-24
---
# AlpacaHack Round 1 (Pwn) Writeup

> 赛事：AlpacaHack 2024 | 方向：pwn | 难度：easy

## 一句话总结

AlpacaHack Round 1 Pwn — abs(INT_MIN) 整数溢出旁路 size 校验 + unsigned 比较触发 280 字节栈溢出 + p32(win) 覆盖返回地址。

## 攻击链

1. get_size: scanf("%d%*c", &size); size = abs(size); size > 0x100 exit
2. abs(INT_MIN) = INT_MIN = -2147483648 > 0x100 不会触发 exit
3. size = -2147483648, 但 get_data for 循环 i < size 是 unsigned 比较
4. i < -2147483648 (unsigned) = i < 0x80000000 永真 (size_t 64位)
5. 实际写满 0x100 + 溢出覆盖返回地址
6. 280 字节 padding + p32(win) 覆盖返回地址
7. win(): execve("/bin/cat", "/flag.txt", NULL)

## 关键 payload

```
abs(INT_MIN)=INT_MIN 整数溢出 / get_data unsigned 比较 / 280 字节 + p32(win) / win() /bin/cat /flag.txt
```

## 经验教训

abs() 整数溢出是 size 校验旁路经典手法;unsigned 比较 -1 > BUF_SIZE 也是常见;No PIE + No canary 时代栈溢出是基础。

## 标签

abs(INT_MIN)、整数溢出、scanf %d%*c、BUF_SIZE 0x100、栈溢出 No canary、No PIE、win函数、/bin/cat /flag.txt、280字节padding

## 参考来源

- https://www.ctfiot.com/200153.html
- 原文件：AlpacaHack_Round_1_(Pwn)_Writeup.full.md
