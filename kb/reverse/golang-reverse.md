---
title: Golang 逆向（恢复函数名与结构体）
category: reverse
tags: [Golang, GoReSym, pclntab, 符号恢复, 结构体]
signals: [二进制很大且静态链接, 出现 runtime.morestack_noctxt, 反编译里满是 goroutine 相关代码, 函数名是 sub_xxx 但字符串有大量 Go 路径, 有 pclntab 段]
difficulty: medium
source: "CTF-Wiki Golang 逆向入门 / GoReSym / Go 官方 runtime"
tools: [GoReSym, IDA, Ghidra, gdb, objdump, go tool nm]
updated: 2026-10-22
---

## 一、识别信号（题面长什么样）

- `file ./chall` 显示 `statically linked`，体积 2~10 MB。
- `strings` 里大量 `github.com/...`、`main.`、`runtime.` 前缀。
- 反编译里出现 `runtime.morestack_noctxt`、`runtime.newobject`。
- 函数名残缺（`main_main` 可能被识别，但大部分是 `sub_4xxxxx`）。
- 题目是 CLI 工具风格：读参数、读文件、打印。

## 二、原理

Go 二进制的关键元数据：

| 元数据 | 作用 | 位置 |
|---|---|---|
| `pclntab` | 函数地址 ↔ 名字/文件/行号映射 | `.gopclntab` 段 / 符号 `runtime.pclntab` |
| `moduledata` | 模块信息（类型、itab、text 范围） | `firstmoduledata` |
| `gopclntab` magic | `0xFFFFFFF1`（1.20+）、`0xFFFFFFF0`（1.16~1.19）、`0xFFFFFFFA`（1.2~1.15） | 段首 |
| 类型信息 | 结构体布局（`type.*`） | `.rodata` |
| itab | 接口方法表 | `.rodata` |

**为什么要恢复函数名**：Go 默认剥离符号，但 `pclntab` 是运行时反射必需，**一定保留**（除非 strip 掉 pclntab 并改 magic）。恢复后用「名字搜索」定位 `main.main` / `main.check` 极快。

Go 调用约定（1.17+ 寄存器传参）：
- `RAX, RBX, RCX, RDI, RSI, R8, R9, R10, R11` 依次传参
- 返回值也在寄存器
- 每个 Go 函数开头几乎都有栈溢出检查（`CMPQ SP, 0x10(R14)`）

## 三、checksec 判读与利用思路

Golang 逆向的判读顺序：

```text
1. go version 特征：strings | grep -o "go1\.[0-9.]*" | head
2. 是否有 pclntab：objdump -h | grep -i pc
3. 是否 strip：go tool nm 是否有输出
4. 是否 il2cpp/Unity 内嵌：查 GameAssembly
```

策略：

1. `GoReSym -t ./chall -m ./chall` 恢复符号 → 生成 IDA/Ghidra 可导入的符号表。
2. 用 `main.main` / `main.check` / `main.encrypt` 直接定位逻辑。
3. 结构体用 `runtime.newobject` 交叉引用反推大小。
4. 字符串常量通过 `.rodata` 引用恢复（Go 字符串是 `(ptr, len)` 对）。

## 四、可直接运行的 exp 脚本

