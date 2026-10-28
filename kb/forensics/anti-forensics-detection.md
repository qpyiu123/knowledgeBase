---
title: 反取证识别（删除痕迹、时间戳篡改、日志清理）
category: forensics
tags: [anti-forensics, wiper, timestomp, log-clearing, evidence-of-absence]
signals: [日志显示事件 id 1102 表示审计日志被清空, 用户事件日志中间出现大段时间空洞, 文件时间戳被改成 1970 或 2000 年, 磁盘上出现大量随机字节的覆盖区域, 程序使用了 sdelete 或 shred 的痕迹, 系统还原点和卷影副本被删除, 题目直接问攻击者做了哪些反取证操作]
difficulty: hard
source: "MITRE ATT&CK T1070 Indicator Removal / SANS 反取证与检测公开课程材料"
tools: [python, volatility3, evtx_dump, usn-journal, MFTECmd, Autopsy, binwalk]
updated: 2026-10-22
exec_yaml: ok
---

## 一、识别信号（题面长什么样）

- Windows 安全日志里只有一条 `1102`（audit log cleared）或 `104`（System 日志被清）。
- 某个用户目录下文件的时间戳是 `1970-01-01`、`1601-01-01` 或未来时间。
- 磁盘空闲区域本该是 `0x00` 或旧文件残影，却出现**均匀随机字节**。
- 出现 `cipher /w`、`sdelete`、`shred`、`dd if=/dev/urandom` 的执行痕迹。
- 卷影副本（VSS）列表为空，但系统刚装不久。
- 题目问"攻击者删除了哪些证据"而不是"找到 flag"。

## 二、原理

反取证的本质是**破坏证据的三个属性之一**：可用性（删除/覆盖）、完整性（修改）、可信性（伪造时间/日志）。

| 手法 | 痕迹 | 检测点 |
| --- | --- | --- |
| 删除文件 | `$MFT` 中 `in_use=0` 的记录 | `$MFT` 记录仍在，只是位图释放 |
| 覆写/擦除 | 空闲空间熵接近 8 bit/byte | 正常空闲区多为 0 或旧数据（熵低） |
| 抹除日志 | 事件日志 `1102`/`104`，`.evtx` 文件大小骤减 | 日志文件头 `chunk count` 与时间范围 |
| 改时间 | `$SI` 与 `$FN` 不一致；时间早于文件系统格式化时间 | 双时间戳对比 |
| 删卷影 | `vssadmin delete shadows` 命令历史 | Prefetch、`$UsnJrnl`、Event ID 8222 |
| 清 USN | `fsutil usn deletejournal` | `$J` 时间断点 |
| 时间线伪造 | 大量文件同一秒创建 | 直方图异常尖峰 |

**关键思维：反取证本身会留下"证据的缺席"（evidence of absence）。** 一段完全没日志的时间、一个空得离谱的目录、一个熵值过高的空闲区，本身就是线索。

## 三、操作步骤

1. **列出"应当有却没有"的东西**：应该有条目的日志/目录/进程。
2. **日志完整性检查**：`evtx_dump` 解析每个 chunk 的首尾时间与记录数，对比相邻日期。
3. **文件系统层**：TSK 的 `fls -d`（只列已删除）与 `$MFT` 里 `in_use=0` 的记录。
4. **双时间戳**：`$SI` 与 `$FN` 不一致即 timestomp。
5. **空闲空间熵**：`binwalk` 之外，用 python 按 4KB 块算熵，找"擦除区"。
6. **命令历史**：注册表 `UserAssist`、`Prefetch`、PowerShell 脚本块日志（4104）、bash `history`。
7. **VSS/快照**：`vssadmin list shadows`（离线时读 `System Volume Information`）。

## 四、命令 / 脚本

