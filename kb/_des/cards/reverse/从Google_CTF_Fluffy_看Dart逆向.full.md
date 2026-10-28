---
title: "从Google CTF Fluffy看Dart逆向"
category: reverse
tags: ["Google CTF 2025", "reverse", "Dart", "ARM64", "DecompressPointer", "HEAP"]
signals: ["Google CTF 2025 2025", "Dart", "ARM64", "DecompressPointer", "HEAP", "base62", "rol1", "ror1", "时间戳爆破", "reverse", "AOT", "b62", "token", "pin"]
difficulty: hard
source: "https://www.ctfiot.com/261979.html"
tools: []
origin: des-import
origin_kind: cards
updated: 2026-10-24
---
# 从Google CTF Fluffy看Dart逆向

> 赛事：Google CTF 2025 2025 | 方向：reverse | 难度：hard

## 一句话总结

Dart AOT ARM64 逆向 + 自定义 b62 编解码 + 时间戳爆破 token + 多线程预计算 pin 优化。

## 攻击链

1. 静态分析 Dart AOT 编译产物（AArch64）识别 saveSecret/update_token_bytes/b62encode
2. 还原算法 saveSecret: pin 轮循环 rol1(byte + token_bytes[j%8], j&7) + memmove 循环
3. 还原 update_token_bytes: memmove 循环 + ror1(token_bytes[j], (pin^((round&3)+1))&7)
4. 还原 generate_token: gctf25_{ts} SHA1 前 8 字节 b62encode
5. 写 restoreSecretWithPrecomputed 逆算法 (ror1 - token_bytes)
6. 预计算 token_bytes_list 10000 项避免重复 update
7. 24 线程并行 bf_secret_thread 搜 timestamp 范围
8. 测 '}' 字符快速过滤可打印解密
9. 拼接 3 段 flag: Ok4y_h4v3_u_0ptim1zed + brUt3_f0rcE_0R_y0u_jUst + ...

## 关键 payload

```
CTF{Ok4y_h4v3_u_0ptim1zed_brUt3_f0rcE_0R_y0u_jUst
```

## 经验教训

Dart AOT 没有标准运行时元数据，靠 DecompressPointer+HEAP 寻址对象；优化 pin 循环时预计算 token_bytes_list 把 update 提到 pin 循环外，多线程按时间分片爆破 ts 范围。

## 标签

Dart、ARM64、DecompressPointer、HEAP、base62、rol1、ror1、时间戳爆破、多线程、预计算

## 参考来源

- https://www.ctfiot.com/261979.html
- 原文件：从Google_CTF_Fluffy_看Dart逆向.full.md
