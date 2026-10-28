---
title: "2026 年第三届\"长城杯\"网数智安全大赛 Reverse AK 题解（DokiLogic Renpy 游戏逆向）"
category: reverse
tags: ["2026 第三届长城杯网数智", "reverse", "长城杯 2026 第三届 网数智", "Reverse AK 三题", "DokiLogic Renpy 游戏引擎", "rpyc pickle 序列化"]
signals: ["2026 第三届长城杯网数智 2026", "长城杯 2026 第三届 网数智", "Reverse AK 三题", "DokiLogic Renpy 游戏引擎", "rpyc pickle 序列化", "文件监控拷贝 .1.exe", "UPX 脱壳", "XOR 0x23=35 加密", "renpy script.py load_file 打印 .rpyc", "reverse", "crypto_unknown", "web_unknown", "Reverse", "DokiLogic"]
difficulty: medium
source: "https://www.ctfiot.com/307007.html"
tools: ["Python"]
origin: des-import
origin_kind: cards
updated: 2026-10-24
---
# 2026 年第三届"长城杯"网数智安全大赛 Reverse AK 题解（DokiLogic Renpy 游戏逆向）

> 赛事：2026 第三届长城杯网数智 2026 | 方向：reverse | 难度：medium | 工具：Python

## 一句话总结

2026 长城杯网数智 Reverse AK：DokiLogic Renpy 游戏逆向 - .rpyc 打印 + 文件监控拷贝 .1.exe + UPX 脱壳 + XOR 35。

## 攻击链

1. Renpy 游戏 → game 目录 .rpyc 文件 → 修改 renpy/script.py Script.load_file 打印加载的 .rpyc
2. 还原游戏逻辑：user_input = renpy.input().strip() → l11111l1ll1l(user_input) == ll111l11l111
3. 创建 ./1.exe 子程序 → 执行 → 拿密文 → 删除 .1.exe
4. Python 脚本文件监控：os.path.exists(".1.exe") → shutil.copy2 → 123.exe
5. upx.exe -d 123.exe 脱壳
6. 动态调试拿 Buffer 密文
7. 加密: chr(ord(c) ^ 35) → 直接异或 35 还原

## 关键 payload

```
chr(ord(ll1l111ll11l) ^ llll1l111ll1=35)
```

## 经验教训

Renpy 引擎逆向 = 修改 renpy/script.py load_file 把 .rpyc 反编译输出到日志；游戏运行时临时创建又删除的子程序要文件监控拷贝（inotify/while 轮询）才能拿到；UPX 脱壳后 XOR 35 是经典小加密。

## 标签

长城杯 2026 第三届 网数智、Reverse AK 三题、DokiLogic Renpy 游戏引擎、rpyc pickle 序列化、文件监控拷贝 .1.exe、UPX 脱壳、XOR 0x23=35 加密、renpy script.py load_file 打印 .rpyc

## 参考来源

- https://www.ctfiot.com/307007.html
- 原文件：2026年第三届“长城杯”网数智安全大赛Reverse_AK题解（含总决赛全部题目附件）.full.md
