---
title: AES-CBC 字节翻转 / 逐字节解密（Padding Oracle）
category: crypto
tags: [aes, cbc, 字节翻转, padding oracle, 分组密码]
signals: [cbc 模式, 密文十六进制很长, iv 可篡改, 已知明文前缀, admin 权限被加密, padding error, 分组大小 16, 提交密文后报错, 解密失败提示]
difficulty: medium
source: "CTF-Wiki / 公开 writeup"
tools: [python, pwntools, pycryptodome]
updated: 2026-10-22
---

## 一、识别信号（题面长什么样）

- 密文是 16 字节整数倍，常与 `IV` 一起给出（前面 16 字节或单独字段）。
- 题面："user=guest" 加密后交给服务器，目标是伪造 "user=admin"。
- 服务端对错误密文返回"解密失败 / Padding error / 500"——这就是 **padding oracle**。
- 可变长输入：提交 `name=AAAA...` 后返回的密文长度随输入增长 —— 说明输入和明文拼接（前缀攻击）。
- 关键词：CBC、IV、xor、flip、padding、bit-flipping。
- 变体：给了加密接口和"解密后是否合法"的判断接口，两者分离。

## 二、原理

CBC 解密：

```
P_i = D(C_i) XOR C_{i-1}      (C_0 = IV)
```

**字节翻转**：只要篡改 `C_{i-1}` 的第 `j` 字节，就能让 `P_i` 的第 `j` 字节变成任意值（`D(C_i)[j]` 不变）。代价是会破坏 `P_{i-1}` 整块，所以只能翻转**非第一个可控块**。

**Padding Oracle**：PKCS#7 填充要求末块解密后末字节 = 填充长度 `n`（`0x01`、`0x02 0x02`...）。oracle 只要告诉我们"填充是否合法"，就能逐字节恢复：

1. 对密文 `C = C_1..C_n`，构造 `C' = C_{n-1} XOR guess || C_n`，让服务端"解密"并观察是否合法。
2. 已知末块是 `0x01` 时，只需爆破倒数第 1 字节（256 次）；命中后设 `desired[-1] = 0x02`，再爆破第 2 字节…… 每字节至多 256 次。
3. 得到中间值 `I = P XOR C_{n-1}`，则 `P = I XOR C_{n-1}`。移到上一块继续。

## 三、解题步骤

1. 确认块大小（16）与 IV 位置。
2. 若目标是"篡改已知内容"（如 `admin=0` → `admin=1`），直接用异或翻转对应字节。
3. 若目标是"读取未知明文"，用 padding oracle 逐块恢复。
4. 若是"前缀攻击"（加密 oracle 拼接固定前缀），逐字节恢复明文后拼出 flag。
5. 写脚本时先本地用已知 key 自测，再打远端。

## 四、可直接运行的脚本

脚本 A —— 精准字节翻转：

```python
from Crypto.Util.Padding import pad
from Crypto.Cipher import AES

def flip_block(key, iv, ct, block_idx, offset, old_byte, new_byte):
    """修改 P[block_idx] 的第 offset 字节：old_byte -> new_byte"""
    ct = bytearray(ct)
    prev = iv if block_idx == 0 else ct[(block_idx - 1) * 16: block_idx * 16]
    prev = bytearray(prev)
    prev[offset] ^= old_byte ^ new_byte
    if block_idx == 0:
        iv = bytes(prev)
    else:
        ct[(block_idx - 1) * 16: block_idx * 16] = prev
    return iv, bytes(ct)

# --- 自测：把 user=guest 改成 user=admin ---
key = b"0" * 16
iv = b"\x00" * 16
plain = b"user=guest&role=low"          # 20 字节，补齐后 32
ct = AES.new(key, AES.MODE_CBC, iv).encrypt(pad(plain, 16))
# 第 1 块内 'guest' 的 g 改成 a
i = plain.index(b"guest")
new_iv, new_ct = flip_block(key, iv, ct, 0, i, ord('g'), ord('a'))
out = AES.new(key, AES.MODE_CBC, new_iv).decrypt(new_ct)
print(out)   # b'user=aest&role=low...'  ← 注意后续字节全被破坏
```

脚本 B —— Padding Oracle 逐字节恢复：

