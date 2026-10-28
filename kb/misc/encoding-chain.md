---
title: 编码套娃（base64/base32/base85/URL/Hex/XXencode）
category: misc
tags: [编码, base64, base32, base85, xxencode, uuencode]
signals: [给了一长串字符, 结尾有等号, 字符串只有大小写字母和数字, 满屏百分号, 文本里出现 \\x or \\u, 解码后还是编码, 题目叫 套娃/摩斯/多层]
difficulty: easy
source: "CTF-Wiki 编码分析章节 / CyberChef Magic / RFC 4648"
tools: [CyberChef, python, base64, xxd, dencode, dcode]
updated: 2026-10-22
differs_from: [misc/encoding-auto-detect.md]
---

## 一、识别信号（题面长什么样）

- 附件 `flag.txt`，内容只有一行 `ZmxhZ3t...==` 之类。
- 字符串结尾带 `=` 或 `==`，长度是 4 的倍数 → base64。
- 只有 `A-Z`、`2-7` 和等号 → base32；只有 `0-9A-V` → base32hex。
- 满屏 `%7B`、`%25` → URL 编码。
- 文本里出现 `\x89PNG`、`\u4f60` → 字符串转义。
- 解码一次又是另一串编码——题名常叫「套娃」「千层饼」「层层深入」。

## 二、原理

编码是**无损可逆**的映射，不提供任何保密性，CTF 里用来制造"看不出是什么"的错觉。每个编码都有**字母表和长度特征**，可以先肉眼分辨：

| 编码 | 字符集特征 | 长度规则 | 典型前缀/后缀 |
| --- | --- | --- | --- |
| Base16/Hex | `0-9A-F` 偶数长 | 2 倍膨胀 | |
| Base32 | `A-Z2-7` + `=` | 8 的倍数 | 补 `=`×6 |
| Base32hex | `0-9A-V` | 8 的倍数 | |
| Base58 | 去掉 `0OIl` 的字母数字 | 无 | 比特币地址 |
| Base62 | `0-9A-Za-z` | 无 | |
| Base64 | `A-Za-z0-9+/` + `=` | 4 的倍数 | `==` |
| Base64url | 用 `-_` 替代 `+/` | 4 的倍数 | JWT |
| Base85 (ASCII85) | 从 `<~` 开始、`~>` 结束，含标点 | 5 的倍数 | `<~ ~>` |
| Base85 (Z85/AD85) | 可打印字符集 | 5 的倍数 | |
| Base91 | 90 个可打印字符 | 无 | |
| XXencode | 字母数字加 `+-`，字母小到大重排 | 60 字符/行 | 以 `+`/`-` 结尾 |
| UUencode | 首行 `begin 644` | 每行首字母=长度 | `begin/end` |
| Quoted-Printable | 大量 `=XX` 且 `=` 后跟大写 | 行尾 `=` 续行 | |
| URL 编码 | `%XX` | | |
| 摩斯 | `.` `-` `/` 空格 | | |

## 三、操作步骤

1. **观察字符集**，先按上表猜一次，用 Python/CyberChef 试。
2. **自动嗅探**：CyberChef 的 `Magic` 操作会并行尝试几十种编码并给出置信度。
3. **写循环**：明明还在"乱码"说明还有一层，把解码逻辑写成 `while` 循环，直到出现 `flag{`。
4. **注意二进制**：解码结果 `file` 一下，可能直接是图片/压缩包。
5. **别搞错 base64 变种**：`-_` 是 url-safe，需要先转 `+/`。

## 四、命令/脚本

### 单步解码

```bash
echo 'ZmxhZ3t0ZXN0fQ==' | base64 -d
echo 'MZWGCZ33NBSW4Y3EMFXGK===' | base32 -d
echo 'uff!}`s' | base85 -d 2>/dev/null || printf '%s' 'BOu!rDZ' | python -c "import sys,base64;print(base64.a85decode(sys.stdin.buffer.read()))"
python -c "import urllib.parse,sys;print(urllib.parse.unquote(sys.argv[1]))" '%7B%22a%22%3A1%7D'
xxd -r -p hex.txt        # hex -> bin
printf '%b' '\x66\x6c\x61\x67'   # 转义串还原
```

### 通用套娃解码器（Python）

```python
#!/usr/bin/env python3
# decode_chain.py —— 自动识别常见编码并循环解码，直到看到 flag
import base64, binascii, re, sys, urllib.parse, codecs

