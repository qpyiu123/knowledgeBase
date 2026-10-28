---
title: 符号执行进阶（angr CFG / reaching、Triton、Manticore 对比）
category: reverse
tags: [angr, triton, manticore, symbolic-execution, cfg]
signals: [程序校验逻辑有大量位运算与分支, 输入长度固定且只有 16~64 字节, 校验失败输出 "wrong" 且无任何提示, 静态反编译出上千行的位级运算, 题面提示「符号执行」「约束求解」, 想一次性求解而 z3 手工建模太慢, 有大量 memcmp 逐字节比较, 题目要求「求出所有可行输入」, 二进制里有循环依赖的 checksum]
difficulty: hard
source: "angr 文档 / Triton / Manticore"
tools: [angr, z3, triton, manticore]
updated: 2026-10-22
---

## 一、识别信号（题面长什么样）

- 校验函数是**上千行位运算**（`>>`、`&`、`^`、`rol`），手工建模 z3 极其痛苦。
- 输入长度固定（`len(input) == 32`），有明确的"成功/失败"字符串。
- 失败输出只有 `Wrong.`，成功才打印 flag —— 需要一个路径可达性判断。
- 有循环把输入分块处理（每 4 字节一次），但循环次数固定。
- 题面提示：`符号执行`、`symbolic`、`angr`、`Triton`、`Manticore`、`约束求解`。
- `z3-solve` 篇的"手工建模"已经太慢，需要自动化。
- 目标是 **binary**（不是纯算法），需要"找路径"而不是"解方程"。

## 二、原理

### 1. 三个工具的定位

| 工具 | 定位 | 强项 | 弱项 |
|---|---|---|---|
| **angr** | Python 库，CFG + symbolic | 易用、生态大、能跑带库的程序 | 速度慢，复杂程序易爆 |
| **Triton** | C++/Python，指令级符号执行 | 精细控制、支持大量指令、插件化 | API 低层，需要自己写遍历 |
| **Manticore** | Python 框架 | 自动探索 + 可插拔 hooks | 项目维护趋缓，兼容性一般 |

### 2. angr 的三种用法

1. **CFG（控制流图）**：`CFGFast` / `CFGEmulated`，快速定位函数与调用关系。
2. **探索（exploration）**：`project.factory.simulation_manager(state)`，用 `find`/`avoid` 指定目标。
3. **Reaching（可达性）**：从 `entry` 到 `target_addr` 的路径存在性，配合 `state.preconstrainer` 求输入。

### 3. 为什么"找路径"比"解方程"难

- 符号执行会对**每个分支**克隆状态，分支爆炸。
- 有循环时，循环次数取决于输入 → 无限展开。
- 需要 `avoid`（避免死循环/失败路径）和 `find`（目标）来剪枝。

## 三、解题步骤

1. **CFG 快速摸底**：`CFGFast` 找 `main`、`check`，看分支密度。
2. **选路线**：
   - 校验简单、目标是「找到通过 check 的输入」→ angr `find/avoid`。
   - 需要精细控制（如 anti-angr、循环太多）→ Triton 手写。
   - 需要跑很多输入/并发探索 → Manticore。
3. **设 symbolic**：`BVS('input', 8*N)`，`state.memory.store(addr, input)`。
4. **设 found/avoid**：`check_addr` 里打印成功 → find；失败 → avoid。
5. **对抗 drop 状态**：加 `Veritesting`（`angr.options`）、限制步数、用 `SimulationManager.explore` 的 `num_find`。
6. **拿输出**：`state.posix.dumps(0)` 或 `state.solver.eval(input)`。

## 四、可直接运行的脚本

angr 基础（find/avoid）：

```python
import angr, claripy

BIN = "./check"
N = 32

p = angr.Project(BIN, auto_load_libs=False)
cfg = p.analyses.CFGFast()          # 先摸底：看 main/check 的分支密度
st = p.factory.entry_state(stdin=angr.SimFileStream)

# 从 CFG 里定位"成功/失败"基本块（换成题目里的地址）
FOUND = 0x401234
AVOID = 0x401250

flag = claripy.BVS("flag", N * 8)
st.memory.store(st.regs.rsp + 0x100, flag)     # 视题目而定

sm = p.factory.simulation_manager(st)
sm.explore(find=FOUND, avoid=AVOID)
if sm.found:
    print(sm.found[0].solver.eval(flag, cast_to=bytes))
else:
    print("no path; check addresses")
```

