---
title: z3 约束求解还原算法
category: reverse
tags: [z3, 约束求解, SMT, 算法还原, 位向量]
signals: [校验是纯算术没有复杂分支, 输入长度固定 10~64, 有大量异或与移位, 需要逆推输入, angr 跑不动但逻辑是直线代码]
difficulty: medium
source: "CTF-Wiki z3 / Z3 Guide / ir0nstone Using Z3"
tools: [z3, Python, IDA, gdb]
updated: 2026-10-22
---

## 一、识别信号（题面长什么样）

- 校验逻辑是**直线代码**（没有分支或很少），大量 `^ + << >>` 运算。
- 输入长度固定（如 `char buf[32]`），最后和目标常量数组比较。
- angr 跑不动（状态爆炸）或根本没有可执行环境（只给了算法片段）。
- 出现了明显的加密轮函数迹象：`rol`/`ror`、`xor key`、`sbox` 查表。
- 题目给了多组「输入-输出」对，可以反推。

## 二、原理

把算法建模成 **SMT 公式**：把每个未知输入字节声明为位向量（BitVec），把每一步运算翻译成 z3 表达式，最后 `add(target == computed)` 求解。

关键类型：

| 用途 | z3 写法 |
|---|---|
| 8 位字节 | `BitVec('c%d' % i, 8)` |
| 32 位字 | `BitVec('x', 32)` |
| 循环左移 | `RotateLeft(x, n)` |
| 逻辑右移 | `LShR(x, n)`（不能用 `>>`，那是算术右移） |
| 有符号右移 | `x >> n` |
| 异或/与/或 | `^`、`&`、`|` |
| 取第 n 位 | `Extract(n, n, x)` |
| 8 位拆 4 个 | `Extract(31, 24, x)` |
| 零扩展 | `ZeroExt(24, b)` |
| 拼接 | `Concat(a, b)` |

**求解顺序**：`s = Solver(); s.add(...); s.check(); s.model()`。

## 三、checksec 判读与利用思路

z3 建模的三步法：

1. **确定未知量**：输入长度、每字节宽度（8 位）、是否有 `\x00` 截断。
2. **逐条翻译**：把反编译出的伪 C 一行对一行改成 z3 表达式，**不要简化**。
3. **加约束**：`== target`，再补可打印字符约束；先不加字符集跑一次看是否有解。

可行性判读：

| 特征 | z3 表现 |
|---|---|
| 线性算术 / 异或 / 移位 | 秒级 |
| 乘法 / 除法 | 中等，可能需 `bitblast` |
| 查表（S-box） | 慢，改用数组或分块 |
| 大循环（>1000 轮） | 很慢，优先考虑轮函数逆推 |

## 四、可直接运行的 exp 脚本

