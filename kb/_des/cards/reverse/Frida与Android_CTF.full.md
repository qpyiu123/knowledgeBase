---
title: "Frida 与 Android CTF"
category: reverse
tags: ["看雪/Tide 安全 (kanxue/pediy1)", "reverse", "Frida", "Android", "JNI", "Java.perform"]
signals: ["看雪/Tide 安全 (kanxue/pediy1) 2022", "Frida", "Android", "JNI", "Java.perform", "Java.choose", "enumerateClassLoaders", "Interceptor.replace", "kill", "reverse", "misc_unknown", "hook", "frida", "spawn"]
difficulty: medium
source: "https://www.ctfiot.com/31515.html"
tools: ["Frida", "Java"]
origin: des-import
origin_kind: cards
updated: 2026-10-24
---
# Frida 与 Android CTF

> 赛事：看雪/Tide 安全 (kanxue/pediy1) 2022 | 方向：reverse | 难度：medium | 工具：Frida、Java

## 一句话总结

Frida hook + 爆破绕过 Android JNI 校验 + kill 拦截绕反调试

## 攻击链

1. frida -U -f 目标包 spawn 注入
2. Java.perform hook 关键方法 VVVV(context, str)
3. Java.choose 找 MainActivity 实例注入伪 context
4. Java.enumerateClassLoaders 找正确 classloader
5. 枚举 0-99999 爆破正确输入拿 true 返回
6. Interceptor.replace(libc.so!kill) 绕反调试

## 关键 payload

```
Java.use("com.kanxue.pediy1.VVVVV").VVVV(CONTEXT2, String(x))
```

## 经验教训

Android CTF 高频工具是 Frida；自定义 classloader 需 enumerateClassLoaders 切换；JNI 反调试常见用 kill(pid, 0) 检测 tracerpid

## 标签

Frida、Android、JNI、Java.perform、Java.choose、enumerateClassLoaders、Interceptor.replace、kill、anti-debug

## 参考来源

- https://www.ctfiot.com/31515.html
- 原文件：Frida与Android_CTF.full.md
