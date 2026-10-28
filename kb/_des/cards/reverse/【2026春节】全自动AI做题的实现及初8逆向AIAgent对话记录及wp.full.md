---
title: "【2026春节】全自动AI做题的实现及初8逆向AI Agent对话记录及wp"
category: reverse
tags: ["春节活动", "reverse", "AI-Agent", "multi-model", "point-system", "OpenViking-context"]
signals: ["春节活动 2026", "AI-Agent", "multi-model", "point-system", "OpenViking-context", "calling-func", "jadx", "IDA", "libhajimi.so", "reverse", "Tokeii", "Agent", "Android", "JNI"]
difficulty: hard
source: "https://www.ctfiot.com/304188.html"
tools: ["IDA", "Java"]
origin: des-import
origin_kind: cards
updated: 2026-10-24
---
# 【2026春节】全自动AI做题的实现及初8逆向AI Agent对话记录及wp

> 赛事：春节活动 2026 | 方向：reverse | 难度：hard | 工具：IDA、Java

## 一句话总结

2026 春节 Tokeii 的全自动 AI Agent 做题系统分享，逆向题 Android JNI 实战。

## 攻击链

1. 多模型协作 + 总结反思系统 + 点子系统 + 常见工具 calling func 减少 token/上下文压缩和会话分支参考 OpenViking 实现/打 tag 系统/JNI: 1. jadx 反编译 APK 找 native 调用 2. IDA 分析 libhajimi.so (x86_64) 找 JNI 函数 3. 提取密钥和常量 4. 写脚本恢复 flag

## 关键 payload

```
Aclasses.dex (Java/Kotlin) + libhajimi.so (多架构 native)
```

## 经验教训

AI Agent 多模型协作可降低单模型偏差；常见工具 calling func 大幅减少 token；OpenViking 上下文压缩参考实现；Android JNI 逆向两件套 jadx (Java 层) + IDA (native 层) 是标准流程。

## 标签

AI-Agent、multi-model、point-system、OpenViking-context、calling-func、jadx、IDA、libhajimi.so、JNI、multi-arch

## 参考来源

- https://www.ctfiot.com/304188.html
- 原文件：【2026春节】全自动AI做题的实现及初8逆向AIAgent对话记录及wp.full.md
