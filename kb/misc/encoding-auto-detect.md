---
title: 编码自动识别（写一个多层编码侦探脚本）
category: misc
tags: [encoding-detect, automation, base, magic, entropy, script]
signals: [题目给了一段看不出是什么编码的字符串, 密文解一层后还是乱码需要继续解, 字符串里混了 base64 和 rot13 和 hex 三层, 题目一串字段给出来看着像密文但没有明确提示, 给的是一个 .txt 里面每一行都是不同编码, 解出来的结果末尾还有等号或者下划线]
difficulty: hard
source: "Python 标准库 base64/codecs / CyberChef Magic 操作 / 经验型识别规则"
tools: [python, cyberchef, ciphey, chardet]
updated: 2026-10-22
exec_yaml: ok
---

## 一、识别信号（题面长什么样）

- 附件只有一串文本，题面没有任何"这是 xx 编码"的提示。
- 解一层 base64 得到 `Vm0wd2Qy...` 又像 base64，套娃层数未知。
- 一行里混着 base64 尾部的 `=`、URL 安全的 `-_`、十六进制字符。
- 每行长度不等，且各自看起来像不同的编码（一行 base32，一行 rot13）。
- 解出来的结果里有 `flag{` 的碎片，说明方向对但只解了一半。
- 题目分值是 misc 里偏高的，且 hint 说"注意多层"。

## 二、原理

**自动识别的本质是"给每一种编码打一个可信度分数，取最高者解一层，循环直到出现明文"。**

几个可靠的判据：

| 编码 | 判据 | 误判风险 |
| --- | --- | --- |
| Base64 | 字符集 `A-Za-z0-9+/`，长度 %4==0（或补 `=`） | 误把普通英文单词判成 b64 |
| Base32 | 仅 `A-Z2-7`，长度 %8==0 | 短串 |
| Base16/hex | 仅 `0-9a-fA-F`，偶数长度 | 短串 |
| URL 编码 | 含 `%XX` | 低 |
| HTML 实体 | 含 `&#\d+;` 或 `&[a-z]+;` | 低 |
| rot13 | 解后英文词频提升 | 中 |
| rot47 | 全可打印且解后词频提升 | 中 |
| 摩斯 | 只有 `.- / ` | 低 |
| 二进制 | 只有 `01` 且长度 %8==0 | 中 |
| Unicode 转义 | 含 `\uXXXX` / `\xXX` | 低 |

**关键在"解得对不对"**：解一层后看**可打印比例**与**常见子串**（`flag`、`ctf`、`{`）是否上升。这比单纯规则匹配稳得多。

## 三、操作步骤

1. **归一化输入**：去空白、去 BOM、断言是 ASCII。
2. **规则打分**：按上表给候选列表。
3. **逐个尝试 + 评估**：每解出一层，计算"可打印率"和"词表命中"，只有分数上升才接受。
4. **BFS/DFS 搜索**：把解码过程看成一棵树，用优先队列按分数扩展，命中 `flag{` 就停。
5. **记录路径**：输出每一层的编码类型，方便写 WP。
6. **兜底**：交给 CyberChef 的 Magic 或 ciphey 再做一遍交叉验证。

## 四、命令 / 脚本

```bash
pip install ciphey chardet          # ciphey 需要较新的 python
ciphey -t "Vm0wd2QyUXlVWGxW..."
cyberchef 的 Magic 操作在线跑：https://gchq.github.io/CyberChef/
```

