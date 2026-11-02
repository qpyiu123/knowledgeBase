---
title: 方法卡 · 哈希长度扩展伪造（md5/sha1）
category: crypto
tags: [方法卡, 长度扩展, hash length extension, md5, sha1, mac, 签名绕过]
signals: [sign = md5(secret + data), 只校验签名不校验长度, 参数可控的 mac, 无 hmac, 想追加参数]
difficulty: medium
source: kb/crypto/hash-length-extension.md
tools: [python, 内置脚本]
updated: 2026-11-02
---

# 方法卡 · 哈希长度扩展伪造（md5/sha1）

## 适用场景

网站/题面用 `md5(secret || data)` 或 `sha1(secret || data)` 当"签名"，
只给你 `data` 和它的签名，且 `data` 是可控的（如 `user=guest&role=user`）。
目标是**在不知道 secret 的情况下**，构造 `data'` 让服务端仍然校验通过，并在 `data'` 里塞进 `&role=admin`。

## 前置条件

- 算法是 **MD5 / SHA-1 / SHA-256/512（Merkle–Damgård 家族）**，且是 `secret || data` 的拼接顺序。
- 服务端没有改用 **HMAC**（HMAC 免疫本攻击）。
- 签名比较是"非恒时"或长度固定的原样比较（本题只需伪造出正确签名即可）。
- 关键是**知道 secret 的长度**：长度为 8 就试 8，不知道就暴力枚举 0–64（脚本原生支持）。

## 步骤

1. 从服务端响应里抄下原始 `data`、它的十六进制签名。
2. 报文格式通常要求"原 data + 填充字节 + 追加内容"一起发回去；
   填充字节由 `len(secret) + len(data)` 决定，脚本会自动生成。
3. 枚举 secret 长度（0–64），对每个长度产出一条伪造报文与对应签名。
4. 逐条提交，观察哪一条被接受（被接受的那条就锁定了 secret 长度）。
5. 注意 **URL 编码**：`\x80` 等二进制字节要按 `%80` 转义再过表单/查询串，否则服务端解析出的字节不同。

## 立即可用脚本

脚本路径：`kb/_methods/scripts/hash_length_extension.py`

```powershell
# 自检（md5 可复现、sha1 可复现、长度猜错不命中、长度枚举唯一命中、短摘要报错、glue 对齐，<2s）
.\.venv\Scripts\python.exe kb/_methods/scripts/hash_length_extension.py --selftest

# 实战：已知 secret 长度
.\.venv\Scripts\python.exe kb/_methods/scripts/hash_length_extension.py --algo md5 `
  --orig-data "user=guest&role=user" --orig-sig ee4628cc8e8cde3e463d676fa4f18235 `
  --append "&role=admin" --secret-len 3 --json

# 实战：不知道长度，枚举 0-64
.\.venv\Scripts\python.exe kb/_methods/scripts/hash_length_extension.py --algo sha1 `
  --orig-data "user=guest" --orig-sig <40位hex> --append "&role=admin" --secret-len-range 0-64 --json
```

- 公开函数：`glue_padding(algo, total_len)`、`forge(algo, orig_data, orig_sig, append, secret_len)`
  → `{algo, secret_len, new_data, new_data_hex, new_sig}`；内部含 `_md5_compress`、`_sha1_compress`。
- ⚠️ `orig_sig` 必须传**原始字节**（在函数里）；命令行传的是 hex 字符串，脚本会自动转。
  直接调用 `forge()` 时传 hex 字符串会报 `ValueError: md5 摘要应为 16 字节，实际 32`。
- 自检输出形如 `selftest ok: 6/6（md5 伪造签名可被 md5(secret+新data) 复现、sha1 同类、长度猜错不命中、长度枚举唯一命中、短摘要报错、glue 对齐 64）`。

## 手工示例

```powershell
# 已知 secret = b"k3y"，原报文 user=guest&role=user
# 原签名 = md5(b"k3y" + b"user=guest&role=user") = ee4628cc8e8cde3e463d676fa4f18235
.\.venv\Scripts\python.exe kb/_methods/scripts/hash_length_extension.py --algo md5 `
  --orig-data "user=guest&role=user" --orig-sig ee4628cc8e8cde3e463d676fa4f18235 `
  --append "&role=admin" --secret-len 3 --json
```

输出：

```json
[{"algo": "md5", "secret_len": 3,
  "new_data_hex": "757365723d677565737426726f6c653d75736572 80...00 b8 0000...00 26726f6c653d61646d696e",
  "new_sig": "39e5ee13aa5a979ab346271ead1bd273"}]
```

验证：`md5(b"k3y" + bytes.fromhex(new_data_hex)) == 39e5ee13aa5a979ab346271ead1bd273` ✔
—— 也就是说服务端按 `md5(secret + data)` 重算会得到与伪造签名一致的结果。

## 失效场景

- **服务端用 HMAC**：`HMAC(K, m)` 每次都内层/外层双哈希，长度扩展无效。
- **算法是 SHA-3 / BLAKE2**：海绵结构，不适用。
- **拼接顺序是 `data || secret`**：本卡不适用（此时需要已知 secret 或其它攻击）。
- **服务端校验了报文的长度/格式**（例如先 `json.loads` 再签名）：填充字节会破坏解析。
- **secret 长度未知且无法枚举**（服务端不反馈接受/拒绝）：只能靠题面提示或已知 cookie 结构猜。

## 相关文档

- `kb/crypto/hash-length-extension.md`（原理、hashpump/hash_extender、长度枚举与 URL 编码坑）
- `kb/_imported_cats/misc/PHP hash_equals：比较而非计算哈希（reference）__fn-php-hash-equals.md`（恒时比较的防御侧）
- `kb/misc/encoding-chain.md`（提交前对二进制字节做编码）
- 方法卡：`kb/_methods/enc_chain_decode.md`

## 目录与收录说明

本卡直接放在 `kb/_methods/` 下、文件名不带下划线前缀，是为了同时满足两件事：
`tools/kb/parser.py` 的 `iter_md_paths` 会跳过名字以 `_` 开头的文件（脚本目录 `scripts/` 不受影响），
而这些方法卡需要在 `python tools/cli.py index` 之后能被正常检索到。
