---
title: "HKCERT CTF 2022 Postmortem (II): Harder Crypto Challenges"
category: crypto
tags: ["HKCERT CTF 2022", "crypto", "crypto", "aes", "batch-file", "windows-aes"]
signals: ["HKCERT CTF 2022 2022", "crypto", "aes", "batch-file", "windows-aes", "subbytes-shiftrows-mixcolumns", "block-cipher", "batch-attack", "crypto_rsa", "HKCERT", "Harder", "Crypto", "Windows", "AES"]
difficulty: hard
source: "https://www.ctfiot.com/87575.html"
tools: []
origin: des-import
origin_kind: cards
updated: 2026-10-24
---
# HKCERT CTF 2022 Postmortem (II): Harder Crypto Challenges

> 赛事：HKCERT CTF 2022 2022 | 方向：crypto | 难度：hard

## 一句话总结

HKCERT 2022 Harder Crypto：Windows批处理AES+双密钥密文对比

## 攻击链

1. Windows批处理实现AES加密（aes.bat）
2. 已知明文+密文对
3. 红色 4czfHjwa9rl+Xds/1EbFuJioVRnYL0ym86UZ2WDMQPgBKGT5AN3Cqe7OShpvkxIt
4. 蓝色 4czIHjwaYd8F1St/xEb7rJioV0+RLnygf6UGZWDMQPuBClqKAX35Te9ONhsv2mkp
5. 红色+蓝色→flag
6. AES-128 SubBytes+ShiftRows+MixColumns
7. AES batch file完整实现
8. 加密已知明文ABCDEFGHIJKLMNOPQRSTUVWXYZ...+/
9. 调整密文+密文

## 关键 payload

```
已知明文+密文对+多密钥差异
```

## 经验教训

批处理文件实现AES是新颖密码学题形式

## 标签

crypto、aes、batch-file、windows-aes、subbytes-shiftrows-mixcolumns、block-cipher、batch-attack

## 参考来源

- https://www.ctfiot.com/87575.html
- 原文件：HKCERT_CTF_2022_Postmortem_(II)-_Harder_Crypto_Challenges.full.md
