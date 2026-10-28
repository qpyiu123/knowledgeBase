---
title: "2026 软件系统安全赛初赛 re1（dropper+stager .pyc 反编译 视频解码）"
category: reverse
tags: ["2026 软件系统安全赛", "reverse", "软件系统安全赛 2026 初赛", "64 位 .elf Loader dropper", "video.mp4 黑白色块", "stager_pyc_base64 内嵌"]
signals: ["2026 软件系统安全赛 2026", "软件系统安全赛 2026 初赛", "64 位 .elf Loader dropper", "video.mp4 黑白色块", "stager_pyc_base64 内嵌", ".pyc 反编译 decompyle3 uncompyle6", "AES 解密视频数据", "魔改算法双重保护", "AI 梭解两道题", "reverse", "crypto_unknown", "stego_traffic", "re1", "elf"]
difficulty: hard
source: "https://www.ctfiot.com/302112.html"
tools: []
origin: des-import
origin_kind: cards
updated: 2026-10-24
---
# 2026 软件系统安全赛初赛 re1（dropper+stager .pyc 反编译 视频解码）

> 赛事：2026 软件系统安全赛 2026 | 方向：reverse | 难度：hard

## 一句话总结

2026 软件系统安全赛 re1：64 位 .elf Loader dropper + 内嵌 base64 .pyc stager + 视频黑白色块解码。

## 攻击链

1. 64 位 .elf Loader 加载 video.mp4
2. file_exists(video.mp4) 检查
3. 内嵌 stager_pyc_base64[] + base64_decode
4. 加载 .pyc 字节码执行（dropper 模式）
5. 视频帧黑白色块 → 解码出 flag
6. re1 AI 梭出，re2 手动调半天，re3 .so 加密逻辑没找到

## 关键 payload

```
stager_pyc_base64 → base64_decode → .pyc exec
```

## 经验教训

Loader 加载 video.mp4 + 内嵌 stager_pyc 是 2026 新型 ELF 逆向套路；.pyc 字节码用 decompyle3/uncompyle6 反编译；视频像素作密文/明文是新颖 stego 形式。

## 标签

软件系统安全赛 2026 初赛、64 位 .elf Loader dropper、video.mp4 黑白色块、stager_pyc_base64 内嵌、.pyc 反编译 decompyle3 uncompyle6、AES 解密视频数据、魔改算法双重保护、AI 梭解两道题、re2 re3 没解出来

## 参考来源

- https://www.ctfiot.com/302112.html
- 原文件：2026软件系统安全赛_初赛-re1（dropper+stager_.pyc反编译_视频解码）.full.md
