---
title: "贵阳大数据及网络安全精英对抗赛 Reverse EZRE_0 解题"
category: reverse
tags: ["贵阳大数据", "reverse", "TLS-callback", "RC4", "JT8U9ptt", "multi-stage"]
signals: ["贵阳大数据 2023", "TLS-callback", "RC4", "JT8U9ptt", "multi-stage", "param-control", "encrypt-decrypt-flag", "chence", "key-extraction", "reverse", "EZRE_0", "Reverse", "TLS", "x65"]
difficulty: medium
source: "https://www.ctfiot.com/115285.html"
tools: ["C"]
origin: des-import
origin_kind: cards
updated: 2026-10-24
---
# 贵阳大数据及网络安全精英对抗赛 Reverse EZRE_0 解题

> 赛事：贵阳大数据 2023 | 方向：reverse | 难度：medium | 工具：C

## 一句话总结

EZRE_0 Reverse：错位异或 + TLS 回调 RC4(JT8U9ptt) + 自定义变换（参数 0x65/0x64 切换加解密）+ 5 阶段。

## 攻击链

1. 32 位 C++ 程序，无壳
2. 输入 flag{77e52c5b-b141-4f3b-92ec-aa680ca38} (38 字符)
3. 错位异或: x[i] ^= x[i+1]
4. TLS 回调函数: RC4 加密, 密码 JT8U9ptt
5. 第 3 阶段: 自定义变换函数, 第 5 个参数 0x65 = 加密, 0x64 = 解密
6. 5 次变换后比对
7. 解法: 拿最终正确值, 把变换函数参数 5 改成 0x64 解密, 再 RC4 解密, 再错位 XOR 逆
8. flag = flag{068d772e155448f0ba101abb62a2a837}

## 关键 payload

```
JT8U9ptt (RC4 key) + 第 5 参数 0x64 解密 + 错位 XOR 逆 + flag{068d772e155448f0ba101abb62a2a837}
```

## 经验教训

TLS 回调函数是 RE 隐蔽执行点；自定义算法通过第 5 参数切换加解密是好出题思路。

## 标签

TLS-callback、RC4、JT8U9ptt、multi-stage、param-control、encrypt-decrypt-flag、chence、key-extraction、debugger

## 参考来源

- https://www.ctfiot.com/115285.html
- 原文件：贵阳大数据及网络安全精英对抗赛Reverse_EZRE_0解题.full.md
