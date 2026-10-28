---
title: 内存取证进阶（malfind/malfind2 进程注入与隐藏进程）
category: forensics
tags: [volatility3, malfind, process-injection, rootkit, hollowing, vads]
signals: [题目说某个进程被注入了恶意代码, 内存镜像里存在明显不在磁盘上的可执行区域, 进程列表里有一个名字很怪的进程, 从 pslist 能看到但是从 psscan 看不到或者反过来, 题目要求 dump 出被注入的 shellcode, 内存里有 RWX 权限的可读可写可执行大块区域, 存在父进程已经退出的孤儿进程]
difficulty: hard
source: "Volatility 3 官方文档 malfind 模块 / Volatility 基金会 malfind 说明 / MITRE ATT&CK 进程注入分类"
tools: [python, volatility3, memprocfs, pefile, capstone, yara]
updated: 2026-10-22
exec_yaml: ok
---

## 一、识别信号（题面长什么样）

- 题目给了 Windows 内存镜像（`.raw`/`.dmp`），说"这台机器可能被植入了后门"。
- `windows.pslist` 里有可疑进程，比如名称是 `svch0st.exe`、随机串，或父子关系异常。
- 要求"shellcode"或"被注入的 DLL"，题目 hint 里出现 "injection / hollowing / APC"。
- `malfind` 输出一大片 `PAGE_EXECUTE_READWRITE` 区域，且首字节是 `MZ` 或 `4D 5A`。
- `psscan` 能扫到而 `pslist` 扫不到的进程（DKOM 隐藏）。
- 进程的 `Vad` 树里有不属于任何模块的 `MZ` 头。
- 题面说明有 "process hollowing"，且要求还原本体 PE。

## 二、原理

**`malfind` 的判定逻辑（Volatility 3 与 2 一致）：**

1. 遍历目标进程的 VAD（`Windows` 的虚拟地址描述符树）。
2. 找 **可执行** 且（非 `MEM_IMAGE` 类型，或有 `VadS` tag）的私有内存区。
3. 取区域开头 N 字节，若以 `MZ`（`4D 5A`）或典型 shellcode 开头（`e8`/`e9`/`ff 25`/`55 8b ec`）则报告。

**为什么这样能命中：**
- 正常的代码页类型是 `MEM_IMAGE`，映射自磁盘 PE 文件；注入进 `VirtualAlloc`/`VirtualProtect` 出来的区域类型是 `MEM_PRIVATE`。
- **Process Hollowing**：`CreateProcess(SUSPENDED)` → `NtUnmapViewOfSection` 卸载原映像 → `VirtualAlloc` 写新 PE → `SetThreadContext` 改入口点 → `ResumeThread`。结果：进程名合法，但映像基址的页是 `MEM_PRIVATE`，`malfind` 会命中。
- **`malfind2`** 是社区插件，额外支持"只报 RWX"、按 YARA 规则过滤、自动 dump 到文件。
- **隐藏进程**：
  - `pslist` 走 `ActiveProcessLinks` 双向链表（DKOM 可以从链表里摘掉自己）。
  - `psscan` 走池扫描（`PoolScan`），能发现链表外的 `_EPROCESS`。
  - 两者差集就是可疑对象；`csrss`/`smss` 的 `ActiveProcessLinks` 反查也可做交叉验证。

## 三、操作步骤

1. 先确认镜像 profile：`windows.info`。
2. 跑 `windows.pslist` / `windows.psscan` / `windows.cmdline` / `windows.pstree`，做差集找幽灵进程。
3. 对可疑 PID 跑 `windows.malfind --pid <PID> --dump`。
4. 关键：**判断 dump 出来的是 PE 还是 shellcode**：`MZ` → `pefile` 解析；否则 `capstone` 反汇编前 64 字节看调用（`GetProcAddress`/`LoadLibraryA` 的哈希常量）。
5. 用 `windows.handles` / `windows.dlllist` 看有没有无路径的模块。
6. 追踪注入来源：`windows.netscan` 看外连 C2、`windows.mbrscan` 看内核回调。
7. 需要全局匹配时用 `windows.vadyarascan --yara-file rules.yar`。

## 四、命令 / 脚本

