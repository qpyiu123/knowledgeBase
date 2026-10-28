---
title: "【WP】第二届\"红明谷\"杯数据安全大赛题目解析（一）"
category: crypto
tags: ["红明谷", "crypto", "Coppersmith-small-roots", "RSA-padding", "m=M+k*r", "Zmod-polynomial"]
signals: ["红明谷 2022", "Coppersmith-small-roots", "RSA-padding", "m=M+k*r", "Zmod-polynomial", "beta-0.03", "phar-upload", "Laminas-chain", "TemplateMapResolver", "crypto_rsa", "RSA", "Coppersmith", "phar", "Laminas"]
difficulty: hard
source: "https://www.ctfiot.com/32078.html"
tools: ["Sage"]
origin: des-import
origin_kind: cards
updated: 2026-10-24
---
# 【WP】第二届"红明谷"杯数据安全大赛题目解析（一）

> 赛事：红明谷 2022 | 方向：crypto | 难度：hard | 工具：Sage

## 一句话总结

第二届红明谷杯数据安全大赛题解（一），RSA Coppersmith 小根攻击 + phar 反序列化 Laminas 链。

## 攻击链

1. 1. RSA 加密 + 512 位素数 r + M = m%r + 32 位随机填充 /2. m 约 591 位 + r 512 位 + k 约 79 位 /3. 构造多项式 f=(M+x*r)^e - c 在 Zmod(n) 上找小根 k /4. k < 2^79 < n^(1/e) 用 Sage small_roots 求解 /5. 还原 m = M + k*r /6. phar 上传绕 + phar 反序列化 Laminas 链子

## 关键 payload

```
Coppersmith small_roots X=2^100, beta=1, epsilon=0.03  phar 反序列化 LaminasViewResolver.TemplateMapResolver
```

## 经验教训

m = M + k*r + 32 填充，k < n^(1/e) 是 Coppersmith 小根攻击标准配置；Laminas 框架 phar 反序列化链利用 TemplateMapResolver.setBody = system。

## 标签

Coppersmith-small-roots、RSA-padding、m=M+k*r、Zmod-polynomial、beta-0.03、phar-upload、Laminas-chain、TemplateMapResolver

## 参考来源

- https://www.ctfiot.com/32078.html
- 原文件：【WP】第二届“红明谷”杯数据安全大赛题目解析（一）.full.md
