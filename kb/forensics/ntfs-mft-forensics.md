---
title: NTFS / $MFT 取证（数据流 ADS、时间戳伪造识别）
category: forensics
tags: [ntfs, mft, ads, timestomp, usn-journal, timestomp]
signals: [附件是一个 ntfs 分区镜像或者一个 MFT 文件, 题目问某个文件什么时候被创建或被删除, 要求找出 Alternate Data Stream 里藏的内容, 时间戳明显不符合逻辑比如修改早于创建, 文件名在十六进制里是 UTF-16 双字节交替, 题目说要找被改名的文件, 镜像里存在 $UsnJrnl 或 $Secure]
difficulty: hard
source: "NTFS 官方结构文档（Microsoft）/ MFTECmd 文档 / Windows 时间戳与 USN 公开研究"
tools: [python, MFTECmd, analyzeMFT, ntfs-3g, fls, icat, Get-ZimmermanTools]
updated: 2026-10-22
exec_yaml: ok
---

## 一、识别信号（题面长什么样）

- 附件是 `.dd` / `.raw` / `.img` 分区镜像，或直接给一个 `$MFT` 文件。
- `file` 识别为 `DOS/MBR boot sector, NTFS`。
- 题目出现"文件被删了""谁改了文件""找出 3 月 1 日之后创建的所有文件"。
- 题目说"flag 藏在一个不可见的文件或者流里"。
- 十六进制里文件名呈 `p\0n\0g\0` 的 UTF-16LE 交替。
- 镜像里能看到 `$UsnJrnl`、`$LogFile`、`$Secure:$SDS` 等系统文件。
- 存在同一文件两个不同来源的时间戳对不上（`$SI` 与 `$FN`）。

## 二、原理

**NTFS 的元数据全在 `$MFT`（Master File Table）里，每个文件占一条 1024 字节记录。**

- 记录头：`FILE` 魔数、`update sequence array`（fixup，偏移 48）、`sequence number`、`hard link count`、`used size`、`base record`。
- 属性链：`$STANDARD_INFORMATION(0x10)`、`$FILE_NAME(0x30)`、`$DATA(0x80)`、`$ATTRIBUTE_LIST(0x20)`、`$INDEX_ALLOCATION(0xA0)`、`$OBJECT_ID(0x40)`。
- **两套时间戳**：`$SI` 有 4 个（created/modified/MFT-modified/accessed），`$FN` 有 4 个；**Windows API 的 `SetFileTime` 只能改 `$SI`**，`$FN` 不动。所以 `$SI` 与 `$FN` 不一致就是 timestomp 的直接证据。
- **ADS（Alternate Data Stream）**：同一文件可以有多个 `$DATA` 属性，名字不同，例如 `flag.txt:hidden`。`dir` 看不到，`dir /r` 或 `Get-Item -Stream *` 才看得到。
- **常驻 vs 非常驻**：小于约 700 字节的 `$DATA` 直接存在 MFT 记录里（resident），不占簇；稍大的走 `runlist`。
- **`$UsnJrnl:$J`** 记录文件的所有变更（创建/写入/改名/删除），即使文件已被删除也有痕迹，是"文件被改名"的关键证据。

## 三、操作步骤

1. **确认镜像类型**：`file`、`mmls`（分区表）、`ntfsinfo -m`（MFT 位置）。
2. **用 `fls` 遍历**：`fls -r -p image.dd` 列出所有文件含 ADS（`-p` 带全路径）。
3. **导出 `$MFT`**：`icat image.dd 0 > $MFT`，然后 `MFTECmd -f $MFT --csv out.csv`。
4. **解析时间戳对**：CSV 里对每个文件比较 `SI` 与 `FN` 四组时间，找异常。
5. **找 ADS**：`fls -r` 输出里含 `:streamname` 的条目；或 `ntfs-3g` 挂载后 `ls -lR | grep ':'`。
6. **改名历史**：`MFTECmd -f $UsnJrnl:$J --csv usn.csv`，按文件引用号（FRN）聚合事件。
7. **删除时间**：MFT 里已删除记录的 `$SI` 修改时间近似删除时刻；结合 `$logfile` 更准。

## 四、命令 / 脚本

```bash
# TSK 工具链
mmls disk.dd                       # 找 NTFS 分区起始扇区
fls -o <offset> -r -p disk.dd | head -50
fls -o <offset> -r disk.dd | grep ':'      # ADS 条目（含 :stream 名）
icat -o <offset> disk.dd 0 > MFT.bin       # 0 号记录即 $MFT
icat -o <offset> disk.dd <inode> | xxd | head     # 直接读某个文件
# MFTECmd（Windows 原生，推荐）
MFTECmd.exe -f MFT.bin --csv out --csvf mft.csv
MFTECmd.exe -f '$J' --csv out --csvf usn.csv -m <MFT 路径>
```

