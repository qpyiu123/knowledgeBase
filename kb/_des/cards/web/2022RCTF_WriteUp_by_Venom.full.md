---
title: "2022 RCTF WriteUp by Venom"
category: web
tags: ["RCTF 2022", "web", "Prettier", "RCE", "prettierrc.js", "parser"]
signals: ["RCTF 2022 2022", "Prettier", "RCE", "prettierrc.js", "parser", "child_process", "_load", "mainModule", "constructor", "rce", "crypto_oracle", "prettierrc", "Lua", "XXTEA"]
difficulty: medium
source: "https://www.ctfiot.com/85431.html"
tools: []
origin: des-import
origin_kind: cards
updated: 2026-10-24
---
# 2022 RCTF WriteUp by Venom

> 赛事：RCTF 2022 2022 | 方向：web | 难度：medium

## 一句话总结

Prettier .prettierrc.js RCE + Lua XXTEA 变种 + srand 爆破

## 攻击链

1. Prettier RCE: 写 .prettierrc.js 配置 parser 字段
2. parser 触发: module.exports = function babel(text, parsers, opts) { return text + flag }
3. flag = exec('/readflag') 通过 global.process.mainModule.constructor._load 拿 child_process.execSync
4. Crypto Lua: 8 轮 XXTEA 变种 sum=0xB8 delta=0x37
5. b = { key[0], key[1], key[2], key[3] }
6. strDecrypt(s, k) 按 2 字符一组解密
7. math.random(33, 126) 生成 4 字符密码 srand 爆破
8. Decrypt() 调 strDecrypt 拿 flag

## 关键 payload

```
parser = .prettierrc + _load('child_process').execSync('/readflag')
```

## 经验教训

Prettier 配置 RCE 是 npm 供应链攻击典型；Lua TEA 变种是 reverse/crypto 入门

## 标签

Prettier、RCE、prettierrc.js、parser、child_process、_load、mainModule、constructor、Lua、TEA、XXTEA、bxor、srand、math.random

## 参考来源

- https://www.ctfiot.com/85431.html
- 原文件：2022RCTF_WriteUp_by_Venom.full.md
