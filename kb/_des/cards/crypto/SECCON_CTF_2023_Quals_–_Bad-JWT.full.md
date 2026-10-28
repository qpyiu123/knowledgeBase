---
title: "SECCON CTF 2023 Quals - Bad-JWT"
category: crypto
tags: ["SECCON CTF 2023 Quals", "crypto", "jwt", "prototype-pollution", "map-vs-object", "toprimitive"]
signals: ["SECCON CTF 2023 Quals 2023", "jwt", "prototype-pollution", "map-vs-object", "toprimitive", "type-juggling", "node-js", "alg-constructor", "crypto_oracle", "SECCON", "CTF", "Quals", "Bad-JWT", "JWT"]
difficulty: hard
source: "https://www.ctfiot.com/135314.html"
tools: []
origin: des-import
origin_kind: cards
updated: 2026-10-24
---
# SECCON CTF 2023 Quals - Bad-JWT

> 赛事：SECCON CTF 2023 Quals 2023 | 方向：crypto | 难度：hard

## 一句话总结

SECCON CTF 2023 Quals Bad-JWT：自研 JWT alg 字段未白名单 + prototype chain attack + 算法名 'constructor' 触发 Buffer.from(Symbol.toPrimitive) 类型转换 bypass 签名校验。

## 攻击链

1. 自研 JWT: HS256/HS512 algorithms + base64UrlEncode/Decode + parseToken + sign + verify
2. verify 用 Buffer.compare(calculated_buf, expected_buf) !== 0 校验
3. 漏洞: header.alg.toLowerCase() + algorithms[alg](data, secret) 索引
4. 攻击 1: alg=''constructor'' → algorithms[''constructor''] = undefined
5. calculated_signature = undefined(data, secret) → 触发 String 转换
6. crypto.createHmac("sha256", secret) → Hmac 接受 undefined secret 报 TypeError
7. 但 undefined(..., ...) 在 JS 中调用返回 undefined 字符串
8. 攻击 2: alg 改成 "constructor" 后 calculated_signature 包含 base64 字符串
9. 把 calculated_signature 复制到 signature 字段 → 校验通过
10. jwt = header(alg=constructor) + payload(isAdmin=true) + calculated_sig
11. Buffer.compare 接收 "calculated" + "expected" 都是 base64 字符串
12. 关键: 算法名 prototype chain attack + Buffer.from(string, ''base64'') 接受 Symbol.toPrimitive
13. 实战: class Bar [Symbol.toPrimitive] = ''eyJ0eXAi...'' 触发 Buffer.from 转换
14. 完整 chain: 1) alg=constructor 2) 复制 calculated_signature 3) 提交 session cookie
15. flag: SECCON{Map_and_Object.prototype.hasOwnproperty_are_good}

## 关键 payload

```
header = {"typ": "JWT", "alg": "constructor"} + body = {"isAdmin": true} + jwt.signature = calculated_signature
```

## 经验教训

JWT 实现 alg 字段必须白名单 (HS256/RS256) 防 prototype 链污染；Map/Object.prototype.hasOwnProperty 是 JS 通用过滤工具；Buffer.from(symbol, 'base64') 接受 Symbol.toPrimitive 是 Node 经典 bypass。

## 标签

jwt、prototype-pollution、map-vs-object、toprimitive、type-juggling、node-js、alg-constructor

## 参考来源

- https://www.ctfiot.com/135314.html
- 原文件：SECCON_CTF_2023_Quals_–_Bad-JWT.full.md