```python
#!/usr/bin/env python3
# 最小可用 $MFT 解析：枚举记录、属性、$SI/$FN 时间戳与 ADS
import struct, sys, datetime

ATTRS = {0x10: 'STANDARD_INFORMATION', 0x20: 'ATTRIBUTE_LIST', 0x30: 'FILE_NAME',
         0x40: 'OBJECT_ID', 0x50: 'SECURITY_DESCRIPTOR', 0x80: 'DATA',
         0x90: 'INDEX_ROOT', 0xA0: 'INDEX_ALLOCATION', 0xB0: 'BITMAP'}

def ft(v):
    return datetime.datetime(1601, 1, 1) + datetime.timedelta(microseconds=v // 10)

def parse(mft):
    rec = 0
    for base in range(0, len(mft) - 1024, 1024):
        r = mft[base:base + 1024]
        if r[:4] != b'FILE':
            continue
        rec += 1
        # fixup
        usa_off, usa_cnt = struct.unpack('<HH', r[4:8])
        fixed = bytearray(r)
        if usa_cnt:
            usn = r[usa_off:usa_off + 2]
            for i in range(1, usa_cnt):
                pos = i * 512 - 2
                if r[pos:pos + 2] != usn:
                    fixed[pos:pos + 2] = r[usa_off + 2 * i: usa_off + 2 * i + 2]
        attr_off = struct.unpack('<H', fixed[20:22])[0]
        in_use = fixed[22] & 1
        name, si, fn, streams = None, None, None, []
        p = attr_off
        while p + 4 <= 1024:
            atype, alen = struct.unpack('<II', fixed[p:p + 8])
            if atype == 0xFFFFFFFF or alen == 0:
                break
            nonres = fixed[p + 8]
            name_len, name_off = fixed[p + 9], struct.unpack('<H', fixed[p + 10:p + 12])[0]
            aname = fixed[p + name_off:p + name_off + 2 * name_len].decode('utf-16-le', 'ignore')
            vlen, voff = struct.unpack('<IH', fixed[p + 16:p + 22])
            body = fixed[p + voff:p + voff + vlen]
            if atype == 0x30 and len(body) >= 66:
                name = body[66:66 + 2 * body[64]].decode('utf-16-le', 'ignore')
                si_fn = [ft(x) for x in struct.unpack('<QQQQ', body[8:40])]
                fn = si_fn
            elif atype == 0x10 and len(body) >= 32:
                si = [ft(x) for x in struct.unpack('<QQQQ', body[0:32])]
            elif atype == 0x80:
                streams.append((aname or '$DATA', 'resident' if not nonres else 'non-resident', vlen))
            p += alen
        if name is None:
            continue
        tag = '' if in_use else '[DELETED]'
        print('%4d %-10s %-40s SI=%s FN=%s streams=%s' %
              (rec, tag, name, si[1] if si else '-', fn[1] if fn else '-', streams))

if __name__ == '__main__':
    parse(open(sys.argv[1], 'rb').read())
```

```python
#!/usr/bin/env python3
# Timestomp 检测：$SI 与 $FN 时间对不上（$FN 一般早于或等于 $SI 的创建时间）
def detect(stomp_rows):
    for name, si_created, fn_created in stomp_rows:
        if fn_created and si_created and si_created < fn_created:
            print('[!] 可疑: %s  SI创建 %s 早于 FN创建 %s' % (name, si_created, fn_created))
```

## 五、常见坑 / 变体

- **必须做 fixup 修正**：`$MFT` 记录末尾 2 字节会被 update sequence 替换，不修正读出来的属性会错位。
- **`$MFT` 是分片的**：镜像里 `$MFT` 可能不连续，用 `icat` 导出的才是完整版，别直接按偏移硬切。
- **resident 数据在属性里**：小 flag 直接写在 MFT 记录内，此时"找文件内容"就是解析 resident 属性。
- **`$FILE_NAME` 的父子引用**：改名后旧名可能还留在 `$ATTRIBUTE_LIST` 或 `$UsnJrnl` 里，单看 `$MFT` 看不到旧名。
- **时区**：NTFS 时间是 UTC，题目说"北京时间"要 +8。
- **`$LogFile` 可覆盖**：约 64MB 环形，只保留最近操作，`$UsnJrnl` 更持久。
- **变体**：ReFS（根本不同的结构）、exFAT/FAT32（无 `$MFT`，靠目录项时间）、APFS（时间戳精度纳秒，伪造检测思路相同）。

## 六、参考来源

- [Microsoft NTFS 参考（属性类型与 MFT 记录结构）](https://github.com/libyal/libfsntfs)
- [MFTECmd：解析 $MFT / $J / $Boot 的官方仓库](https://github.com/EricZimmerman/MFTECmd)
- [Eric Zimmerman 工具集总入口（Get-ZimmermanTools）](https://ericzimmerman.github.io/)
- [Sleuth Kit 文档（fls / icat / mmls 用法）](https://www.sleuthkit.org/sleuthkit/man/)
- [Timestomp 与 $SI/$FN 双时间对比的取证原理](https://www.magnetforensics.com/blog/)
