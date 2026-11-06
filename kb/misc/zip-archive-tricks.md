---
title: ZIP 压缩包技巧（伪加密/明文攻击/CRC 爆破）
category: misc
tags: [zip, 伪加密, 明文攻击, CRC32, bkcrack, fcrackzip]
signals: [给了一个加密压缩包, 解压要密码但题面没给, 同一个 readme 出现两份, 压缩包里有 4 字节小文件, Linux 下能直接解压, 7z 提示 CRC 错误, 压缩包注释里有奇怪字符串]
difficulty: medium
source: "CTF-Wiki ZIP 格式章节 / bkcrack 文档 / PKWARE APPNOTE / ZipCrypto 原理"
tools: [bkcrack, fcrackzip, pkcrack, zipinfo, john, 010editor, zipdetails]
updated: 2026-10-22
---

## 一、识别信号（题面长什么样）

- 附件 `challenge.zip`，解压提示「需要密码」，题面没有任何密码线索。
- 解压出来的目录里同时有 `readme.txt` 和 `Desktop.zip`，两边都有同名文件。
- 包里一堆 **4~6 字节**的 `*.txt` 小文件，数量很多——典型 CRC32 爆破题。
- 在 Kali/WSL 下 `unzip` 居然不需要密码就开了（伪加密）。
- `zipinfo -v` 显示 `General purpose bit flag: 0x0009`（bit 0 表示加密，bit 3 表示带数据描述符）。
- `unzip` 报 `bad CRC`，只说明读取出的内容与校验值不符；密码错误、数据损坏或格式读错都可能出现。
- 包注释里有 base64/hex，解出来是一段明文。

## 二、原理

ZIP 结构：`Local File Header (50 4B 03 04)` + 数据 + `Central Directory (50 4B 01 02)` + `EOCD (50 4B 05 06)`。

1. **伪加密**：条目设了加密位，但压缩数据实际是明文。用目录定位具体条目后，在副本上只清 bit 0，再尝试解压和校验。`09 00` 应变为 `08 00`，保留 bit 3。若副本校验失败，保留原包，继续查密码或压缩数据。
2. **用 CRC32 筛候选**：ZIP 通常记录未加密内容的 CRC32。若条目很短且字符范围已知，可以枚举候选并比较 CRC；可能有多个结果，用题目的其他线索继续筛。
3. **明文攻击（已知明文）**：ZipCrypto（传统加密）非常弱，只要知道**同一个文件至少 12 字节连续的明文**（且压缩算法一致），就能通过 Biham–Kocher 攻击恢复 3 个内部密钥，再用密钥解出整包。`bkcrack` 是现代实现，几分钟内完成。
4. **AES 加密（ZipCrypto 之外）**：只能爆破/字典，`zip2john + john` 转换后跑哈希。

## 三、操作步骤

1. **看结构**：`zipinfo -v target.zip`、`zipdetails target.zip`，先判断是「真加密」还是「伪加密」。
2. **试伪加密**：核对中央目录和本地文件头里的同一条目。只清两处的加密位，用 ZIP 读取器重读副本。不要在整个文件中搜到签名就改，压缩数据中也可能出现相同字节。
3. **小文件 → CRC 爆破**：读出中央目录里的 CRC32，枚举候选串。
4. **有已知明文 → bkcrack**：把已知文件用**相同压缩器和相同压缩级别**重新压成 zip，再 `bkcrack -C ... -c ... -p ... -P ...`。
5. **需要密码字典 → fcrackzip / john**：`zip2john target.zip > h.txt && john h.txt --wordlist=rockyou.txt`。
6. **解出后再继续迭代**：里面常是 base64 → 另一个压缩包 → 图片隐写。

## 四、命令/脚本

### 结构诊断

```bash
zipinfo -v target.zip | head -60        # 详细属性：加密方式、CRC、压缩方法
zipdetails target.zip                   # 逐字段解析（Perl 工具）
zip -FF target.zip --out repaired.zip   # 修复损坏的压缩包
7z l -slt target.zip                    # 列出 method / encrypted 字段
zipinfo -l target.zip                         # 列出实际目录条目
```

### 试验单个条目是否只是设了加密位

脚本用中央目录和本地头里的实际偏移修改同一个条目。副本解压且 CRC 通过才另存；普通条目不用改，真实加密应回原包找密码。Nothing to See 的密码线索就在外层图像里。

