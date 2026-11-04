---
title: 方法卡 · pwn ret2libc（GOT 泄露 → libc 基址 → system("/bin/sh")）
category: pwn
tags: [ret2libc, GOT泄露, ASLR, libc-database, 栈对齐, ROP, ret2csu]
signals: [附件同时给了 pwn 和 libc.so.6, 程序只有 puts/write 没有 system, NX 开启且二进制里没有 win 函数, 有 canary 但没开 PIE, 程序打印菜单后读输入且能回到 main, 远程与本地 libc 版本不一致, ROPgadget 找不到 pop rsi]
difficulty: medium
source: kb/pwn/ret2libc-offset-leak.md, kb/pwn/ret2csu.md
tools: [pwntools, ROPgadget, ropper, gdb, libc-database, patchelf]
updated: 2026-11-03
---

# 方法卡 · pwn ret2libc

## 适用场景

- 附件压缩包里同时有 `pwn` 和 `libc.so.6`（常常还有 `ld-2.31.so`）——最明确的信号；
- 程序只用 `read` + `puts`/`write`，没有 `system`，但 `puts@plt` 存在；
- `checksec` 显示 `NX enabled`、`No PIE`，GOT 可读；
- 题面写「ASLR 已开启」，暗示必须先泄露再算；
- 溢出一次后程序能回到 `main`（末尾 `read` 或 `while`），可做两次交互；
- 找不到 `pop rsi`/`pop rdx` 时，接 `__libc_csu_init` 的 ret2csu 两段 gadget。

## 前置条件

- 必须用**题目给的 libc**（`patchelf --set-interpreter ./ld-2.31.so --set-rpath . ./pwn` 或 `LD_PRELOAD`），系统 libc 只用于粗试；
- 需要知道溢出偏移、`pop rdi; ret`、`ret` 三个量（本卡脚本用 `--offset/--pop-rdi/--ret` 显式给出）；
- 需要 8 字节泄露的真实地址（`puts`/`write` 输出）；本卡脚本负责**地址运算、对齐校验、payload 布局、libc 低 12 位候选比对**，不联网、不连靶机。

## 步骤

1. **定位泄漏点**：先确认 GOT 里目标符号已被解析（程序调用过才能泄露真实地址）；`Full RELRO` 只影响写 GOT，**读 GOT 泄露仍然有效**。
2. **算 libc base**：`libc_base = leaked - libc.sym[name]`；再取 `system = base + sym['system']`、`binsh = base + next(libc.search(b"/bin/sh\x00"))`。
3. **验版本**：拿泄露值与候选 libc 的符号偏移做 `& 0xfff` 低位比对（本卡 `--match` 子命令），低位不符就换 libc；未知 libc 用 `libc-database/find puts <低12位> <后3位>`。
4. **对齐**：64 位 `system` 内部走 `movaps`，要求调用时 `rsp % 16 == 8`；把 payload 长度喂给脚本 `--align-auto`，它会告诉你是否需要多插一个 `ret`。
5. **两次利用**：`pop rdi; puts_got; puts_plt; main` → 接泄露 → 第二轮 `pop rdi; binsh; ret; system`；回不到 `main` 就叠一条长链或用 csu（`rbx=0, rbp=1`，`call` 后补 8 字节填充 + 6 个 pop + ret 位共 7 个 8 字节）。
6. **兜底**：`puts` 输出遇 `\n` 截断，`recvuntil(b"\n").ljust(8, b"\x00")`；`/bin/sh` 被过滤就 `read` 写进 `.bss` 再传 `.bss` 地址。

```powershell
# 已知泄露值 + libc 符号偏移，算 base 与 system
.\.venv\Scripts\python.exe kb/_methods/scripts/pwn_ret2libc.py --leak 0x7f1234500690 --sym puts=0x875a0 --sym system=0x55410 --binsh 0x1b75aa
# 校验候选 libc 是否与泄露值同版本
.\.venv\Scripts\python.exe kb/_methods/scripts/pwn_ret2libc.py --match 0x7f1234500690 --sym puts=0x875a0
# 生成两段 payload（含栈对齐判断）
.\.venv\Scripts\python.exe kb/_methods/scripts/pwn_ret2libc.py --build --offset 0x48 --pop-rdi 0x401293 --ret 0x40101a --leak-func puts
```

## 脚本

脚本路径：`kb/_methods/scripts/pwn_ret2libc.py`（纯标准库，离线）

- `libc_base(leaked, sym_off)` / `resolve(base, offs)`：基址与绝对地址换算，越界与非法地址明确报错；
- `check_match(leaked, sym_off, page=0x1000)`：按低 12 位比对，不符直接拒绝（防止拿错 libc）；
- `align_gap(chain_len, start_align=8)`：判断 `rsp%16` 是否需要插入 `ret`；
- `build_leak_payload` / `build_execve_payload`：按 8 字节小端拼 ROP，自动决定是否插对齐 `ret`；
- `csu_chain`：无 `pop rsi` 时拼 `__libc_csu_init` 两段 gadget；
- `--selftest`：固定向量断言，退出码 0 才算过。

## 失效场景

- **远程 libc 与本地不同**：最经典的翻车点，偏移全错、`system` 直接崩；必须 `patchelf` 成题目 libc。
- **`puts` 吞 `\n` 或 `\x00`**：`puts` 遇 `\x00` 直接停，泄露可能只有 6 字节，务必 `ljust(8, b"\x00")`；`read` 泄露则用 `recvn(8)`。
- **栈没对齐崩在 `movaps`**：多插/少插一个 `ret` 都可能好或崩，必须按 payload 实际长度算，不能凭经验。
- **程序不回到 `main`**：只能泄露一次时改用栈迁移或 `ret2dlresolve`，本卡的两段模板不适用。
- **GCC 8+ 无 `__libc_csu_init`**：ret2csu 退化为不可用，要找 `pop rdx; pop rbx; ret` 或走 SROP。
- **PIE 开启**：`elf.got/plt` 不再是绝对地址，得先泄露代码基址再加一次偏移。

## 相关文档

- `kb/pwn/ret2libc-offset-leak.md`（泄露原理、libc-database 反查、常见坑）
- `kb/pwn/ret2csu.md`（`__libc_csu_init` 两段 gadget 与 7 个 8 字节填充）
- 方法卡：`kb/_methods/binary_patch.md`（拿到程序后打补丁调偏移）
