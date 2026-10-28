---
title: "AliyunCTF 2025 Jtools Fury 反序列化利用分析"
category: web
tags: ["AliyunCTF", "web", "Apache Fury", "hutool", "feilong", "DisallowedList"]
signals: ["AliyunCTF 2025", "Apache Fury", "hutool", "feilong", "DisallowedList", "MapProxy动态代理", "Convert.convertWithCheck", "BeanConverter", "ObjectUtil.deserialize", "deserialize", "AliyunCTF", "Jtools", "Apache", "Fury"]
difficulty: hard
source: "https://www.ctfiot.com/229693.html"
tools: []
origin: des-import
origin_kind: cards
updated: 2026-10-24
---
# AliyunCTF 2025 Jtools Fury 反序列化利用分析

> 赛事：AliyunCTF 2025 | 方向：web | 难度：hard

## 一句话总结

AliyunCTF 2025 Jtools — Apache Fury 二次反序列化绕黑名单：PriorityQueue + PropertyComparator + hutool MapProxy 动态代理 + Convert + BeanConverter + ObjectUtil.deserialize 链触发二次反序列化。

## 攻击链

1. hutool 构建 Web, fury.deserialize 处理请求参数
2. 类黑名单 checkNotInDisallowedList 在 createSerializer 触发
3. 二次反序列化: ValidateObjectInputStream 重载 resolveClass 但默认黑白名单 null
4. 调用点 ObjectUtil#deserialize 不受黑白名单影响
5. 触发链: PriorityQueue.readObject → PropertyComparator.compare → TemplatesImpl.getOutputProperties
6. 二次链: PropertyComparator → MapProxy.invoke(Proxy) → Convert.convert → BeanConverter.convertInternal → ObjectUtil.deserialize → ValidateObjectInputStream.readObject (黑白名单 null)
7. 走两次反序列化,第二次绕过黑名单

## 关键 payload

```
PriorityQueue + PropertyComparator + MapProxy + Convert + BeanConverter + ObjectUtil.deserialize + ValidateObjectInputStream(黑白名单null) / 二次反序列化绕黑名单
```

## 经验教训

hutool ObjectUtil.deserialize 默认黑白名单 null;动态代理 MapProxy#invoke 是触发 Convert 转换的入口;PropertyComparator 走 feilong PropertyUtilsBean.getProperty 是 feilong 依赖特色。

## 标签

Apache Fury、hutool、feilong、DisallowedList、MapProxy动态代理、Convert.convertWithCheck、BeanConverter、ObjectUtil.deserialize、ValidateObjectInputStream 黑白名单null、PropertyComparator、TemplatesImpl#getOutputProperties、二次反序列化

## 参考来源

- https://www.ctfiot.com/229693.html
- 原文件：AliyunCTF2025_题解之_Jtools_Fury_反序列化利用分析.full.md
