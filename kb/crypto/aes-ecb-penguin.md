---
title: AES-ECB 分组相等分析（ECB Penguin）
category: crypto
tags: [aes, ecb, 分组相等, 逐字节爆破, ecb penguin]
signals: [ecb 模式, 相同明文块产生相同密文块, 可以控制输入前缀, 加密后返回密文, 16 字节一块, 图片加密后轮廓可见, ecb oracle, 密文出现重复块]
difficulty: easy
source: "CTF-Wiki / Cryptopals Set 2 Challenge 12"
tools: [python, pycryptodome, pwntools]
updated: 2026-10-22
---

## 一、识别信号（题面长什么样）

- 题面明确说 `AES.MODE_ECB`，或给了 `encrypt(plaintext)` 接口而看不出模式。
- 提交大量相同字符 `A*N`，返回密文里出现**重复的 16 字节块** —— 铁证是 ECB。
- 题目让你"加密任意输入"，并在后面拼接 secret：`encrypt(user_input + flag)`。
- 图片 BMP/TGA 加密后再解密可见"企鹅轮廓"（ECB Penguin 的图片版）。
- 关键词：block、ECB、same block、16、重复、secret 拼接在末尾、逐字节。

## 二、原理

ECB 对每 16 字节独立加密，**相同明文块 → 相同密文块**，与块位置无关。

由此可以做**逐字节恢复**（前缀攻击）：

1. 已知拼接结构 `E(user_input + S)`（`S` 为 secret）。
2. 用填充让 `S` 的第 1 个字节刚好落在某块的**末尾**：前面填 `15` 字节，则明文块 = `A*15 + S[0]`。
3. 构造字典：对所有 256 个字节 `b`，计算 `E(b'A'*15 + b)` 的首块密文，与 `E(b'A'*15 + S)` 的前缀块比较。命中即得 `S[0]`。
4. 恢复 `S[0]` 后，用 `14` 字节填充，使 `A*14 + S[0] + S[1]` 占据一块，重复上一步得到 `S[1]`……以此类推。
5. 当 `S` 跨块时，把前一块的已知部分也纳入 `known`，对齐方式不变。

## 三、解题步骤

1. 探测块大小：发送 `A*1, A*2, ...` 观察密文长度跳变点，得到块大小（16）。
2. 探测"前缀长度"（是否有固定 header）：逐字节增加 `A`，直到出现两个相同块 —— 说明 `A` 的重复块被挤到一起。
3. 构造 `pad + known` 的字典表，与 `pad + secret` 比对。
4. 循环直到恢复出 `}` 或失败。
5. 若 secret 中含不可打印字节，照样恢复（`bytes` 层面）。

## 四、可直接运行的脚本

```python
from Crypto.Cipher import AES
from Crypto.Util.Padding import pad
import os

key = os.urandom(16)
SECRET = b"flag{3cb_p3ngu1n_1s_my_f4vor1te}"
BS = 16

def oracle(user_input: bytes) -> bytes:
    """题目提供的加密接口：ECB(input + SECRET)"""
    return AES.new(key, AES.MODE_ECB).encrypt(pad(user_input + SECRET, BS))

def split_blocks(ct: bytes, bs=BS):
    return [ct[i:i + bs] for i in range(0, len(ct), bs)]

def find_block_size(oracle_fn):
    base = len(oracle_fn(b""))
    for i in range(1, 65):
        if len(oracle_fn(b"A" * i)) != base:
            return len(oracle_fn(b"A" * i)) - base
    raise ValueError("块大小探测失败")

def find_dup_block(oracle_fn):
    """发送大量 A，返回 (前缀字节数, 重复块的序号)，用于定位固定 header 偏移"""
    for i in range(1, 3 * BS):
        blocks = split_blocks(oracle_fn(b"A" * (i + 2 * BS)))
        for idx in range(len(blocks) - 1):
            if blocks[idx] == blocks[idx + 1]:
                return i, idx
    return 0, 0

def ecb_byte_at_a_time(oracle_fn, prefix_blocks=0):
    known = b""
    while True:
        padlen = (BS - 1 - (len(known) + prefix_blocks * BS) % BS) % BS
        feed = b"A" * (padlen + prefix_blocks * BS)
        idx = len(feed) // BS + len(known) // BS
        targets = split_blocks(oracle_fn(feed))
        if idx >= len(targets):
            break
        target = targets[idx]
        for b in range(256):
            blocks = split_blocks(oracle_fn(feed + known + bytes([b])))
            if idx < len(blocks) and blocks[idx] == target:
                known += bytes([b])
                break
        else:
            break
    return known

print("块大小:", find_block_size(oracle))
print(ecb_byte_at_a_time(oracle))
```

图片版 ECB Penguin（判断是否 ECB 的快速实验）：

```python
from Crypto.Cipher import AES
from PIL import Image
import io

key = b"0" * 16
img = Image.open("penguin.bmp").convert("RGB")
raw = img.tobytes()
# ECB 加密后同样的颜色块 -> 同样密文块，图像轮廓原样保留
enc = AES.new(key, AES.MODE_ECB).encrypt(raw[: len(raw) // 16 * 16])
Image.frombytes("RGB", img.size, enc[: len(raw)]).save("penguin_ecb.bmp")
```

## 五、常见坑 / 变体

- **`target_block` 下标算错**：`len(known) // BS` 只在 `known` 恰好按块推进时正确；有固定前缀时要减去前缀块数。
- **固定前缀**（例如服务端拼了 `"user="`）：需要先用重复块找准偏移，之后所有探测都带着 `pad_len + prefix_remainder`。
- **secret 长度未知**：循环直到比对失败（候选密文块越界）为止。
- `Bytes` 拼接别用 `str`，`b"flag"` 和 `"flag"` 混用会直接 Type 错误。
- 变体：**ECB + 替换**：若能控制某块内容，可用"同块替换"直接拼出攻击载荷（如 admin 块）。
- 变体：**未被填充的 ECB**（`raw` 不是 16 倍数）→ 长度都得对齐才能比较。
- 判别 ECB 的通用手法：`A*64` 输入，若密文出现重复块则必定是 ECB（CBC/CTR 不会有）。

## 六、参考来源

- [CTF-Wiki 分组模式 ECB](https://ctf-wiki.org/crypto/blockcipher/mode/ecb/)
- [CTF-Wiki 分组模式简介](https://ctf-wiki.org/crypto/blockcipher/mode/introduction/)
- [Cryptopals Challenge 12: Byte-at-a-time ECB decryption](https://cryptopals.com/sets/2/challenges/12)
- [ECB Penguin 演示](https://github.com/google/google-ctf)
