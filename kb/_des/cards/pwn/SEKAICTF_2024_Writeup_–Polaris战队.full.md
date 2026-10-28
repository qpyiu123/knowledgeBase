---
title: "SEKAICTF 2024 Writeup – Polaris战队"
category: pwn
tags: ["SEKAICTF", "pwn", "nolibc", "custom-protocol", "group-theory", "randomness-recovery"]
signals: ["SEKAICTF 2024", "nolibc", "custom-protocol", "group-theory", "randomness-recovery", "heap_exploit", "PWN", "Crypto", "Misc", "Polaris", "EoP", "Group", "Theory", "DLP"]
difficulty: medium
source: "https://www.ctfiot.com/203638.html"
tools: []
origin: des-import
origin_kind: cards
updated: 2026-10-24
---
# SEKAICTF 2024 Writeup – Polaris战队

> 赛事：SEKAICTF 2024 | 方向：pwn | 难度：medium

## 一句话总结

50+ 道 PWN/Crypto/Misc 联合战场，Polaris 靠 nolibc EoP + Group Theory DLP 攻破密码套件。

## 攻击链

1. 构造大量 add chunk 触发 tcache 耗尽
2. 通过 set bitmap attribute 翻转 EPROCESS 关键位完成 EoP
3. 远程 nolibc 触发 show_win 弹出 flag
4. 客户端通过 judge 二分位 + reseed 重置 PRNG 状态
5. 利用 fight_bot 写任意 64-bit word 至 libssl 内部 FILE 结构
6. hijack IO 改写 stdout vtable 调用 system
7. CIPHER_SUITE randbelow 2^256 作为 random.seed 输入
8. 构造 GSIZE=8209 阶群 G 与 GNUM=79 阶非交换积
9. gexp(tuple(g)) 计算置换 g 的幂
10. 已知明文 + 密文 + 公钥解 DLP 还原私钥

## 关键 payload

```
judge(int(''1''*bit+''0''*(64-bit), 2))  # PRNG 状态位判定
```

## 经验教训

自研协议常依赖「randbelow」类可种子化 PRNG；一旦能二分位恢复状态即等于控制输出流。

## 标签

nolibc、custom-protocol、group-theory、randomness-recovery

## 参考来源

- https://www.ctfiot.com/203638.html
- 原文件：SEKAICTF_2024_Writeup_–Polaris战队.full.md