```python
def padding_oracle_decrypt(ct, iv, oracle, block_size=16):
    """oracle(prev_block: bytes, block: bytes) -> True 表示填充正确
       返回完整明文（不含 padding）"""
    blocks = [iv] + [ct[i:i+block_size] for i in range(0, len(ct), block_size)]
    plaintext = b""
    for bi in range(len(blocks) - 1, 0, -1):
        prev, cur = bytearray(blocks[bi - 1]), blocks[bi]
        inter = bytearray(block_size)                   # 中间值 D(C_i)
        for pad_len in range(1, block_size + 1):
            pos = block_size - pad_len
            for g in range(256):
                prev[pos] = g
                if oracle(bytes(prev), cur):
                    # 排除 pad_len=1 时的歧义（改前一字节再验一次）
                    if pad_len == 1:
                        prev[pos - 1] ^= 0xFF
                        if not oracle(bytes(prev), cur):
                            continue
                        prev[pos - 1] ^= 0xFF
                    inter[pos] = g ^ pad_len
                    break
            for j in range(pos, block_size):
                prev[j] = inter[j] ^ (pad_len + 1)
        plaintext = bytes(inter) + plaintext
    return plaintext.rstrip(b"\x00")  # 或用 pkcs7 unpad
```

脚本 C —— 加密 oracle 前缀攻击（读取固定前缀之外的 secret）：

```python
import requests

def prefix_attack(encrypt_fn, block=16, known=b""):
    """encrypt_fn(data: bytes) -> bytes(密文)
       结构：E(secret_prefix + data + secret_suffix)，先爆破前缀块数再逐字节恢复"""
    # 1) 探测前缀长度：发的 A 足够多时，A 会填满并跨块，出现重复块
    for i in range(1, 2 * block + 1):
        ct = encrypt_fn(b"A" * (i + 2 * block))
        blocks = [ct[j:j + block] for j in range(0, len(ct), block)]
        if len(blocks) != len(set(blocks)):
            prefix_len = i + 2 * block - (len(blocks) - len(set(blocks)))
            break
    # 2) 逐字节恢复（与 aes-ecb-penguin.md 中的字典法相同，只需带上前缀偏移）
    while True:
        padlen = (block - 1 - (len(known) + prefix_len) % block) % block
        ct = encrypt_fn(b"A" * (padlen + prefix_len))
        target_idx = (len(known) + prefix_len) // block
        target = ct[target_idx * block:(target_idx + 1) * block]
        for b in range(256):
            cand = encrypt_fn(b"A" * (padlen + prefix_len) + known + bytes([b]))
            blocks = [cand[j:j + block] for j in range(0, len(cand), block)]
            if target_idx < len(blocks) and blocks[target_idx] == target:
                known += bytes([b]); print(known); break
        else:
            return known
```

## 五、常见坑 / 变体

- **翻转只影响目标块**：`C_{i-1}` 被改后 `P_{i-1}` 全乱，若明文结构敏感（JSON、签名）则整体失效。
- **padding oracle 的 `pad_len=1` 歧义**：命中 `0x01` 时也可能是其他字节被改成 `0x01` 的误报，必须用"改前一字节再验一次"排除。
- **最后一字节爆破顺序**：从 `pad_len=1` 开始（最后 1 字节），不是从最后一个字节往前。
- 若 `ct` 长度不是 16 倍数，说明有 base64/hex 编码没解开。
- 变体：**CBC bit-flipping 配合 `XOR` 已知明文**：想要 `P_i = desired`，则 `C_{i-1}' = desired XOR D(C_i)`，需要已知 `P_{i-1}` 反推 `D(C_i) = P_i XOR C_{i-1}`。
- 变体：IV 被复用/固定 → 可做"字典比对"，同类明文产生相同首块。
- 变体：**CBC-R**（Cipher Block Chaining Reverse）：用 oracle 生成任意明文块。

## 六、参考来源

- [CTF-Wiki 分组模式 CBC](https://ctf-wiki.org/crypto/blockcipher/mode/cbc/)
- [CTF-Wiki Padding Oracle Attack](https://ctf-wiki.org/crypto/blockcipher/mode/padding-oracle-attack/)
- [CTF-Wiki 填充方式](https://ctf-wiki.org/crypto/blockcipher/mode/padding/)
- [Kudelski, "The Padding Oracle Attack"（经典说明）](https://robertheaton.com/2013/07/29/padding-oracle-attack/)