def try_each(s: str):
    cands = []
    s2 = s.strip()
    for name, fn in [
        ('url', lambda x: urllib.parse.unquote(x)),
        ('hex', lambda x: bytes.fromhex(x).decode('latin1')),
        ('base64', lambda x: base64.b64decode(x + '=' * (-len(x) % 4)).decode('latin1')),
        ('b64url', lambda x: base64.urlsafe_b64decode(
            x.replace('-', '+').replace('_', '/') + '=' * (-len(x) % 4)).decode('latin1')),
        ('base32', lambda x: base64.b32decode(x + '=' * (-len(x) % 8)).decode('latin1')),
        ('b32hex', lambda x: base64.b32hexdecode(x + '=' * (-len(x) % 8)).decode('latin1')),
        ('base85', lambda x: base64.b85decode(x).decode('latin1')),
        ('a85', lambda x: base64.a85decode(x.encode()).decode('latin1')),
        ('rot13', lambda x: codecs.decode(x, 'rot13')),
    ]:
        try:
            out = fn(s2)
        except Exception:
            continue
        if out and out != s2 and all(9 <= ord(c) < 127 for c in out):
            cands.append((name, out))
    return cands

s = open(sys.argv[1]).read() if len(sys.argv) > 1 else sys.stdin.read()
for depth in range(12):
    hits = try_each(s)
    if not hits:
        print('[!] 无法继续，当前内容：'); print(s[:300]); break
    name, s = hits[0]
    print(f'[{depth}] {name:8s} -> {s[:120]!r}')
    if re.search(r'flag\{|ctf\{', s, re.I):
        print('[+] FLAG:', re.search(r'.{0,10}flag\{.*?\}.{0,10}', s, re.I | re.S).group(0))
        break
```

```bash
python decode_chain.py cipher.txt
```

### XXencode / UUencode / Quoted-Printable

```bash
# XXencode：可用 pip install xxencode 或在线 dencode.com
pip install xxencode base91 pybase62
python -c "import xxencode,sys;print(xxencode.xxdecode(open('enc.txt').read().strip()))"
# UUencode
uudecode -o out.bin enc.uu      # 或 python -c "import uu,uu_codec..."（py3 用 binascii.a2b_uu）
# Quoted-Printable
python -c "import quopri,sys;print(quopri.decodestring(open('enc.txt','rb').read()).decode('utf8','replace'))"
# Base91
python -c "import base91;print(base91.decode(open('enc.txt').read().strip()))"
```

### CyberChef 流水线（可直接在网页里保存）

```
From Base64 -> From Base64 -> From Base32 -> URL Decode -> Detect File Type
# 快捷键：Magic 面板勾选 "Intensive mode"，把 3-4 层一次性叠出来
```

## 五、常见坑 / 变体

- **Base64 里的换行/空格**：先 `tr -d '\n\r '`，否则 `b64decode` 报错。
- **URL-safe 与标准混用**：`-` `_` 要先换成 `+` `/`。
- **Base64 索引表被改**：题目自定义字母表（如把 `A-Za-z0-9+/` 乱序），先找字母表再 `bytes.translate`。可用 `base64.b64decode(s, altchars=...)` 或手写映射。
- **多层 base64 中间夹 hex**：循环解码器会自动过，但注意"看起来像 hex 也可能是密文"。
- **摩斯/培根/零宽**：先看分隔符（`/`、空格、`0/1`），零宽字符要先 stats 出 `U+200B/200C/200D`。
- **二维码/图片的 base64**：`iVBORw0KGgo` 开头是 PNG，直接写文件。
- **编码后的二进制**：解码结果 `file` 一下，是 `PK` 就解压，是 `\x89PNG` 就存成图片。

## 六、参考来源

- [CTF Wiki - 编码分析（计算机相关编码）](https://ctf-wiki.org/misc/encode/computer/)
- [CTF Wiki - 通信领域常用编码](https://ctf-wiki.org/misc/encode/communication/)
- [GNU coreutils base64 手册](https://www.gnu.org/software/coreutils/manual/html_node/base64-invocation.html)
- [RFC 4648 - Base16/32/64 规范](https://datatracker.ietf.org/doc/html/rfc4648)
- [CyberChef - 编码解码利器](https://gchq.github.io/CyberChef/)
- [dencode.com - 在线编码对照](https://dencode.com/)
