---
title: "[原创] Realworld CTF 2023 The_cult_of_8_bit 详解"
category: web
tags: ["Real World CTF 2023", "web", "some_attack_jsonp", "xhr_sync_xhr_policy", "url_null_byte_error", "focus_iframe_alphabet"]
signals: ["Real World CTF 2023 2023", "some_attack_jsonp", "xhr_sync_xhr_policy", "url_null_byte_error", "focus_iframe_alphabet", "post_id_crypto_randomuuid_leak", "opener_opener_xss", "same_origin_method_execution", "post_ejs", "xss", "Realworld", "CTF", "cult", "bit"]
difficulty: hard
source: "https://www.ctfiot.com/91479.html"
tools: []
origin: des-import
origin_kind: cards
updated: 2026-10-24
---
# [原创] Realworld CTF 2023 The_cult_of_8_bit 详解

> 赛事：Real World CTF 2023 2023 | 方向：web | 难度：hard

## 一句话总结

Realworld CTF 2023 The cult of 8 bit 详解：JSONP callback SOME 攻击 + XHR %00 报错触发 fallback + iframe name 字符 focus 事件 + opener 跨域访问，逐字符泄漏 36 字符 UUID post id 后访问 /post/?id= 取 flag。

## 攻击链

1. 后端 /post/:id 路由 + res.jsonp({success, name, body}) + DOMPurify 强过滤 + admin CSRF/csrf token 保护 + admin.user==='admin' 拒 create/post todo → post.ejs JSONP XHR fallback (XHR 错误时) → 注入 id%3Fcallback=alert%23 覆盖 callback → SOME 攻击 + iframe name=0123456789abcdef- focus 事件 + opener 跨域访问 → 逐字符泄漏 flag post id (36 字符 UUID) → /post/?id=flag 访问 flag

## 关键 payload

```
?id={uuid}%00 让 XHR.open 报错 / ?id={uuid}%3Fcallback=alert%23%00 切断 callback / iframe.allow="sync-xhr 'none'" 禁用 XHR / charList = "0123456789abcdef-" / 36 字符 UUID 长度爆破
```

## 经验教训

SOME (Same-Origin Method Execution) 攻击是黑帽 EU 14 论文提出的经典 XSS 替代技术；sync-xhr 特征策略 + %00 URL 截断是绕 XHR fallback 触发 JSONP 的标配。

## 标签

some_attack_jsonp、xhr_sync_xhr_policy、url_null_byte_error、focus_iframe_alphabet、post_id_crypto_randomuuid_leak、opener_opener_xss、same_origin_method_execution、post_ejs、8bit_xsleak

## 参考来源

- https://www.ctfiot.com/91479.html
- 原文件：[原创]Realworld_CTF_2023_The_cult_of_8_bit详解.full.md
