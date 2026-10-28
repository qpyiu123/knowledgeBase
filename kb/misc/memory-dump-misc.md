---
title: 内存 / 进程 dump 分析（misc 向：strings、堆块、回写文件）
category: misc
tags: [memory-dump, minidump, strings, procfs, gcore, mimipenguin]
signals: [附件是一个几十 MB 到几个 GB 的 vmem 或 raw 或 dmp, 题目说这是某个进程崩溃时的内存转储, 文件里能 strings 出 flag 但被切成几段, 题目给了个 pid 或者进程名, 内存镜像的头部是 MDMP 或者 ELF core 魔数, 内存里还能看到完整的文件名和路径, 要求从内存里还原出被删除的文件]
difficulty: medium
source: "Windows Minidump 官方结构文档 / Volatility 3 文档 / strings 与 grep 实战规范"
tools: [python, strings, volatility3, memprocfs, gcore, gdb, 010editor]
updated: 2026-10-22
exec_yaml: ok
---

## 一、识别信号（题面长什么样）

- 附件是一个几百 MB、扩展名 `.mem` / `.vmem` / `.raw` / `.dmp` / `.core` 的大文件。
- 题目描述出现"进程名是 xxx""21:30 时刻的内存快照""从小程序容器里 dump 出来的"。
- 文件头 4 字节是 `MDMP`（Windows Minidump）或 `7f45 4c46`（ELF，core dump）或 `454c 4643 4c41 5353`（LIME Linux 内存）。
- `strings -n 8` 直接能看到 `C:\Users\...\flag.txt`、`/home/ctf/flag`、SQL 语句、HTTP 请求。
- `strings` 出来的 flag 被 `\x00` 或换行切成好几段，需要按堆块拼接。
- 文件里出现大量 `PK\x03\x04`、`JFIF`、`%PDF-` 片段——内存里有文件残影。
- 题目说"flag 在这段内存里"，但 grep 不到完整 `flag{`，只有 `flag` 和 `{` 分开出现。

## 二、原理

- **进程虚拟内存是页映射的**：一份完整 dump 通常是"所有已提交 VAD / 所有匿名映射页"的平铺，物理上连续不代表逻辑上连续。所以 `strings` 强读能出东西，但**跨页的对象需要按"页集合"重排**。
- **堆块生命周期**：分配→写入明文→free 后内存不清零，所以被释放的缓冲区（如 Python 字符串、Go 的 byte slice）内容仍可读，只是可能被后续分配覆盖成碎片。
- **Minidump 有两类**：`MiniDumpNormal`（栈 + 线程上下文 + 若干模块）体量小，只有栈上数据；`MiniDumpWithFullMemory` 才包含完整堆。判断方式是解析 `MINIDUMP_DIRECTORY` 里有没有 `Memory64ListStream`。
- **ELF core**：`ELF header` → `PT_LOAD` 段表，每段有 `p_vaddr`（虚拟地址）与 `p_offset`（文件偏移），据此可以做 `vaddr ↔ offset` 双向换算。
- **明文识别永远靠"结构 + 语义"**：优先找文件签名和结构化文本，再退回熵值扫。

## 三、操作步骤

1. **判类型**：`head -c 8 | xxd`，确定 minidump / ELF core / LIME / 裸平铺。
2. **粗扫 strings**：`strings -n 6 -e s` 与 `-e l`（UTF-16LE）都跑一遍，直接 `grep -i flag`。
3. **用 volatility3 或 MemProcFS 结构化遍历**（如果镜像可被其识别为 Windows/Linux 内存）。
4. **段映射还原**：对 ELF core 解析 PT_LOAD，把每个段按 `p_vaddr` 落盘成 `seg_0xXXXXXXXX.bin`，方便逐段分析。
5. **对象级搜索**：按已知结构（如 Python 的 `PyASCIIObject`、Java heap 的 `String` 头、Go 的 string header）确定性扫描。
6. **回写文件**：找到 `PK\x03\x04` 后用长度字段切出完整 zip；找到 `JFIF` 就往后找 `FF D9`。
7. **交叉验证**：`binwalk` 扫一遍，`strings` 的结果与结构化遍历互相印证。

## 四、命令 / 脚本

```bash
# 类型判定
head -c 16 mem.dmp | xxd
file mem.dmp
# 快速命中
strings -n 6 mem.dmp | grep -iE 'flag|ctf|key|passwd|token' | head -50
strings -n 6 -e l mem.dmp | grep -iE 'flag|ctf' | head -20     # UTF-16LE
# 嵌入文件扫描
binwalk mem.dmp | head -40

# volatility3（Windows 镜像）
python -m volatility3 -f mem.dmp windows.info
python -m volatility3 -f mem.dmp windows.pslist
python -m volatility3 -f mem.dmp windows.dumpfiles --virtaddr <VA> 2>/dev/null | tail
# volatility3（Linux 镜像）
python -m volatility3 -f mem.lime linux.bash
python -m volatility3 -f mem.lime linux.pslist
```