```python
#!/usr/bin/env python3
# 通用：把反编译出的算法翻译成 z3 约束
from z3 import *
import sys

# ---------- 1) 题目给的常量（从 IDA 里 dump 出来） ----------
TARGET = [0x1a, 0x2b, 0x3c, 0x4d, 0x5e, 0x6f, 0x70, 0x81]
KEY    = 0x37
LEN    = len(TARGET)

# ---------- 2) 逐字节建模：常见三种形态 ----------
def model_xor_rotate():
    """形态 A：c[i] ^ key，再循环左移 3 位，等于 target[i]"""
    s = Solver()
    cs = [BitVec(f"c{i}", 8) for i in range(LEN)]
    for i in range(LEN):
        v = RotateLeft(cs[i] ^ BitVecVal(KEY, 8), 3)
        s.add(v == BitVecVal(TARGET[i], 8))
        s.add(cs[i] >= 0x20, cs[i] <= 0x7e)     # 可打印优先
    return s, cs

def model_add_chain():
    """形态 B：累加链 c[0]+c[1]+... 分段等于 target（类似线性方程）"""
    s = Solver()
    cs = [BitVec(f"c{i}", 8) for i in range(LEN)]
    acc = BitVecVal(0, 8)
    for i in range(LEN):
        acc = acc + cs[i]
        s.add(acc == BitVecVal(TARGET[i], 8))
        s.add(cs[i] >= 0x20, cs[i] <= 0x7e)
    return s, cs

def model_32bit_block(block_words):
    """形态 C：每次取 4 字节并用 32 位运算（rol/xor/mul）"""
    s = Solver()
    cs = [BitVec(f"c{i}", 8) for i in range(4 * len(block_words))]
    for j, target32 in enumerate(block_words):
        w = Concat(cs[4*j], cs[4*j+1], cs[4*j+2], cs[4*j+3])
        w = RotateLeft(w ^ BitVecVal(0x9e3779b9, 32), 5)
        w = w + BitVecVal(0x1234567, 32)
        s.add(w == BitVecVal(target32, 32))
    for c in cs:
        s.add(c >= 0x20, c <= 0x7e)
    return s, cs

# ---------- 3) 求解 ----------
def solve(s, cs, name="flag"):
    if s.check() != sat:
        print("unsat —— 约束建错了，或常量抄错")
        return None
    m = s.model()
    ans = bytes([m.eval(c, model_completion=True).as_long() for c in cs])
    print(f"[+] {name} = {ans!r}")
    return ans

# ---------- 4) 「不给常量」时：用输入-输出对反推 ----------
def solve_from_pairs(pairs):
    """
    pairs: [([in bytes], [out bytes]), ...]
    思路：把未知 key 也声明成 BitVec，用多组样本求 key
    """
    s = Solver()
    key = BitVec("key", 8)
    for inp, out in pairs:
        for i, (a, b) in enumerate(zip(inp, out)):
            s.add(BitVecVal(a, 8) ^ key == BitVecVal(b, 8))
    if s.check() == sat:
        k = s.model()[key].as_long()
        print(f"[+] key = {k:#x}")
        return k
    print("[-] 无法确定 key")
    return None

if __name__ == "__main__":
    s, cs = model_xor_rotate()
    solve(s, cs, "xor+rol")
    s2, cs2 = model_add_chain()
    solve(s2, cs2, "add-chain")
    solve_from_pairs([(b"AAAA", bytes(x ^ 0x37 for x in b"AAAA"))])
```

从 IDA 直接导出常量数组（免手工抄）：

```python
# IDAPython：导出 0x404060 处 32 个 dword
import ida_bytes, struct
data = ida_bytes.get_bytes(0x404060, 32 * 4)
vals = struct.unpack("<%dI" % 32, data)
print(", ".join(hex(v) for v in vals))
```

## 五、常见坑 / 变体

- **`>>` 与 `LShR` 搞混**：z3 的 `>>` 是**算术右移**（保留符号位），要逻辑右移必须 `LShR`。
- **忘记加宽度**：`BitVecVal(0x37, 8)` 要显式给位宽，否则默认 32 位导致约束错位。
- **可打印约束太早加**：先不加字符集求解，无解时说明建模错；有位向量解但不可打印再逐个收紧。
- **`if` 分支建模**：分支用 `If(cond, a, b)` 或分路求解，不要直接照抄 C 的 `if`。
- **查表问题**：S-box 用 `Array` + `Select`，或对 256 个值分段求解。
- **`model_completion=True`**：不加这个参数时未约束变量返回 `None`，`as_long()` 会崩。
- **要唯一解**：加 `s.add(Or(cs[0] != ans[0], ...))` 再 check 一次，确认没有多解。

## 六、参考来源

- [CTF-Wiki: z3 约束求解](https://ctf-wiki.org/reverse/tools/constraint/z3/)
- [Z3 Guide（官方教程）](https://microsoft.github.io/z3guide/)
- [z3 Python API 源码](https://github.com/z3prover/z3/blob/master/src/api/python/z3/z3.py)
- [ir0nstone: Using Z3](https://ir0nstone.gitbook.io/notes/misc/using-z3)
- [CTF-Wiki: 常见加密算法和编码识别](https://ctf-wiki.org/reverse/identify-encode-encryption/introduction/)
- [Compiler Explorer（对照 C 与汇编验证轮函数）](https://godbolt.org/)
