---
title: "春节领红包 9 Web 中级题 wasm 逆向"
category: web
tags: ["春节领红包", "web", "WASM", "HMAC-SHA1", "custom-Base64", "SHA-256"]
signals: ["春节领红包 2026", "WASM", "HMAC-SHA1", "custom-Base64", "SHA-256", "audio-stitching", "WebAssembly.instantiate-hook", "crypto.getRandomValues-hook", "audio-wav", "web_unknown", "instantiate", "memory", "getRandomValues", "HMAC"]
difficulty: hard
source: "https://www.ctfiot.com/303352.html"
tools: []
origin: des-import
origin_kind: cards
updated: 2026-10-24
---
# 春节领红包 9 Web 中级题 wasm 逆向

> 赛事：春节领红包 2026 | 方向：web | 难度：hard

## 一句话总结

WASM 验证码生成：劫持 instantiate 暴露 memory + 劫持 getRandomValues 消除随机 + 内存扫描提 HMAC Key + Base64 字典。

## 攻击链

1. 目标: WASM gen(uid, voice) 函数生成 50 位自定义 Base64 验证码
2. Step 1: 生成 17 字节随机数 rand
3. Step 2: uid (小端序) ^ rand[0:4] 拼接 rand[0:17] = 21 字节 msg
4. Step 3: 14 字节硬编码 HMAC Key (WASM 内存 1295967 偏移) 对 msg HMAC 签名
5. Step 4: msg + HMAC 前 16 字节 = 37 字节，自定义字典 Base64 编码 → 50 位字符
6. Step 5: 50 位验证码明文 SHA-256 嵌套 8230 次得到 hash
7. Step 6: 验证码字符 → 内置 wav 碎片拼接音频返回前端
8. 漏洞 1: 劫持 WebAssembly.instantiate 暴露 window.wasmMem
9. 漏洞 2: 劫持 crypto.getRandomValues 填 0 消除随机性
10. 漏洞 3: 内存扫描定位 HMAC Key (1295967 偏移) + 自定义字典 (1295903 偏移)
11. 漏洞 4: 截取原生匹配文本，扫描整个 WASM 内存找 flag

## 关键 payload

```
uid=2406132, rand=17 字节全 0, HMAC Key = 0001010101010100010001000502 (14 字节)
```

## 经验教训

WASM 加密逻辑不是黑盒，memory 暴露后 key + 算法全可被逆向；crypto API 钩子是 WASM 加密验证类 CTF 的核心突破口。

## 标签

WASM、HMAC-SHA1、custom-Base64、SHA-256、audio-stitching、WebAssembly.instantiate-hook、crypto.getRandomValues-hook、audio-wav、XaraMysteria、voice-captcha

## 参考来源

- https://www.ctfiot.com/303352.html
- 原文件：春节解题领红包之九_{Web_中级题}_题解_–_wasm逆向.full.md
