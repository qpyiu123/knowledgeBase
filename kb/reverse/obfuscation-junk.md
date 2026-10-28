---
title: 花指令与控制流平坦化还原（含 IDA 脚本）
category: reverse
tags: [花指令, 控制流平坦化, OLLVM, 去混淆, IDAPython]
signals: [IDA 反编译报 call analysis failed, 函数里出现 jmp 跳到中间, 有大量无意义 xor/nop, 一个主循环 + 状态变量分发, 分支都被拆成同一层]
difficulty: hard
source: "CTF-Wiki 花指令 / 控制流平坦化 / OLLVM"
tools: [IDA, IDAPython, Ghidra, angr, de-ollvm 脚本]
updated: 2026-10-22
---

## 一、识别信号（题面长什么样）

- IDA 里函数 body 大量红色（未定义），反编译弹 `call analysis failed`。
- 出现 `jmp loc_XXX+1`（跳到指令中间）、`push addr; ret` 这种伪跳转。
- 大量 `xor eax, eax` / `nop` / `add esp, 0` 等无效指令夹杂在逻辑中。
- 函数结构是：`while(1) { switch(state) { case 1: ... } }`，所有基本块都在同一层。
- 变量 `state` / `v17` 在每轮被重新赋值为常量。

## 二、原理

### 花指令（junk code）

在真实指令之间插入「机器码合法但永远不会被执行」的字节，让线性反汇编错位：

```asm
   jmp  short real      ; 跳过垃圾字节
   db 0xE8              ; 垃圾（伪 call 的开头）
real:
   mov eax, 1           ; 真实逻辑
```

或者利用**同一段字节的两种解释**：反汇编器从 `loc` 开始解码得到错误指令，而 CPU 跳进 `loc+1` 才是正确解码。常见模式：

- `jmp $+1` / `call $+5; pop reg`（取地址）
- `push imm32; ret`（等价 `jmp imm32`）
- `xor eax, eax; jz always`（恒真跳转）
- 死代码块（永不执行的分支）

### 控制流平坦化（OLLVM `Flattening`）

原逻辑 `if (a) { body1 } else { body2 }` 被改写成：

```c
state = INIT;
while (1) {
    switch (state) {
        case INIT: state = cond ? B1 : B2; break;
        case B1:   body1; state = END; break;
        case B2:   body2; state = END; break;
        case END:  goto out;
    }
}
```

消除平坦化的关键是**常量传播**：`state` 的运行期取值是常量，用符号执行或数据流分析逐个恢复真实边。

## 三、checksec 判读与利用思路

判读要点：

| 现象 | 手法 |
|---|---|
| 函数字节有未定义 | 花指令：`ida_bytes.del_items` → 重新 `create_insn` |
| `jmp` 到指令中间 | 用 IDAPython 修正目标，垃圾字节定义成 `db` |
| 主循环 + switch | 平坦化：符号执行或 `state` 常量传播 |
| `switch` 参数来自复杂表达式 | 先把 `state` 声明成 `int`，再跑反编译器 |
| 每个 case 结尾都是 `state = X` | 追 `X` 的赋值链 |

## 四、可直接运行的 exp 脚本

### 1. IDAPython：自动修复「jmp 到指令中间」型花指令

```python
#@category CTF
import ida_bytes, idc, idaapi, idautils

def fix_junk(start=0x401000, end=0x402000):
    """把跳到非法地址/指令中间的 jmp 指回真实位置，并清理垃圾字节"""
    fixed = 0
    for ea in idautils.Heads(start, end):
        if idc.print_insn_mnem(ea) != "jmp":
            continue
        tgt = idc.get_operand_value(ea, 0)
        if tgt == idaapi.BADADDR:
            continue
        if not ida_bytes.is_code(ida_bytes.get_flags(tgt)):
            ida_bytes.del_items(tgt, 0, 1)
            if ida_bytes.create_insn(tgt):
                fixed += 1
                print(f"[+] {hex(ea)} jmp -> {hex(tgt)} 重建指令成功")
    print(f"[*] 共修复 {fixed} 处")

fix_junk()
```

