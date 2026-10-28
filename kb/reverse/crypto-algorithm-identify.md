---
title: 算法还原套路（TEA / XXTEA / RC4 / 自定义变换的识别特征）
category: reverse
tags: [tea, xtea, rc4, 算法识别, 加密还原]
signals:
  - "反编译里出现 (v5 << 4) ^ (v5 >> 5) 这种移位+异或组合"
  - "常量 0x9E3779B9 或 0x61C88647 出现在代码里"
  - "有一个 256 字节的 S 盒初始化循环，随后两次 swap"
  - "输入按 8 字节一组处理，长度必须是 8 的倍数"
  - "循环次数固定为 16 / 32 / 64 轮"
  - "rol/ror 或成对的 << 与 >> 指令密集出现"
  - "十进制常量 0x52CFB1E3、0x5A827999 之类魔数"
  - "题面提示词出现 加密 / 算法还原 / TEA / RC4 / 自定义变换"
difficulty: medium
source: "TEA / XXTEA / RC4 原始论文与参考实现"
tools: [python, ida, z3, ctypes]
updated: 2026-10-22
---

## 一、识别信号（题面长什么样）

- 反编译里出现 `v4 = (v4 + ((v5 << 4) ^ (v5 >> 5))) ^ ...` 这种"移位 + 异或 + 加法"的组合。
- 常量：`0x9E3779B9`（TEA delta）、`0x61C88647`（负 delta）、`0xC6EF3720`（sum 初值）、`0x52CFB1E3`。
- 有一个 256 字节的数组初始化循环（RC4 的 KSA），随后的伪随机交换（PRGA）。
- 数据按 **8 字节**（TEA）或 **4 字节**（RC4/XOR）一组处理。
- 循环次数固定为 16、32、64（TEA 轮数）。
- 有 `rol`/`ror`/`<<`/`>>` 密集出现，且成对（左移 + 右移）。
- 题面提示：`加密`、`算法`、`还原`、`TEA`、`RC4`、`自定义变换`。

## 二、原理

### 1. TEA（Tiny Encryption Algorithm）

```c
void encrypt(uint32_t v[2], uint32_t k[4]) {
    uint32_t v0 = v[0], v1 = v[1], sum = 0, delta = 0x9E3779B9;
    for (int i = 0; i < 32; i++) {
        sum += delta;
        v0 += ((v1 << 4) + k[0]) ^ (v1 + sum) ^ ((v1 >> 5) + k[1]);
        v1 += ((v0 << 4) + k[2]) ^ (v0 + sum) ^ ((v0 >> 5) + k[3]);
    }
    v[0] = v0; v[1] = v1;
}
```


### 2. XTEA / XXTEA

- **XTEA**：同样用 delta，但 key 通过 `sum & 3` 选择下标；`v0 += (((v1<<4) ^ (v1>>5)) + v1) ^ (sum + k[sum&3])`。
- **XXTEA（Corrected Block TEA）**：处理任意长度，`delta` 仍是 `0x9E3779B9`，但循环条件是 `n` 个块，特征常量 `0x9E3779B9` + `(n = len)` + `z/y` 循环。

### 3. RC4

```c
// KSA
for (i = 0; i < 256; i++) s[i] = i;
for (i = 0, j = 0; i < 256; i++) {
    j = (j + s[i] + key[i % keylen]) % 256;
    swap(s[i], s[j]);
}
// PRGA
for (n = 0; n < data_len; n++) {
    i = (i + 1) % 256; j = (j + s[i]) % 256;
    swap(s[i], s[j]);
    out[n] = in[n] ^ s[(s[i] + s[j]) % 256];
}
```


### 4. 自定义变换的常见"指纹"

| 特征 | 可能的算法 |
|---|---|
| `0x9E3779B9` | TEA / XTEA / XXTEA |
| 256 字节 + S 盒 + swap | RC4 |
| 每字节查一个 256 字节表 + 异或 | AES S-box / 自定义混淆 |
| `idx = (idx * A + B) % M` | LCG 伪随机 |
| 大常量（如 `0x5A827999`） | SHA / 自定义魔数 |
| `4 字节一组 + 32 轮` | TEA 族 |
| `+0x30`、`^0x12` 之类 | 简单 XOR/加法混淆 |
| `% 0x1F` + `<<` | base32 编码 |

## 三、解题步骤

1. **看数据流**：找出 `input → 变换 → 常量比较` 的主干。
2. **抓常量**：`0x9E3779B9` 一出，基本锁定 TEA 族。
3. **定分组**：输入长度必须是 8 的倍数 → 确认 TEA。
4. **找 key**：硬编码 4 个 dword、字符串展开、或 `MD5(password)`。
5. **手写解密**：TEA/XTEA 照搬公式改方向；RC4 同样 KSA/PRGA 异或；自定义用 z3 或 `ctypes` 调 DLL 逆推。
6. **验证**：加密已知明文，比对密文与题目常量是否一致。

## 四、可直接运行的脚本

TEA / XTEA / XXTEA 全集（解密为主）：