```python
import struct
import sys
from io import BytesIO
from pathlib import Path
from zipfile import ZipFile

source = Path(sys.argv[1])
name = sys.argv[2]
data = bytearray(source.read_bytes())
with ZipFile(BytesIO(data)) as z:
    central = z.start_dir
    for entry in z.infolist():
        assert data[central:central + 4] == b"PK\x01\x02"
        if entry.filename == name:
            local = entry.header_offset
            assert data[local:local + 4] == b"PK\x03\x04"
            if not entry.flag_bits & 1:
                raise SystemExit("这个条目没有设置加密位，不用修复。")
            for offset in (central + 8, local + 6):
                flag = struct.unpack_from("<H", data, offset)[0]
                struct.pack_into("<H", data, offset, flag & ~1)
            break
        sizes = struct.unpack_from("<HHH", data, central + 28)
        central += 46 + sum(sizes)
    else:
        raise SystemExit("找不到指定的条目。")
with ZipFile(BytesIO(data)) as z:
    z.read(name)  # 读取并核对 CRC
source.with_name(source.stem + "_fixed.zip").write_bytes(data)
```

### CRC32 撞库（已知 CRC 反推短明文）

```python
#!/usr/bin/env python3
# crc_crack.py —— 已知文件名+CRC，枚举 1~5 字节明文；也支持按字母表 4 字节全枚举
import binascii, itertools, struct, sys, zipfile, string

ALPHA = (string.printable[:95]).encode()          # 可见 ASCII
targets = []                                      # [(name, crc32)]
with zipfile.ZipFile(sys.argv[1]) as z:
    for info in z.infolist():
        targets.append((info.filename, info.CRC & 0xffffffff))

ALPHABET = sys.argv[3].encode() if len(sys.argv) > 3 else ALPHA
maxlen = int(sys.argv[2]) if len(sys.argv) > 2 else 5

table = {}
for name, crc in targets:
    for L in range(1, maxlen + 1):
        for tup in itertools.product(ALPHABET, repeat=L):
            s = bytes(tup)
            if binascii.crc32(s) & 0xffffffff == crc:
                table[name] = s
                print(f'[+] {name}: {s!r}')
                break
print('done, solved', len(table), '/', len(targets))
```

> 4 字节全字母表（62^4≈1.4e7）用纯 Python 约几分钟；5 字节建议用开源的 `ZipCrcCracker` / `crc-kracker`（C 实现，秒级）。

### 明文攻击（bkcrack）

```bash
# 1) 已知明文 plain.bin 与包内同名文件内容一致，且压缩方式一致
zip -0 known_plain.zip plain.bin            # store 模式；如果包里 deflate 就用 -9
bkcrack -C target.zip -c readme.txt -p plain.bin        # 直接给明文
bkcrack -C target.zip -c readme.txt -p plain.zip -P readme.txt   # 从已知 zip 里取
# 2) 恢复出内部密钥后解包
bkcrack -C target.zip -k KEYS -U decrypted.zip PASS   # 用已知 keys 重打包，PASS 可任意
unzip -o decrypted.zip
```

```bash
# 旧方案 pkcrack
pkcrack -C target.zip -c readme.txt -p plain.bin -d out.zip -a
```

### 密码字典 / 哈希

```bash
fcrackzip -u -D -p /usr/share/wordlists/rockyou.txt target.zip
zip2john target.zip > hash.txt && john hash.txt --wordlist=rockyou.txt
```

## 五、常见坑 / 变体

- **只改本地头不改中央目录**会失败：解析器读的是中央目录（EOCD 后的 `PK\x01\x02` 段）。
- **压缩算法必须一致**：出题人用 7z 的 zip 实现压缩，你用 `zip -9` 生成的明文包算法不同，bkcrack 会失败。**先用包里其他文件的 `Compression method` 选 `-0/-9` 或直接用 7z**。
- **明文至少 12 字节连续**，位置固定；不足 12 字节就退化为 crc 撞库。
- **RAR/7z**：伪加密与明文攻击思路不同，RAR 需 `rar2john`；WinRAR 的部分压缩包有「RAR 伪加密」可通过修改头部 CRC 处理。
- **嵌套包**：解出 zip 里还有 zip，且第二层密码就是第一层解出的字符串。
- **AES-256**：写字楼里常见的 `PK\x03\x04` + `99` 版本号（AES）包无法用 bkcrack，只能跑字典。
- **分卷包**：`z01/z02/...zip`，先 `7z x target.zip` 让其自动拼接。

## 六、参考来源

- [CTF Wiki - ZIP 格式（爆破/CRC32/明文攻击/伪加密）](https://ctf-wiki.org/misc/archive/zip/)
- [bkcrack - ZipCrypto known-plaintext attack](https://github.com/kimci86/bkcrack)
- [PKWARE APPNOTE（ZIP 规范）](https://pkware.cachefly.net/webdocs/APPNOTE/APPNOTE-6.2.0.txt)
- [Aperi'Solve 速查表（Password-protected ZIP 分支）](https://www.aperisolve.com/cheatsheet)
- [fcrackzip](https://github.com/hyc/fcrackzip)
