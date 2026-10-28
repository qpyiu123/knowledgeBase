---
title: 哈希长度扩展攻击（Hash Length Extension）
category: crypto
tags: [哈希长度扩展, md5, sha1, MAC, Merkle-Damgard]
signals: [md5(secret+data), sha1(key+msg), MAC 可被伪造, 已知 hash 值和消息, secret 长度未知, 可以劫持参数, 签名校验, 只知道哈希不能改消息, length extension]
difficulty: medium
source: "CTF-Wiki / hashpump"
tools: [python, hashpump, hash_extender, pwntools]
updated: 2026-10-22
---

## 一、识别信号（题面长什么样）

- 服务端用 `md5(secret + user_input)` 做签名，并把 `data` 和 `signature` 一起返回。
- 校验逻辑形如 `if md5(secret + data) == signature:` —— 注意 `secret` 在前。
- 题面允许你提交 `data` 与 `signature`，且 `secret` 长度未知（或明确说 16/32 字节）。
- 常见场景：`file=test&sign=xxx`，想追加 `&admin=1`。
- 关键词：MAC、signature、hmac 替代品、`secret+`、Merkle–Damgård。
- 变体：sha256 同理；HMAC 免疫此攻击。

## 二、原理

MD5 / SHA1 / SHA256 都是 Merkle–Damgård 结构：消息先按块填充（`0x80` + 若干 `0x00` + 8 字节长度），再逐块压缩，块间以 128/256/512 bit 的中间状态链接。

攻击者已知 `h = H(secret || data)`，但不知道 `secret`。由于哈希完整状态就藏在 `h` 里，攻击者可以：

1. 从已知的 `h` 重建链接变量 IV；
2. 在 `data` 的填充之后继续追加 `extra`；
3. 得到 `h' = H(secret || data || padding || extra)`，无需 `secret`。

服务端重算 `H(secret + 新data)` 时看到完全一致的哈希 —— 因为 MD5 内部计算的就是这个串。

限制：只知道 `secret` 的**长度**（或用循环尝试 1~64 字节）。

## 三、解题步骤

1. 记录 `data` 与原 `signature = H(secret || data)`。
2. 猜测 `secret` 长度 `k`（一般 8、16、32，或 0..64 全试）。
3. 用 hashpump 等工具计算：`new_data = data || padding(k + len(data)) || ";admin=1"`，`new_sign = ...`。
4. 把 `new_data`（注意是 `bytes`，常要 URL 编码）和 `new_sign` 一起提交。
5. 若返回成功即命中；失败就换下一个 `k`。

## 四、可直接运行的脚本

脚本 A —— 用 hashpump（Linux / WSL）：

```bash
# 安装
git clone https://github.com/miekrr/HashPump && cd HashPump
make && sudo make install

# 用法：-k 密钥长度  -s 原签名  -d 原数据  -a 追加数据
hashpump -k 16 \
  -s 5f4dcc3b5aa765d61d8327deb882cf99 \
  -d "user=guest" \
  -a "&admin=1"
# 输出：
# New Signature: ...
# New String: user=guest\x80\x00....&admin=1
```

脚本 B —— 纯 Python 实现 MD5 长度扩展（可直接跑，无需第三方）：