```bash
# 基础流程
python -m volatility3 -f mem.raw windows.info
python -m volatility3 -f mem.raw windows.pslist
python -m volatility3 -f mem.raw windows.psscan
python -m volatility3 -f mem.raw windows.pstree | head -60
python -m volatility3 -f mem.raw windows.cmdline | grep -v System
# 注入检测
python -m volatility3 -f mem.raw windows.malfind --pid 1234 --dump
python -m volatility3 -f mem.raw windows.malfind > malfind.txt
# 全局 YARA（找已知家族）
python -m volatility3 -f mem.raw windows.vadyarascan --yara-file rules.yar
# 网络连接与句柄
python -m volatility3 -f mem.raw windows.netscan
python -m volatility3 -f mem.raw windows.dlllist --pid 1234 | grep -v '\\Windows\\'
```

```python
#!/usr/bin/env python3
# malfind 结果归类：区分 PE / shellcode / 已知模式
import re, sys, subprocess, pefile

def classify(path):
    d = open(path, 'rb').read(4096)
    if d[:2] == b'MZ':
        try:
            pe = pefile.PE(path, fast_load=True)
            return 'PE', {'entry': hex(pe.OPTIONAL_HEADER.AddressOfEntryPoint),
                          'sections': [s.Name.rstrip(b'\0').decode() for s in pe.sections]}
        except Exception as e:
            return 'MZ-unparsable', {'err': str(e)}
    # 常见 shellcode 特征
    pats = {b'\xfc\xe8': 'metasploit-stager-ish', b'\x4c\x8b\xdc': 'x64 prologue',
            b'\x55\x8b\xec': 'x86 mov ebp,esp', b'\x64\xa1': 'PEB access'}
    for k, v in pats.items():
        if d.startswith(k):
            return 'shellcode', {'hint': v}
    return 'unknown', {'first16': d[:16].hex()}

if __name__ == '__main__':
    import glob
    for f in glob.glob(sys.argv[1]):
        print(f, classify(f))
```

```bash
# peek/反汇编被 dump 的 shellcode
python - <<'EOF'
import capstone
d = open('pid.1234.0x400000.dmp','rb').read(128)
md = capstone.Cs(capstone.CS_ARCH_X86, capstone.CS_MODE_64)
for i in md.disasm(d, 0x400000):
    print('%#x: %-24s %s %s' % (i.address, i.bytes.hex(), i.mnemonic, i.op_str))
EOF
# pefile 修复 dump 出的 PE（hollowing 常见：文件头被清空）
python - <<'EOF'
import pefile
pe = pefile.PE('dumped.exe', fast_load=True)
print('imphash', pe.get_imphash(), 'sections', len(pe.sections))
pe.write('rebuilt.exe')
EOF
```

## 五、常见坑 / 变体

- **Volatility 3 与 2 的插件名不同**：`vol.py -f x --profile=Win10x64 malfind` → `python -m volatility3 -f x windows.malfind`；且 V3 需符号表（ISF），离线要提前准备。
- **`malfind` 误报多**：JIT（.NET/Java/V8）会分配 RWX 区，需结合"该进程是不是 JIT 宿主"判断。
- **`--dump` 命名混乱**：V3 输出 `pid.<PID>.0x<ADDR>.dmp`，`0x0` 表示从 VAD 起点开始。
- **hollowing 的基址**：被替换的映像 `ImageBase` 可能与 PE 头里的 `OptionalHeader.ImageBase` 不同，用 `windows.vadinfo` 对比。
- **`psscan` 不是万能的**：池扫描依赖 `_EPROCESS` 签名，被 rootkit 覆写的进程可能两边都找不到。
- **优先级**：先看 `netscan`（C2 连接）再看 `malfind`，网络痕迹通常更直接地指向"哪个进程"。
- **变体**：`windows.modscan`/`windows.callbacks`（内核钩子）、`windows.driverirp`、`windows.ssdt`。

## 六、参考来源

- [Volatility 3 malfind 模块文档（参数与判定条件）](https://volatility3.readthedocs.io/en/stable/volatility3.plugins.windows.malfind.html)
- [Volatility 2 Command Reference — Mal（malfind 原理与示例）](https://github.com/volatilityfoundation/volatility/wiki/Command-Reference-Mal)
- [MITRE ATT&CK：Process Injection 技术说明](https://attack.mitre.org/techniques/T1055/)
- [MemProcFS：用文件系统方式浏览进程与 VAD](https://github.com/ufrisk/memprocfs)
- [pefile 文档（PE 解析与 imphash）](https://pefile.readthedocs.io/en/latest/)
