---
title: "Paradigm CTF 2021 - Lockbox"
category: crypto
tags: ["Paradigm CTF 2021", "crypto", "blockchain", "ethereum", "solidity", "ecdsa"]
signals: ["Paradigm CTF 2021 2021", "blockchain", "ethereum", "solidity", "ecdsa", "ecrecover", "abi-encode", "assembly", "lockbox", "crypto_rsa", "Paradigm", "Lockbox", "stage", "blockhash"]
difficulty: hard
source: "https://www.ctfiot.com/141643.html"
tools: []
origin: des-import
origin_kind: cards
updated: 2026-10-24
---
# Paradigm CTF 2021 - Lockbox

> 赛事：Paradigm CTF 2021 2021 | 方向：crypto | 难度：hard

## 一句话总结

Paradigm 2021 Lockbox 通过 assembly 链式调用 6 个 stage 合约，分别用 blockhash、ecrecover、uint16 溢出、数组排序、keccak 选择、calldata 长度约束完成。

## 攻击链

1. Entrypoint 修饰符 _ 用 assembly 调 getSelector() 拿当前 stage 函数选择器
2. 把 calldata 原样透传给 Stage 合约
3. Stage 0: 猜 blockhash(block.number-1) 的前 4 字节
4. Stage 1: ecrecover(keccak("stage1")) 验证 v=28 + r=0x1f9c.. + s=0x6e95.. 还原地址
5. Stage 2: uint16 a+b<a 触发 uint16 溢出 (a=0xff1c, b=任意)
6. Stage 3: keys 数组 < lock 数组 + 升序 + 差值为偶数
7. Stage 4: choices[choice%6]==keccak256("choose")
8. Stage 5: msg.data.length<256 (8 个参数 + 4 字节 selector = 260 略超)
9. 单笔 calldata 串联所有 stage：先算 blockhash 前 4 字节 + 16 位溢出值 + r/s
10. abi.encodePacked 拼装 8 个 bytes32 + 1 个 uint
11. lockBoxExploit 用 assembly call gas() entry 0 size 0 触发整链路

## 关键 payload

```
uint16(0xff1c) + bytes32(0x1f9c551056...) r + bytes32(0x6e95dc...) s + bytes32(keccak('choose')) + choice=4
```

## 经验教训

Ethereum assembly call 可以串联多个合约；ecrecover 私钥可控时 signHash 拿 v/r/s；uint16 加法溢出绕 (a>0 && b>0 && a+b<a)；msg.data 长度硬限制 <256。

## 标签

blockchain、ethereum、solidity、ecdsa、ecrecover、abi-encode、assembly、lockbox

## 参考来源

- https://www.ctfiot.com/141643.html
- 原文件：Paradigm_CTF_2021——Lockbox.full.md
