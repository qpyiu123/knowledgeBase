---
title: 补丁与 crackme 型题目（patch 思路与 keygen 生成）
category: reverse
tags: [crackme, patch, keygen, 注册机, nop]
signals: [程序要求输入序列号或注册码, 输入错误弹窗 "Invalid license", 验证函数里只有一个条件跳转决定成败, 题面要求「给出注册机」或「patch 后能跑」, 二进制校验文件自身哈希, 有 trial 剩余次数或时间限制, 弹窗字符串里有 "Correct" 与 "Wrong" 并列, 题目提供输入后输出 flag 的程序, 提示「爆破」「patch」「keygen」]
difficulty: easy
source: "IDA / x64dbg / keygenme 传统"
tools: [ida, x64dbg, python, keystone]
updated: 2026-10-22
---

## 一、识别信号（题面长什么样）

- 程序启动后要求 `Enter your serial:`，错误时弹 `Invalid license` / `Wrong password`。
- 成功分支与失败分支在反汇编里**只差一条 `jz`/`jnz`**。
- 题面要求提交 **注册机（keygen）**、**patch 后的二进制**、或**能通过校验的输入**。
- 有 trial 计数：`if (++count > 5) exit()`。
- 程序启动时校验自身哈希或文件大小（自校验）。
- 题面提示：`crackme`、`爆破`、`patch`、`keygen`、`注册机`、`license`。
- 附件里有 `README` 说明"输入正确则输出 flag"。

## 二、原理

### 1. crackme 的三类解法

| 类型 | 做法 | 适用 |
|---|---|---|
| **爆破（Brute-force patch）** | 改 `jz` → `jnz`，或 `call check` → `nop` | 只需"通过"，不要 flag 语义 |
| **Keygen（注册机）** | 还原算法，写脚本生成有效输入 | 需要任意用户/任意输入都通过 |
| **内存破解（动态）** | 改寄存器/内存值 | 静态难定位时 |

### 2. patch 的三种粒度

```
① 跳转反转：74 xx (JZ) → 75 xx (JNZ)
② 无条件化：74 xx → EB xx (JMP)（后面填 NOP）
③ 直接跳过：E8 xx xx xx xx (CALL) → 90 90 90 90 90 或 5 个 NOP
④ 返回成功：B8 01 00 00 00 C3  (mov eax,1; ret)
```

x64 上 `MOV EAX,1; RET` = `B8 01 00 00 00 C3`；x86 一样。

### 3. 自校验的处理

- 程序对自身哈希做校验 → 直接 patch 会失败。
- 对策：找**校验函数**，patch 它的返回值；或改哈希常量（但会导致哈希本身不符）。

### 4. Keygen 的还原思路

1. 找到 `check(serial)` 函数。
2. 判断 serial 与用户名/常量之间的关系。
3. 依次尝试：
   - **纯比较**：`strcmp(input, "flag{...}")` → 直接抄字符串。
   - **算术**：`sum == 0x1A2B` → 写反解。
   - **校验和**：每字节的 `(c*i) ^ 0x33` 加起来等于常量。
   - **加密**：输入经 TEA/AES 加密后与常量比较 → 解密即可。
4. 用 Python 实现**正向算法**，生成合法输入。

## 三、解题步骤

1. **运行程序**：输入 `AAAA`，看错误字符串。
2. **定位比较**：在 IDA 里搜 `Wrong` / `Invalid` 字符串 → 交叉引用 → 找上游 `call`。
3. **动态验证**：x64dbg 在比较处下断，输入不同值，看寄存器变化。
4. **爆破**：patch 掉关键 `jz`，保存再跑。
5. **Keygen**：反向解出算法后写 Python。
6. **自校验**：若 patch 后崩溃，先 patch 自校验函数（返回 1）。
7. **验证**：`./patched` 或 `python keygen.py` 输出注册码。

## 四、可直接运行的脚本

最小 crackme（练手用）：

```c
// check.c —— 编译：gcc -O0 -o check check.c
#include <stdio.h>
#include <string.h>

int main(void) {
    char buf[64];
    printf("serial: ");
    if (!fgets(buf, sizeof(buf), stdin)) return 1;
    buf[strcspn(buf, "\n")] = 0;
    if (strlen(buf) != 16) { puts("Invalid length"); return 1; }
    unsigned int sum = 0;
    for (int i = 0; i < 16; i++) sum += (unsigned char)buf[i] * (i + 1);
    if (sum == 0x1A2B) { puts("Correct! flag{y0u_g0t_1t}"); return 0; }
    puts("Wrong.");
    return 1;
}
```

patch 脚本（用 keystone / capstone 自动定位并改指令）：

