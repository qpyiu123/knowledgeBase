---
title: "强网拟态2025初赛 Mobile方向 just Writeup - Unity il2cpp Frida hook"
category: reverse
tags: ["强网拟态2025初赛 Mobile方向", "reverse", "Unity", "il2cpp", "Frida", "hook_clone"]
signals: ["强网拟态2025初赛 Mobile方向 2025", "Unity", "il2cpp", "Frida", "hook_clone", "Arm64Writer", "nop_64", "crc_check", "global-metadata.dat", "reverse", "Mobile", "just", "NOP", "CRC"]
difficulty: hard
source: "https://www.ctfiot.com/275655.html"
tools: []
origin: des-import
origin_kind: cards
updated: 2026-10-24
---
# 强网拟态2025初赛 Mobile方向 just Writeup - Unity il2cpp Frida hook

> 赛事：强网拟态2025初赛 Mobile方向 2025 | 方向：reverse | 难度：hard

## 一句话总结

强网拟态2025初赛Mobile just:Unity il2cpp Frida hook_clone NOP CRC+global-metadata.dat XOR解密。

## 攻击链

1. Frida hook_clone监听子线程栈地址 → 识别libjust.so → nop_64(base+0x119F8)过CRC校验 → Il2CppDumper dump global-metadata.dat → dec_global_metadata函数:XOR解密 (src[2*v2+0x202] ^ src[2*(v9%v2)+0x202])

## 关键 payload

```
Frida hook_clone + nop_64(0x119F8) CRC + global-metadata.dat XOR解密 + Il2CppDumper
```

## 经验教训

Unity il2cpp游戏Mobile逆向:Frida hook clone监控子线程栈地址,识别目标so后NOP关键地址过CRC校验;global-metadata.dat需Il2CppDumper解;dec_global_metadata用XOR链式解v9%v2;Arm64Writer.w.putRet()写RET指令。

## 标签

Unity、il2cpp、Frida、hook_clone、Arm64Writer、nop_64、crc_check、global-metadata.dat、dec_global_metadata、XOR解密、Il2CppDumper、Android_Reverse、Mobile

## 参考来源

- https://www.ctfiot.com/275655.html
- 原文件：强网拟态2025初赛_Mobile方向just_Writeup.full.md