```python
#!/usr/bin/env python3
"""多层编码自动侦探：BFS + 可信度评分"""
import base64, binascii, codecs, html, heapq, re, string, sys

PRINTABLE = set(string.printable)
HINTS = [b'flag{', b'flag', b'{', b'ctf', b'CTF', b'key', b'pass']
ENC = 'ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789+/='

def score(b: bytes) -> float:
    if not b:
        return -100
    pr = sum(chr(c) in PRINTABLE for c in b) / len(b)
    s = pr * 2
    low = b.lower()
    for h in HINTS:
        if h in low:
            s += 3
    # 英文词占比的粗估
    words = re.findall(rb'[A-Za-z]{3,}', b)
    s += min(len(words) / 8.0, 1.0)
    return s

def rot(n):
    def f(b):
        out = bytearray()
        for c in b:
            if 65 <= c <= 90:
                out.append((c - 65 + n) % 26 + 65)
            elif 97 <= c <= 122:
                out.append((c - 97 + n) % 26 + 97)
            else:
                out.append(c)
        return bytes(out)
    return f

def rot47(b):
    return bytes(33 + (c - 33 + 47) % 94 if 33 <= c <= 126 else c for c in b)

def b64fix(s: bytes) -> bytes:
    t = s.strip().replace(b'-', b'+').replace(b'_', b'/')
    t += b'=' * (-len(t) % 4)
    return base64.b64decode(t, validate=False)

DECODERS = {
    'base64':       lambda b: b64fix(b) if all(chr(c) in ENC for c in b.strip()) else None,
    'base32':       lambda b: base64.b32decode(b.strip().upper() + b'=' * (-len(b.strip()) % 8)) if set(b.strip().upper()) <= set(b'ABCDEFGHIJKLMNOPQRSTUVWXYZ234567=') else None,
    'base16':       lambda b: bytes.fromhex(b.strip().decode()) if re.fullmatch(rb'[0-9a-fA-F\s]+', b) and len(re.sub(rb'\s', b'', b)) % 2 == 0 else None,
    'url':          lambda b: bytes.fromhex('') if b'%' not in b else __import__('urllib.parse', fromlist=['unquote_to_bytes']).unquote_to_bytes(b),
    'html':         lambda b: html.unescape(b.decode('utf-8', 'replace')).encode() if b'&' in b else None,
    'rot13':        lambda b: codecs.encode(b.decode('latin1'), 'rot13').encode('latin1'),
    'rot47':        rot47,
    'binary':       lambda b: bytes(int(b[i:i+8], 2) for i in range(0, len(b.strip()) // 8 * 8, 8)) if re.fullmatch(rb'[01\s]+', b) and len(re.sub(rb'\s', b'', b)) % 8 == 0 else None,
    'unicode_esc':  lambda b: b.decode('unicode_escape').encode('latin1', 'ignore') if b'\\u' in b or b'\\x' in b else None,
    'utf16':        lambda b: b.decode('utf-16-le').encode('utf-8') if b.count(0) > len(b) // 4 else None,
}

def search(data: bytes, max_depth=8, verbose=True):
    seen, heap = {data}, []
    heapq.heappush(heap, (-score(data), 0, data, []))
    while heap:
        neg, depth, cur, path = heapq.heappop(heap)
        if depth >= max_depth:
            continue
        for name, fn in DECODERS.items():
            try:
                out = fn(cur)
            except Exception:
                continue
            if not out or out in seen or len(out) > 4 * max(len(cur), 1):
                continue
            seen.add(out)
            sc, np_ = score(out), path + [name]
            if verbose:
                print('%-5d %-12s %s | %r' % (depth + 1, name, ' -> '.join(np_), out[:60]))
            if b'flag{' in out.lower():
                print('\n[+] FOUND:', out.decode('latin1', 'replace'))
                return np_, out
            heapq.heappush(heap, (-sc, depth + 1, out, np_))
    return None, None

if __name__ == '__main__':
    data = open(sys.argv[1], 'rb').read().strip()
    search(data)
```

```bash
# 批量：每行独立解
python - <<'EOF'
import subprocess, sys
for i, line in enumerate(open('lines.txt', encoding='latin1')):
    open('/tmp/l.txt', 'wb').write(line.encode('latin1'))
    r = subprocess.run([sys.executable, 'detect.py', '/tmp/l.txt'], capture_output=True, text=True)
    print(i, r.stdout.strip().splitlines()[-1] if r.stdout.strip() else 'FAIL')
EOF
```

## 五、常见坑 / 变体

- **base64 的"宽容解码"陷阱**：`base64.b64decode(validate=False)` 会静默丢弃非法字符，导致把普通文本"解"成垃圾。判分必须看解出来的东西是否更像人话。
- **打分函数决定成败**：光看可打印率会把所有 base64 都判为高分（b64 输出常也是可打印）。必须加"词表命中 / `flag{` / JSON 结构"这类语义信号。
- **搜索爆炸**：层数一多，组合数量指数增长；必须限制 `max_depth`、总尝试数、以及"输出长度不得超过输入 ×4"。
- **UTF-16 误判**：随机二进制里零字节很多，会被误当 UTF-16；要求零字节位置呈规律（奇数位或偶数位）。
- **rot13 与 EBCDIC 一样是"自逆/群"**：跑两遍会回到起点，BFS 里要 `seen` 去重。
- **多层里混入 AES/RSA**：那是 `encoding-chain` 之外的密码，静态识别无法解，需题目 hint。
- **工具类推荐**：CyberChef 的 Magic 操作、`ciphey`、`pograms/ciphey` 的替代品 `pywhat`。

## 六、参考来源

- [CyberChef 官方在线工具（Magic 操作自动识别）](https://gchq.github.io/CyberChef/)
- [Python 标准库 base64 / codecs 文档](https://docs.python.org/3/library/base64.html)
- [HTML 实体转义（html.unescape）标准](https://html.spec.whatwg.org/multipage/parsing.html#named-character-references)
- [ciphey：自动解码工具的算法思路说明](https://github.com/bee-san/ciphey)
- [CTF-Wiki：Misc 编码链与识别](https://ctf-wiki.org/misc/introduction/)
