---
title: "解析第九届 XCTF Tch3s"
category: crypto
tags: ["XCTF 第九届", "crypto", "timing-attack", "weak-PRNG", "srand-time", "seed-bruteforce"]
signals: ["XCTF 第九届 2024", "timing-attack", "weak-PRNG", "srand-time", "seed-bruteforce", "LD_PRELOAD", "GDB-modify", "AES-key-recover", "side-channel", "crypto_oracle", "XCTF", "Tch3s", "PRNG", "srand"]
difficulty: medium
source: "https://www.ctfiot.com/278232.html"
tools: ["GDB"]
origin: des-import
origin_kind: cards
updated: 2026-10-24
---
# 解析第九届 XCTF Tch3s

> 赛事：XCTF 第九届 2024 | 方向：crypto | 难度：medium | 工具：GDB

## 一句话总结

第九届XCTF Tch3s时序攻击+弱PRNG爆破,识别srand(time(NULL))弱种子+遍历时间戳匹配测试明文+LD_PRELOAD劫持+GDB调用解密函数。

## 攻击链

1. 程序srand(time(NULL))初始化PRNG,16次rand()%256生成16字节key
2. 加密flag输出密文后,进行多轮测试(随机明文加密+记录时间)
3. 测试数据泄露随机数序列(明文就是rand()%256的输出)
4. 遍历可能时间戳(~4000万值)作为候选seed
5. 跳过16次rand()后生成16字节,与第一个测试明文匹配
6. 找到正确seed后,LD_PRELOAD劫持srand设置SRAND环境变量
7. GDB断点加密函数入口(0x30ba),写output密文到rdi缓冲区
8. 直接调用解密函数(0x31a1),传入相同rdi/rsi/rdx参数
9. 读取rsi缓冲区得flag

## 关键 payload

```
XCTF{Tch3s_PRNG_...}
```

## 经验教训

srand(time(NULL))是经典弱PRNG,精度仅秒级,几分钟内可遍历几年;LD_PRELOAD劫持srand+GDB调用解密函数是经典的二进制复用技巧;侧信道信息泄露(测试明文)可作为种子恢复证据。

## 标签

timing-attack、weak-PRNG、srand-time、seed-bruteforce、LD_PRELOAD、GDB-modify、AES-key-recover、side-channel

## 参考来源

- https://www.ctfiot.com/278232.html
- 原文件：解析第九届_XCTF_Tch3s.full.md