```python
#!/usr/bin/env python3
# Go 二进制侦察 + 从 gopclntab 手工恢复函数名（无 GoReSym 时的兜底）
import sys, struct, subprocess, re, pathlib

BIN = sys.argv[1] if len(sys.argv) > 1 else "./chall"

# ---------- 1) 基础侦察 ----------
def recon(path):
    data = pathlib.Path(path).read_bytes()
    m = re.search(rb"go1\.\d+(\.\d+)?", data)
    print("[*] go version:", m.group().decode() if m else "未找到")
    for magic, ver in ((0xFFFFFFF1, "1.20+"), (0xFFFFFFF0, "1.16-1.19"),
                       (0xFFFFFFFA, "1.2-1.15")):
        idx = data.find(struct.pack("<I", magic))
        if idx >= 0:
            print(f"[*] pclntab magic {magic:#x} ({ver}) @ {idx:#x}")
    print("[*] size:", len(data))

# ---------- 2) 用 go tool nm 恢复（需要保留 symtab） ----------
def go_tool_nm(path):
    try:
        out = subprocess.run(["go", "tool", "nm", path], capture_output=True, text=True)
        lines = [l for l in out.stdout.splitlines() if " main." in l]
        print(f"[*] main.* 符号共 {len(lines)} 个")
        for l in lines[:40]:
            print("   ", l)
        return lines
    except FileNotFoundError:
        print("[-] 未安装 Go 工具链")
        return []

# ---------- 3) GoReSym 调用（最推荐） ----------
def goresym(path):
    cmd = ["GoReSym", "-t", path, "-m", path, "-d", path + ".json"]
    try:
        out = subprocess.run(cmd, capture_output=True, text=True)
        print(out.stdout[:2000])
        print("[+] 已生成", path + ".json（含函数名/类型/文件行号）")
    except FileNotFoundError:
        print("[-] 未安装 GoReSym: go install github.com/mandiant/GoReSym@latest")

# ---------- 4) 从 .rodata 里捞 Go 字符串（UTF-8 长串） ----------
def dump_strings(path, min_len=8):
    data = pathlib.Path(path).read_bytes()
    strs = re.findall(rb"[\x20-\x7e]{%d,}" % min_len, data)
    hints = [s for s in strs if any(k in s for k in
             (b"flag", b"correct", b"wrong", b"input", b"key", b"encrypt"))]
    for s in hints[:40]:
        print("   ", s[:100])
    return hints

# ---------- 5) 结构体大小推断：找 runtime.newobject 的调用 ----------
def guess_struct_sizes(path):
    """从反汇编里找 newobject(type)，反查 type 的 size 字段"""
    out = subprocess.run(["objdump", "-d", path], capture_output=True, text=True).stdout
    callers = len(re.findall(r"call.*runtime\.newobject", out))
    print(f"[*] runtime.newobject 调用点: {callers} 处（每个对应一次堆分配）")

if __name__ == "__main__":
    recon(BIN)
    go_tool_nm(BIN)
    dump_strings(BIN)
    guess_struct_sizes(BIN)
    if "--goresym" in sys.argv:
        goresym(BIN)
```

把 GoReSym 结果导入 IDA：

```bash
# 1) 生成符号脚本
GoReSym -t ./chall -d chall.json
# 2) 转成 IDAPython 可执行的 rename 脚本（社区脚本或自写）
python3 -c "
import json
d = json.load(open('chall.json'))
with open('apply_syms.py','w') as f:
    f.write('import idc\n')
    for fn in d.get('UserFunctions', []) + d.get('StdFunctions', []):
        f.write(f\"idc.set_name({fn['Start']}, '{fn['FullName']}', idc.SN_NOWARN)\n\")
"
```

## 五、常见坑 / 变体

- **strip 掉 pclntab**：magic 被改成 `0xFFFFFFFF`，GoReSym 会报错；手动把 magic 改回 `0xFFFFFFF1` 再跑。
- **Go 1.20 的 pclntab 变化**：新增 `funcnametab` 分离，旧版解析脚本会失败。
- **字符串不是 C 字符串**：Go 字符串是 `{ptr, len}`，`strings` 命中的位置不一定在引用点附近，要用 `lea rax, [rip+xxx]` 反查。
- **`main.main` 找不到**：包名可能不是 `main`（如 `main.(*Server).handler`），按前缀搜。
- **内联优化**：Go 内联很激进，小函数被展平进调用者，看不到独立函数体。
- **goroutine 干扰**：大量 `runtime.gopanic`/`chansend` 分支，聚焦 `main.*` 即可。
- **Garble 混淆**：函数名被改成随机串，需要用字符串/常量特征定位，而非名字。

## 六、参考来源

- [CTF-Wiki: Golang 逆向入门](https://ctf-wiki.org/reverse/language/go/introduction/)
- [mandiant/GoReSym（恢复 Go 符号）](https://github.com/mandiant/GoReSym)
- [CTF-Wiki: 语言相关逆向总览](https://ctf-wiki.org/reverse/language/introduction/)
- [Go 官方 runtime 源码](https://golang.org/src/runtime/)
- [Go 标准库 debug/gosym](https://go.dev/src/debug/gosym/)
- [goretk/gore（Go 二进制分析库）](https://github.com/goretk/gore)
