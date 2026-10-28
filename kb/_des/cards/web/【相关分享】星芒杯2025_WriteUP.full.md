---
title: "【相关分享】星芒杯 2025 WriteUP"
category: web
tags: ["星芒杯", "web", "代码审计", "call_user_func-RCE", "ISO-8859-1-to-UTF8", "盲文解码"]
signals: ["星芒杯 2025", "代码审计", "call_user_func-RCE", "ISO-8859-1-to-UTF8", "盲文解码", "file读取-LFI", "隼目安全", "web_unknown", "Web", "call_user_func", "RCE", "ISO-8859-1", "UTF-8", "LFI"]
difficulty: medium
source: "https://www.ctfiot.com/285553.html"
tools: ["PHP"]
origin: des-import
origin_kind: cards
updated: 2026-10-24
---
# 【相关分享】星芒杯 2025 WriteUP

> 赛事：星芒杯 2025 | 方向：web | 难度：medium | 工具：PHP

## 一句话总结

星芒杯 2025 Web WP，代码审计 call_user_func RCE + ISO-8859-1/UTF-8 编码还原 + 盲文解码 + LFI 文件读取。

## 攻击链

1. 1. PHP 代码审计 call_user_func($func, $param) 函数名 RCE /2. 提交 flag{call_user_func} /3. 布莱切利庄园 ISO-8859-1 → UTF-8 username 还原 /4. 盲文 password 解码 /5. /archives?file= 文件读取

## 关键 payload

```
flag{call_user_func}  darkguard98 / secretgate45  ISO-8859-1 latin1
```

## 经验教训

call_user_func($func, $param) 是 PHP 经典 RCE；ISO-8859-1 → UTF-8 双重编码还原是乱码恢复经典；盲文密码可直接解码；?file= LFI 是常见文件读取。

## 标签

代码审计、call_user_func-RCE、ISO-8859-1-to-UTF8、盲文解码、file读取-LFI、隼目安全

## 参考来源

- https://www.ctfiot.com/285553.html
- 原文件：【相关分享】星芒杯2025_WriteUP.full.md
