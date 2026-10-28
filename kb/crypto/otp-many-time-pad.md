---
title: OTP / Many-Time-Pad 与 CRIB 拖拽还原
category: crypto
tags: [otp, many-time-pad, crib, 异或, 流密码]
signals: [多段密文长度接近且看起来等长, xor 后出现大量可见字符, 题目说密钥流重复使用, 一次性密码本却被复用, 每段密文是 hex 串且长度相同, 密文异或后出现空格样子的规律字节, 源码里 key 只生成一次, 密文里能猜出 flag 格式开头, 有 CTR 模式同一 nonce 加密多条消息]
difficulty: medium
source: "CTF-Wiki 流密码 / Cryptopals Set 1"
tools: [python, pwntools, CyberChef]
updated: 2026-10-22
---

## 一、识别信号（题面长什么样）

- 给了**多段**密文，长度都接近，且每段都是 hex / base64 编码的字节串。
- 题目明说「key 只生成一次」「我们复用了同一个 OTP」「nonce 固定」。
- 把两段密文异或后，大量字节落在 `0x41-0x5A` / `0x20` / 小写区间，像「明文异或」而不是随机。
- 源码：`key = os.urandom(len(flag))` 只执行一次，循环里对多条 message 做 XOR。
- 某个位置用空格 `0x20` 试异或后，得到的是字母（说明该位置原文是空格）。
- 是 CTR 模式，且所有消息用同一个 `nonce`/`counter`——等价于 Many-Time-Pad。
- 明文是英文句子 / flag 列表 / 带引号的 JSON（有大量可猜的固定字符）。

## 二、原理

```
c_i = m_i XOR k        （k 固定，长度 >= 最长明文）
c_i XOR c_j = m_i XOR m_j
```

**密钥在异或里被消掉**，剩下的只有明文之间的关系。`m_i XOR m_j` 的性质：

1. 两个 ASCII 字母异或，结果通常 < 0x20（全落在小写区间）；两个字母若有一个是大写、一个是小写，会翻转 `0x20` 位。
2. **明文是空格 `0x20` 时**：`0x20 XOR 字母` = 字母大小写翻转的那一位，结果**仍是字母**。所以「`c_i XOR c_j` 在某位置是字母」强烈提示该位置有一方的原文是空格。
3. **flag 格式**：`flag{`、`}`、`\n`、`"`、`'` 这些固定字符可以当 crib 直接拖到任意一段上，得到该段的密钥片段，再解其它段。
4. **统计法（无 crib 时）**：逐位置统计所有两两异或结果，选出「最像空格」的位置，逐步恢复；或按「字母 vs 非字母」打分做贪心。
5. **CTR 复用**：`c_i = m_i XOR E(nonce||ctr)`，密钥流固定，与 OTP 完全等价，攻击方法一模一样。

## 三、解题步骤

1. 解 hex/base64，得到 `n` 段字节串；确认长度一致（或补齐到相等）。
2. 先做**两两异或表**，肉眼扫有没有大量可读字符——有就直接进入 crib 拖拽。
3. 选一个 crib（`flag{`、`The `、`"`、`,'` 等），在每一段的所有偏移上试，命中标准是「该段位置出现可打印字符」。
4. 用命中段推出密钥流片段，解其它段；解出的明文里继续找新 crib，递归。
5. 全解后拼出 key 或 flag，注意大小写与非字母字符。

## 四、可直接运行的脚本

```python
# Many-Time-Pad 的 crib 拖拽（自动 + 交互两种用法）
import itertools, string

PRINTABLE = set(bytes(string.printable, "ascii"))

def xor_bytes(a, b):
    return bytes(x ^ y for x, y in zip(a, b))

def xor_table(cts):
    """打印所有两两异或的可读率，辅助肉眼判断。"""
    for i, j in itertools.combinations(range(len(cts)), 2):
        x = xor_bytes(cts[i], cts[j])
        ratio = sum(b in PRINTABLE for b in x) / max(1, len(x))
        yield i, j, ratio, x

def crib_drag(cts, crib, min_printable=0.8):
    """在每段密文的每个偏移上尝试 crib；命中则返回 (段号, 偏移, 恢复的密钥片段)。"""
    crib = crib if isinstance(crib, bytes) else crib.encode()
    hits = []
    for idx, c in enumerate(cts):
        for off in range(0, len(c) - len(crib) + 1):
            key_part = xor_bytes(c[off:off + len(crib)], crib)
            # 用该密钥片段去解其它段，看是否大多可打印
            ok = 0
            total = 0
            for other in cts:
                if len(other) >= off + len(crib):
                    seg = xor_bytes(other[off:off + len(crib)], key_part)
                    total += len(seg)
                    ok += sum(b in PRINTABLE for b in seg)
            if total and ok / total >= min_printable:
                hits.append((idx, off, key_part))
    return hits

def recover_key_stream(cts, known):
    """known: [(offset, bytes)] 已知密钥流片段；返回 bytearray 形式的 key。"""
    L = max(len(c) for c in cts)
    key = bytearray(b"\x00" * L)
    mask = bytearray(b"\x00" * L)
    for off, part in known:
        for i, b in enumerate(part):
            key[off + i] = b
            mask[off + i] = 1
    return key, mask

if __name__ == "__main__":
    # 构造 5 条明文，共用一个 60 字节 key
    import os
    key = bytes(range(0x41, 0x41 + 60))
    msgs = [
        b"the quick brown fox jumps over the lazy dog and runs",
        b"flag{otp_is_only_pad_once_and_never_more_than_once_hy}",
        b"never reuse a one time pad because it becomes plain xor",
        b"attack at dawn with the second battalion near the ridge",
        b"cryptography is fun when the nonce is not random at all!",
    ]
    cts = [xor_bytes(m, key) for m in msgs]
    print("可读率矩阵:")
    for i, j, r, _ in xor_table(cts):
        if r > 0.6:
            print("  ", i, j, round(r, 3))

    hits = crib_drag(cts, "flag{")
    # 注意：命中会很多（任意偏移都可能凑出可打印字符），要靠人工/后续验证挑出真正的
    good = [h for h in hits if h[0] == 1 and h[1] == 0]
    print("crib 'flag{' 总命中:", len(hits), "| 第 1 段偏移 0 的命中:", good[:1])
    assert good, "应在第 1 段开头命中"
    idx, off, kp = good[0]
    key2, mask = recover_key_stream(cts, [(off, kp)])
    dec1 = xor_bytes(cts[1][off:off + len(kp)], kp)
    dec0 = xor_bytes(cts[0][off:off + len(kp)], kp)
    print("第 1 段:", dec1, "| 第 0 段同位置:", dec0)
    assert dec1.startswith(b"flag{") and dec0.startswith(b"the ")
```

