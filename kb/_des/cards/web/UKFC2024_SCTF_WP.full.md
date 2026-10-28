---
title: "UKFC2024 SCTF WP"
category: web
tags: ["SCTF", "web", "factory-menu", "custom-vm-shellcode", "go-string-rodata", "kernel-uffd-modprobe"]
signals: ["SCTF 2024", "factory-menu", "custom-vm-shellcode", "go-string-rodata", "kernel-uffd-modprobe", "prototypeless-spawn", "rsa-continued-fraction", "snow3g-lfsr", "web_unknown", "SCTF", "factory", "ret2libc", "shellcode", "rodata"]
difficulty: hard
source: "https://www.ctfiot.com/208397.html"
tools: ["Go"]
origin: des-import
origin_kind: cards
updated: 2026-10-24
---
# UKFC2024 SCTF WP

> 赛事：SCTF 2024 | 方向：web | 难度：hard | 工具：Go

## 一句话总结

SCTF 2024：factory 菜单 ret2libc + 自定义 VM shellcode + Go .rodata 拼接 + 内核 userfaultfd tty 劫持。

## 攻击链

1. factory (Pwn): "How many factorys do you want to build" 菜单 + 38 项
2. 24 触发 sort + pop rdi + puts_got 泄 libc
3. libc_base = puts - sym['puts']
4. 第二次 24 触发 pop rdi + ret + system + /bin/sh
5. 自定义 VM 21 个 opcode 0x23-0x33 (xor/exch/push/low_8/shr/shl/rotate/and/syscall)
6. shellcode = b'\x28\x26flag' + xor + syscall 调 open+sendfile
7. Go 字符串在 .rodata 用 x00 填充 + 拼接 gadget 地址 poprax
8. /bin/sh/bin/sh/...` 重复拼接 rax / rdi / rsi
9. Kernel: userfaultfd + modprobe_path 劫持 tty_struct
10. tty_fd=open("/dev/ptmx", O_RDWR)
11. fake_ops[12] = WORK_FOR_CPU_FN + commit_creds(0) + init_cred
12. work_for_cpu_fn 0xffffffff810bd960 (magic 跳转)
13. Web ExP0rtApi: file.replace(/\.\.\//g, '''') 替换绕过 → 改 __proto__ prototype 污染
14. {user: "__proto__", date: 2, reportmessage: {shell: "/bin/bash", env: {BASH_FUNC_whoami%%: ...}}}
15. 通过 require-in-the-middle 拦截 child_process spawn
16. prototypelessSpawnOpts = Object.create(null) 防止 prototype 锁
17. Crypto: N+1 窗口 RSA gift 解 p,q (连分数展开)
18. 雪花 3G LFSR 解密 (32 bit 输出 + 1 bit 输入)

## 关键 payload

```
tty_struct[12] = WORK_FOR_CPU_FN  # kernel EoP
```

## 经验教训

tty_struct[12] = work_for_cpu_fn + commit_creds(0) 是 Linux 内核 EoP 经典手法。

## 标签

factory-menu、custom-vm-shellcode、go-string-rodata、kernel-uffd-modprobe、prototypeless-spawn、rsa-continued-fraction、snow3g-lfsr

## 参考来源

- https://www.ctfiot.com/208397.html
- 原文件：UKFC2024_SCTF_WP.full.md
