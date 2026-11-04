---
title: 方法卡 · 逆向补丁与 keygen（跳转反转 / NOP / 自校验绕过）
category: reverse
tags: [方法卡, patch, crackme, keygen, 注册机, 反调试, nop]
signals: [程序要求输入序列号, 输入错误弹窗 Invalid license, 验证函数里只有一个条件跳转, 题面要求给出注册机, 有 trial 剩余次数限制, 二进制校验文件自身哈希, 下断点程序直接退出, Correct 与 Wrong 并列]
difficulty: easy
source: kb/reverse/patch-and-keygen.md, kb/reverse/anti-debugging.md
tools: [python, 内置脚本, ida, x64dbg]
updated: 2026-11-03
---

# 方法卡 · 逆向补丁与 keygen（跳转反转 / NOP / 自校验绕过）

## 适用场景

- 程序启动要求 `Enter your serial:`，输错弹 `Invalid license` / `Wrong.`；
- 成功与失败分支在反汇编里**只差一条 `jz`/`jnz`**，或差一个 `call check`；
- 题面要"注册机 / keygen / patch 后的二进制 / 能通过校验的输入"；
- 有 trial 计数（`if (++count > 5) exit()`）、或启动时算自身哈希 / CRC 自校验；
- 附带：下断点就跑不起来（反调试），需要先绕过再 patch。

## 前置条件

- 拿到文件偏移（`file_off`）而不只是 RVA：`file_off = rva - section.VirtualAddress + PointerToRawData`。
- 已知目标指令的**确切字节**：x86/x64 的 `jz rel8 = 74`、`jnz rel8 = 75`、`jz rel32 = 0F 84`、`jnz rel32 = 0F 85`、
  `jmp rel8 = EB`、`nop = 90`、`mov eax,1; ret = B8 01 00 00 00 C3`、`xor eax,eax; ret = 31 C0 C3`。
- 自校验题：要同时定位校验函数，把返回值改成 1；只改 `.text` 会触发 CRC 失败。
- 本卡脚本**只做内存中的字节级改写与 keygen 求解**，输入输出都走文件/标准流，绝不联网、不删除。

## 步骤

1. **跑一次**：输入 `AAAA`，记下错误串（`Wrong.`/`Invalid`），后续按字符串交叉引用定位比较点。
2. **定补丁粒度**：能过的优先反转跳转（1 字节）；要"永不失败"就 `74 xx → EB xx`；要跳过函数就整段 `90`；
   要伪造成功返回值就 `B8 01 00 00 00 C3`。本卡脚本 `--patch --file --offset --mode jz2jnz|jmp|nop-call|true-ret`。
3. **对自校验**：先找 CRC/哈希函数（常见 `IsDebuggerPresent` 旁的 `.init_array` 检查），把其返回值改成 1 再处理主校验。
4. **写 keygen**：还原正向算法后反解。本卡的示范题是 `sum(buf[i]*(i+1)) == TARGET`，
   固定中段 `s[2..len-2]`、只解 `s[0]`(权重1)/`s[1]`(权重2)/`s[-1]`(权重 len) 三个未知数（`--keygen`）。
5. **验证**：对每个候选 serial 用纯 Python 重算一次校验和，确认 `sum == TARGET` 再提交。

```powershell
# 生成合法 serial（算法：sum(buf[i]*(i+1)) == 0x1A2B，16 字节可打印）
.\.venv\Scripts\python.exe kb/_methods/scripts/binary_patch.py --keygen --target 0x1A2B --length 16
# 校验任意 serial 是否满足该算法
.\.venv\Scripts\python.exe kb/_methods/scripts/binary_patch.py --check-serial AAAAAAAAAAAAAAAA --target 0x1A2B
# 反汇编判断某个偏移是不是条件跳转，并生成补丁字节
.\.venv\Scripts\python.exe kb/_methods/scripts/binary_patch.py --patch --file chall.bin --offset 0x1140 --mode jz2jnz
```

## 脚本

脚本路径：`kb/_methods/scripts/binary_patch.py`（纯标准库，离线）

- 公开函数：`classify_jump(b)`、`patch_bytes(mode, data, off)`、`keygen(target, length)`、`checksum(serial)`；
- `--patch --file F --offset O --mode M`：在内存里改字节后写到 `F.patched`，**绝不覆盖原文件**；
  支持 `jz2jnz`（反转）、`jmp`（无条件化）、`nop-call`（5 个 90）、`true-ret`（`B8 01 00 00 00 C3`）；
- `--dis-bytes`：把十六进制字节流分类成跳转/调用/NOP，给出"这里能不能 patch"的判断；
- `--keygen` / `--check-serial`：示范题的 keygen 与校验（算法与 `kb/reverse/patch-and-keygen.md` 的 check.c 一致）；
  可达区间 `[32+64+32L+rest, 126+252+126L+rest]`，`rest = Σ base*(i+1), i∈[2,L-2]`，target 越界会明确报错。

## 失效场景

- **PIE/ASLR 下直接用 RVA 当偏移**：地址全错，patch 会改到代码中间导致崩溃 —— 先按节区换算。
- **`jz rel8` 反转换了 `jnz` 还是跳不到**：±127 限制与语义都要成立，条件依赖多个标志位时反转不一定对，改用 `jmp` + 清理栈。
- **有 CRC / 哈希自校验**：只 patch 主分支必然崩，须先让校验函数返回 1，或打开"算哈希前先解压/延时"的分支。
- **keygen 无解**：算法里含 TEA/AES 之类加密时，"调参凑数"不可能成功，必须逆加密函数，别暴力。
- **反调试误判**：程序下断点退出不一定是反调试，也可能是 SIGTRAP/异常处理，先 `handle SIGTRAP nostop noprint pass` 排除。

## 相关文档

- `kb/reverse/patch-and-keygen.md`（crackme 三类解法、patch 粒度、keygen 还原思路）
- `kb/reverse/anti-debugging.md`（打补丁前要过的一层：IsDebuggerPresent/ptrace/TracerPid）
- `kb/reverse/static-analysis-ghidra.md`（定位校验函数的静态流程）
- 方法卡：`kb/_methods/vm_obfuscation.md`（校验逻辑被 VM 化时的接续）
