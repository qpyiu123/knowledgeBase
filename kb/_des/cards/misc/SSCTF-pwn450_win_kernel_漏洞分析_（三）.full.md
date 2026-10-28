---
title: "SSCTF-pwn450 win kernel 漏洞分析 (三)"
category: misc
tags: ["SSCTF", "misc", "windows-kernel", "gdi-bug", "bitmap-surfobj", "kmdf-driver"]
signals: ["SSCTF 2014", "windows-kernel", "gdi-bug", "bitmap-surfobj", "kmdf-driver", "win32k-bsod", "misc_unknown", "Windows", "SP1", "x86", "win32k", "EngPaint", "BSoD", "CloverSec"]
difficulty: hard
source: "https://www.ctfiot.com/154359.html"
tools: ["x86/x64"]
origin: des-import
origin_kind: cards
updated: 2026-10-24
---
# SSCTF-pwn450 win kernel 漏洞分析 (三)

> 赛事：SSCTF 2014 | 方向：misc | 难度：hard | 工具：x86/x64

## 一句话总结

Windows 7 SP1 x86 下 win32k!EngPaint 越界 BSoD 漏洞剖析 (CloverSec bee13oy 作品)。

## 攻击链

1. demo_CreateBitmapIndirect 创建 8x8 灰度 HBITMAP
2. NtGdiSetBitmapAttributes 系统调用号 0x1110
3. argv1 = 0x8f9 触发 win32k!EngPaint BSOD
4. CreateRectRgnIndirect(rect.left=0x368c, top=0x400000) 创建巨型 region
5. CreateCompatibleDC(0) 拿 HDC
6. SelectObject 选入 HDC 触发 SURFOBJ 越界
7. FillRgn 调用 EngPaint 崩溃 win32k!bGetRealizedBrush
8. 手工双机调试 kd 下断 EngPaint + pvGetEngRbrush
9. fe723018 即 SURFOBJ 结构体
10. fe723008+1c 偏移是 SURFOBJ c 字段
11. test [eax+24h],1 触发 access violation
12. 通过构造特殊 SURFOBJ 走 if 分支 bIsCompatible 失败

## 关键 payload

```
NtGdiSetBitmapAttributes(hBitmap1, 0x8f9)
```

## 经验教训

早期 win32k 图形子系统有大量未公开 IOCTL/结构偏移；现代 Win10/Win11 已修复此类 ENG 路径。

## 标签

windows-kernel、gdi-bug、bitmap-surfobj、kmdf-driver、win32k-bsod

## 参考来源

- https://www.ctfiot.com/154359.html
- 原文件：SSCTF-pwn450_win_kernel_漏洞分析_（三）.full.md
