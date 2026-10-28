---
title: UPX 脱壳与手动脱壳（Windows / Linux）
category: reverse
tags: [UPX, 脱壳, OEP, ESP定律, IAT修复]
signals: [strings 里几乎什么都没有, 段名是 UPX0/UPX1, 自解压循环, 入口处有 pushad/popad, 文件比功能预期小很多]
difficulty: easy
source: "CTF-Wiki 脱壳技术 / UPX 官方 / 打包工具综述"
tools: [upx, x64dbg, OllyDbg, Scylla, importREC, CFF Explorer, pefile]
updated: 2026-10-22
---

## 一、识别信号（题面长什么样）

- `strings ./chall` 只有很少的字符串，几乎没有用户提示语。
- 用 `pefile`/`readelf` 看段表，出现 `UPX0`、`UPX1`、`.upx`。
- 文件开头有明显 `pushad`（`60`）后跟长串代码。
- 程序大小异常小（几 KB），但功能看起来复杂。
- 反编译工具报大量「无法解析的段」或入口点不在 `.text`。

## 二、原理

UPX 是**自解压壳**：加壳后文件结构变成

```text
+--------+  压缩数据（原程序所有段）
| UPX1   |  解压器 stub（入口点指向这里）
+--------+
| UPX0   |  未初始化，加载后解压目标（VirtualSize 大、RawSize = 0）
+--------+
```

运行流程：

```text
entry: pushad           ; 保存现场
       ...              ; 解压 UPX0 区域
       popad            ; 恢复现场（ESP 定律的观测点）
       jmp OEP          ; 跳到原始入口点（Original Entry Point）
```

**ESP 定律**：`pushad` 把 8 个寄存器压栈后，栈顶是 `ESP`；在 `popad` 处下**硬件访问断点**（`[esp]`），断下后单步几步就落在 OEP。

## 三、checksec 判读与利用思路

脱壳前的判读：

```text
1. 段表：段名 UPX0/UPX1/.upx?  → UPX
        rwx 段 + 高熵数据      → 自研壳 / VMProtect
2. 熵值：python -c "见下方脚本"
       熵 > 7.0 → 加密/压缩壳
3. 入口点：不属于 .text → 壳 stub
```

流程：

1. **先试 `upx -d`**（90% 的 CTF 题用默认 UPX）。
2. 失败（魔数被改）→ 手动脱壳。
3. 手动流程：找 OEP → dump 内存 → 修复 IAT。
4. Linux ELF 也有 UPX，`upx -d` 同样有效。

## 四、可直接运行的 exp 脚本

### 1. 先试自动脱壳

```bash
# 查看壳信息（UPX 会打印版本；魔数被改时会报 CantUnpackException）
upx -l ./chall
upx -d ./chall -o ./chall_unpacked
# 报 "CantUnpackException: header corrupted" 说明魔数被改
```

### 2. 魔数被改时修复（UPX 特征串 `UPX!` 被替换）

```python
#!/usr/bin/env python3
# 修复被改写的 UPX 魔数：常见做法是把 "XXXX" 改成 "UPX!"
import sys, pathlib
p = pathlib.Path(sys.argv[1])
data = bytearray(p.read_bytes())
for wrong in (b"XXXX", b"ABXD", b"UPX0"):
    idx = data.find(wrong)
    if idx >= 0 and wrong != b"UPX0":
        data[idx:idx+4] = b"UPX!"
        print(f"[+] 在 {hex(idx)} 修复魔数 {wrong} -> UPX!")
# 有的变体会改 packheader 的 l_info 结构，需要手工对照
p.with_suffix(".fixed").write_bytes(bytes(data))
```

### 3. 熵值探测（判断是否有壳）

