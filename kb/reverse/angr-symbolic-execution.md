---
title: angr 符号执行求 flag
category: reverse
tags: [angr, 符号执行, 约束求解, CFG, 自动化]
signals: [校验逻辑复杂且分支极多, 输入逐字节比较, 有大量 if/else 且无法反推, 需要自动化跑出正确输入, 程序里只有一个 check 函数]
difficulty: medium
source: "angr 官方文档 / angr-doc examples / CTF-Wiki angr"
tools: [angr, claripy, z3, IDA, gdb]
updated: 2026-10-22
---

## 一、识别信号（题面长什么样）

- 校验函数里有几十个 `if`，每次只比一个字节，人工推导要几小时。
- 输入长度已知（`read(0, buf, 32)`），成功分支里打印 `"Correct"` / `"Right"`。
- 有大量算术运算（`+ - ^ <<`）作用于输入，最后与常量比较。
- 程序里只有一个 `check(char *)`，其余都是 IO。
- 常规逆向（反编译 + 手算）成本远高于自动化。

## 二、原理

angr 基于 **VEX IR** 做符号执行：

1. **符号化输入**：把输入缓冲区设为 `claripy.BVS`（symbolic bitvector）。
2. **模拟执行**：从入口跑到 `find` 地址，状态空间用 `SimulationManager` 管理。
3. **约束收集**：每次条件分支都往路径约束里加一条表达式。
4. **求解**：到达 `avoid`/`find` 时用 z3 解出满足所有约束的具体值。

关键概念：

| 概念 | 作用 |
|---|---|
| `entry_state` / `blank_state` | 起始状态（前者从入口跑，后者任意地址） |
| `simgr.explore(find=, avoid=)` | 找目标地址，避开失败地址 |
| `state.solver.eval(...)` | 求具体值 |
| `state.posix.dumps(fd)` | 取某个 fd 的输出 |
| `state.solver.add(...)` | 手工加约束（如字符集限制） |
| `CFGFast` / `CFGEmulated` | 构建控制流图加速定位 |
| `SimProcedure` | 替换外部函数（hook `strcmp` 等） |

## 三、checksec 判读与利用思路

angr 的「判读」是**可行性判读**：

| 条件 | 可行性 |
|---|---|
| 无大量循环展开 | 高（秒级） |
| 输入 32 字节以内 | 高 |
| 有 `ptrace`/反调试 | 需 hook 掉 |
| 有 `scanf`/`read` 且有长度限制 | 中（要 hook 输入函数） |
| 有 freopen 文件读输入 | 中（手工 preload 文件） |
| 大量加密运算（AES） | 低（状态爆炸），改用 z3 手工建模 |

标准写法顺序：先定位 `main` → 找 success/fail 地址 → 构造输入 → explore。

## 四、可直接运行的 exp 脚本