**reaching** 形式（给目标地址找路径）：

```python
import angr

p = angr.Project("./check", auto_load_libs=False)
cfg = p.analyses.CFGFast(normalize=True)

start = p.loader.main_object.entry
target = 0x401234

# 用 CFG 判断是否可达
node_start = cfg.get_any_node(start)
node_target = cfg.get_any_node(target)
print("funcs:", len(cfg.functions))
print("has node:", node_start is not None, node_target is not None)
```

Triton 手写（精细控制，适合 anti-angr）：

```python
from triton import TritonContext, ARCH, Instruction, MemoryAccess, CPUSIZE

ctx = TritonContext(ARCH.X86_64)
ctx.setMode(ctx.mode.ALIGNED_MEMORY, True)

def symbolize(addr, n):
    for i in range(n):
        ctx.symbolizeMemory(MemoryAccess(addr + i, CPUSIZE.BYTE), "flag_%d" % i)

def emulate(code_bytes, addr):
    for off in range(0, len(code_bytes)):
        inst = Instruction(addr + off, code_bytes[off:off + 15])
        ctx.processing(inst)
        if inst.getType() == 0x6:      # 示例：判断某指令
            pass

# 详细用法：triton 的 bindings 文档里 Concrete/Emulation 示例
print("triton ready", ctx.getArchitecture())
```

Manticore（自动探索 + hooks）：

```python
from manticore.native import Manticore

m = Manticore("./check")
m.context["count"] = 0

@m.hook(0x401234)         # found 基本块
def on_success(state):
    print("FOUND", bytes(state.read_bytes(state.read_register("rsp") + 8, 32)))

@m.hook(0x401250)         # fail 基本块
def on_fail(state):
    print("fail path"); state.abandon()

m.run()
```

## 五、常见坑 / 变体

- **地址猜错**：先用 CFG + `cfg.get_any_node` 确认 `FOUND` 确实是"成功"那条。
- **angr 卡在 scanf**：给 `stdin` 用 `SimFileStream`，或用 `state.posix.get_fd(0)` 的 hook。
- **anti-angr**（`!defined(_WIN32)` 检查、`angr` 字符串检测）：用 Triton 手写，或 `Veritesting` 关闭。
- **循环次数依赖输入**：用 `state.solver.add(len == N)` 或 `find` 在循环出口。
- **Triton 性能**：逐条 `processing` 很快，但需自己实现 fork 逻辑（`ctx.addCallback`）。
- **Manticore 安装**：Python 3.11+ 兼容性一般，建议 3.9 环境。
- **变体：需要多个输入（多阶段）** → 分段符号执行，每段求一个。
- **变体：混合执行（Concolic）** → `angr` 的 `concretization` 策略，或 Triton + Z3 结合。
- **变体：非 x86（ARM/ARM64）** → angr 支持 `arch=archinfo.ArchARM()`；Triton 也支持 ARM64。
- **变体：WASM** → 见 `wasm-reverse.md`，angr 有 WASM 支持但有限。
- **常用 options**：`angr.options.LAZY_SOLVES`、`angr.options.SYMBOL_FILL_UNCONSTRAINED_MEMORY` 能显著提速。

## 六、参考来源

- [angr 文档 — Control-flow Graph Recovery](https://docs.angr.io/built-in-analyses/cfg)
- [angr-doc](https://github.com/angr/angr-doc)
- [Triton](https://github.com/JonathanSalwan/Triton)
- [Manticore](https://github.com/trailofbits/manticore)
- [pharos（CMU SEI 的符号执行框架）](https://github.com/cmu-sei/pharos)
- [Decompiling Connect Four with angr](https://mborgerson.com/decompiling-connect-four-with-angr)
