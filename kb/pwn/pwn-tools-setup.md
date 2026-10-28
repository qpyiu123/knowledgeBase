---
title: Pwn 环境搭建（pwntools / pwndbg / patchelf / glibc-all-in-one）
category: pwn
tags: [环境搭建, pwntools, pwndbg, patchelf, glibc-all-in-one, 录题]
signals: [新机器要配 pwn 环境, 本地能过远程不过, ldd 显示系统 libc 与题目不一致, 需要多版本 libc 切换, 想用 pwndbg 看堆]
difficulty: easy
source: "pwntools 文档 / pwndbg / glibc-all-in-one / patchelf"
tools: [pwntools, pwndbg, gef, patchelf, glibc-all-in-one, checksec, one_gadget]
updated: 2026-10-22
---

## 一、识别信号（题面长什么样）

- 附件里有 `libc.so.6` + `ld-2.x.so`，但本地跑起来 `ldd ./pwn` 显示的是 `/lib/x86_64-linux-gnu/libc.so.6`。
- 本地打通远程崩、或偏移在远程算不出来 —— 环境不一致。
- 需要同时准备 2.23 / 2.27 / 2.31 / 2.35 多套 libc。
- 想在 gdb 里用 `heap`、`bins`、`vis_heap_chunks` 这些命令。
- 在 Windows/WSL 下写题，需要和 Docker 里的 Ubuntu 环境对齐。

## 二、原理

pwn 环境的核心矛盾：**二进制在编译时链接了一个特定版本的 libc，运行时用的是本机 libc**。两者版本不同 → 符号偏移不同 → 泄露算出的 base 是错的。

解决办法两选一：
1. **patchelf**：把 ELF 的 `PT_INTERP`（动态加载器）和 `DT_NEEDED`（依赖的 libc）改成题目目录下的文件。
2. **Docker / WSL**：直接用题目版本的发行版镜像跑。

pwndbg 提供堆相关调试命令；`glibc-all-in-one` 负责批量下载与切换。

## 三、checksec 判读与利用思路

环境自检清单（依次过）：

```text
1. python3 -c "import pwn; print(pwn.__version__)"        # pwntools
2. gdb -q -ex "pi import pwndbg" -ex q                    # pwndbg 已装
3. patchelf --version                                     # patchelf
4. which one_gadget ROPgadget ropper seccomp-tools         # 常用工具
5. ldd ./pwn_patched                                      # 指向题目 libc
6. ./pwn_patched 与 nc 远程 行为一致
```

**判定"环境对不对"** 的唯一标准：同一份 exp 本地与远程结果一致。

## 四、可直接运行的 exp 脚本

### 1. 一键安装（Ubuntu 20.04 / 22.04 / WSL2）

```bash
sudo apt update
sudo apt install -y python3-pip python3-dev git libssl-dev libffi-dev \
    build-essential gcc-multilib gdb patchelf file binutils \
    netcat-openbsd socat qemu-user qemu-system-x86
pip3 install --upgrade pwntools ropgadget z3-solver angr
gem install one_gadget                    # 需要 ruby
```

### 2. pwndbg（替代默认 gdb 配置）

```bash
git clone https://github.com/pwndbg/pwndbg ~/pwndbg
cd ~/pwndbg && ./setup.sh
# 验证
gdb -q -ex "pi import pwndbg" -ex q
```

常用命令速查：

| 命令 | 作用 |
|---|---|
| `heap` | 列出所有 chunk |
| `bins` | 列出 tcache/fastbin/unsorted/large |
| `vis_heap_chunks` | 图形化堆布局 |
| `canary` | 显示 canary |
| `telescope $rsp` | 展开栈 |
| `vmmap` | 内存布局（找 libc base） |

### 3. glibc-all-in-one（多版本 libc）

```bash
git clone https://github.com/matrix1001/glibc-all-in-one ~/glibc-all-in-one
cd ~/glibc-all-in-one
./update_list                              # 更新可用版本
cat list                                   # 看所有版本
./download 2.31-0ubuntu9.9_amd64           # 下载指定版本
./download libc6_2.35-0ubuntu3_amd64       # 也可以下 deb 包版本
ls libs/                                   # 下载结果
```

