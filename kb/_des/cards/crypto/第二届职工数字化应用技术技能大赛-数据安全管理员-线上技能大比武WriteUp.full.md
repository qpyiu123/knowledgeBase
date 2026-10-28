---
title: "第二届职工数字化应用技术技能大赛-数据安全管理员-线上技能大比武WriteUp"
category: crypto
tags: ["职工数字化应用技术技能大赛", "crypto", "数据安全", "Cookie伪造", "URL编码", "符号替代"]
signals: ["职工数字化应用技术技能大赛 2025", "数据安全", "Cookie伪造", "URL编码", "符号替代", "Base32魔改", "XOR", "key循环", "crypto_rsa", "cookie", "username", "date", "URL", "Base32"]
difficulty: easy
source: "https://www.ctfiot.com/281761.html"
tools: []
origin: des-import
origin_kind: cards
updated: 2026-10-24
---
# 第二届职工数字化应用技术技能大赛-数据安全管理员-线上技能大比武WriteUp

> 赛事：职工数字化应用技术技能大赛 2025 | 方向：crypto | 难度：easy

## 一句话总结

3道数据安全题,11名成绩,涵盖cookie伪造(username+date+URL编码)+符号替代密码表(!→1..)→0)+自定义Base32(32字母表)解码+首字节^0x33+8字节循环XOR key(37704cf0)

## 攻击链

1. 数据泄露: 伪造auth cookie username=administrator&date=UTC时间戳+URL编码→访问index.php|数据混淆: 符号替代(!→1,@→2,#→3,$→4,%→5,^→6,&→7,*→8,(→9,)→0)→|数据脱敏: 自定义Base32字母表FNT5BMYAJD4IHLKU6RE3VQWGCO27SPZX+首字节^0x33+其余字节循环XOR key=37704cf0(8字节)→取第12行第2列

## 关键 payload

```
cookie_value=quote_plus(''username=administrator&date=2025-11-XX+0000&'')|FNT5BMYAJD4IHLKU6RE3VQWGCO27SPZX|unxor: res[0] ^= 0x33; for i in range(1,len): res[i] ^= key[i & 7]
```

## 经验教训

1) 服务端可能只验证cookie中username+date而不验证签名,直接quote_plus伪造; 2) 符号替代密码本质是字符替换,优先级!@#$%^&*()对应1234567890; 3) 自定义Base32字母表(FNT5...)要识别反查索引; 4) XOR解密三层:首字节单值^0x33+其余循环XOR 8字节key; 5) 完整文件解密后需定位行+列(本例第12行第2列=865975201629227428)

## 标签

数据安全、Cookie伪造、URL编码、符号替代、Base32魔改、XOR、key循环

## 参考来源

- https://www.ctfiot.com/281761.html
- 原文件：第二届职工数字化应用技术技能大赛-数据安全管理员-线上技能大比武WriteUp.full.md
