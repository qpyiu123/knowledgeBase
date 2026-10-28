---
title: "TJCTF 部分 Crypto-wp"
category: crypto
tags: ["TJCTF", "crypto", "baconian-cipher", "case-encoding", "custom-rc4", "rsa-multi-prime"]
signals: ["TJCTF 2025", "baconian-cipher", "case-encoding", "custom-rc4", "rsa-multi-prime", "lcg-time-seed", "crypto_rsa", "TJCTF", "Crypto", "Baconian", "RC4", "RSA", "LCG", "chr"]
difficulty: medium
source: "https://www.ctfiot.com/273223.html"
tools: ["C", "netcat"]
origin: des-import
origin_kind: cards
updated: 2026-10-24
---
# TJCTF 部分 Crypto-wp

> 赛事：TJCTF 2025 | 方向：crypto | 难度：medium | 工具：C、netcat

## 一句话总结

TJCTF 2025 部分 Crypto：4 题 Baconian + 自定义 RC4 + 多模数 RSA + LCG 伪随机爆破。

## 攻击链

1. Baconian 加密 + 大小写编码
2. chr(ord(c)-13) 减位 → 解码
3. 大写/小写对应 1/0
4. 5 字符一组映射回 Baconian 二进制 → 明文
5. tictf" 改为 "tjctf" 包裹花括号
6. alchemist-recipe 自定义 RC4-like 加密 (SHA256 派生 key + 256 字节 S-box 初始化)
7. deschuffle 排序还原 + XOR 还原 + S-box 逆映射
8. 多模数 RSA 攻击：CRT 合并 C，iroot 求 e 次方根
9. LCG 伪随机数 (m=2^32, a=157, c=1) seed=time.asctime()
10. nc tjc.tf 31493 拿 ciphertext
11. 2 小时时间窗口爆破 seed → AES-ECB 解密

## 关键 payload

```
AES-ECB(key, ciphertext) where key = LCG.randbytes(32)
```

## 经验教训

多模数 RSA 当 e 较小时 e 次方根可解；LCG 种子若用 time.asctime()，时间窗口可爆破。

## 标签

baconian-cipher、case-encoding、custom-rc4、rsa-multi-prime、lcg-time-seed

## 参考来源

- https://www.ctfiot.com/273223.html
- 原文件：TJCTF部分Crypto-wp.full.md
