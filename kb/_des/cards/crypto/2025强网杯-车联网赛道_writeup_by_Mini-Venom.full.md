---
title: "2025 强网杯车联网赛道 writeup by Mini-Venom（CPA 侧信道 AES + RC4 变种 + CAN 信号频次）"
category: crypto
tags: ["2025 强网杯车联网赛道", "crypto", "强网杯 2025 车联网", "CPA 相关功耗分析 AES-128", "AES128.trs 功耗轨迹", "SubBytes 字节位置枚举 256"]
signals: ["2025 强网杯车联网赛道 2025", "强网杯 2025 车联网", "CPA 相关功耗分析 AES-128", "AES128.trs 功耗轨迹", "SubBytes 字节位置枚举 256", "plaintext⊕key S-box 汉明重量", "皮尔逊相关系数", "SCAAES 侧信道", "IMG_256 flag{CCAEEED667CD6C04C7ABCCC26DC793F1}", "block_cipher", "side_channel", "web_unknown", "misc_unknown", "SCAAES"]
difficulty: hard
source: "https://www.ctfiot.com/276948.html"
tools: []
origin: des-import
origin_kind: cards
updated: 2026-10-24
---
# 2025 强网杯车联网赛道 writeup by Mini-Venom（CPA 侧信道 AES + RC4 变种 + CAN 信号频次）

> 赛事：2025 强网杯车联网赛道 2025 | 方向：crypto | 难度：hard

## 一句话总结

2025 强网杯车联网：SCAAES CPA 侧信道攻击 AES-128 + IMG_256 + RC4 变种小程序 + CAN 信号频次统计。

## 攻击链

1. SCAAES: AES128.trs 功耗轨迹 → SubBytes 字节攻击
2. plaintext_byte ^ key_guess → SBOX[intermediate] → HW[sbox_output]
3. 与实际功耗 trace 计算皮尔逊相关系数，最大值即正确 key
4. 恢复 16 字节 AES-128 key → flag{...}
5. IMG_256: flag{CCAEEED667CD6C04C7ABCCC26DC793F1}
6. Reverse applet 小程序 chunk_1.appservice 解包 → 魔改 RC4
7. KSA 正向+反向双轮 PRGA: K = S[(S[i]+S[j]+S[t])%256] ^ (k%256)
8. CAN 信号: signal_map 定义 sig_20-52 各字段 byte 位置
9. 统计各信号出现频次最高 → flag{V3h1cle_N3tw0rk1ng_53cu71ty}

## 关键 payload

```
CPA: correlations = np.dot(hw_normalized, traces_normalized) / num_traces
```

## 经验教训

车联网安全常考 CPA（相关功耗分析）攻击 AES-128 密钥，SubBytes 字节攻击 + S-box 汉明重量 + 皮尔逊相关是标准流程；RC4 变种 KSA 正向+反向双轮 + PRGA S[(S[i]+S[j]+S[t])%256] 是新变种。

## 标签

强网杯 2025 车联网、CPA 相关功耗分析 AES-128、AES128.trs 功耗轨迹、SubBytes 字节位置枚举 256、plaintext⊕key S-box 汉明重量、皮尔逊相关系数、SCAAES 侧信道、IMG_256 flag{CCAEEED667CD6C04C7ABCCC26DC793F1}、RC4 变种 正向+反向 KSA、S[(S[i]+S[j]+S[t])%256] PRGA、小程序 chunk_1.appservice 解包、CAN 信号 sig_20-52 频次统计

## 参考来源

- https://www.ctfiot.com/276948.html
- 原文件：2025强网杯-车联网赛道_writeup_by_Mini-Venom.full.md