```python
#!/usr/bin/env python3
# ELF core 段映射导出 + 按虚拟地址查偏移
import struct, sys, os

def parse_elf_core(path, outdir='segs'):
    d = open(path, 'rb').read()
    assert d[:4] == b'\x7fELF', 'not ELF'
    is64 = d[4] == 2
    os.makedirs(outdir, exist_ok=True)
    segs = []
    if is64:
        e_phoff = struct.unpack('<Q', d[0x20:0x28])[0]
        e_phentsize, e_phnum = struct.unpack('<HH', d[0x36:0x3A])
        for i in range(e_phnum):
            o = e_phoff + i * e_phentsize
            p_type, p_flags, p_offset, p_vaddr, p_paddr, p_filesz, p_memsz = \
                struct.unpack('<IIQQQQQ', d[o:o+0x38])
            if p_type == 1 and p_filesz:          # PT_LOAD
                seg = d[p_offset:p_offset + p_filesz]
                name = '%s/seg_%02d_%016x.bin' % (outdir, i, p_vaddr)
                open(name, 'wb').write(seg)
                segs.append((p_vaddr, p_filesz, name))
    for va, sz, name in segs:
        print('vaddr=0x%016x size=%-10d %s' % (va, sz, name))
    return segs

def vaddr_to_offset(segs, va):
    for base, sz, name in segs:
        if base <= va < base + sz:
            return name, va - base
    return None, None

if __name__ == '__main__':
    s = parse_elf_core(sys.argv[1])
    if len(sys.argv) > 2:
        print(vaddr_to_offset(s, int(sys.argv[2], 16)))
```

```python
#!/usr/bin/env python3
# 在原始内存里找跨页/跨块的 flag 片段：把非打印分隔符视为候选拼接点
import re, sys

FLAG = re.compile(rb'[A-Za-z0-9_]{2,40}\{[ -~]{4,200}\}')
def scan(path):
    d = open(path, 'rb').read()
    for m in FLAG.finditer(d):
        off, s = m.start(), m.group()
        print('@%#x %d %r' % (off, len(s), s))

def scattered(path, head=b'flag', window=64):
    """grep 不到完整 flag 时，找 head 附近窗口里的可打印串"""
    d = open(path, 'rb').read()
    for i in range(len(d)):
        j = d.find(head, i)
        if j < 0: break
        i = j + 1
        chunk = d[j:j + window]
        pr = re.findall(rb'[\x20-\x7e]{4,}', chunk)
        if pr:
            print('@%#x %s' % (j, b' | '.join(pr[:4])))

if __name__ == '__main__':
    scan(sys.argv[1]); scattered(sys.argv[1])
```

## 五、常见坑 / 变体

- **dump 是"物理内存"还是"虚拟内存"**：物理镜像里同一个进程的多页不连续，`strings` 出来的长字符串会被拦腰截断；虚拟内存 dump（如 `gcore`）才连续。
- **`MiniDumpNormal` 没有堆**：只有栈，且每个线程的栈大小有限，flag 若在堆上就什么都找不到，题目会说明是 full dump。
- **压缩/加密的镜像**：Windows 的 hiberfil.sys 虽是内存镜像但走 XPRESS 压缩，需 `volatility3 windows.hiberinfo` 之类处理。
- **多进程同页共享**：同物理页被多个进程映射（如 `libc`），dump 里只出现一份。
- **UTF-16 字符串**：`strings -e l` 才能扫出 `W i d e S t r i n g`；漏掉这一步是新手最常见失误。
- **栈上数据被覆盖**：越靠近 dump 时刻越可靠，回溯早期数据要靠未被重写的页。
- **Mimikatz / 凭据类题目**：这类实现细节归 `memory-forensics-volatility`，本篇只管"拿到 flag"。
- **变体**：浏览器进程 dump（`chrome_renderer.dmp`）、Java heap dump（`.hprof`，`jhat`/MAT 打开）、Go core。

## 六、参考来源

- [Volatility 3 官方文档（插件与内存格式）](https://volatility3.readthedocs.io/en/stable/)
- [MemProcFS：把内存镜像挂载成文件系统](https://github.com/ufrisk/memprocfs)
- [MemProcFS 实战：高级内存取证](https://www.pentestpartners.com/security-blog/mounting-memory-with-memprocfs-for-advanced-memory-forensics/)
- [ELF 格式规范（Program Header 与 PT_LOAD）](https://refspecs.linuxfoundation.org/elf/elf.pdf)
- [CTF-Wiki：Misc 内存取证入门](https://ctf-wiki.org/misc/introduction/)
