---
title: 内存取证（Volatility 2/3 常用插件与 profile 判定）
category: forensics
tags: [内存取证, volatility, volatility3, memory dump, profile, 进程树]
signals: [附件是内存 dump, 文件后缀 raw 或 mem 或 vmem, 题目问运行了什么进程, 需要从内存里找密码, 需要 dump 出进程内存, 需要判定操作系统版本]
difficulty: medium
source: "Volatility 3 文档 / Volatility 2 Command Reference / CTF-Wiki 磁盘内存分析题目"
tools: [volatility3, volatility2, strings, bulk_extractor, memprocfs, mmls]
updated: 2026-10-22
---

## 一、识别信号（题面长什么样）

- 附件 `memory.dmp` / `flag.vmem` / `challenge.raw`，几十 MB 到几 GB。
- 题目问「机器上跑过什么程序」「找到管理员密码」「从这个进程里 dump 出文件」。
- `strings` 里能看到明显的进程名、URL、`MZ` 头。
- `file` 输出 `PCAP` 或纯二进制，没有文件系统特征。

## 二、原理

内存镜像里包含：进程列表（`_EPROCESS` 双向链表）、每个进程的 VAD（虚拟地址描述符）与页面表、内核模块、注册表 hive 缓存、网络连接、环境变量与明文凭据。

Volatility 的通用思路：
1. **判定 profile / symbol**（最重要的一步）：内存里的内核基址与版本决定结构体布局。
   - **Volatility 2**：手工选 profile（`Win7SP1x64`、`Win10x64_19041` 等），或 `imageinfo` 自动猜。
   - **Volatility 3**：自动下载/匹配 **符号表（ISF / PDB）**，失败时可用 `symbols` 插件看缺什么，离线可放 `symbols/` 目录。
2. **插件链**：`pslist` → `pstree` → `cmdline` → `netscan` → `malfind` → `dumpfiles`/`memmap`。
3. **提取**：从进程内存里 carve 出文件，从注册表 hive 里读 SAM/LSA 凭据。

## 三、操作步骤

1. **确认是内存镜像**：`strings -n 8 | grep -i 'windows\\system32'` 或看是否有 `KDBG`。
2. **Volatility 3 首选**：`vol -f mem.raw windows.info`，看版本与内存布局。
3. **进程链**：`windows.pslist` → `windows.pstree` → 找可疑进程（`pslist` 看不到但 `psscan` 看得到 = 隐藏进程）。
4. **命令行与网络**：`windows.cmdline`、`windows.netscan`、`windows.netstat`。
5. **注入检测**：`windows.malfind` 的高熵页 → 提取 shellcode。
6. **文件与凭据**：`windows.dumpfiles`、`windows.hashdump`、`windows.lsadump`；Linux 用 `linux.bash`、`linux.envars`。
7. **最后手段**：`strings` + `bulk_extractor` 对全镜像做关键字扫描。

## 四、命令/脚本

### Volatility 3（推荐）

```bash
pip install volatility3
vol -f mem.raw windows.info                 # 系统信息（第一必跑）
vol -f mem.raw windows.symbols              # 查看缺哪些符号
vol -f mem.raw -h | grep -i windows | head  # 插件列表
vol -f mem.raw windows.pslist                # 进程列表（含 PPID）
vol -f mem.raw windows.pstree                # 进程树
vol -f mem.raw windows.psscan                # 扫描已终止/隐藏进程
vol -f mem.raw windows.cmdline               # 命令行参数
vol -f mem.raw windows.netscan               # 网络连接（含已关闭）
vol -f mem.raw windows.malfind               # 可疑注入内存（RWX 页）
vol -f mem.raw windows.hashdump              # 导出 SAM 哈希
vol -f mem.raw windows.lsadump               # 导出 LSA secrets
vol -f mem.raw windows.registry.hivelist     # 注册表 hive 列表
vol -f mem.raw windows.registry.printkey --key "Software\Microsoft\Windows\CurrentVersion\Run"
vol -f mem.raw windows.filescan              # 文件对象扫描
vol -f mem.raw windows.dumpfiles --virtaddr 0x...      # 按对象导文件
```

```bash
# Linux 内存镜像
vol -f mem.lime linux.banner
vol -f mem.lime linux.pslist
vol -f mem.lime linux.bash           # 历史命令（题目最爱）
vol -f mem.lime linux.envars
vol -f mem.lime linux.check_syscall
```

### Volatility 2（老题常用）

