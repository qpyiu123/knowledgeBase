---
title: "ACTF WriteUp"
category: web
tags: ["ACTF", "web", "XOR爆破", "zstd循环解压", "RSA e=-1", "b=-2*n方程"]
signals: ["ACTF 2022", "XOR爆破", "zstd循环解压", "RSA e=-1", "b=-2*n方程", "sympy.solve", "libc-2.27 64堆菜单", "ret2csu ARM aarch64", "2048 qemu", "web_unknown", "ACTF", "XOR", "zstd", "RSA"]
difficulty: hard
source: "https://www.ctfiot.com/46538.html"
tools: ["ARM"]
origin: des-import
origin_kind: cards
updated: 2026-10-24
---
# ACTF WriteUp

> 赛事：ACTF 2022 | 方向：web | 难度：hard | 工具：ARM

## 一句话总结

ACTF 综合多题 — XOR爆破 + zstd循环解压 + RSA e=-1 方程 + libc-2.27 堆菜单 + aarch64 ret2csu 2048 AI + RunPE Process Hollowing + BigI 128 进制 + chainId 6666 bet。

## 攻击链

1. Crypto1: a,b 两数组 XOR 27 字符
2. Crypto2: zstd/bunzip2 循环解压 10000 次出 flag ACTF{r0cK_4Nd_rolL_1n_C0mpr33s1Ng_aNd_uNCOmrEs5iNg}
3. Crypto3: RSA e=-1 方程 -m*x² + x - e*n = 0, sympy.solve 解出 m=46280, 求 p,q
4. Pwn1: libc-2.27 64 堆菜单 0/1/2/3/4 add/delete/edit/show/q, 多次 edit 改 size 字段 + unlink 拿 libc
5. Pwn2: aarch64 qemu 跑 2048 游戏, ret2csu 调 system 拿 shell
6. Reverse1: PE Process Hollowing (RunPE), FindResourceW/LoadResource/LockResource 读资源, VirtualAllocEx 申请空间, WriteProcessMemory 写入, SetThreadContext + ResumeThread
7. Reverse2: BigI 128 进制数, encrypt 8 轮: add+mul+subabs+add+mul+subabs+add+subabs+add+subabs+add+subabs, 已知 targ 反推
8. Web3: chainId=6666, bet 合约, nonce 推测 + pre_time 修正

## 关键 payload

```
libc-2.27 64 堆菜单 / aarch64 ret2csu / 2048 Minimaxab AI / Process Hollowing RunPE / BigI 128 进制多项式加密 / chainId 6666 bet
```

## 经验教训

ACTF 风格是把所有方向都做一遍；Process Hollowing 的关键是 FindResourceW 找 PE 资源；BigI 128 进制加密逆推可直接列线性方程组；2048 这类游戏可接 Minimax AI。

## 标签

XOR爆破、zstd循环解压、RSA e=-1、b=-2*n方程、sympy.solve、libc-2.27 64堆菜单、ret2csu ARM aarch64、2048 qemu、Minimaxab AI、Process Hollowing、RunPE、FindResourceW、VirtualAllocEx、WriteProcessMemory、SetThreadContext、BigI 128进制、encrypt=add+mul+subabs多次轮、web3 6666链

## 参考来源

- https://www.ctfiot.com/46538.html
- 原文件：ACTF-WriteUp.full.md
