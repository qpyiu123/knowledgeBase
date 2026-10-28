---
title: "Frida Hook Android method（一）"
category: reverse
tags: ["ad2001 Frida 系列", "reverse", "frida", "android", "hook", "java.perform"]
signals: ["ad2001 Frida 系列 2023", "frida", "android", "hook", "java.perform", "caesar-cipher", "get_random", "check", "reverse", "Frida", "Hook", "Android", "Caesar-21", "flag"]
difficulty: easy
source: "https://www.ctfiot.com/151304.html"
tools: ["Frida"]
origin: des-import
origin_kind: cards
updated: 2026-10-24
---
# Frida Hook Android method（一）

> 赛事：ad2001 Frida 系列 2023 | 方向：reverse | 难度：easy | 工具：Frida

## 一句话总结

Frida Hook Android：get_random+check函数hook+Caesar-21解flag

## 攻击链

1. get_random返回0-99随机整数
2. check(i, i2) 验证 (i*2)+4==i2
3. 成功返回"AMDYV{WVWT_CJJF_0s1}"的Caesar变种
4. charAt-21取模26+26
5. Frida hook get_random返回真实值
6. Frida hook check(int, int)强制参数8, 20

## 关键 payload

```
AMDYV{WVWT_CJJF_0s1}  # Caesar-21后flag
```

## 经验教训

Frida可用Java.use+"implementation"覆盖Java方法

## 标签

frida、android、hook、java.perform、caesar-cipher、get_random、check

## 参考来源

- https://www.ctfiot.com/151304.html
- 原文件：Frida_Hook_Android_method（一）.full.md
