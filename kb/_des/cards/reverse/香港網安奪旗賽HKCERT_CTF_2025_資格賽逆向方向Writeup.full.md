---
title: "香港網安奪旗賽HKCERT CTF 2025 資格賽逆向方向Writeup"
category: reverse
tags: ["HKCERT CTF 2025 資格賽", "reverse", "SM4", "custom-SBOX", "XXTEA", "modified-TEA"]
signals: ["HKCERT CTF 2025 資格賽 2025", "SM4", "custom-SBOX", "XXTEA", "modified-TEA", "AES-custom", "custom-Base64", "rsa", "key-schedule", "reverse", "HKCERT", "SBOX", "AES", "SBOX_P"]
difficulty: hard
source: "https://www.ctfiot.com/288018.html"
tools: []
origin: des-import
origin_kind: cards
updated: 2026-10-24
---
# 香港網安奪旗賽HKCERT CTF 2025 資格賽逆向方向Writeup

> 赛事：HKCERT CTF 2025 資格賽 2025 | 方向：reverse | 难度：hard

## 一句话总结

HKCERT 2025资格赛逆向方向5题,涵盖魔改SM4+自定义SBOX+魔改AES+魔改XXTEA+随机种子爆破,密码学逆向全方向深度。

## 攻击链

1. 题目1SM4魔改: 重新派生SBOX_P=SBOX[(i^167)&255]再rotl8(val, i&3),tau函数4字节替换+T=tau^rotl^rotl^rotl^rotl,expand_key 32轮派生rk
2. 题目2魔改AES+自定义Base64: 32字节KEY_SEED+256字节SBOX+32字节CIPHERTEXT打包,密钥扩展10轮(每轮f=17+1~10)
3. 题目3魔改XXTEA: sum从DELTA*32开始倒推,key=[0x3C2D1E0F,0x78695A4B,0xB4A59687,0xF0E1D2C3],解密逆向v3/v4
4. 题目4 srand随机+alloca栈帧: time(0)^getpid()%20作为srand seed,生成36字节cipherXOR,爆破seed
5. 题目5混淆比较: 主函数将s[j]^rand()与cipher比较,绕混淆爆破随机种子

## 关键 payload

```
hkcert25{...}
```

## 经验教训

魔改对称加密的破题关键是先识别原算法(SM4/AES/XXTEA),再识别SBOX/常量/DELTA/key的修改,逐项还原。随机数种子爆破:time^pid取低20位是常见弱种子。

## 标签

SM4、custom-SBOX、XXTEA、modified-TEA、AES-custom、custom-Base64、rsa、key-schedule、cipher-reversal

## 参考来源

- https://www.ctfiot.com/288018.html
- 原文件：香港網安奪旗賽HKCERT_CTF_2025_資格賽逆向方向Writeup.full.md
