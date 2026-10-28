---
title: "Android 爬虫比赛 第一关解析"
category: web
tags: ["爬虫 CTF", "web", "yuanrenxue match2022", "frida hook", "Sign.sign", "page+timestamp"]
signals: ["爬虫 CTF 2022", "yuanrenxue match2022", "frida hook", "Sign.sign", "page+timestamp", "retrofit2", "BodyObservable", "lambda$initListeners$2", "Python累加", "reverse", "Android", "frida", "hook", "ChallengeOneFragment"]
difficulty: medium
source: "https://www.ctfiot.com/92066.html"
tools: ["Frida", "Java", "Python"]
origin: des-import
origin_kind: cards
updated: 2026-10-24
---
# Android 爬虫比赛 第一关解析

> 赛事：爬虫 CTF 2022 | 方向：web | 难度：medium | 工具：Frida、Java、Python

## 一句话总结

猿人学 Android 爬虫第一关 — frida hook ChallengeOneFragment + Sign.sign + Python rpc.exports.callsecretfunctionedy + 100 页 value 累加得 flag count。

## 攻击链

1. jadx 反编译 com.yuanrenxue.match2022
2. 翻页时抓包, 发现 page + t + sign 三个参数
3. frida hook ChallengeOneFragment.lambda$initListeners$2(OooOO0O) 看 this.page.value
4. sb = "page=" + page + timestamp → bArr = bytearray utf8
5. frida hook Sign.sign(byte[]) 拿加密结果
6. Python rpc.exports.callsecretfunctionedy(bArr) 调 Java Sign.sign
7. 100 页累加 value 即 flag count

## 关键 payload

```
page + timestamp 拼接 / Sign.sign(bArr) 加密 / retrofit2 BodyObservable 返回值 / 100 页累加 / frida rpc.exports
```

## 经验教训

frida + rpc.exports 是 Java <-> Python 跨语言调标准做法;byte[] 参数先 bytearray('utf-8') 再传;sign 加密是 page+timestamp 拼接后单函数。

## 标签

yuanrenxue match2022、frida hook、Sign.sign、page+timestamp、retrofit2、BodyObservable、lambda$initListeners$2、Python累加、看雪论坛

## 参考来源

- https://www.ctfiot.com/92066.html
- 原文件：Android爬虫比赛_第一关解析.full.md
