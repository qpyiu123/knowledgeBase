---
title: "corCTF 2024：位运算虚拟机及 gpu hash 爆破"
category: reverse
tags: ["corCTF", "reverse", "bit-vm", "hasher", "gpu-bruteforce", "numba"]
signals: ["corCTF 2024", "bit-vm", "hasher", "gpu-bruteforce", "numba", "cuda", "2060", "reverse", "corCTF", "GPU", "hash", "x1290", "xED853", "mov"]
difficulty: hard
source: "https://www.ctfiot.com/197191.html"
tools: ["C", "Ghidra", "IDA"]
origin: des-import
origin_kind: cards
updated: 2026-10-24
---
# corCTF 2024：位运算虚拟机及 gpu hash 爆破

> 赛事：corCTF 2024 | 方向：reverse | 难度：hard | 工具：C、Ghidra、IDA

## 一句话总结

corCTF 2024 逆向题，把位运算 VM 反编译为 32 位整型运算后用 GPU 跑 hash 爆破。

## 攻击链

1. 0x1290~0xED853 mov byte 提取位运算
2. 输入按位拆分到字节数组
3. 32 次写入识别 5 种运算 (add/and/or/xor/circular-shift)
4. 反编译 C 代码
5. numba + CUDA 7 分半跑完
6. 还原 flag

## 关键 payload

```
位运算 VM 模拟 32 位整型 + GPU 加速 hash 爆破
```

## 经验教训

当反编译工具 IDA/Ghidra 因一坨 mov byte 失败时，先识别"位运算 VM 模拟整型"模式，再反编译为 C/C++。

## 标签

bit-vm、hasher、gpu-bruteforce、numba、cuda、2060

## 参考来源

- https://www.ctfiot.com/197191.html
- 原文件：corCTF_2024：位运算虚拟机及gpu_hash爆破.full.md
