---
title: 冷门编码家族（UTF-7/16、EBCDIC、rot47、base91/92、QP、Punycode）
category: misc
tags: [encoding, utf7, ebcdic, base92, punycode, rot47]
signals: [密文里出现大量反斜杠加号开头的片段, hex 里每隔一个字节是 00 或者 0x00 后置, 字符集里有 + - * / 和大量标点但读不出单词, 编码结果里有大量的等号后面跟两个十六进制, 字符串以 xn-- 开头, 字母都是异或了 0x20 之后的 ARET, 给出的十六进制高位是 0x4B 0x4C 这种 0xC0 以上区间的值, 提示说这不是 ASCII]
difficulty: medium
source: "RFC 3492 Punycode / RFC 2045 Quoted-Printable / RFC 2152 UTF-7 / IBM CP037 编码表 / base92 官方仓库"
tools: [python, cyberchef, iconv, dcode, xxd]
updated: 2026-10-22
exec_yaml: ok
---

## 一、识别信号（题面长什么样）

- 密文里 `+` 后面跟着 2~4 个可打印字符，然后又是 `-`，比如 `+AGEAYgBj-`——典型 **UTF-7 修改版 Base64**。
- 十六进制 dump 里每个字符后面都跟 `00`（`66 00 6c 00 61 00 67`）——**UTF-16LE**；反之前置 `00 xx` 是 UTF-16BE。
- 十六进制落在 `0x81~0xA9`、`0xC1~0xE9` 这类区间，像乱码又不是随机——**EBCDIC（CP037）**。
- 明文只由 `!` 到 `~` 的 ASCII 组成但每个字节都是"可打印字符 XOR 0x20"的味道——**ROT47**。
- 密文含 `"`、`'`、`\`、`-`、`_` 等标点且比 Base64 更短——可能是 **base91**；出现了 `~` 单独作为分隔/空串——可能是 **base92**。
- HTML 邮件源码里出现 `=E4=BD=A0=` 这种"等号 + 两个大写十六进制"——**Quoted-Printable**。
- 字符串以 `xn--` 开头，后接 `a-zA-Z0-9-`——**Punycode**。
- 题目提示"这不是标准编码""老古董的东西"。

## 二、原理

- **UTF-7（RFC 2152）**：直接可打印 ASCII 原样输出，非 ASCII 段用 `+` 开头、Base64（去掉 `=`，字母表与标准一致）编码、`-` 结尾；`+-` 表示字面量 `+`。CTF 常把它当"看起来像乱码的 base64"。
- **UTF-16**：每字符 2 字节（BMP），代理对处理非 BMP。识别关键就是**零字节的规律分布**。
- **EBCDIC**：IBM 大型机字符集，字母**不是连续的**（`I`/`J` 之间有空洞），`A=0xC1`、`a=0x81`、`0=0xF0`、空格 `0x40`。用 `iconv -f CP037` 转。
- **ROT47**：对 33~126 范围内每个字符做 `c < 33+47 ? c+47 : c-47`，等价于 `(ord(c)-33+47)%94+33`。它与大小写无关地打乱字母，结果仍是可见 ASCII。
- **base91**：把 13 bit 一组映射到 91 字符表，压缩率约 1.23（比 b64 的 1.33 好）。**base92** 在 91 字符表之外额外允许 `~` 表示空串/结尾，且分组为 13 bit→2 字符再加 6 bit 处理，注意**是 91 个有效符号而不是 92**。
- **Quoted-Printable**：`=` 后跟两个十六进制表示不可打印字节；行尾单个 `=` 表示软换行（解码时删除）。
- **Punycode（RFC 3492）**：IDN 的 Bootstring 编码，把 Unicode 标签转成 `xn--` 加 ASCII，用 delta 与可变长整数表示码位。

## 三、操作步骤

1. **先量化字符分布**：`python -c` 统计字符集大小、是否全可打印、零字节位置。零字节规律 → UTF-16；全可打印 → rot47/baseXX；含 `=` + hex → QP。
2. **UTF-7/16 直接解码**：Python 内置 `'utf-7'`、`'utf-16-le'` 编解码器就够，注意 UTF-7 解码器对不完整序列会抛错，可用 `errors='replace'` 先看轮廓。
3. **EBCDIC**：`iconv -f CP037 -t UTF-8`，若 CP037 不对就依次试 CP500/CP1047。
4. **rot47**：一次即可（47*2=94 是自逆），解出后再看是否有二次编码。
5. **base91/92**：装 `pybase91`、`base92` 包，或直接用 dcode 在线解。
6. **QP**：`python -c "import quopri,sys;print(quopri.decodestring(open('in.txt','rb').read()))"`。
7. **Punycode**：`s.encode('ascii').decode('punycode')`（去掉 `xn--` 前缀）。
8. **串联验证**：每一层解出后打印前 64 字符，人工判断下一层是什么。

## 四、命令 / 脚本

```bash
# 快速试探：把常见冷门编码一次跑完
python - <<'EOF'
import codecs, quopri
s = open('cipher.txt', 'rb').read().strip()
for name in ('utf-7', 'utf-16-le', 'utf-16-be', 'cp037', 'cp500', 'mbcs'):
    try:
        print(name, '->', s.decode(name)[:80])
    except Exception as e:
        print(name, 'FAIL', type(e).__name__)
