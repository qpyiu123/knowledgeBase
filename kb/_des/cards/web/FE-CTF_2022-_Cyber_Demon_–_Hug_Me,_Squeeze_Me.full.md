---
title: "FE-CTF 2022: Cyber Demon – Hug Me, Squeeze Me"
category: web
tags: ["FE-CTF 2022", "web", "pwn", "lzma", "sqz", "libsqz.so"]
signals: ["FE-CTF 2022 2022", "pwn", "lzma", "sqz", "libsqz.so", "elf-section", "fetch-verbose", "彩蛋", "web_unknown", "FE-CTF", "Hug", "Squeeze", "ELF", "libsqz"]
difficulty: medium
source: "https://www.ctfiot.com/78935.html"
tools: []
origin: des-import
origin_kind: cards
updated: 2026-10-24
---
# FE-CTF 2022: Cyber Demon – Hug Me, Squeeze Me

> 赛事：FE-CTF 2022 2022 | 方向：web | 难度：medium

## 一句话总结

FE-CTF Hug Me Squeeze Me：ELF彩蛋+libsqz.so LZMA压缩+OOM Kill

## 攻击链

1. SECTIONS有._STRIP_ELF_BEFORE_CTF_ = 0x1337 彩蛋符号
2. 运行./words.elf (LD_LIBRARY_PATH)
3. 交互: Count/Unique/Ignore case/Verbose/Links/Words/Fetch
4. Fetch https://www.google.com 被Killed（OOM）
5. 改 libsqz.so → touch libsqz.c → gcc -shared 创建空库
6. Fetch https://neverssl.com 不Killed
7. libsqz是 LZMA 压缩库

## 关键 payload

```
_STRIP_ELF_BEFORE_CTF_ = 0x1337  # ELF彩蛋
```

## 经验教训

替换 libsqz.so 为空库可绕过OOM Kill

## 标签

pwn、lzma、sqz、libsqz.so、elf-section、fetch-verbose、彩蛋

## 参考来源

- https://www.ctfiot.com/78935.html
- 原文件：FE-CTF_2022-_Cyber_Demon_–_Hug_Me,_Squeeze_Me.full.md