```bash
# 事件日志：找 1102 / 104 / 8222
evtx_dump.py -o jsonl Security.evtx | jq -r 'select((.EventID|tostring)=="1102") | [.TimeCreated, .Channel] | @tsv'
evtx_dump.py -o jsonl System.evtx | jq -r 'select((.EventID|tostring)=="104") | [.TimeCreated] | @tsv'
# 日志时间空洞
evtx_dump.py -o jsonl Security.evtx | jq -r '.TimeCreated' | sort | head -3
# 已删除文件（TSK）
fls -rd -o 63 disk.dd | head -50
# 命令痕迹
grep -rE 'sdelete|shred|cipher /w|vssadmin delete|wevtutil cl|fsutil usn delete' --include='*.log' -l .
```

```python
#!/usr/bin/env python3
# 空闲空间熵扫描：定位"被擦除"的区块
import math, sys, collections

def entropy(b):
    if not b:
        return 0.0
    c = collections.Counter(b)
    n = len(b)
    return -sum((v / n) * math.log2(v / n) for v in c.values())

def scan(path, bs=4096):
    f = open(path, 'rb')
    idx = 0
    while True:
        blk = f.read(bs)
        if not blk:
            break
        e = entropy(blk)
        if len(blk) >= bs:
            yield idx, e, blk[:16].hex()
        idx += 1

if __name__ == '__main__':
    high = [(i, e, h) for i, e, h in scan(sys.argv[1]) if e > 7.9]
    print('高熵块数量:', len(high))
    for i, e, h in high[:20]:
        print('blk %6d off 0x%08x entropy=%.2f %s' % (i, i * 4096, e, h))
```

```python
#!/usr/bin/env python3
# timestomp 检测：$MFT 里 $SI 与 $FN 的"创建时间"不一致，或时间早于卷创建时间
import datetime

VOL_CREATED = datetime.datetime(2024, 1, 1, 0, 0, 0)   # 从卷信息里取

def check(name, si_created, fn_created, si_modified):
    flags = []
    if si_created and fn_created and si_created < fn_created:
        flags.append('SI创建早于FN创建')
    if si_modified and si_modified < VOL_CREATED:
        flags.append('修改时间早于卷创建')
    if si_created and si_created.year < 2000:
        flags.append('时间戳被置为上古时间')
    if flags:
        print('[!] %-40s %s  SI=%s FN=%s' % (name, ','.join(flags), si_created, fn_created))
```

## 五、常见坑 / 变体

- **`1102` 不是唯一清日志证据**：`wevtutil cl` 之外还有直接删 `.evtx` 文件，此时日志文件会"不存在"，需查 `$MFT` 里该文件的删除记录。
- **时间戳可以被完美伪造**：用内核驱动或 `SetFileInformationByHandle` 可以同时改 `$SI` 与 `$FN`（`NtSetInformationFile` 的 `FileBasicInformation`）。此时要看 `$UsnJrnl` 里对应事件的真实时间。
- **"擦除"不一定擦干净**：SSD 的 TRIM 会物理擦除，但普通硬盘上 `cipher /w` 只覆盖空闲区；NTFS 压缩/稀疏文件残余更难清。
- **高熵 ≠ 一定擦除**：加密文件、压缩包、内存转储本身熵就高，必须结合文件系统元数据（是否已删除）才成立。
- **时间线尖峰**：批量改时间会留下"同一秒内创建上千文件"的直方图异常，是最稳的检测特征。
- **变体**：Linux 上 `timestomp` 对应 `touch -d`、`debugfs` 删日志；容器里清 `/var/log` + `docker system prune`。

## 六、参考来源

- [MITRE ATT&CK T1070：Indicator Removal（含 clear logs / timestomp 子技术）](https://attack.mitre.org/techniques/T1070/)
- [Timestomp 检测：$SI 与 $FN 双时间对比原理](https://www.magnetforensics.com/blog/)
- [文档取证课程模块：检测反取证活动](https://pages.cs.oslomet.no/bytewitness-f95d73/module4/task_4-4.html)
- [evtx 解析工具（python-evtx / evtx_dump）](https://github.com/williballenthin/python-evtx)
- [Sleuth Kit：fls/icat 与已删除文件恢复](https://www.sleuthkit.org/sleuthkit/man/fls.html)
