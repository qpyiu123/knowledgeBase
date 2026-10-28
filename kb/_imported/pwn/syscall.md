---
title: "syscall"
category: pwn
tags: [NewStar CTF 2025, wp prose]
signals: [syscall]
difficulty: medium
source: "https://github.com/pj-newstar/wiki-docs/blob/1a0f2ba21a30f950276396118b315eef0328371c/docs/wp/2025/week2/pwn/syscall.md"
tools: []
origin: imported
origin_id: official-e74a1c4841251401115e01
origin_sha256: bedab84497760147e9ee21474a01d895d11b771c29ec6d2e41ea56be3efdd6c6
origin_event: "NewStar CTF 2025"
origin_kind: wp_prose
license: "MIT"
updated: 2026-10-23
---
# NewStar CTF 2025 / syscall

> 来源：NewStar CTF 2025  |  类型：wp_prose  |  https://github.com/pj-newstar/wiki-docs/blob/1a0f2ba21a30f950276396118b315eef0328371c/docs/wp/2025/week2/pwn/syscall.md

import Container from '@/components/docs/Container.vue'

# syscall


本题考查需要写入 `/bin/sh` 的 ret2syscall 利用。

## 分析

程序是静态链接，32 位的。

漏洞点在 `read` 的溢出，并且没有 `canary` 的保护，偏移是 `0x16`


在 IDA 中，按 <kbd>⇧ shift</kbd> <kbd>F12</kbd> 查看字符串，发现没有 `/bin/sh` 字符串，程序也没有找到后门函数，因此考虑利用 ret2syscall。

## ret2syscall 介绍

### 系统调用

函数系统调用，指运行在**用户空间**的程序向**操作系统内核**请求需要更高权限运行的服务。系统调用提供用户程序与操作系统之间的接口。大多数系统交互式操作需求在内核态执行。如设备 IO 操作或者进程间通信。

Linux 的系统调用通过 `int 80h`<span data-desc>（32 位）</span> 或 `syscall`<span data-desc>（64位）</span>实现，用系统调用号来区分入口函数。

**应用程序调用系统调用的过程是：**

1. 把系统调用的编号存入 `EAX`；
2. 把函数参数存入其它通用寄存器；
3. 触发 `0x80` 号中断<span data-desc>（`int 0x80`）</span>或 `call syscall`。

#### 系统调用号

可查询[系统调用表](https://blog.csdn.net/winter2121/article/details/119845443)来获取系统调用号，如 32 位程序 `execve()` 的系统调用号位 `0xb`.

#### 参数传递

| 系统 | 顺序                                        |
| ---- | ------------------------------------------- |
| 32位 | `eax` → `edx` → `ecx` → `ebx`               |
| 64位 | `rdi` → `rsi` → `rdx` → `rcx` → `r8` → `r9` |

### 具体实现

#### 32位

一般通过调用 `execve("/bin/sh", NULL, NULL)` 来 getshell


##### ROPgadgets工具


## 做题

由于程序没有 `binsh` 字符串，应该先构造一个 `read` 将 `/bin/sh` 写入 `.bss` 段中。

先利用 ROPgadget 查找控制寄存器的值，32 位系统调用号存在 `eax` 中


读取 `/bin/sh` 后就可以构造 `execve("/bin/sh",0,0)` 完成利用了；

还有一点要注意的就是，查找 `int 80` 时，使用 `ROPgadget --binary rop --only 'int'` 查找的 `int 80` 后面没有 `ret` 导致 ROP 链进行不下去，可以用 `ROPgadget --binary rop --opcode cd80c3` 查找。

exp：
