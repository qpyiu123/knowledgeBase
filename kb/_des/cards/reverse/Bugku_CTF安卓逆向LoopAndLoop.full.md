---
title: "Bugku CTF 安卓逆向 LoopAndLoop"
category: reverse
tags: ["Bugku", "reverse", "APK逆向", "JNI反弹调用", "check1+check2+check3", "100/1000/10000循环累加"]
signals: ["Bugku 2022", "APK逆向", "JNI反弹调用", "check1+check2+check3", "100/1000/10000循环累加", "1835996258校验", "alictf{}", "JNI FindClass GetMethodID CallIntMethod", "IDA F5", "reverse", "Bugku", "LoopAndLoop", "JNI", "chec"]
difficulty: hard
source: "https://www.ctfiot.com/167027.html"
tools: ["ARM", "IDA", "Java"]
origin: des-import
origin_kind: cards
updated: 2026-10-24
---
# Bugku CTF 安卓逆向 LoopAndLoop

> 赛事：Bugku 2022 | 方向：reverse | 难度：hard | 工具：ARM、IDA、Java

## 一句话总结

Bugku 安卓逆向 LoopAndLoop — JNI chec 反射调 check1+check2+check3 三函数累加 + check(input,99)==1835996258 + stringFromJNI2 还原 alictf{} flag。

## 攻击链

1. APK jadx 看 MainActivity: input → check(input, 99) == 1835996258 触发
2. check 调 chec(input, s) JNI native
3. so chec 用 FindClass("net/bluelotus/.../MainActivity") 反射拿 check1/check2/check3 methodID
4. CallIntMethod 调 (a2, v10[2*s%3], t, s-1) 反弹调 Java
5. check1: t += 1..99
6. check2: s%2==0 → t += 1..999; else t -= 1..999
7. check3: t += 1..9999
8. s=99 → v10[2*99%3] = v10[0] = check1; s=98 → check2; s=97 → check3; s=96 → check1
9. 循环递归直到 s=1 返回 t
10. flag: alictf{stringFromJNI2(in_int)}

## 关键 payload

```
check(input,99) == 1835996258 / JNI chec FindClass GetMethodID CallIntMethod 反射 / check1+check2+check3 三函数累加 / 2*s%3 索引 / stringFromJNI2 flag
```

## 经验教训

JNI 反弹调 Java 函数是 Android 逆向难点;2*s%3 索引巧妙选函数;stringFromJNI2(in_int) 是 flag 生成函数。

## 标签

APK逆向、JNI反弹调用、check1+check2+check3、100/1000/10000循环累加、1835996258校验、alictf{}、JNI FindClass GetMethodID CallIntMethod、IDA F5、ARM F5

## 参考来源

- https://www.ctfiot.com/167027.html
- 原文件：Bugku_CTF安卓逆向LoopAndLoop.full.md
