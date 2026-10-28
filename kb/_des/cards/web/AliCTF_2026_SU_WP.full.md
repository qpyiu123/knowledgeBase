---
title: "AliCTF 2026 SU WP - Fileury"
category: web
tags: ["AliCTF", "web", "Apache Fury", "DisallowedList黑名单", "SimpleCache$StoreableCachingMap", "LazyMap"]
signals: ["AliCTF 2026", "Apache Fury", "DisallowedList黑名单", "SimpleCache$StoreableCachingMap", "LazyMap", "TiedMapEntry", "TransformingComparator", "StringValueTransformer", "PriorityQueue", "deserialize", "AliCTF", "Fileury", "Apache", "Fury"]
difficulty: hard
source: "https://www.ctfiot.com/295357.html"
tools: []
origin: des-import
origin_kind: cards
updated: 2026-10-24
---
# AliCTF 2026 SU WP - Fileury

> 赛事：AliCTF 2026 | 方向：web | 难度：hard

## 一句话总结

AliCTF 2026 Fileury — Apache Fury 黑名单 bypass: SimpleCache$StoreableCachingMap + LazyMap + TiedMapEntry + TransformingComparator(StringValueTransformer) 链写 jre/lib/ext/dnsns.jar 自动加载触发 DNSNameService 二次反序列化。

## 攻击链

1. Apache Fury 黑名单: requireClassRegistration(false) 仍走 DisallowedList
2. com.feilong 缺失 → 无法用去年二次反序列化思路
3. 未拦截: SimpleCache$StoreableCachingMap / LazyMap / TiedMapEntry / TransformingComparator / StringValueTransformer
4. PriorityQueue.readObject → heapify → comparator.compare
5. TransformingComparator(StringValueTransformer).compare
6. String.valueOf(TiedMapEntry) → toString → getValue
7. LazyMap.get(key) → ConstantFactory.create 返回预设 byte[]
8. StoreableCachingMap.put(key, value) → writeToPath 写文件
9. 写入 jre/lib/ext/dnsns.jar 自动加载
10. DNSNameServiceDescriptor 二次反序列化触发

## 关键 payload

```
PriorityQueue + TransformingComparator(StringValueTransformer) + TiedMapEntry + LazyMap(StoreableCachingMap, ConstantFactory) + writeToPath / jre/lib/ext/dnsns.jar / DNSNameServiceDescriptor
```

## 经验教训

Apache Fury 黑名单 checkNotInDisallowedList 只在序列化时走;LazyMap(StoreableCachingMap, ConstantFactory) 是新 gadget 链关键;jre/lib/ext 自动加载是经典文件写提权路径。

## 标签

Apache Fury、DisallowedList黑名单、SimpleCache$StoreableCachingMap、LazyMap、TiedMapEntry、TransformingComparator、StringValueTransformer、PriorityQueue、writeToPath、jre/lib/ext、dnsns.jar、DNSNameServiceDescriptor、二次反序列化

## 参考来源

- https://www.ctfiot.com/295357.html
- 原文件：AliCTF_2026_SU_WP.full.md
