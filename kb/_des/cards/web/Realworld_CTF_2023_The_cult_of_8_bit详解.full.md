---
title: "Realworld CTF 2023 The_cult_of_8_bit 详解"
category: web
tags: ["Realworld CTF 2023", "web", "jsonp", "same-origin-method-execution", "iframe-focus", "post-id-leak"]
signals: ["Realworld CTF 2023 2023", "jsonp", "same-origin-method-execution", "iframe-focus", "post-id-leak", "csrf", "char-by-char-extract", "opensearch-opener", "xss", "Realworld", "CTF", "The_cult_of_8_bit", "JSONP", "callback"]
difficulty: hard
source: "https://www.ctfiot.com/107619.html"
tools: []
origin: des-import
origin_kind: cards
updated: 2026-10-24
---
# Realworld CTF 2023 The_cult_of_8_bit 详解

> 赛事：Realworld CTF 2023 2023 | 方向：web | 难度：hard

## 一句话总结

Realworld CTF 2023 The_cult_of_8_bit：JSONP callback + URL %00 截断 + opener opener 跨窗口访问 admin home + iframe focus 监听逐字符提取 UUID 拿到 flag post。

## 攻击链

1. 博客系统: /login /register /report /post / 五个路由
2. admin 用户密码 sha256(ADMIN_PASSWORD || "password") + Object.freeze
3. 初始 flag post: crypto.randomUUID() 作 id, body=FLAG env
4. admin 不可创建 todo (Nice try redirect)
5. 漏洞 1: XSS todo 注入 - new URL(text) 检测 + javascript: 黑名单
6. 漏洞 2: JSONP callback 跨域调用 load_post({success, name, body})
7. 漏洞 3: URLSearchParams.get(''id'') 不 url-decode → null byte 注入
8. 攻击: %00 截断 + %3F 替换 ? + callback=alert%23
9. 完整链: post/?id=UUID%3Fcallback=alert%23%00 → innerHTML 渲染 callback
10. admin 通过 report URL 访问 → callback 触发 → opener 跨窗口调用
11. 技巧: opener.opener.document.body...text[i] 逐字符提取 post id
12. iframe focus 监听: charList="0123456789abcdef-" + createIframe(name)
13. document.activeElement.name 获焦点 iframe name → 还原 36 字符 UUID
14. feature policy allow="sync-xhr 'none'" 阻止 sync-xhr
15. 完整利用: open /b.html + location=/(admin home) + listenFocus + exploit 36 次
16. 36 次循环: for i=0..35 { challenge.location = /post/?id=...%3Fcallback=...+text[i]+.focus }

## 关键 payload

```
opener[opener.opener.document.body.children[1].childNodes[1].children[0].children[0].children[3].children[0].children[0].children[0].text[${i}]].focus
```

## 经验教训

JSONP + URLSearchParams.get 不解码是 web 高阶绕过；opener.opener 跨窗口读取同源页面内容是经典 XSS 提权；iframe name + focus + activeElement 是逐字符提取 UUID 的盲注技巧。

## 标签

jsonp、same-origin-method-execution、iframe-focus、post-id-leak、csrf、char-by-char-extract、opensearch-opener

## 参考来源

- https://www.ctfiot.com/107619.html
- 原文件：Realworld_CTF_2023_The_cult_of_8_bit详解.full.md
