---
title: Electron / JS 混淆还原
category: reverse
tags: [Electron, asar, JS混淆, 去混淆, obfuscator.io]
signals: [附件是 .asar 或 resources/app 目录, 有 app.asar / electron.asar, js 里满是 _0x1a2b 变量名, 有 if/else 嵌套控制流, 标题栏是 Electron 默认样式]
difficulty: medium
source: "Electron 官方文档 / asar / js-beautify / HackTricks"
tools: [asar, js-beautify, de4js, Babel, Node.js, Chrome DevTools, mitmproxy]
updated: 2026-10-22
---

## 一、识别信号（题面长什么样）

- 安装目录里出现 `resources/app.asar`、`resources/app/`、`electron.exe`。
- JS 里全是 `_0x4f2a1b`、`a0_0x3c` 变量名，字符串被数组化（`_0x1234["push"](...)_0x1234["shift"]()`）。
- 代码里能看到 `obfuscator.io` 的典型结构：字符串数组 + 位移函数 + 控制流平坦化。
- 打包版有 `"use strict";` + 一整个 IIFE 包裹。
- 有 `nodeIntegration: true` 的 `BrowserWindow` 配置（可提权到命令执行，但 CTF 里通常只考逻辑还原）。

## 二、原理

Electron 应用结构：

```text
app.asar
  package.json          # main 字段指向入口
  main.js               # 主进程（Node 环境，可 require('fs')）
  preload.js            # 预加载脚本（contextBridge）
  renderer/index.html   # 渲染进程（浏览器环境）
  renderer/app.js       # 前端逻辑
```

**asar** 是简单的 tar 类归档（不是压缩），`npx asar extract app.asar out/` 即可得到源码。

**obfuscator.io 的四种变换**：

| 变换 | 特征 | 还原方式 |
|---|---|---|
| stringArray | 字符串集中到数组，用 `_0xabc(0x1f3)` 取值 | AST 求值后内联 |
| rotateStringArray | 数组被 `push(shift())` 旋转 | 先执行旋转再解析 |
| controlFlowFlattening | `while(true){ switch(_0x["state"]) {...} }` | 常量传播后还原 |
| deadCodeInjection | 大量恒假分支 | 静态删除 |
| selfDefending | 格式化就报错（依赖 `toString` 长度） | **不要格式化**，直接 AST 处理 |
| debugProtection | 打开 DevTools 就卡死 | 在 Node 里跑静态分析，别开浏览器 |

## 三、checksec 判读与利用思路

判读流程：

```text
1. 找 resources/app.asar 或 resources/app
2. npx asar list app.asar          # 看文件树，找 main / preload / 逻辑文件
3. 看 package.json 的 main 与 version
4. 判断混淆类型：strings 里有没有 obfuscator.io 特征
5. 静态跑：node 里 require 入口前先 stub 掉 electron
```

常见混淆程度与工具选择：

| 程度 | 表现 | 首选 |
|---|---|---|
| 无混淆 | 可读 JS | js-beautify |
| 字符串数组 | `_0x` 函数调用 | AST 内联（Babel） |
| + 控制流平坦化 | `switch(state)` | 常量传播 |
| + selfDefending | 格式化后报错 | 用 `de4js` 或自写 AST |

## 四、可直接运行的 exp 脚本

### 1. 解包 asar

```bash
npm i -g asar        # 或 npx asar
asar list ./app.asar
asar extract ./app.asar ./app_out
asar extract-file ./app.asar main.js
```

### 2. Node 里静态加载 main.js（stub electron）

```javascript
// stub_load.js —— node stub_load.js，用于在不启动 GUI 的情况下跑主进程逻辑
const Module = require("module");
const origResolve = Module._resolveFilename;

// 把 electron 替换成 stub
const fakeElectron = {
  app: {
    whenReady: () => Promise.resolve(),
    on: () => {},
    quit: () => {},
    getPath: () => process.cwd(),
  },
  BrowserWindow: class {
    constructor() { this.webContents = { on: () => {}, openDevTools: () => {} }; }
    loadFile() {}
    loadURL() {}
    on() {}
  },
  ipcMain: { on: () => {}, handle: () => {} },
  dialog: { showOpenDialogSync: () => [] },
  shell: { openExternal: () => {} },
};

Module._resolveFilename = function (request, ...rest) {
  if (request === "electron") return "electron_stub";
  return origResolve.call(this, request, ...rest);
};
require.cache["electron_stub"] = { id: "electron_stub", exports: fakeElectron, loaded: true };

// 然后加载目标
process.argv = [process.argv[0], "main.js"];
require("./app_out/main.js");
```

