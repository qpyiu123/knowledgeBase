---
title: "UCTC CTF 2024 高校新生网安赛 部分 WriteUp"
category: forensics
tags: ["UCTC CTF 2024 高校新生网安赛", "forensics", "UCTC", "新生赛", "zip-reverse", "010-Editor"]
signals: ["UCTC CTF 2024 高校新生网安赛 2024", "UCTC", "新生赛", "zip-reverse", "010-Editor", "栈溢出", "partial-RELRO", "amd64", "format-string", "forensic_disk", "ret2libc", "fmt_string", "reverse", "MISC"]
difficulty: easy
source: "https://www.ctfiot.com/218709.html"
tools: ["010Editor", "Java", "Python"]
origin: des-import
origin_kind: cards
updated: 2026-10-24
---
# UCTC CTF 2024 高校新生网安赛 部分 WriteUp

> 赛事：UCTC CTF 2024 高校新生网安赛 2024 | 方向：forensics | 难度：easy | 工具：010Editor、Java、Python

## 一句话总结

UCTC 高校新生赛 5 大题：MISC zip 反转 + PWN 栈溢出 + 格式化串 + py 反编译 + Java smali

## 攻击链

1. MISC 神秘的文件: 010 Editor 看到 zip 头被反转 → reverse() 还原 → 改头 50 4B 03 04 → 解压
2. PWN EZ_Stack: 栈溢出 offset=0x4c → pop_rdi_ret + /bin/sh + system
3. PWN userlogin: format string %13$s 泄漏 rootPassword → buffer overflow ret2backdoor 0x401262
4. REVERSE hash&py: pyinstxtractor 解包 → pyc 修 magic 0x0A0D0D55 (3.8) → md5 4 段拼接
5. REVERSE just_re_java: jadx 看 smali → Enc.ah 改码表 base64 → Flag 类 $() 拼结果

## 关键 payload

```
pyc magic 0x0A0D0D55 (Python 3.8) 修复后 md5 解密
```

## 经验教训

新生赛涵盖 reverse/pwn/web/misc；md5 4 段拼接 + base64 码表替换是入门 reverse

## 标签

UCTC、新生赛、zip-reverse、010-Editor、栈溢出、partial-RELRO、amd64、format-string、%s、pyinstxtractor、pyc、magic-number、md5、Android、smali、base64、码表替换

## 参考来源

- https://www.ctfiot.com/218709.html
- 原文件：UCTC_CTF_2024高校新生网安赛_部分WriteUp.full.md
