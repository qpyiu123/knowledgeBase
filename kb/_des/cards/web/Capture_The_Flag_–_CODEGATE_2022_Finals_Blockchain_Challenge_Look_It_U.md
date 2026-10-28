---
title: "Capture The Flag – CODEGATE 2022 Finals Blockchain Challenge Look It Up Writeup"
category: web
tags: ["CODEGATE 2022 Finals", "web", "blockchain", "solidity", "foundry", "paradigm-ctf"]
signals: ["CODEGATE 2022 Finals 2022", "blockchain", "solidity", "foundry", "paradigm-ctf", "NTT", "isPowerOf2", "bn256", "web_unknown", "CODEGATE", "Finals", "Look", "proof", "uuid"]
difficulty: hard
source: "https://www.ctfiot.com/95239.html"
tools: []
origin: des-import
origin_kind: cards
updated: 2026-10-24
---
# Capture The Flag – CODEGATE 2022 Finals Blockchain Challenge Look It Up Writeup

> 赛事：CODEGATE 2022 Finals 2022 | 方向：web | 难度：hard

## 一句话总结

CODEGATE 2022 Finals区块链题 Look It Up，3层proof验证

## 攻击链

1. nc启动私有链+uuid+RPC+private key
2. Setup合约challenge=new Challenge()
3. Challenge合约含flag但query()需10000 ether
4. isPowerOf2验证n+1为2的幂
5. sanity_check: f.length==n + t/s1/s2.length==n+1
6. 三个子条件solved1/solved2/solved3全true后declareSolved
7. 题目核心是构造三个有效proof（f, t, s1, s2）

## 关键 payload

```
web3.sha3(text="isSolved()")[:4] → solved() call
```

## 经验教训

Paradigm CTF框架部署区块链题，需10000 ether绕过+构造f/t/s1/s2

## 标签

blockchain、solidity、foundry、paradigm-ctf、NTT、isPowerOf2、bn256

## 参考来源

- https://www.ctfiot.com/95239.html
- 原文件：Capture_The_Flag_–_CODEGATE_2022_Finals_Blockchain_Challenge_Look_It_Up_Writeup.full.md
