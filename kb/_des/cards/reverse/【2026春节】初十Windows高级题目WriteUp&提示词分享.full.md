---
title: "【2026春节】初十 Windows 高级题目 WriteUp & 提示词分享"
category: reverse
tags: ["春节活动", "reverse", "whitebox-crypto", "MBA-obfuscation", "opaque-predicate", "SSE-MBA"]
signals: ["春节活动 2026", "whitebox-crypto", "MBA-obfuscation", "opaque-predicate", "SSE-MBA", "Unicorn-emulation", "CHIMERA1", "SipHash-variant", "PRISMWB3", "reverse", "Windows", "MBA", "Unicorn", "HookD3B20"]
difficulty: hard
source: "https://www.ctfiot.com/304400.html"
tools: ["IDA"]
origin: des-import
origin_kind: cards
updated: 2026-10-24
---
# 【2026春节】初十 Windows 高级题目 WriteUp & 提示词分享

> 赛事：春节活动 2026 | 方向：reverse | 难度：hard | 工具：IDA

## 一句话总结

2026 春节初十 Windows 高级题，~95M 指令白盒密码 + MBA 混淆 + Unicorn 全指令模拟逆向。

## 攻击链

1. PE 映射到 Unicorn 内存 / HookD3B20 比较函数读 rdx 期望值 / 白盒密码 20 轮 PRISMWB3 / 642 行 SSE/MBA 派生函数 / MBA 状态机包裹的 memcpy / 280 字节派生 / 32 字节 SipHash 变体

## 关键 payload

```
RVA 0x154E50 已知白盒密码上下文 (~2.7MB) + RVA 0xAD7660 自定义白盒密码上下文 (~28.8MB) + CHIMERA1 头验证
```

## 经验教训

MBA(mixed boolean arithmetic) 表达式 n*(n+1) 或 n*(n-1) 是不透明谓词；白盒密码 20 轮 + 28.8MB 查找表让 IDA F5 失败；Unicorn 全指令模拟 + Hook 关键函数是处理混淆巨无霸二进制唯一可行路径。

## 标签

whitebox-crypto、MBA-obfuscation、opaque-predicate、SSE-MBA、Unicorn-emulation、CHIMERA1、SipHash-variant、PRISMWB3

## 参考来源

- https://www.ctfiot.com/304400.html
- 原文件：【2026春节】初十Windows高级题目WriteUp&提示词分享.full.md