### 3. AST 去混淆（字符串数组内联 + 常量折叠）

```javascript
// deobf.js —— npm i @babel/parser @babel/traverse @babel/generator @babel/types
const fs = require("fs");
const parser = require("@babel/parser");
const traverse = require("@babel/traverse").default;
const generate = require("@babel/generator").default;
const t = require("@babel/types");

const code = fs.readFileSync(process.argv[2], "utf8");
const ast = parser.parse(code, { sourceType: "script" });

// 第一步：收集「字符串数组」与「取值函数」的名字
let strArrName = null, getterName = null;
traverse(ast, {
  VariableDeclarator(p) {
    if (t.isArrayExpression(p.node.init) &&
        p.node.init.elements.length > 20 &&
        p.node.init.elements.every(e => t.isStringLiteral(e))) {
      strArrName = p.node.id.name;
    }
    if (t.isFunctionExpression(p.node.init) && p.node.init.params.length >= 1) {
      getterName = p.node.id ? p.node.id.name : getterName;
    }
  },
});

// 第二步：把 _0xabc(0x1f) 替换成字符串字面量（带旋转的数组需先模拟执行）
const arrDecl = ast.program.body.find(x => t.isVariableDeclaration(x) &&
  x.declarations.some(d => t.id && d.id.name === strArrName));
const els = arrDecl ? arrDecl.declarations[0].init.elements : [];
let replaced = 0;
traverse(ast, {
  CallExpression(p) {
    const c = p.node.callee;
    if (!(t.isIdentifier(c) && c.name === getterName)) return;
    const arg = p.node.arguments[0];
    if (!(arg && t.isNumericLiteral(arg))) return;
    const el = els[arg.value];
    if (el && t.isStringLiteral(el)) { p.replaceWith(t.stringLiteral(el.value)); replaced++; }
  },
});

console.log(`[+] 内联字符串 ${replaced} 处`);
fs.writeFileSync(process.argv[3] || "deob.js", generate(ast).code);
```

### 5. Python 侧批量取字符串

```python
#!/usr/bin/env python3
# 先看 asar 里有没有明文提示，再决定是否上 AST 去混淆
import re, sys, pathlib, subprocess

ROOT = pathlib.Path(sys.argv[1] if len(sys.argv) > 1 else "app_out")

def dump_js_strings(root, min_len=6):
    for js in root.rglob("*.js"):
        src = js.read_text(encoding="utf-8", errors="ignore")
        for m in re.finditer(r"'([^']{%d,})'|\"([^\"]{%d,})\"" % (min_len, min_len), src):
            print(f"{js.name}: {(m.group(1) or m.group(2))[:80]!r}")

if __name__ == "__main__":
    if (ROOT.parent / "app.asar").exists():
        print(subprocess.run(["npx", "asar", "list", str(ROOT.parent / "app.asar")],
                             capture_output=True, text=True).stdout[:1000])
    dump_js_strings(ROOT)
```

## 五、常见坑 / 变体

- **selfDefending 一格式化就失效**：程序检测自身 `toString()` 长度，格式化后 `_0x` 函数自毁。解决方案：只在内存里做 AST 处理，不落格式化文件。
- **字符串数组有旋转**：`while(!![]){ try { _0x.push(_0x.shift()) } ... }`，需先用 `node -e` 执行前几行拿到旋转后的数组。
- **多包一层 `debugProtection`**：DevTools 一开就 `debugger` 死循环，用 Node 跑静态分析。
- **wasm 内嵌**：部分 Electron 游戏把算法放进 `.wasm`，配合 wasm 逆向篇。
- **打包成单文件 exe（pkg 之类）**：先找 `~` 开头的虚拟文件系统段，用 `node` 提取。

## 六、参考来源

- [Electron 官方文档](https://www.electronjs.org/docs/latest/)
- [electron/asar（asar 归档工具）](https://github.com/electron/asar)
- [js-beautify](https://github.com/beautifier/js-beautify)
- [beautifier.io 在线格式化](https://beautifier.io/)
- [Babel（AST 遍历与替换）](https://babeljs.io/docs/babel-traverse)
- [HackTricks: 逆向常用 API 与工具](https://book.hacktricks.wiki/en/reversing/common-api-used-in-malware.html)