带「空格统计」的自动恢复（无 crib 时的常用套路）：

```python
def best_space_positions(cts):
    """对每个位置，统计所有两两异或结果是否落在『字母』区间；
    空格 XOR 字母 == 大小写翻转的字母，因此该位置若出现最多『字母』，
    说明大概率有一方是空格。返回每个位置的 (命中数, 最可能的空格段, 该位置字节)。"""
    L = max(len(c) for c in cts)
    res = []
    for pos in range(L):
        cands = []
        for i, c in enumerate(cts):
            if pos >= len(c):
                continue
            hits = 0
            for j, d in enumerate(cts):
                if i == j or pos >= len(d):
                    continue
                x = c[pos] ^ d[pos]
                if (65 <= x <= 90) or (97 <= x <= 122):
                    hits += 1
            cands.append((hits, i, c[pos]))
        if cands:
            cands.sort(reverse=True)
            res.append(cands[0])
    return res

if __name__ == "__main__":
    key = bytes(range(0x41, 0x41 + 60))
    msgs = [
        b"the quick brown fox jumps over the lazy dog and runs",
        b"flag{otp_is_only_pad_once_and_never_more_than_once_hy}",
        b"never reuse a one time pad because it becomes plain xor",
        b"attack at dawn with the second battalion near the ridge",
        b"cryptography is fun when the nonce is not random at all!",
    ]
    cts = [bytes(m[i] ^ key[i] for i in range(len(m))) for m in msgs]
    guess = best_space_positions(cts)
    # 用「疑似空格」反推该段明文，验证前若干位置
    print("前 12 个位置的 (命中数, 段号, 该段明文):")
    for hits, seg, b in guess[:12]:
        print("  ", hits, seg, chr(b ^ 0x20) if (b ^ 0x20) in range(32, 127) else "?")
    # 位置 3 处第 0 段是空格（"the " 的尾空格），命中数应为最高（= 4，即与其余 4 段都构成字母）
    top_hits, top_seg, top_byte = guess[3]
    print("位置 3 最高命中:", top_hits, "段", top_seg, "推测明文:", chr(top_byte ^ 0x20))
    assert top_hits == 4, "其余 4 段该位置都是字母，空格应得满分"
    assert ord(" ") in msgs[top_seg][3:4], "被选中的段该位置确实应为空格"
    print("空格位置统计 OK")
```

## 五、常见坑 / 变体

- **长度不一致**：先把所有密文截到 `min(len)`，或按最长补 0（补 0 会污染异或结果，优先截断）。
- **key 长度小于明文长度**：key 会**循环使用**（类似 Vigenère），此时是「多密钥流」题，要按列分别统计，而不是当成严格 OTP。
- **明文含大量非 ASCII**：可读率判断失效，改用「字符频率」或直接 cryptanalysis 打分函数（英文四元组频率）。
- **CTR 的 counter 递增**：若每次加密的 nonce 固定但 counter 从头开始，则完全等价；若 counter 延续，则只有前缀重叠部分可攻击。
- **`crib` 大小写**：`flag{` 与 `FLAG{` 都要试；有的题目 flag 在 base64 里，可以先 base64 解码再拖拽。
- **多次命中**：同一 crib 在多个偏移命中时，用「解出其它段的可读率」排序，最高者最可信。
- **伪命中**：短 crib（3 字节以下）的误报率很高，用 ≥4 字节的 crib 或人工确认。

## 六、参考来源

- [CTF-Wiki 流密码总览](https://ctf-wiki.org/crypto/streamcipher/intro/)
- [CTF-Wiki RC4（流密码输入/输出特点）](https://ctf-wiki.org/crypto/streamcipher/special/rc4/)
- [Wikipedia: ChaCha20-Poly1305（nonce 复用危害）](https://en.wikipedia.org/wiki/ChaCha20-Poly1305)