```python
import struct, hashlib

# ---------- MD5 核心 ----------
S = [7,12,17,22]*4 + [5,9,14,20]*4 + [4,11,16,23]*4 + [6,10,15,21]*4
K = [int(abs(__import__("math").sin(i + 1)) * 2**32) & 0xFFFFFFFF for i in range(64)]

def _md5_compress(state, block):
    a, b, c, d = state
    M = list(struct.unpack("<16I", block))
    for i in range(64):
        if i < 16:   f, g = (b & c) | (~b & d), i
        elif i < 32: f, g = (d & b) | (~d & c), (5*i + 1) % 16
        elif i < 48: f, g = b ^ c ^ d, (3*i + 5) % 16
        else:        f, g = c ^ (b | (~d & 0xFFFFFFFF)), (7*i) % 16
        f = (f + a + K[i] + M[g]) & 0xFFFFFFFF
        a, d, c = d, c, b
        b = (b + ((f << S[i]) | (f >> (32 - S[i])))) & 0xFFFFFFFF
    return [(state[0] + a) & 0xFFFFFFFF, (state[1] + b) & 0xFFFFFFFF,
            (state[2] + c) & 0xFFFFFFFF, (state[3] + d) & 0xFFFFFFFF]

def md5_pad(msg_len):
    """返回 msg_len 长度消息在 MD5 中的填充字节"""
    pad = b"\x80"
    pad += b"\x00" * ((56 - (msg_len + 1) % 64) % 64)
    pad += struct.pack("<Q", (msg_len * 8) & 0xFFFFFFFFFFFFFFFF)
    return pad

def md5_continue(known_hash_hex, secret_len, data, extra):
    """已知 H(secret||data)，返回 (new_msg, new_hash_hex)"""
    state = list(struct.unpack("<4I", bytes.fromhex(known_hash_hex)))
    total_len = secret_len + len(data)
    glue = md5_pad(total_len)
    forged_prefix = data + glue
    # 用已知 state 作为 IV 继续压缩 extra
    msg = extra
    # 补齐到 64 字节再切块
    body = msg + md5_pad(total_len + len(glue) + len(msg))
    for i in range(0, len(body), 64):
        state = _md5_compress(state, body[i:i+64])
    new_hash = struct.pack("<4I", *state).hex()
    return forged_prefix + extra, new_hash

# ---------- 自测 ----------
secret = b"0123456789abcdef"          # 16 字节，未知
data   = b"user=guest"
sig    = hashlib.md5(secret + data).hexdigest()
msg, new_sig = md5_continue(sig, 16, data, b"&admin=1")
# 服务端会计算 md5(secret + msg)，验证是否一致：
print("match:", hashlib.md5(secret + msg).hexdigest() == new_sig)
```

脚本 C —— 交互式利用：

```python
import requests

orig_data, orig_sign = "user=guest", "5f4d..."
for k in range(0, 65):
    msg, sig = md5_continue(orig_sign, k, orig_data.encode(), b"&admin=1")
    r = requests.get("http://TARGET/index.php",
                     params={"data": msg, "sign": sig})
    if b"flag" in r.content or "success" in r.text:
        print("secret_len =", k); print(r.text); break
```

## 五、常见坑 / 变体

- **URL 编码坑**：`msg` 里有 `\x80` 和 `\x00`，requests 的 `params` 会正确编码，但手工拼 `?data=` 时必须 `quote(msg, errors='ignore')`，否则服务端解不动。
- **`secret` 长度扫描**：0~64 全试，别只看 16；有的题 `secret` 是随机长度。
- **`secret` 在后**（`H(data || secret)`）时**不能**用长度扩展（追加内容后 secret 不在中间）。
- **HMAC 免疫**：若服务端用 `hmac.new(key, data, hashlib.sha256)`，放弃本攻击。
- **SHA512 的 padding 长度字段是 128 bit**，长度扩展时注意字节序和位宽。
- 变体：**盐值 + 长度扩展 + 反序列化**组合，常见于 `.php` 签名绕过。
- 工具对比：`HashPump`（C，支持 md5/sha1/sha256）、`hash_extender`（命令行 `--format md5 --secret 16`）、`hlextend`（Python 库）。

## 六、参考来源

- [CTF-Wiki Hash Attack（哈希长度扩展攻击）](https://ctf-wiki.org/crypto/hash/attack/)
- [HashPump（bwall）](https://github.com/miekrr/HashPump)
- [hash_extender（iagox86）](https://github.com/iagox86/hash_extender)
- [Hash Length Extension Attack 中文笔记](https://ciphersaw.me/2017/11/12/hash-length-extension-attack/)
