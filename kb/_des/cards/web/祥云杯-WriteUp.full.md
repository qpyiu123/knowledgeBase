---
title: "祥云杯-WriteUp"
category: web
tags: ["祥云杯", "web", "fastjson反序列化", "BCEL字节码", "Codeception RunProcess", "Guzzle AppendStream"]
signals: ["祥云杯 2021", "fastjson反序列化", "BCEL字节码", "Codeception RunProcess", "Guzzle AppendStream", "OpisClosure", "内网穿透", "Spring路径穿越", "deserialize", "fastjson", "BCEL", "Codeception", "Guzzle", "system"]
difficulty: hard
source: "https://www.ctfiot.com/1349.html"
tools: []
origin: des-import
origin_kind: cards
updated: 2026-10-24
---
# 祥云杯-WriteUp

> 赛事：祥云杯 2021 | 方向：web | 难度：hard

## 一句话总结

祥云杯fastjson反序列化+BCEL字节码+Codeception/Guzzle/OpisClosure多链触发system

## 攻击链

1. 内网fastjson反序列化→BCEL字节码执行→CodeceptionExtensionRunProcess链→GuzzleHttpPsr7AppendStream→CachingStream→PumpStream→OpisClosure序列化system('cat /flag.txt')→/admin/test路径穿越

## 关键 payload

```
$$BCEL$$字节码;CodeceptionExtensionRunProcess;GuzzleHttpPsr7AppendStream/CachingStream/PumpStream;OpisClosureserialize system('cat /flag.txt');fastjson反序列化;10.10.1.11:8080/xxxx/..;/admin/test
```

## 经验教训

fastjson+BCEL+Spring路径穿越(..;)+Codeception/Guzzle/OpisClosure gadget链组合

## 标签

fastjson反序列化、BCEL字节码、Codeception RunProcess、Guzzle AppendStream、OpisClosure、内网穿透、Spring路径穿越

## 参考来源

- https://www.ctfiot.com/1349.html
- 原文件：祥云杯-WriteUp.full.md