```python
#!/usr/bin/env python3
from pwn import *
import angr, claripy, sys

context.log_level = "info"

BIN          = sys.argv[1] if len(sys.argv) > 1 else "./chall"
FIND_ADDR    = 0x401234        # 成功分支（打印 Correct 的地址）
AVOID_ADDR   = 0x401256        # 失败分支（打印 Wrong 的地址）
INPUT_LEN    = 32              # 输入长度
INPUT_ARG    = None            # 若输入通过参数传递，填参数序号（0=argv0）；用 stdin 则保持 None

def build_state(proj, flag_bytes):
    st = proj.factory.entry_state(
        stdin=angr.SimFileStream(name="stdin",
                                 content=claripy.Concat(*flag_bytes) + b"\n"),
        add_options={
            angr.options.ZERO_FILL_UNCONSTRAINED_MEMORY,
            angr.options.ZERO_FILL_UNCONSTRAINED_REGISTERS,
            angr.options.SYMBOL_FILL_UNCONSTRAINED_MEMORY,
            angr.options.SYMBOL_FILL_UNCONSTRAINED_REGISTERS,
        },
    )
    # 限制为可打印字符：省一大半时间（二进制输入题请删掉这三行）
    for b in flag_bytes:
        st.solver.add(b >= 0x20)
        st.solver.add(b <= 0x7e)
    return st

def solve(BIN, find, avoid, length=INPUT_LEN):
    proj = angr.Project(BIN, auto_load_libs=False)
    flag_bytes = [claripy.BVS(f"c{i}", 8) for i in range(length)]
    st = build_state(proj, flag_bytes)
    simgr = proj.factory.simgr(st)
    simgr.explore(find=find, avoid=avoid, num_find=1,
                  enable_veritesting=True)      # 大函数必开，提速 10x+
    if not simgr.found:
        warn("没找到路径：检查 find/avoid 地址、输入方式、是否被反调试拦截")
        warn("当前活跃状态数: %d" % len(simgr.active))
        return None
    found = simgr.found[0]
    answer = [found.solver.eval(b) for b in flag_bytes]
    return bytes(answer), found.posix.dumps(1)

def find_addrs(BIN, want=b"Correct"):
    """按字符串自动定位 find/avoid 地址（比手工翻 IAT 快）"""
    proj = angr.Project(BIN, auto_load_libs=False)
    hits = []
    for sym in proj.loader.main_object.symbols:
        if sym.name and want.decode(errors="ignore") in sym.name:
            hits.append(hex(sym.rebased_addr))
    # 更稳的是在 IDA 里对字符串做 XREF 找引用的比较分支
    return hits

if __name__ == "__main__":
    if FIND_ADDR == 0x401234:
        warn("请先在 IDA/Ghidra 里确认 FIND_ADDR / AVOID_ADDR 再跑")
    res = solve(BIN, FIND_ADDR, AVOID_ADDR)
    if res:
        ans, out = res
        success(f"input = {ans!r}")
        print(out.decode(errors="ignore"))
```

hook 掉 `strcmp`/`ptrace` 等外部函数（避免跟车进库）：

```python
#!/usr/bin/env python3
import angr, claripy

BIN = "./chall"
proj = angr.Project(BIN, auto_load_libs=False)

@proj.hook(addr=proj.loader.find_symbol("strcmp").rebased_addr, length=5)
def hook_strcmp(state):
    """让 strcmp 直接返回 0，跳过库函数"""
    state.regs.rax = 0

@proj.hook(addr=proj.loader.find_symbol("ptrace").rebased_addr, length=5)
def hook_ptrace(state):
    """反调试桩：ptrace 一律返回 -1"""
    state.regs.rax = 0xffffffffffffffff

state = proj.factory.entry_state()
simgr = proj.factory.simgr(state)
simgr.explore(find=lambda s: b"Correct" in s.posix.dumps(1), num_find=1)
```

## 五、常见坑 / 变体

- **忘记 `enable_veritesting`**：不开启时分支爆炸，开启后很多题从小时级降到秒级。
- **find/avoid 填错**：把 `0x401234` 填成 `main` 会让 angr 立刻「成功」，务必核对地址。
- **输入方式设错**：`scanf("%s", buf)` 用 stdin 会连同 `\n` 一起进状态，需要 `SimFileStream` 加尾部 `\n`。
- **字符集限制太严**：`>= 0x20` 且 `<= 0x7e` 排除了二进制输入，flag 含 `\x00` 时必失败。
- **反调试导致路径全断**：`ptrace`/`IsDebuggerPresent` 要 hook。
- **AES/RSA 类加密**：符号执行几乎不可行，改为「已知明文差分」+ z3 建模。
- **`selfmodifying code`（SMC）**：angr 对自修改支持有限，先手工 dump 解密后的代码段。

## 六、参考来源

- [angr 官方文档](https://docs.angr.io/)
- [angr cheatsheet（最常用 API 汇总）](https://docs.angr.io/en/latest/appendix/cheatsheet.html)
- [angr 模拟执行核心概念](https://docs.angr.io/en/latest/core-concepts/simulation.html)
- [angr-doc examples（大量可直接跑的例题）](https://github.com/angr/angr-doc/tree/master/examples)
- [CTF-Wiki: angr](https://ctf-wiki.org/reverse/tools/simulate-execution/angr/)
- [cle（angr 的加载器）](https://github.com/angr/cle)
