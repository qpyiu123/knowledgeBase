---
title: "DASCTF X GFCTF 2022 十月挑战赛 cuteRE WriteUp"
category: reverse
tags: ["DASCTF+GFCTF", "reverse", "base64-custom", "rc4", "dynamic-debug", "swpu"]
signals: ["DASCTF+GFCTF 2022", "base64-custom", "rc4", "dynamic-debug", "swpu", "szv", "controlflow-obfuscation", "deflat", "reverse", "cuteRE", "base64", "RC4", "key", "IDA"]
difficulty: easy
source: "https://www.ctfiot.com/72634.html"
tools: ["IDA"]
origin: des-import
origin_kind: cards
updated: 2026-10-24
---
# DASCTF X GFCTF 2022 十月挑战赛 cuteRE WriteUp

> 赛事：DASCTF+GFCTF 2022 | 方向：reverse | 难度：easy | 工具：IDA

## 一句话总结

cuteRE 入门逆向，动态调出运行时修改的 base64 表 + RC4 key。

## 攻击链

1. IDA 主函数 4 子函数
2. 32 字符按奇偶分 2 部分
3. sub_405700 自定义 base64 表生成
4. sub_4059F0 控制流混淆 deflat
5. sub_406270 RC4
6. 动态调 sub_405700 后取 byte_609450 = 新 base64 表
7. 动态调 sub_4059F0 后取 byte_6090A0 = 'szv~
8. base64 解密文 1
9. RC4(szv~) 解密文 2
10. 奇偶拼回

## 关键 payload

```
动态调试拿真实 key (szv~) + 自定义 base64 表
```

## 经验教训

当 reverse 题 IDA 静态看不出真实 key，优先动态调试 print 实际写入的地址值。

## 标签

base64-custom、rc4、dynamic-debug、swpu、szv、controlflow-obfuscation、deflat

## 参考来源

- https://www.ctfiot.com/72634.html
- 原文件：DASCTF_X_GFCTF_2022十月挑战赛_cuteRE_WriteUp.full.md
