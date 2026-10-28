---
title: "深育杯-WriteUp"
category: web
tags: ["深育杯", "web", "Java反序列化", "Commons Beanutils", "TemplatesImpl", "LLL格密码"]
signals: ["深育杯 2021", "Java反序列化", "Commons Beanutils", "TemplatesImpl", "LLL格密码", "fmtstr泄露canary+elfbase", "House of Botcake", "deserialize", "Java", "CommonsBeanutils", "LLL", "fmtstr", "canary", "elfbase"]
difficulty: medium
source: "https://www.ctfiot.com/10032.html"
tools: []
origin: des-import
origin_kind: cards
updated: 2026-10-24
---
# 深育杯-WriteUp

> 赛事：深育杯 2021 | 方向：web | 难度：medium

## 一句话总结

深育杯多方向：Java反序列化CommonsBeanutils+LLL格密码+fmtstr泄canary+elfbase+ret2libc

## 攻击链

1. Web:weblog CommonsBeanutils+TemplatesImpl Javassist动态类Runtime.exec→Crypto:LLL格密码(grid=[[1,h],[0,p]])+f=gcd→m=a*inverse_mod(f*f,g)%g→PWN:fmtstr泄canary+elfbase→ret2libc+House of Botcake

## 关键 payload

```
BeanComparator(null, String.CASE_INSENSITIVE_ORDER);setFieldValue(templates, '_bytecodes', targetByteCodes);v1=vector(ZZ, [1, h]);v2=vector(ZZ, [0, p]);grid.LLL();'%17$llx, %15$llx' canary+elfbase
```

## 经验教训

CommonsBeanutils+TemplatesImpl+Javassist动态类是Java反序列化经典链；LLL格密码二维向量构造

## 标签

Java反序列化、Commons Beanutils、TemplatesImpl、LLL格密码、fmtstr泄露canary+elfbase、House of Botcake

## 参考来源

- https://www.ctfiot.com/10032.html
- 原文件：深育杯-WriteUp.full.md
