---
title: "Bad Asm"
category: pwn
tags: [NewStar CTF 2024, wp prose]
signals: [Bad Asm]
difficulty: medium
source: "https://github.com/pj-newstar/wiki-docs/blob/1a0f2ba21a30f950276396118b315eef0328371c/docs/wp/2024/week2/pwn/bad-asm.md"
tools: []
origin: imported
origin_id: official-cabb4c9808fe0332438d52
origin_sha256: 27b8116745dfc4d07cecd16741f7d2a86b77c6f60f88240517bfc39fa9e53d22
origin_event: "NewStar CTF 2024"
origin_kind: wp_prose
license: "MIT"
updated: 2026-10-23
---
# NewStar CTF 2024 / Bad Asm

> 来源：NewStar CTF 2024  |  类型：wp_prose  |  https://github.com/pj-newstar/wiki-docs/blob/1a0f2ba21a30f950276396118b315eef0328371c/docs/wp/2024/week2/pwn/bad-asm.md

# Bad Asm

程序过滤 `syscall` / `sysenter` / `int 0x80` 的汇编指令的机器码。

`strcpy` 限制了 shellcode 的机器码中不能出现 `0x00`.

开启的可执行的段具有写的权限，用异或搓出来 syscall 的机器码之后用 `mov` 写入到 shellcode 后面，中间用 `nop` 连接一下就行了。

由于程序清空了 `rsp` `rbp` 寄存器，我们需要恢复一下 `rsp` 的值，任意一个可读写的段即可，否则 `push` 操作会寄掉。

可以用异或先把 syscall 的机器码插入到当前 shellcode 的后面来执行 `read` 的 syscall，利用 `read` 在旧的 shellcode 后面插入 `execve("/bin/sh", 0, 0)` 的 shellcode，第二次输入的 payload 中 `0x42` 个 `a` 的作用是覆盖掉旧的 shellcode，毕竟执行过了也没用了。

恢复 `rsp` 的作用是为了能够正常执行 `push` `pop` 指令，这里 `push` `pop` 指令位于 `shellcraft.sh()` 生成的 shellcode 中。否则其生成的 shellcode 无法正常执行。


除了异或的方法，我们可以用另一种方法布置 syscall 的机器码。

题目检查 syscall 的时候采用的方法是检测相邻两个字节，所以我们可以将两个字节分别用一个汇编指令写入到内存中，比如用 `mov`，这样我们就可以将其机器码 `0xf 0x5` 拆开，而不是连续的字节，这样也可以通过检查。


最后保证控制执行流执行到写入的 `0f05` 那里就行了。

下面的 EXP 中直接异或搓了一个 `execve("/bin/sh", 0, 0)`，这样也是可以的。


除此之外，由于我们把栈放在可执行段上面了，我们可以直接异或整出来 syscall 的机器码然后 push 到栈上面，最后 `jmp rsp` 即可。由于这种方法我们并不依赖 `nop` 指令进行连接，在送 Payload 的时候可以去掉 `ljust` 了。


在把 `/bin/sh\x00` push 到栈上面的时候，我们为了清除最后的 `0x00`，采用了异或的方法。除了这种方法外我们可以调整一下这个字符串，比如我们可以改为使用 `/bin///sh`，`shellcraft.sh()` 生成的 shellcode 采用的就是这种方法。

按照这种方法更改的 shellcode，也是可以拿到 shell 的。