```python
from keystone import Ks, KS_ARCH_X86, KS_MODE_64

def patch_jz_to_jnz(path, file_off):
    """0x74 (JZ rel8) -> 0x75 (JNZ)，0F 84 (JZ rel32) -> 0F 85"""
    data = bytearray(open(path, "rb").read())
    if data[file_off] == 0x74:
        data[file_off] = 0x75
    elif data[file_off] == 0x0F and data[file_off + 1] == 0x84:
        data[file_off + 1] = 0x85
    else:
        raise SystemExit("not a JZ at 0x%x: 0x%02x" % (file_off, data[file_off]))
    open(path + ".patched", "wb").write(data)
    print("patched ->", path + ".patched")

ks = Ks(KS_ARCH_X86, KS_MODE_64)
print(bytes(ks.asm("mov eax, 1; ret")[0]).hex())     # b801000000c3
```

用 pefile 找 `Wrong` 字符串并在附近打 NOP：

```python
import pefile

pe = pefile.PE("check.exe")
target = b"Wrong.\x00"
for sec in pe.sections:
    data = sec.get_data()
    idx = data.find(target)
    if idx >= 0:
        print("Wrong @ section", sec.Name, "rva", hex(sec.VirtualAddress + idx))
        break
```

自动把 `call check` 替换成 "mov eax,1; ret"：

```python
from keystone import Ks, KS_ARCH_X86, KS_MODE_64

ks = Ks(KS_ARCH_X86, KS_MODE_64)
code, _ = ks.asm("mov eax, 1; ret")
print(bytes(code).hex())        # b8010000c0c3 → b8 01 00 00 00 c3
```

Python 版 keygen（对应上面 check.c 的算法）：

```python
# sum(buf[i] * (i+1)) == 0x1A2B，取 16 字节可打印字符
TARGET = 0x1A2B
BASE = ord('A')

buf = [BASE] * 16
cur = sum(c * (i + 1) for i, c in enumerate(buf))

# 只用最后一个字节调整（权重 16）
diff = TARGET - cur
if diff % 16 == 0 and 0 <= BASE + diff // 16 <= 126:
    buf[15] = BASE + diff // 16
    print("".join(map(chr, buf)))
else:
    # 用前两个字节微调（权重 1 与 2）
    for d in range(-32, 33):
        nb = list(buf); nb[0] = BASE + d
        rest = TARGET - sum(c * (i + 1) for i, c in enumerate(nb))
        if rest % 16 == 0:
            nb[15] = BASE + rest // 16
            if 32 <= nb[15] <= 126 and 32 <= nb[0] <= 126:
                print("".join(map(chr, nb))); break
```

用 pwntools 批量验证注册机：

```python
from pwn import process

def check(serial: str) -> bool:
    p = process("./check")
    p.sendline(serial.encode())
    out = p.recvall(timeout=3)
    return b"Correct" in out

for s in ["AAAAAAAABBCCCCCC", "ABCDEFGHIJKLMNOP"]:
    print(s, check(s))
```

## 五、常见坑 / 变体

- **PIE/ASLR 偏移**：RVA 与文件偏移不同，`jz` 在 `.text` 里要算 `file_off = rva - VirtualAddress + PointerToRawData`。
- **patch 后崩溃**：可能改了长度（`jz rel8` 只能跳 ±127），越界就换 `jnz` 反转而不是插 NOP。
- **自校验**：程序对 `.text` 做 CRC → 需同时 patch 校验函数（返回 1）。
- **签名校验**：Windows 的 Authenticode 签名会失效，要 `osslsigncode` 重签或去掉。
- **keygen 无解**：如果算法含加密，就**逆向加密函数**，别暴力。
- **变体：多阶段输入**（用户名 + 序列号）→ 序列号通常由用户名计算（`MD5(name)[:8]`）。
- **变体：反调试 + crackme** → 先绕过反调试（见 `decompile-failure-dynamic-tuning.md`）。
- **变体：Go/Rust 写的小体积 crackme** → 字符串比较在 runtime 里，断 `runtime.memequal`。
- **变体：要求"最少修改字节"** → 优先考虑反转跳转（1 字节）。
- **工具**：`keypatch`（IDA 内置）、`Keystone`、`LIEF`（改节区）、`pwntools`（验证）。

## 六、参考来源

- [IDA Python API](https://github.com/idapython/src)
- [x64dbg](https://github.com/x64dbg/x64dbg)
- [keystone-engine/keystone](https://github.com/keystone-engine/keystone)
- [LIEF — Library to Instrument Executable Formats](https://github.com/lief-project/LIEF)
- [Unicorn Engine](https://github.com/unicorn-engine/unicorn)
- [pwntools](https://docs.pwntools.com/en/stable/)
