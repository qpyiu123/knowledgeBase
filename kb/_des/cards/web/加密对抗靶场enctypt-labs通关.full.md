---
title: "加密对抗靶场enctypt-labs通关"
category: web
tags: ["encrypt-labs / 加密对抗靶场", "web", "encrypt-labs", "AES", "DES", "RSA"]
signals: ["encrypt-labs / 加密对抗靶场 2024", "encrypt-labs", "AES", "DES", "RSA", "HmacSHA256", "加签验签", "防重放", "弱口令", "web_unknown", "key", "admin", "t3giDeeWT99XilzCslD9EQ", "jVQ1xurlO1dvxYRk9TvRA"]
difficulty: medium
source: "https://www.ctfiot.com/216940.html"
tools: ["Flask"]
origin: des-import
origin_kind: cards
updated: 2026-10-24
---
# 加密对抗靶场enctypt-labs通关

> 赛事：encrypt-labs / 加密对抗靶场 2024 | 方向：web | 难度：medium | 工具：Flask

## 一句话总结

encrypt-labs 8 关通关：对称/AES/RSA/混合/DES/HmacSHA256/防重放/服务端签，最关键是替换 JS 固定 key 和弱口令。

## 攻击链

1. 第 1 关: 对称加密 (算法定位) → admin/1234
2. 第 2 关: AES key 固定 t3giDeeWT99XilzCslD9EQ== iv=+jVQ1xurlO1dvxYRk9TvRA==
3. 第 3 关: RSA 加密 (只公钥, 只能加密不能解密)
4. 第 4 关: AES+RSA 混合 → 替换 JS 固定 key/iv (复用第 2 关)
5. 第 5 关: DES 规律 key (username=test → key=key66666, iv=9999test)
6. 第 6 关: HmacSHA256 加签 → secret_key=be56e057f20f883e, timestamp 10 位
7. 第 7 关: 防重放 + RSA 加密 timestamp 13 位 + Yakit 热加载
8. 第 8 关: 加签 key 在服务端 → 弱口令 admin/123456
9. autodecoder 一键解密 (前 5 关)
10. 第 6-7 关自写 Flask /encode /decode 接口

## 关键 payload

```
admin/1234 + admin/123456 弱口令 + autodecoder + Yakit热加载
```

## 经验教训

加密对抗核心思路: 1) 抓包定位算法位置 2) 提取 key/iv (硬编码/可预测/可替换 JS) 3) autodecoder 一键解密 4) 防重放注意 timestamp + nonce; 5) 实在不行弱口令爆破。

## 标签

encrypt-labs、AES、DES、RSA、HmacSHA256、加签验签、防重放、弱口令、autodecoder、Yakit热加载

## 参考来源

- https://www.ctfiot.com/216940.html
- 原文件：加密对抗靶场enctypt-labs通关.full.md
