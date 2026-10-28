---
title: checksec 与保护机制判读速查
category: pwn
tags: [checksec, 保护机制, NX, PIE, RELRO, canary]
signals: [拿到二进制先 checksec, 题目给了 libc.so.6, 远程 nc 可交互, Dockerfile 里写了 ubuntu:20.04, 附件里有 ld-linux, 程序 fork 后循环]
difficulty: easy
source: "CTF-Wiki / pwntools checksec / HackTricks"
tools: [checksec, pwntools, gdb, pwndbg]
updated: 2026-10-22
---

## 一、识别信号（题面长什么样）

- 附件是一个 ELF + 一个 `flag` 描述文件，几乎必然要用 checksec 判读。
- 题面强调「给了 libc.so.6」「给了 ld-2.31.so」「附件含 Dockerfile」——说明是**实地址利用**而非本地爆破。
- 题面说「每次连接都重启服务」「服务 fork 后循环处理」——决定能不能爆破 canary / ASLR。
- 远程是 `nc TARGET PORT` 直连的菜单题，说明大概率要走堆 / 格式化字符串路线。
- 出现 `.so` 依赖文件，说明 `patchelf` + `glibc-all-in-one` 需要就位。

## 二、原理

checksec 检查的是 ELF 编译/链接期写入的元信息，判定依据固定：

| 保护 | 判定依据 | 关联 section / 标记 |
|---|---|---|
| RELRO | `DT_BIND_NOW` 或 `PT_GNU_RELRO` 段 | `Partial`=仅 RELRO 段；`Full`=还 BIND_NOW |
| Canary | `__stack_chk_fail` 符号存在 | 由 `-fstack-protector(-all/strong)` 引入 |
| NX | `PT_GNU_STACK` 的 `PF_X` 位 | 无该段时默认可执行（老二进制） |
| PIE | ELF `e_type == ET_DYN` | 与 `libc.so` 同为 DYN |
| SHSTK / IBT | `GNU_PROPERTY_X86_FEATURE_1_*` | CET，新版 Ubuntu 才默认开 |
| FORTIFY | `__*_chk` 系列符号 | `_FORTIFY_SOURCE` |

关键推论：
- **Partial RELRO** ⇒ GOT 可写 ⇒ 格式化字符串 / 任意写的第一靶点。
- **Full RELRO** ⇒ GOT 只读 ⇒ 改走 `__malloc_hook` / `__free_hook` / `_IO_FILE` / 栈上返回地址。
- **PIE 关** ⇒ 代码段地址固定 ⇒ 直接 ret2text / ROP，无需泄露。
- **PIE 开 + 无泄露** ⇒ 需要部分覆盖（只改低 12~16 位）或依赖 `fork` 的稳定布局。

## 三、checksec 判读与利用思路

```text
RELRO           STACK CANARY      NX            PIE             RPATH      RUNPATH
Full RELRO      Canary found      NX enabled    PIE enabled     No RPATH   No RUNPATH
```

按「缺失的保护」倒推第一步：

1. **NX 关** → 栈/堆上写 shellcode，`jmp rsp` 或返回到 buffer 地址。
2. **NX 开、PIE 关、无 Canary** → ret2text / ret2libc（GOT 泄露）。
3. **NX 开、PIE 关、有 Canary** → 泄露 canary 后返回到固定 gadget。
4. **PIE 开** → 先找泄露点（格式化字符串、`write(1, buf, n)`、堆上 unsorted bin 残留指针）。
5. **Full RELRO + PIE** → 别想 GOT，走 `_IO_FILE` / 栈迁移 / 堆上函数指针。
6. **SHSTK 开** → 硬件 shadow stack，ROP 基本失效，只有 SIGRETURN 等少数通道。

补充判读命令（checksec 看不到的信息）：

```bash
# 是否动态链接、链接的 interpreter（决定要不要 patchelf）
readelf -l ./pwn | grep -E 'interpreter|GNU_STACK|GNU_RELRO'
# 是否有可写返回点
checksec --file=./pwn --output=json | jq .
# 用题目给的 libc 确认版本与符号偏移
./libc.so.6 2>&1 | head -1 || strings -a libc.so.6 | grep -m1 'GNU C Library'
```

