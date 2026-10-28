---
title: "第七届\"楚慧杯\"网络空间安全实践能力竞赛-预赛WriteUp"
category: misc
tags: ["第七届楚慧杯预赛", "misc", "楚慧杯预赛", "mobile/misc/crypt", "AES解密", "VeraCrypt容器"]
signals: ["第七届楚慧杯预赛 2022", "楚慧杯预赛", "mobile/misc/crypt", "AES解密", "VeraCrypt容器", "BitLocker加密卷", "stegsolve LSB", "passware", "CRC改高度", "misc_unknown", "mobile", "AES", "misc", "VeraCrypt"]
difficulty: medium
source: "https://www.ctfiot.com/106699.html"
tools: ["Stegsolve"]
origin: des-import
origin_kind: cards
updated: 2026-10-24
---
# 第七届"楚慧杯"网络空间安全实践能力竞赛-预赛WriteUp

> 赛事：第七届楚慧杯预赛 2022 | 方向：misc | 难度：medium | 工具：Stegsolve

## 一句话总结

第七届楚慧杯预赛：mobile AES+misc VeraCrypt+BitLocker+stegsolve+改CRC

## 攻击链

1. mobile:level_one(直接看)→level_up AES解密→crypt:VeraCrypt容器从jpg FFD9后提取→secret:BitLocker+改图片高度+stegsolve→pocky:hex写新文件

## 关键 payload

```
flag{380605c6-7123-4f71-b573-601e8c4457b4};flag{6b1df900-1284-11ed-9fa7-5405dbe5e745};flag{4ba7689c6dee7749403380b11c416de6};flag{b6aa5b40559fc9762918cd32f5f6bd0f};password1=OXi password2=ChaiYan;620224-121649-497585-220572-660704-152383-484957-174713
```

## 经验教训

综合取证常用：FFD9后藏文件+改图片高度+BitLocker密码恢复+stegsolve提取

## 标签

楚慧杯预赛、mobile/misc/crypt、AES解密、VeraCrypt容器、BitLocker加密卷、stegsolve LSB、passware、CRC改高度

## 参考来源

- https://www.ctfiot.com/106699.html
- 原文件：第七届“楚慧杯”网络空间安全实践能力竞赛-预赛WriteUp.full.md