```bash
git clone https://github.com/volatilityfoundation/volatility
cd volatility && python2 setup.py install
vol.py -f mem.raw imageinfo                  # 猜 profile（最关键）
vol.py -f mem.raw --profile=Win7SP1x64 pslist
vol.py -f mem.raw --profile=Win7SP1x64 pstree
vol.py -f mem.raw --profile=Win7SP1x64 cmdline | grep -i flag
vol.py -f mem.raw --profile=Win7SP1x64 netscan
vol.py -f mem.raw --profile=Win7SP1x64 hivelist
vol.py -f mem.raw --profile=Win7SP1x64 hashdump -y 0x9f8a4000 -s 0x9f8a4088
vol.py -f mem.raw --profile=Win7SP1x64 memdump -p 1234 -D dumps/
vol.py -f mem.raw --profile=Win7SP1x64 filescan | grep -i flag

# 缺少 profile 时（Windows 10 高版本）
python vol.py --info | grep Win10
# 或用 kdbgscan 确认构建号
vol.py -f mem.raw kdbgscan
```

### 从进程内存里找 flag（Volatility 2/3 通用）

```bash
# 方式 1：dump 全部进程内存，再 grep
vol -f mem.raw windows.memmap --pid 1234 --dump   # 需要 pid
for f in dumps/*.dmp; do strings -n 6 "$f" | grep -i 'flag{' && echo "== $f"; done
# 方式 2：Volatility 2 一步到位
vol.py -f mem.raw --profile=Win7SP1x64 memdump -p 1234 -D dumps/
strings -e l dumps/1234.dmp | grep -i flag
# 方式 3：Volatility 3 dumpfiles 按文件对象
vol -f mem.raw windows.dumpfiles --pid 1234
```

### 直接 strings + bulk_extractor（兜底）

```bash
strings -n 8 mem.raw | grep -iE 'flag\{|ctf\{|password' | head
strings -e l -n 8 mem.raw | grep -iE 'flag\{|password' | head     # UTF-16
sudo apt install -y bulk_extractor
bulk_extractor -o bxt mem.raw -e email -e url -e aes -e gzip
grep -ri flag bxt/ | head
```

### MemProcFS（新工具，挂载式浏览）

```bash
# 把内存镜像挂成文件系统，直接 ls 进程/网络/注册表
./memprocfs -device mem.raw -mount mnt/
ls mnt/pid/ ; ls mnt/registry/
cat mnt/pid/*/cmdline 2>/dev/null | grep -i flag
```

### 凭据提取（合法取证练习）

```bash
vol -f mem.raw windows.hashdump > hashes.txt
hashcat -m 1000 hashes.txt /usr/share/wordlists/rockyou.txt
vol -f mem.raw windows.lsadump --output-file lsa.txt
grep -i -A2 'Password' lsa.txt | head
```

## 五、常见坑 / 变体

- **Volatility 3 找不到符号**：离线环境无法自动下载 ISF，把 `windows.zip` 符号包放进 `volatility3/symbols/`，或退回 Volatility 2 手选 profile。
- **profile 选错的表现**：`pslist` 输出乱码/为空，换 `imageinfo` 给的第一个建议试。
- **内存镜像是"分页文件"或"休眠文件"**：`hiberfil.sys`/`pagefile.sys` 也能取证，但需转换（Volatility 支持 `--profile` + hibernation 文件解析）。
- **Lime / 物理内存**：Linux 用 `avml`/`lime` 生成的格式，Volatility 3 `linux.*` 可直接读。
- **进程被隐藏**：`pslist` 有、`pstree` 断链，或 `psscan` 有而 `pslist` 没有 → 对比着看。
- **中文用户名**：`cmdline` 输出乱码时用 `-e l` 或转码。
- **结合磁盘镜像**：内存 + 磁盘一起给时，先用磁盘镜像定位文件，再用内存找"打开过它的进程"。

## 六、参考来源

- [Volatility 3 官方文档](https://volatility3.readthedocs.io/en/latest/)
- [Volatility 3 GitHub（插件与符号表说明）](https://github.com/volatilityfoundation/volatility3)
- [Volatility 2 Command Reference（插件清单）](https://github.com/volatilityfoundation/volatility/wiki/Command-Reference)
- [CTF Wiki - 磁盘内存分析题目](https://ctf-wiki.org/misc/disk-memory/problem/)
- [Volatility 官方 releases 页](https://www.volatilityfoundation.org/releases)
- [MemProcFS 内存镜像挂载工具](https://github.com/ufrisk/MemProcFS)
