---
title: "几个Web+JS相关CTF题目小记 - Node原型链污染"
category: web
tags: ["多个CTF题目精选(JS+Web)", "web", "Node.js", "原型链污染", "prototype_pollution", "Proxy"]
signals: ["多个CTF题目精选(JS+Web) 2022", "Node.js", "原型链污染", "prototype_pollution", "Proxy", "Fastify", "innerHTML", "SVG_onload", "unhandledrejection", "web_unknown", "Web", "Node", "npm", "preinstall"]
difficulty: medium
source: "https://www.ctfiot.com/84742.html"
tools: ["pwntools"]
origin: des-import
origin_kind: cards
updated: 2026-10-24
---
# 几个Web+JS相关CTF题目小记 - Node原型链污染

> 赛事：多个CTF题目精选(JS+Web) 2022 | 方向：web | 难度：medium | 工具：pwntools

## 一句话总结

5题Web+JS小记:Node原型链污染触发npm preinstall RCE/Proxy拦截/Fastify x-token/innerHTML SVG onload/unhandledrejection。

## 攻击链

1. Node JSON深合并Object.entries原型链污染(Object.prototype.data.path.shell) → npm preinstall脚本读取prototype.path触发RCE → Proxy get()拦截flag访问 → Fastify x-token=hash(user.id)未授权 → innerHTML+SVG onload执行JS → window.addEventListener('unhandledrejection',e.reason.stack)泄露path

## 关键 payload

```
Object.prototype.data = {exports:{"./pwn.js"},name:'./usage.js'} + prototype.shell + prototype.path
```

## 经验教训

Node深合并Object.entries递归赋值是经典原型链污染漏洞;Object.prototype.data.path.shell可被npm preinstall利用;SVG onload可在innerHTML中执行JS;Proxy get()陷阱;window.addEventListener('unhandledrejection')泄露错误堆栈信息。

## 标签

Node.js、原型链污染、prototype_pollution、Proxy、Fastify、innerHTML、SVG_onload、unhandledrejection、npm_preinstall、prototype.shell、prototype.path、Object.prototype.data

## 参考来源

- https://www.ctfiot.com/84742.html
- 原文件：幾個與_Web_跟_JS_相關的_CTF_題目小記.full.md
