---
title: 方法卡 · JWT 伪造（none / 弱密钥 / 算法混淆 / kid·jku）
category: web
tags: [jwt, alg none, 算法混淆, 弱密钥爆破, kid 注入, jku]
signals: [cookie 或 Authorization 是三段 base64url, 解码后 header 含 alg 与 typ, 题目要求成为 admin 但没给私钥, 报错含 Signature verification failed, header 含 kid 或 jku 或 jwk 字段, 提示词出现 jwt token 签名 algorithm confusion]
difficulty: medium
source: kb/web/jwt-forge.md
tools: [python, jwt_tool, hashcat, burpsuite]
updated: 2026-11-03
---

# 方法卡 · JWT 伪造（none / 弱密钥 / 算法混淆 / kid·jku）

## 适用场景

- Cookie 或 `Authorization: Bearer` 是 `xxx.yyy.zzz` 三段 base64url；
- 解码后 header 为 `{"alg":"HS256","typ":"JWT"}` 或 `{"alg":"RS256"}`；
- 题目要求"成为 admin""伪造身份"，但没给私钥；
- 报错里有 `Signature verification failed`、`InvalidAlgorithmError`；
- header 里出现 `kid`、`jku`、`x5u`、`jwk` 字段；
- 关键词：jwt、token、签名、none、algorithm confusion。

## 前置条件

- 先解码确认 `alg` 与 payload 结构（`--decode`），并确认服务端确实**只**依赖 JWT（有 session cookie 时它优先级更高，改 JWT 可能无效）；
- `alg=none` 依赖库版本：新版 PyJWT 默认拒绝，需试大小写变体；
- 算法混淆需要拿到**服务端公钥**（`/jwks.json`、`.well-known`、证书、错误页），且它被当 HMAC 密钥直接使用；
- 本卡脚本**离线**：只伪造/爆破/给建议，不发包；RS256 真签名与公钥提取交给 openssl / jwt_tool。

## 步骤

1. **解码**：`--decode <TOKEN>` 打印 header/payload/签名长度，并按 `alg`、`kid`、`jku` 给出攻击顺序。
2. **alg=none**：`--none`（默认 `none`，变体 `None`/`NONE`/`nOnE`），签名段留空，注意结尾的 `.` 不能省。
3. **HS256 弱密钥**：`--crack <TOKEN> --wordlist rockyou.txt`；默认内置 8 个常见口令，未命中再上 `hashcat -m 16500`。
4. **RS256→HS256 混淆**：拿到公钥 PEM 后 `--confuse pub.pem`（把 PEM 当 HMAC 密钥）；若服务端用原始 DER，则改传 DER 字节。
5. **kid 注入**：`--kid ../../../../dev/null`（空文件 → 空密钥），命令注入用 `--kid '/dev/null; id'`。
6. **jku / jwk**：`--jku https://attacker/jwks.json` 或 `--jwk`（CVE-2018-0114 内嵌公钥），再让服务端去拉取/使用。

```powershell
.\.venv\Scripts\python.exe kb/_methods/scripts/jwt_forge.py --decode 'eyJhbGciOiJSUzI1NiIsImtpZCI6ImsxIn0.eyJ1c2VyIjoiYWRtaW4ifQ.abc'
.\.venv\Scripts\python.exe kb/_methods/scripts/jwt_forge.py --none --payload '{"user":"admin"}'
.\.venv\Scripts\python.exe kb/_methods/scripts/jwt_forge.py --crack '<TOKEN>' --wordlist rockyou.txt
```

## 脚本

脚本路径：`kb/_methods/scripts/jwt_forge.py`（纯标准库，离线）

- `decode(token)` / `b64_decode(token)` / `guess_alg(header)`：解码、宽容 base64、按 header 给攻击顺序；
- `forge_none(payload, variant)` / `forge_hs256(payload, key, header)` / `forge_rs256_as_hs256(payload, pubkey, as_pem)`；
- `forge_kid(payload, kid, key)` / `forge_jku(payload, jku, kid)` / `forge_jwk(payload, n, e)`；
- `crack_hs256(token, words, wordlist)`：字典爆破，非 HS256 直接拒绝；
- `--selftest`：6 组固定断言，退出码 0 才算过。

## 失效场景

- **服务端强制校验 alg**：只接受 `RS256` 且拒绝 `none`/`HS256` 时，none 与混淆同时失效，只能找 `kid`/`jku` 注入。
- **公钥未当 HMAC 密钥**：混淆前提是服务端把公钥字节直接传给 HMAC；某些库会先做 PEM/DER 规范化，签名对不上。
- **kid/jku 被白名单或哈希化**：`kid` 被严格映射到固定密钥数组、`jku` 只允许自家域名时，两条路都断。
- **JWT 与 session 混用**：session cookie 优先级更高，改 JWT 无效，需先登出或删 cookie。
- **payload 时间戳非法**：`exp`/`iat`/`nbf` 不合法直接 401，注意改成未来时间。
- **空密钥被拒**：`kid` 指向 `/dev/null` 得到空串，若库拒绝空密钥则该变体不成立。

## 相关文档

- `kb/web/jwt-forge.md`（原理与攻击面清单、jwt_tool 命令、kid/jku 示例）