```python
#!/usr/bin/env python3
import sys, math, collections, pathlib

def entropy(b):
    if not b: return 0.0
    c = collections.Counter(b)
    n = len(b)
    return -sum((v/n) * math.log2(v/n) for v in c.values())

data = pathlib.Path(sys.argv[1]).read_bytes()
if data[:2] == b"MZ":
    import pefile
    pe = pefile.PE(sys.argv[1])
    for s in pe.sections:
        name = s.Name.rstrip(b"\x00").decode(errors="ignore")
        print(f"{name:10s} entropy={entropy(s.get_data()):.3f}  raw={s.SizeOfRawData:#x}")
else:
    print(f"whole-file entropy = {entropy(data):.3f}")
```

### 4. x64dbg 手动脱壳（Windows）

```text
1. 打开目标，F9 到 entry
2. 在命令栏：bp on popad
3. 也可以在 pushad 后执行：bphws [esp], r, 4   （ESP 定律硬件断点）
4. F9 运行，断下后单步几次，看到 jmp <大跨度> 就是 OEP
5. 右键 → Follow in Dump，确认是原始代码（通常有典型函数序言 push ebp）
6. Scylla 插件：IAT Autosearch → Get Imports → Fix Dump
```

### 5. gdb 手动脱壳（Linux ELF）

```bash
# 1) 找 OEP：在 popad（popal 为 61）后观察
gdb -q ./chall
(gdb) starti                # 停在入口
(gdb) x/20i $pc             # 看是否为壳 stub
(gdb) b *$pc+0x30           # 试探断点，或用 watchpoint
(gdb) watch *(long*)$rsp    # ESP 定律等价物
(gdb) c
(gdb) info proc mappings    # 看解压后的段
# 2) dump 整个映射后重建
gdb -q ./chall -ex "starti" -ex "c" -ex "dump memory dumped.bin 0x400000 0x6f0000"
```

### 6. 一条命令做完「dump + 重建」

```bash
# Linux：利用 /proc/pid/mem 在程序跑到 OEP 后 dump
# 更稳的做法：gdb dump memory 之后用 lief 修入口点（见下方）
pip install lief
python3 -c "
import lief
b = lief.parse('./chall')
b.header.entrypoint = 0x401000     # 填上真实 OEP
b.write('chall_fixed')
"
```

## 五、常见坑 / 变体

- **`CantUnpackException`**：UPX 魔数被改或版本不匹配；先 `python3` 修 `UPX!`，再换对应 UPX 版本。
- **dump 出来跑不了**：IAT 没修复或段对齐错误，用 Scylla / importREC 重建导入表。
- **OEP 找不到**：可能是 `popad` 换成等价指令序列（`pop *` 展开），用 ESP 定律的硬件断点而不是硬编码 `popad`。
- **加了「壳中壳」**：先脱外层 UPX，再处理内层。
- **Linux 静态 UPX**：`upx -d` 后重定位表可能缺失，需 `lief` 修补。
- **ASLR 影响 dump 地址**：本地脱壳时 `setarch -R` 关闭随机化，保证每次地址一致。
- **`upx -d` 成功但程序行为异常**：说明原程序有自校验，需要把校验处 nop。

## 六、参考来源

- [CTF-Wiki: 保护壳简介](https://ctf-wiki.org/reverse/platform/windows/unpack/packer-introduction/)
- [CTF-Wiki: ESP 定律法](https://ctf-wiki.org/reverse/platform/windows/unpack/esp/)
- [CTF-Wiki: 一步到达 OEP 法](https://ctf-wiki.org/reverse/platform/windows/unpack/direct-oep/)
- [CTF-Wiki: DUMP 及 IAT 重建](https://ctf-wiki.org/reverse/platform/windows/unpack/fix-iat/)
- [UPX GitHub 与 README](https://github.com/upx/upx/blob/devel/README)
- [awesome-executable-packing（壳与脱壳工具综述）](https://github.com/packing-box/awesome-executable-packing)
- [pefile（PE 解析与段熵分析）](https://github.com/erocarrera/pefile)