```python
DELTA, M = 0x9E3779B9, 0xFFFFFFFF
def tea_enc(v0, v1, k, r=32):
    s = 0
    for _ in range(r):
        s = (s + DELTA) & M
        v0 = (v0 + (((v1 << 4) + k[0]) ^ (v1 + s) ^ ((v1 >> 5) + k[1]))) & M
        v1 = (v1 + (((v0 << 4) + k[2]) ^ (v0 + s) ^ ((v0 >> 5) + k[3]))) & M
    return v0, v1
def xtea_enc(v0, v1, k, r=32):
    s = 0
    for _ in range(r):
        v0 = (v0 + ((((v1 << 4) ^ (v1 >> 5)) + v1) ^ (s + k[s & 3]))) & M
        s = (s + DELTA) & M
        v1 = (v1 + ((((v0 << 4) ^ (v0 >> 5)) + v0) ^ (s + k[(s >> 11) & 3]))) & M
    return v0, v1
def tea_dec(v0, v1, k, r=32):
    s = (DELTA * r) & M
    for _ in range(r):
        v1 = (v1 - (((v0 << 4) + k[2]) ^ (v0 + s) ^ ((v0 >> 5) + k[3]))) & M
        v0 = (v0 - (((v1 << 4) + k[0]) ^ (v1 + s) ^ ((v1 >> 5) + k[1]))) & M
        s = (s - DELTA) & M
    return v0, v1
def xtea_dec(v0, v1, k, r=32):
    s = (DELTA * r) & M
    for _ in range(r):
        v1 = (v1 - ((((v0 << 4) ^ (v0 >> 5)) + v0) ^ (s + k[(s >> 11) & 3]))) & M
        s = (s - DELTA) & M
        v0 = (v0 - ((((v1 << 4) ^ (v1 >> 5)) + v1) ^ (s + k[s & 3]))) & M
    return v0, v1
def xxtea_dec(data, key):
    n = len(data) - 1
    if n < 1: return data
    y = data[0]; s = ((6 + 52 // (n + 1)) * DELTA) & M
    while s:
        e = (s >> 2) & 3
        for p in range(n, -1, -1):
            z = data[p - 1] if p > 0 else data[n]
            mx = (((z >> 5) ^ (y << 2)) + ((y >> 3) ^ (z << 4))) ^ ((s ^ y) + (key[(p & 3) ^ e] ^ z))
            data[p] = (data[p] - mx) & M
            y = data[p]
        s = (s - DELTA) & M
    return data

# RC4：两次 swap 是铁证
def rc4_dec(data: bytes, key: bytes) -> bytes:
    s = list(range(256)); j = 0
    for i in range(256):
        j = (j + s[i] + key[i % len(key)]) % 256
        s[i], s[j] = s[j], s[i]
    i = j = 0
    out = bytearray()
    for b in data:
        i = (i + 1) % 256
        j = (j + s[i]) % 256
        s[i], s[j] = s[j], s[i]
        out.append(b ^ s[(s[i] + s[j]) % 256])
    return bytes(out)
```

扫描二进制里的 TEA 常量（IDA 里也可直接 Alt+B 搜）：

```python
import sys

data = open(sys.argv[1], "rb").read()
sigs = {"delta": "b979379e", "neg": "4786c861", "sum0": "2072efc6"}
for name, sig in sigs.items():
    i = data.find(bytes.fromhex(sig))
    while i != -1:
        print(name, "@0x%X" % i)
        i = data.find(bytes.fromhex(sig), i + 1)
```

自定义变换用 z3 反解（少量非线性运算时）：

```python
from z3 import BitVec, Solver, sat
s = Solver()
x = [BitVec("x%d" % i, 8) for i in range(8)]
target = bytes.fromhex("1122334455667788")
for i in range(8):
    s.add(((x[i] ^ 0x5A) + 0x13) & 0xFF == target[i])   # 换成题目里的表达式
if s.check() == sat:
    print(bytes(s.model()[v].as_long() for v in x))
```

## 五、常见坑 / 变体

- **轮数不一定是 32**：16/64 都见过，解密循环数要与加密一致。
- **delta 被改**：换成 `0x12345678` 之类，靠 `<<4/>>5` 结构识别。
- **XTEA 的 key 选择**：`k[s & 3]` 与 `k[(s >> 11) & 3]`，两个下标不能搞混。
- **XXTEA 结束条件**：`while (s)` 循环，轮数 `q = 6 + 52/(n+1)`。
- **RC4 的 S 盒被预置**：用 key 长度反推初始化方式。
- **变体：ChaCha20 / Salsa20（`expand 32-byte k`）、CRC32（`0xEDB88320`）、AES/SM4（查 S 盒，AES 起始为 `0x63,0x7c,0x77,0x7b`）**。
- **变体：TEA 加密后再 base64 / 自定义 base64 + XOR** —— 先解码再走上面步骤。
- **实用技巧**：`binwalk -E`、IDA 的 `findcrypt` 插件可自动识别这些常量。
## 六、参考来源

- [TEA 算法维基（含 XTEA/XXTEA 说明）](https://en.wikipedia.org/wiki/Tiny_Encryption_Algorithm)
- [XXTEA 参考实现](https://en.wikipedia.org/wiki/XXTEA)
- [RC4 算法维基](https://en.wikipedia.org/wiki/RC4)
- [TEA 算法的使用及逆向识别技巧（腾讯云社区）](https://cloud.tencent.com/developer/article/2494148)
- [IDA Python API](https://github.com/idapython/src)
- [PyCryptodome 文档](https://pycryptodome.readthedocs.io/en/latest/)
