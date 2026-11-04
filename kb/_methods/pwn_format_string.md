---
title: 方法卡 · 格式化字符串（偏移定位 / %hhn 分字节任意写 / 多目标改写）
category: pwn
tags: [格式化字符串, fmtstr, "百分号n任意写", "%hhn", GOT覆盖, 任意写, 多目标]
signals: [printf(用户输入) 没有格式串, 输入 %p 回显一串十六进制地址, 回显里出现 0x4141414141414141, 需要把 printf@got 改成 system, 只有一次 printf 机会或输出有长度上限, 目标值很大需要写 0x7f 开头的 libc 地址, 64 位下前 6 个参数读不到输入]
difficulty: medium
source: kb/pwn/format-string-arbitrary-write.md, kb/pwn/format-string-advanced-hhn.md
tools: [pwntools, gdb, pwndbg, IDA, ROPgadget]
updated: 2026-11-03
---

# 方法卡 · 格式化字符串（偏移定位 / %hhn 分字节任意写 / 多目标改写）

## 适用场景

- 反编译里 `printf(buf)`、`fprintf(stdout, buf)`、`syslog(msg)` 参数直接就是用户输入；
- 输入 `%p.%p.%p` 回显一串十六进制地址，其中含你自己输入的 `0x70257025` 形态；
- 输入 `AAAA%6$p` 返回 `0x41414141`，说明缓冲区可直接寻址；
- `checksec` 显示 `Partial RELRO`（GOT 可写），需要把 `printf@got → system`；
- 只给一次 `printf` 机会、`read(0, buf, 0x80)` 限制输入长度，却要连续改 4~8 个地址；
- 目标值很大（`system` 的绝对地址 `0x7f...`），`%n` 一次写要输出 2GB，必须 `%hhn` 拆字节。

## 前置条件

- 知道格式串在参数栈上的**起始下标**（x86-64 前 6 个整数参数走 `rdi,rsi,rdx,rcx,r8,r9`，`printf` 的 `rdi` 是 format 本身，所以**偏移通常 ≥ 7**；32 位全走栈，常见 `%1$p` 起）；
- 知道写入目标的地址可写（glibc 2.30+ 对不可写地址 `%n` 会直接 abort：`*** %n in writable segment detected ***`）；
- 输入通道是 `read` 还是 `gets/scanf`：`\x00` 会被截断，payload 里 `p64(addr)` 必然带 `\x00`；
- 本卡脚本**离线**生成探测串与 `%hhn/%hn/%n` 写入 payload，不执行任何目标程序。

## 步骤

1. **定位偏移**：发 `AAAAAAAA.%1$p.%2$p...`，回显里出现 `0x4141414141414141` 的那个下标就是 `OFFSET`；本卡 `--probe` 直接生成这串。
2. **泄露**：`%<idx>$p` 拿 canary/libc（canary 低字节恒 `\x00`，要手工补回）；`addr + %<idx+1>$s` 读任意地址内容。地址要**拼在 payload 尾部**，因为没法把地址当立即数传给 `printf`。
3. **决定写宽**：目标值 > 0xffffffff 一律 `--width byte`（`%hhn`，每字节 ≤255 字符，8 字节最多 ~2000 字符）；只改低 2 字节用 `--width short`（`%hn`，写钩子指向 one_gadget 最省）。
4. **排序**：按「目标字节模 256 递增」排序，`%hhn` 只取计数低 8 位，**「变小」靠自然回绕**，不用重置计数；`(want - cur) & 0xff` 即填充量。
5. **检查长度与坏字节**：输出字符数、payload 长度、含不含 `\x00\x0a\x0d\x20`，超限就拆成两次 `printf`（第一次低 4 字节 `%hn`，第二次高 4 字节）。
6. **打靶**：`printf@got → system` 后紧跟一行 `/bin/sh`；或 `__stack_chk_fail@got → win`、`atoi@got → 0x401234`。

```powershell
# 生成定位偏移的探测串（64 位，从第 6 个参数开始扫）
.\.venv\Scripts\python.exe kb/_methods/scripts/pwn_format_string.py --probe --offset 6 --count 20
# 把 printf@got 写成 system（8 字节，%hhn 分字节，自动排序）
.\.venv\Scripts\python.exe kb/_methods/scripts/pwn_format_string.py --write 0x404020=0x7f12344ce410 --offset 8 --width byte
# 只改低 2 字节（%hn），适合 hook 指向 one_gadget
.\.venv\Scripts\python.exe kb/_methods/scripts/pwn_format_string.py --write 0x7f12345a1234=0x7f12344ce41b --offset 8 --width short --bytes 2
```

## 脚本

脚本路径：`kb/_methods/scripts/pwn_format_string.py`（纯标准库，离线）

- `build_probe(offset, count, marker=b"AAAAAAAA")`：生成 `marker + .%n$p` 探测串，并给出每个下标对应的模板；
- `plan_writes(targets, width)`：把 `{addr: value}` 拆成字节/半字计划，按模基数递增排序并算每步填充量；
- `build_payload(offset, targets, width="byte", hh_size=8, check_bad=True)`：产出 `addrs + %<d>c%<idx>$hhn...` 完整 payload；
- `payload_stats(payload, limit=None)`：报告 payload 长度、总输出字符数、是否超限、坏字节位置；
- `find_hit(output, marker=b"AAAAAAAA")`：从回显里认出 0x41414141 的下标；
- `--selftest`：固定断言，退出码 0 才算过。

## 失效场景

- **题目写成 `printf("%s", buf)`**：`-Wformat-security` 加固后漏洞消失，本卡完全不适用。
- **glibc 2.30+ 写只读地址**：`%n` 直接 abort，必须确认目标在可写段（`.got.plt`/`.bss`/libc 可写段）。
- **`\\x00` 截断**：`scanf/gets/strcpy` 场景下 `p64(addr)` 的零字节会截断；要么把地址放在最前面并确保前面无 `\\x00`，要么改用 `%hhn` 短地址（`addr` 只给低位）。
- **偏移随环境变化**：环境变量长度会改变栈布局，本地复现远程要 `env -i`；不要把本地 `OFFSET` 当绝对值直接打远程。
- **输出上限**：`%<len>c` 越大越慢，`--width byte` 8 字节最多 ~2000 字符，`read` 长度 0x80 时根本放不下，必须拆两次。
- **`%n` 写 8 字节**：64 位下 `%n` 只写 4 字节（`%ln` 才 8），误用会写坏高 4 字节；写大值一律 `%hhn`。

## 相关文档

- `kb/pwn/format-string-arbitrary-write.md`（基础任意读写、GOT 覆盖、偏移定位片段）
- `kb/pwn/format-string-advanced-hhn.md`（分字节写原理、多目标改写链、受限长度拆分）
- 方法卡：`kb/_methods/pwn_ret2libc.md`（写 `printf@got` 前常需先泄露 libc）
