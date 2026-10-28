---
title: "2024 西湖论剑 Qrohttre（Windows 调试器实现父子进程同步 + SMC）"
category: reverse
tags: ["2024 西湖论剑", "reverse", "Qrohttre 父子进程同步调试", "DEBUG_PROCESS CreateProcessA", "0xCC 断点同步用户输入", "TF 单步异常"]
signals: ["2024 西湖论剑 2024", "Qrohttre 父子进程同步调试", "DEBUG_PROCESS CreateProcessA", "0xCC 断点同步用户输入", "TF 单步异常", "f_OnBreakPoint_4070A0 + f_OnSingleStep_407530", "f_OnAccessViolation_406710", "ZwSetInformationThread ThreadHideFromDebugger 0x11 反调试", "双段 SMC 自解密", "reverse", "misc_unknown", "Qrohttre", "Win32", "DEBUG_PROCESS"]
difficulty: hard
source: "https://www.ctfiot.com/172527.html"
tools: ["IDA"]
origin: des-import
origin_kind: cards
updated: 2026-10-24
---
# 2024 西湖论剑 Qrohttre（Windows 调试器实现父子进程同步 + SMC）

> 赛事：2024 西湖论剑 2024 | 方向：reverse | 难度：hard | 工具：IDA

## 一句话总结

Qrohttre 主进程用 Win32 DEBUG_PROCESS 调试子进程，TF 单步 + 双段 SMC 自解密 + 0xCC 断点同步用户输入；patch WriteProcessMemory + CE dump + 父子进程双 IDA patch 是分析套路。

## 攻击链

1. 主进程 CreateProcessA DEBUG_PROCESS 创建子进程
2. 子进程入口点 INT3（0xCC）断点
3. 主进程 f_OnBreakPoint_4070A0: 同步用户输入到子进程 + 设置 TF 单步标志
4. 子进程单步异常 → 主进程 f_OnSingleStep_407530 解密下一条指令 + 上条指令写垃圾
5. ZwSetInformationThread(ThreadHideFromDebugger) 反调试
6. 找到第二段 SMC 起始位置 0x40B991，patch 掉 WriteProcessMemory 回写
7. CE dump 子进程 40B991-40DDB4 解密代码
8. patch 到 QrohttreSub.exe 静态分析
9. 触发访问越权异常 (读写操作数未完全解密)，分发 f_OnAccessViolation_406710 还原地址

## 关键 payload

```
CreateProcessA(..., DEBUG_PROCESS, ...); f_OnSingleStep_407530
```

## 经验教训

Win32 调试 API（DEBUG_PROCESS + TF 单步 + 0xCC 断点）实现父子进程同步通信是 Windows 高级逆向题，patch 掉 WriteProcessMemory 回写 + CE dump 是核心套路；反调试 ThreadHideFromDebugger 用 ZwSetInformationThread(0x11) 设线程。

## 标签

Qrohttre 父子进程同步调试、DEBUG_PROCESS CreateProcessA、0xCC 断点同步用户输入、TF 单步异常、f_OnBreakPoint_4070A0 + f_OnSingleStep_407530、f_OnAccessViolation_406710、ZwSetInformationThread ThreadHideFromDebugger 0x11 反调试、双段 SMC 自解密、CE dump 40B991-40DDB4 内存 patch 回 QrohttreSub.exe、WriteProcessMemory 回写垃圾

## 参考来源

- https://www.ctfiot.com/172527.html
- 原文件：2024西湖论剑_Qrohttre：一道windows调试实现同步题.full.md
