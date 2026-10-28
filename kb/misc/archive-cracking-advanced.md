---
title: 压缩包进阶（7z/RAR 口令破解、嵌套、头部损坏修复）
category: misc
tags: [archive, 7z, rar, hashcat, nested-zip, repair]
signals: [题目给了 7z 或 rar 并且打开就要密码, 压缩包里套压缩包一共套了五层以上, 密码提示是四位数字或者生日格式, rar 版本提示是 RAR5, 解压报头部损坏或者 crc 校验失败, zip 注释里面写着一串 base64, 文件名本身就是乱码或者全是十六进制, 文件里出现了 data 区但 binwalk 只认出了 zip]
difficulty: medium
source: "hashcat 文档（7-Zip 11600 / RAR5 13000）/ john jumbo 的 *2john 脚本 / CTF-Wiki 压缩包专题"
tools: [7z, unrar, hashcat, john, zip2john, rar2john, 7z2john, fcrackzip, bkcrack]
updated: 2026-10-22
exec_yaml: ok
---

## 一、识别信号（题面长什么样）

- 附件是 `.7z` / `.rar`，`7z l` 或 `unrar l` 显示条目带 `*`（加密标记）。
- `7z l` 输出里 **文件列表也需要密码**，说明是 header encryption（7z 的 `-mhe=on`）。
- 解出来是一个 zip，里面又是 tar.gz，再里面又是 base64 文本——**嵌套压缩**。
- 题目提示"密码是四位纯数字""密码和一个日期有关""密码就是文件名"。
- `binwalk -e` 报 `Data after RAR marker`、`Invalid RAR version`。
- zip 的 `unzip -l` 报 `End-of-central-directory signature not found` 但 `binwalk` 能扫到 `PK\x03\x04`。
- 压缩包注释（`7z l -slt` 输出里的 Comment 字段）里塞了提示。
- 文件名是 `4_1.zip`、`4_2.zip` 这种编号，或者文件名就是 `flag.txt.flag.txt.zip`。

## 二、原理

- **加密层级**：ZIP 传统加密是 ZipCrypto（弱，有已知明文攻击）；ZIP AES 与 7z、RAR5 都是基于**派生密钥 + HMAC/AES** 的强加密，只能暴力或字典。
- **命门在"能不能拿到可验证的 hash"**：hashcat 的 `11600 (7-Zip)`、`13000 (RAR5)`、`13600 (WinZip)` 都需要先由 `*2john` 类脚本从压缩包里抽出特定结构。**7z 的 header 加密包最容易提取**，因为文件清单本身被加密，hash 一定存在。
- **嵌套**：本质是"每一层解压后的产物又是一个文件"，可以完全脚本化递归。
- **头部损坏**：ZIP 的中央目录在文件**尾部**，头部的 local header 只决定数据偏移；删掉/损坏中央目录后仍可用 `binwalk -e` 或 `7z x -tzip` 暴力重扫。RAR 的标记块在头部，头两个字节被改就整体不可识别。
- **ZipCrypto 已知明文攻击**：已知压缩包内某文件明文（或可从同版本软件生成），可用 `bkcrack` 恢复密钥，无需口令。

## 三、操作步骤

1. **识别加密方式**：`7z l file.7z -slt | grep -i -E 'password|encrypted|method'`；`unrar l file.rar`；`zipinfo -v file.zip` 看 `compression method` 与 `encrypted` 标记。
2. **先试弱口令**：`rockyou.txt` + 题目提示的规则（4 位数字用 `-a 3 ?d?d?d?d`）。
3. **抽 hash 上 GPU**：`7z2john.pl file.7z > h.txt`（john jumbo）、`rar2john file.rar`、`zip2john file.zip`，再 `hashcat -m <mode> h.txt rockyou.txt`。
4. **嵌套用脚本递归**：自动识别类型 → 解压 → 再识别，直到没有已知压缩格式为止。
5. **头部损坏**：先 `xxd | head` 对比标准魔数；ZIP 用 `binwalk -e --dd='.*'`；RAR 试 `unrar r`（带修复）；7z 基本不可修（有 header CRC），优先从别处找回。
6. **注释/时间戳/文件名编码**：`zipinfo -z`、`7z l -slt`、文件名乱码用 `-mcp=936` 或 `unzip -O CP936`。

## 四、命令 / 脚本

```bash
# 基础探测
7z l -slt target.7z
unrar lt target.rar
zipinfo -v target.zip | head -40
zipinfo -z target.zip          # 只打印注释

# 抽 hash（john jumbo 自带脚本）
7z2john.pl target.7z > h7z.txt
rar2john target.rar > hrar.txt
zip2john target.zip > hzip.txt

# hashcat 破解（模式速查：zip 传统=17200/17210 更像 13600，7z=11600，RAR5=13000）
hashcat -m 11600 h7z.txt rockyou.txt -O
hashcat -m 13000 hrar.txt rockyou.txt -O
hashcat -m 17200 hzip.txt rockyou.txt -O
# 四位数字直接用 mask
hashcat -m 13000 hrar.txt -a 3 ?d?d?d?d -i

# john 路线
john --wordlist=rockyou.txt h7z.txt
john --show h7z.txt

# ZipCrypto 已知明文攻击（无需口令）
bkcrack -C target.zip -c known.txt -p known_plain.txt
bkcrack -C target.zip -c known.txt -k <key1> <key2> <key3> -U out.zip newpass
```

