---
title: "CTF 中的 EJS 漏洞筆記"
category: web
tags: ["EJS CTF", "web", "Express", "EJS", "res.render('index", "req.query)"]
signals: ["EJS CTF 2023", "Express", "EJS", "res.render('index", "req.query)", "settings['view options']污染", "outputFunctionName RCE", "opts.shell", "prepended include", "web_unknown", "CTF", "res", "render", "index"]
difficulty: medium
source: "https://www.ctfiot.com/120877.html"
tools: []
origin: des-import
origin_kind: cards
updated: 2026-10-24
---
# CTF 中的 EJS 漏洞筆記

> 赛事：EJS CTF 2023 | 方向：web | 难度：medium

## 一句话总结

CTF EJS 漏洞笔记 — Express + EJS + res.render('index', req.query) 污染 settings['view options'] + outputFunctionName RCE (CVE-2022-29078 风格)。

## 攻击链

1. Express + EJS 模板引擎
2. res.render('index', req.query) 把 query 直接传给 opts
3. opts.settings['view options'] 被污染
4. outputFunctionName 选项触发 RCE
5. 也可通过 opts.shell / opts.prepended 等 prototype 污染
6. payload: ?settings[view options][outputFunctionName]=...;s=...

## 关键 payload

```
EJS render query 污染 / outputFunctionName RCE / settings[view options] / shell / prepended include / opts.delimiter
```

## 经验教训

EJS render(view, options) 把 options 传到 View 内部,污染 settings/opts 是 RCE 经典链;outputFunctionName 是模板生成函数注入点。

## 标签

Express、EJS、res.render('index、req.query)、settings['view options']污染、outputFunctionName RCE、opts.shell、prepended include、CVE-2022-29078

## 参考来源

- https://www.ctfiot.com/120877.html
- 原文件：CTF_中的_EJS_漏洞筆記.full.md