## 四、可直接运行的 exp 脚本

```python
#!/usr/bin/env python3
# 通用探针：一次拿齐保护信息 + 程序内可利用点
from pwn import *
import json, subprocess

context.binary = elf = ELF("./pwn", checksec=False)
context.log_level = "info"

def probe():
    info("arch=%s bits=%s os=%s" % (context.arch, context.bits, context.os))
    # 1) 保护位
    for k, v in elf.checksec().items():
        info(f"{k:12s} = {v}")

    # 2) 关键符号/BSS 偏移（相对二进制基址）
    for name in ("system", "puts", "printf", "read", "gets", "main", "win", "getshell"):
        if name in elf.sym:
            success(f"sym {name:10s} @ {hex(elf.sym[name])}")

    # 3) GOT 是否可写（Partial RELRO 时才有意义）
    for g in ("printf", "free", "strlen", "read", "atoi"):
        if g in elf.got:
            log.info(f"got {g:10s} @ {hex(elf.got[g])}")

    # 4) 常见的 __free_hook / __malloc_hook 是否存在（libc 侧）
    libc = ELF("./libc.so.6", checksec=False)
    for h in ("__free_hook", "__malloc_hook", "__stack_chk_fail", "_IO_2_1_stdout_"):
        off = libc.sym.get(h)
        info(f"libc sym {h:22s} = {hex(off) if off else 'NOT PRESENT'}")

    # 5) 一键找 gadget，不用再手敲 ROPgadget
    rop = ROP(elf)
    for gname in ("pop rdi; ret", "pop rsi; ret", "pop rdx; ret", "leave; ret", "syscall; ret"):
        try:
            g = rop.find_gadget(gname.split("; "))
            if g:
                success(f"gadget {gname:16s} @ {hex(g.address)}")
        except Exception:
            pass

def start():
    if args.REMOTE:
        return remote(args.HOST or "TARGET", int(args.PORT or 1337))
    return process(elf.path)

if __name__ == "__main__":
    probe()
    if args.REMOTE or args.LOCAL:
        p = start()
        p.interactive()
```

patchelf 对齐运行环境（拿到题目 libc 后必做）：

```bash
cp pwn pwn_patched
patchelf --set-interpreter ./ld-2.31.so --set-rpath . pwn_patched
patchelf --replace-needed libc.so.6 ./libc.so.6 pwn_patched
./pwn_patched   # 此时 ldd 应指向题目 libc
```

## 五、常见坑 / 变体

- `checksec` 说 Canary found 但只覆盖到局部缓冲区之外才触发，先确认溢出长度是否跨过 canary。
- `PIE enabled` 的 `ELF.sym` 是**偏移**不是绝对地址，pwntools 已自动按 base=0 处理，配合泄露相加即可。
- 远程 Ubuntu 22.04+ 的 libc 2.35 已移除 `__free_hook`，看到 `NOT PRESENT` 不要以为是脚本错。
- `patchelf` 改 interpreter 后，`ldd` 仍可能显示系统 libc；用 `./ld-2.31.so --library-path . ./pwn_patched` 更可靠。
- 附件是静态链接（`ldd` 显示 `not a dynamic executable`）时，走 ret2syscall / ret2csu，别找 libc。
- 某些题目 `checksec` 显示 `NX enabled` 但存在 `mprotect` 调用点，属于「伪装 NX」。

## 六、参考来源

- [CTF-Wiki: Linux 用户态环境搭建](https://ctf-wiki.org/pwn/linux/user-mode/environment/)
- [CTF-Wiki: 获取地址（信息泄露汇总）](https://ctf-wiki.org/pwn/linux/user-mode/summary/get-address/)
- [HackTricks: Common Binary Protections and Bypasses](https://book.hacktricks.wiki/en/binary-exploitation/common-binary-protections-and-bypasses/index.html)
- [slimm609/checksec.sh](https://github.com/slimm609/checksec.sh)
- [pwntools 官方文档](https://docs.pwntools.com/en/stable/)
- [glibc-all-in-one（多版本 libc 下载与 patchelf 脚本）](https://github.com/matrix1001/glibc-all-in-one)