```python
#!/usr/bin/env python3
# 嵌套压缩包递归解包（不支持加密，遇到加密就停下并提示）
import subprocess, shutil, os, sys, pathlib

MAGIC = {
    b'PK\x03\x04': 'zip', b'7z\xbc\xaf\x27\x1c': '7z',
    b'Rar!\x1a\x07': 'rar', b'\x1f\x8b': 'gzip',
    b'BZh': 'bzip2', b'\xfd7zXZ': 'xz',
    b'ustar': 'tar', b'!<arch>': 'ar',
}

def sniff(p):
    h = open(p, 'rb').read(8)
    for m, t in MAGIC.items():
        if h.startswith(m) or (t == 'tar' and h[257:262] == b'ustar'):
            return t
    return None

def run(cmd):
    r = subprocess.run(cmd, capture_output=True, text=True)
    return r.returncode, r.stdout + r.stderr

def extract(p, outdir):
    t = sniff(p); os.makedirs(outdir, exist_ok=True)
    if t in ('zip', '7z', 'rar', 'gzip', 'bzip2', 'xz'):
        rc, log = run(['7z', 'x', '-y', '-o' + outdir, p] if t != 'rar' else ['unrar', 'x', '-o+', p, outdir + '/'])
    elif t == 'tar':
        rc, log = run(['tar', '-xf', p, '-C', outdir])
    else:
        return [], 'unknown'
    return ([str(x) for x in pathlib.Path(outdir).iterdir()], log)

def deep(p, depth=0, maxdepth=8):
    indent = '  ' * depth
    t = sniff(p)
    print('%s[%d] %s (%s)' % (indent, depth, os.path.basename(p), t or 'file'))
    if not t or depth >= maxdepth:
        return
    outdir = p + '_d'
    files, log = extract(p, outdir)
    if not files and 'password' in log.lower():
        print(indent + '  !! 需要口令，请先破解: ' + os.path.basename(p))
        return
    for f in files:
        if os.path.isfile(f):
            deep(f, depth + 1, maxdepth)

if __name__ == '__main__':
    deep(sys.argv[1])
```

```bash
# 头部损坏的 zip：找所有 PK 标志并导出
grep -abo $'\x50\x4b\x03\x04' broken.zip
binwalk -e broken.zip
foremost -T -i broken.zip -o out
# RAR 修复模式
unrar r broken.rar
```

## 五、常见坑 / 变体

- **7z header 加密 vs 内容加密**：只有 `-mhe=on` 的包能稳定抽 hash；仅内容加密的包要先拿到文件名列表，hash 抽取失败的几率更高。
- **hashcat 模式记混**：`17200` 是 ZipCrypto、`13600` 是 WinZip AES、区别于 `11600`(7z) / `13000`(RAR5)。用错模式不会报错，只是永远解不出来。
- **rar2john 需要原始 RAR 的前 2KB 以上**，被截断的包抽 hash 必定失败。
- **嵌套递归死循环**：某些包解压后名字与父包相同（`a.zip` 解出 `a.zip`），脚本要记录已见哈希并限深度。
- **文件名编码**：Windows 打包的中文名在 Linux 下乱码，用 `unzip -O CP936` 或 `7z x -mcp=936`；也常有人**把提示写在文件名里**。
- **注释藏 flag**：`zipinfo -z` 和 `7z l -slt` 都能看到注释；RAR 的注释在 header 里，`unrar l` 会显示。
- **伪加密 zip**：修改中央目录的 encryption bit 制造"需要密码"假象，用 `zip -FF` 或十六进制把 `09 00` 改回 `00 00` 即可。
- **bkcrack 前提**：必须知道某个条目的明文 ≥12 字节，且该条目用 ZipCrypto 而非 AES。

## 六、参考来源

- [hashcat 官方站点与示例哈希模式总表](https://hashcat.net/hashcat/)
- [hashcat 论坛：7z / RAR 破解实际操作讨论](https://hashcat.net/forum/thread-11810.html)
- [在线压缩包 hash 抽取工具说明（ZIP/RAR/7z 提取流程）](https://www.onlinehashcrack.com/tools-zip-rar-7z-archive-hash-extractor.php)
- [binwalk 官方仓库](https://github.com/ReFirmLabs/binwalk)
- [CTF-Wiki：Misc 压缩包相关技巧](https://ctf-wiki.org/misc/introduction/)
