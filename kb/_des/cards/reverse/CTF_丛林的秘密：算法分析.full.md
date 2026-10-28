---
title: "CTF 丛林的秘密：算法分析"
category: reverse
tags: ["移动安全", "reverse", "WebAssembly", "wasm2c", "libgogogo.so mm0导出", "Frida hook gogogoJNI.check_key"]
signals: ["移动安全 2024", "WebAssembly", "wasm2c", "libgogogo.so mm0导出", "Frida hook gogogoJNI.check_key", "WebAssembly.instantiate", "set_input_flag_len", "set_input_flag", "check_key", "reverse", "CTF", "libgogogo", "mm0", "wasm"]
difficulty: hard
source: "https://www.ctfiot.com/161579.html"
tools: []
origin: des-import
origin_kind: cards
updated: 2026-10-24
---
# CTF 丛林的秘密：算法分析

> 赛事：移动安全 2024 | 方向：reverse | 难度：hard

## 一句话总结

CTF 丛林的秘密 — 安卓 + WebAssembly 算法分析 + libgogogo.so mm0 导出 wasm 字节 + wasm2c 转 c + 32x32 矩阵 numpy.linalg.solve 还原 flag。

## 攻击链

1. 安卓 APK 装 WebAssembly, 验证逻辑在 wasm 内
2. libgogogo.so 导出 mm0 函数 (readByteArray 拿 wasm 字节)
3. WebAssembly.instantiate + check_key
4. 32 字符 flag, 32x32 矩阵验证
5. wasm2c /root/Desktop/hex.wasm -o web.c 转 c
6. gcc -c web.c → web.o
7. numpy.array 32x32 矩阵
8. scipy.linalg.solve 解线性方程组
9. 还原 flag

## 关键 payload

```
WebAssembly / wasm2c 转 c / libgogogo.so mm0 35000 字节 / gogogoJNI.check_key 32 字符 / 32x32 矩阵 / numpy.linalg.solve
```

## 经验教训

WebAssembly 是 Android 算法保护新趋势;Frida hook 导出函数 + readByteArray 拿 wasm 字节是标准流程;wasm2c 转 c 后用 numpy 解线性方程组。

## 标签

WebAssembly、wasm2c、libgogogo.so mm0导出、Frida hook gogogoJNI.check_key、WebAssembly.instantiate、set_input_flag_len、set_input_flag、check_key、32x32 矩阵、numpy.linalg.solve、linear algebra

## 参考来源

- https://www.ctfiot.com/161579.html
- 原文件：CTF_丛林的秘密：算法分析.full.md