print('qp ->', quopri.decodestring(s)[:80])
EOF

# EBCDIC 用 iconv（更稳）
iconv -f CP037 -t UTF-8 in.bin | head
iconv -f CP1047 -t UTF-8 in.bin | head

# Punycode / IDN
python -c "print('xn--fiqs8s'.encode().decode('punycode'))"
```

```python
#!/usr/bin/env python3
# 一次性批量尝试：rot47 / base91 / base92 / punycode / utf7
import codecs

def rot47(s):
    return ''.join(chr(33 + (ord(c) - 33 + 47) % 94) if 33 <= ord(c) <= 126 else c
                   for c in s)

def try_all(data: bytes):
    txt = data.decode('latin1')
    out = {}
    out['rot47'] = rot47(txt)
    # UTF-7
    try:
        out['utf7'] = txt.encode('latin1').decode('utf-7')
    except Exception as e:
        out['utf7'] = '<%s>' % type(e).__name__
    # punycode（去前缀）
    for pref in ('xn--', ''):
        if txt.startswith(pref):
            try:
                out['punycode'] = txt[len(pref):].encode().decode('punycode')
                break
            except Exception:
                pass
    # base91
    try:
        import base91 as b91
        out['base91'] = b91.decode(txt)
    except Exception:
        pass
    # base92
    try:
        import base92 as b92
        out['base92'] = b92.decode(txt).decode('latin1', 'replace')
    except Exception:
        pass
    return out

if __name__ == '__main__':
    import sys
    for k, v in try_all(open(sys.argv[1], 'rb').read()).items():
        print('[%s] %r' % (k, v if isinstance(v, str) else v[:80]))
```

```bash
# 安装 aux 包
pip install pybase91 base92
```

## 五、常见坑 / 变体

- **UTF-7 的 `+` 容易被误判成 base64**：判断依据是 `+` 后跟的 Base64 段**不以 `=` 结尾**，且以 `-` 收尾。若整串都是 b64 则不是 UTF-7。
- **UTF-16 的 BOM**：`FF FE` 是 LE、`FE FF` 是 BE。若开头没有 BOM 就要靠零字节位置判断。
- **EBCDIC 的字母表不连续**：解码后出现 `¡¢£` 说明码页选错了（0xA1+ 是标点区），换 CP500/CP1047。
- **rot47 跑两遍回到原文**，所以"解出来还是垃圾"往往说明根本不是 rot47。
- **base92 的 `~`**：dcode 与 PyPI `base92` 包对尾部的处理略有差异，遇到解码失败先试 `base91` 或去掉末尾 `~`。
- **QP 的软换行**：直接 `=E4` 之外还有 `=\n`，用 `quopri.decodestring` 会自动处理；手动替换时漏掉会导致整串错位。
- **Punycode 不在开头**：`mailto:user@xn--fiqs8s.com` 这种要先用正则抓 `xn--[a-z0-9-]+`。
- **组合形态**：`rot47 -> base92 -> utf-16` 这类三层叠加在 2023 年后的比赛里很常见，务必逐层打印中间态。

## 六、参考来源

- [RFC 3492：Punycode（Bootstring 编码规范）](https://www.rfc-editor.org/info/rfc3492/)
- [RFC 2045：Quoted-Printable 定义](https://www.rfc-editor.org/info/rfc2045/)
- [RFC 2152：UTF-7（Unicode 的 7 位编码）](https://www.rfc-editor.org/rfc/rfc2152)
- [base92 官方实现（C/Python）](https://github.com/thenoviceoof/base92)
- [dcode：Base 92 编码规则说明（13bit 分组、91 个有效符号）](https://www.dcode.fr/base92-encoding)
- [EBCDIC CP037 转换工具（对照表）](https://atbashcipher.com/tools/ebcdic-converter)