### 4. patchelf 脚本（把二进制的 libc 换掉）

```bash
#!/bin/bash
# usage: ./patch.sh ./pwn ./libc.so.6 ./ld-2.31.so
set -e
BIN=$1; LIBC=$2; LD=$3; OUT=${1}_patched
cp "$BIN" "$OUT"
chmod +x "$OUT"
patchelf --set-interpreter "$(realpath $LD)" "$OUT"
patchelf --set-rpath "$(dirname $(realpath $LIBC))" "$OUT"
patchelf --replace-needed libc.so.6 "$(realpath $LIBC)" "$OUT" 2>/dev/null || true
echo "[*] $OUT"
ldd "$OUT"
```

### 5. pwntools 里最常写的一段 exp 模板

```python
#!/usr/bin/env python3
from pwn import *

context.binary = elf = ELF("./pwn_patched", checksec=False)
context.arch   = elf.arch
context.log_level = "info"
libc = ELF("./libc.so.6", checksec=False)

def start():
    if args.REMOTE:
        return remote(args.HOST or "TARGET", int(args.PORT or 1337))
    p = process(elf.path)
    if args.GDB:
        gdb.attach(p, gdbscript="""
            set pagination off
            b *main
            continue
        """)
    return p

# 便捷 shim：把常见工具都挂到 pwntools 命名空间
def gadgets(binary, pattern):
    from subprocess import check_output
    out = check_output(["ROPgadget", "--binary", binary, "--only", "ret"]).decode()
    return [l.split(":")[0] for l in out.splitlines() if pattern in l]

if __name__ == "__main__":
    p = start()
    if args.CORE:
        core = p.corefile
        info(f"rsp = {hex(core.rsp)}  rip = {hex(core.rip)}")
        info(f"offset = {cyclic_find(core.read(core.rsp, 4))}")
    p.interactive()
```

### 6. 用 Docker 对齐远程（最省心）

```bash
# 直接把题目官方 Dockerfile 用起来
docker build -t challenge ./chall_dir
docker run -it --rm -p 9999:9999 challenge
# 本地连通性验证
nc 127.0.0.1 9999
```

## 五、常见坑 / 变体

- **`patchelf` 后 `ldd` 还显示系统 libc**：`--set-rpath` 用的是目录，要确保目录里有 `libc.so.6`；改用 `./ld-2.31.so --library-path . ./pwn`。
- **`gdb attach` 卡住**：pwndbg 的 `ptrace` 权限问题，`echo 0 > /proc/sys/kernel/yama/ptrace_scope`。
- **WSL 下 gdb 附不上**：用 `gdbserver` + `target remote`，或在 WSL 里原生跑。
- **`one_gadget` 需要 ruby**：`apt install ruby ruby-dev`，失败就改用 pwntools + 手算。
- **`glibc-all-in-one` 下载慢**：把 `download` 换成手动下载 deb 后 `dpkg -x`。
- **`pwntools` 与 `angr` 冲突**：分开 venv，避免 `unicorn` 版本互踩。
- **`checksec` 命令找不到**：`pip install checksec.py` 或直接用 `pwn checksec`。

## 六、参考来源

- [pwntools 官方文档](https://docs.pwntools.com/en/stable/)
- [pwntools 进程与交互（tubes）](https://docs.pwntools.com/en/stable/tubes.html)
- [pwndbg 仓库与命令文档](https://github.com/pwndbg/pwndbg)
- [pwndbg features 文档](https://github.com/pwndbg/pwndbg/blob/dev/docs/features.md)
- [glibc-all-in-one](https://github.com/matrix1001/glibc-all-in-one)
- [NixOS/patchelf](https://github.com/NixOS/patchelf)
- [CTF-Wiki: Linux 用户态环境搭建](https://ctf-wiki.org/pwn/linux/user-mode/environment/)