### 2. IDAPython：统计死块（入度为 0 且非入口）

```python
#@category CTF
import ida_funcs, idautils, idc

def dead_blocks(fname="main"):
    ea = idc.get_name_ea_simple(fname)
    f = ida_funcs.get_func(ea)
    if not f:
        print("function not found"); return []
    succ = {}
    for bb in idautils.FlowChart(f):
        succ[bb.start_ea] = [s.start_ea for s in bb.succs()]
    reach, work = set(), [f.start_ea]
    while work:
        cur = work.pop()
        if cur in reach:
            continue
        reach.add(cur)
        work.extend(succ.get(cur, []))
    dead = [hex(bb.start_ea) for bb in idautils.FlowChart(f) if bb.start_ea not in reach]
    print("[*] 死块:", dead)
    return dead

dead_blocks()
```

### 3. 平坦化还原：用 angr 做逐块符号执行

```python
#!/usr/bin/env python3
# 平坦化还原：在每块入口建 blank_state，收集真实后继
import angr

BIN, FUNC = "./chall", 0x401300
proj = angr.Project(BIN, auto_load_libs=False)

def walk(entry, depth=0, seen=None, out=None):
    seen = seen if seen is not None else set()
    out = out if out is not None else []
    if entry in seen or depth > 200:
        return out
    seen.add(entry)
    out.append(hex(entry))
    st = proj.factory.blank_state(addr=entry)
    sm = proj.factory.simgr(st).step(num_inst=1)
    # 只取可直接确定的后继；间接跳转交给符号求解
    for s in sm.active:
        walk(s.addr, depth + 1, seen, out)
    return out

if __name__ == "__main__":
    print(" | ".join(walk(FUNC)[:60]))
```

### 4. 把 `switch(state)` 还原成伪代码骨架

```python
#!/usr/bin/env python3
# 输入：从反编译里抄出的 state 映射（state 常量 -> 语义）
STATE_MAP = {
    0x1a2b3c4d: ("INIT", "state = cond ? 0x1111 : 0x2222"),
    0x1111:     ("B1",   "body1(); state = 0xFFFF"),
    0x2222:     ("B2",   "body2(); state = 0xFFFF"),
    0xFFFF:     ("END",  "goto out"),
}

def render(entry):
    name, code = STATE_MAP[entry]
    return f"{name}:\n    {code}"

if __name__ == "__main__":
    print(render(0x1a2b3c4d))
```

## 五、常见坑 / 变体

- **花指令删多了**：`del_items` 删错区域会让真指令消失，先备份 IDB，只做小范围操作。
- **OLLVM 的 state 不是常量**：部分变体用 `state = f(input)`，必须符号执行而非静态传播。
- **间接跳转表**：`jmp [rax*8 + table]` 让 IDA 看不到边，需手工 `Switch idiom` 或脚本恢复。
- **Ghidra 去混淆插件**：第三方 `de-ollvm` 类脚本效果好，但对 Ghidra 版本敏感。
- **`push/ret` 跳转**：IDA 不认作跳转，需要脚本把 `push imm; ret` 重写为 `jmp`。
- **混合保护**：花指令 + 平坦化 + 反调试叠加，先过反调试再做静态还原。
- **`call analysis failed` 的真实原因**：有时只是栈不平衡（`add esp` 差值不对），用 `Alt+K` 改栈指针即可。

## 六、参考来源

- [CTF-Wiki: 花指令](https://ctf-wiki.org/reverse/obfuscate/junk-code/)
- [CTF-Wiki: 控制流平坦化](https://ctf-wiki.org/reverse/obfuscate/control-flow-flatten/)
- [CTF-Wiki: Self-Modified Code](https://ctf-wiki.org/reverse/obfuscate/smc/)
- [CTF-Wiki: Linux 下的 False Disassembly](https://ctf-wiki.org/reverse/platform/linux/false-disasm/)
- [angr 官方文档](https://docs.angr.io/)
- [Ghidra 官方](https://ghidra.re/)
