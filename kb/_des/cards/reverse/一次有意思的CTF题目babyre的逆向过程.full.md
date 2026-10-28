---
title: "一次有意思的CTF题目 babyre 的逆向过程"
category: reverse
tags: ["个人赛", "reverse", "S-box", "custom-cipher", "IAT-hook", "IsDebuggerPresent"]
signals: ["个人赛 2022", "S-box", "custom-cipher", "IAT-hook", "IsDebuggerPresent", "virtualprotect", "memcmp", "anti-debug", "Sangfor", "reverse", "babyre", "Windows", "IAT", "hook"]
difficulty: hard
source: "https://www.ctfiot.com/67314.html"
tools: []
origin: des-import
origin_kind: cards
updated: 2026-10-24
---
# 一次有意思的CTF题目 babyre 的逆向过程

> 赛事：个人赛 2022 | 方向：reverse | 难度：hard

## 一句话总结

babyre Windows 逆向，IAT hook IsDebuggerPresent 抗调试 + 自定义 S-box 加密 + 16 轮 XOR 计算。

## 攻击链

1. 1. 32 字节 flag 输入 → sub_401920 初始化 + IsDebuggerPresent 检测 + 有调试器时异或 i/2. sub_4017A0 加密 + sub_401400 memcmp vs unk_405000 32 字节/3. sub_401430 + sub_401280 16 轮计算 v8 v9 + 与 0xC7296F5E/0xD2F4B2A9 异或/4. IAT hook IsDebuggerPresent：遍历 PE 导入表 → VirtualProtect 改 RWX → 改 dword_40514C/5. 逆推 sub_401280_re 还原 flag = Sangfor{855908672599db85b370dcb}

## 关键 payload

```
flag = Sangfor{855908672599db85b370dcb}  v5 = 0x68546749  v6 = 0x79685365
```

## 经验教训

自定义 S-box 加密需要逆推 sub_401280；IAT hook 抗调试是 anti-debug 经典；VirtualProtect 改导入表绕过；32 字节 flag 输入验证。

## 标签

S-box、custom-cipher、IAT-hook、IsDebuggerPresent、virtualprotect、memcmp、anti-debug、Sangfor

## 参考来源

- https://www.ctfiot.com/67314.html
- 原文件：一次有意思的CTF题目babyre的逆向过程.full.md
