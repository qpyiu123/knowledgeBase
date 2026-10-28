---
title: Rust 逆向要点（符号还原 / 结构体 / 内存安全）
category: reverse
tags: [Rust, mangling, rustfilt, 结构体还原, 借用检查]
signals: [字符串里出现 core::panicking, 有 rust_begin_unwind, 函数名形如 _ZN...17h...E, 二进制里有大量 Result/Option 处理, 静态链接且很大]
difficulty: medium
source: "CTF-Wiki Rust 逆向入门 / rustc-demangle / Rust nomicon"
tools: [rustfilt, demangler.com, IDA, Ghidra, gdb, cargo-bloat]
updated: 2026-10-22
---

## 一、识别信号（题面长什么样）

- 函数名是 `_ZN4core3fmt9Formatter3pad17h8a5e...E` 这种怪串。
- `strings` 里有 `core::panicking::panic_fmt`、`alloc::`,
  `library/core/src/` 等路径。
- 有 `rust_begin_unwind`、`rust_eh_personality` 符号。
- 反编译里大量 `Result::unwrap` 的内联展开（`switch` + `panic` 分支）。
- 二进制静态链接，体积大；`readelf -p .comment` 可能显示 `rustc version`。

## 二、原理

Rust 与 C/C++ 逆向的最大差异：

| 维度 | C/C++ | Rust |
|---|---|---|
| 符号命名 | `_Z` (Itanium) | `_ZN...17h<hash>E`（**带 hash 后缀**） |
| 字符串 | C 字符串 | `&str` = `(ptr, len)`，还有 `String`（含 capacity）|
| 错误处理 | 返回值 / errno | `Result<T, E>` = `enum`，`Ok/Err` 判别 |
| 泛型 | 模板实例化 | **单态化**，每个具体类型生成独立函数 |
| 虚拟调用 | vtable 显式 | `dyn Trait` 用 `(data_ptr, vtable_ptr)` 胖指针 |
| 闭包 | std::function | 匿名结构体（`{closure}`）|

**符号反混淆**：`_ZN4core3fmt9Formatter3pad17h...E` 用 `rustfilt` 还原成
`core::fmt::Formatter::pad::h8a5e...`，去掉 `::h<16hex>` 就是可读名字。

**常见模式识别**：
- `Result` 的 `match` → 反编译里 `if (tag == 1) {...} else {...}`，tag 在对象第一个字节。
- `String` 是 24 字节 `{ptr, cap, len}`（x86-64）。
- `Vec<T>` 也是 `{ptr, cap, len}`。
- `Option<&T>` 常被 niche 优化成裸指针（`null` 表示 `None`）。

## 三、checksec 判读与利用思路

Rust 二进制的判读：

```text
1. readelf -p .comment ./chall | grep rustc       # 编译器版本
2. strings -a ./chall | grep -c "library/core"    # 大量命中 = Rust
3. objdump -t ./chall | grep _ZN | head           # mangled 符号
4. cargo-bloat / size                              # 看哪个 crate 最大
```

逆向策略：

1. 先用 `rustfilt` 批量还原所有符号（生成 IDA 重命名脚本）。
2. 只关注 `main` 与 crate 内函数（`core`/`std`/`alloc` 前缀可跳过）。
3. 找到 `clap`/`structopt` 参数解析 → 确定输入出口。
4. 结构体：`String`/`Vec` 按 24 字节切，`Result` 按首个 tag 字节判断。

## 四、可直接运行的 exp 脚本

```python
#!/usr/bin/env python3
# Rust 二进制符号还原 + 结构体辅助识别
import subprocess, re, sys, json, pathlib

BIN = sys.argv[1] if len(sys.argv) > 1 else "./chall"

# ---------- 1) 检测是否为 Rust ----------
def is_rust(path):
    data = pathlib.Path(path).read_bytes()
    marks = [b"rust_begin_unwind", b"core::panicking", b"library/core/src",
             b"rust_eh_personality", b"_ZN4core"]
    hits = [m for m in marks if m in data]
    print("[*] Rust 特征命中:", [h.decode() for h in hits])
    return bool(hits)

# ---------- 2) 用 rustfilt 批量反混淆 ----------
def rustfilt_all(path):
    out = subprocess.run(["objdump", "-t", path], capture_output=True, text=True).stdout
    syms = re.findall(r"_ZN[0-9A-Za-z_$]+E", out)
    syms = sorted(set(syms))
    print(f"[*] mangled 符号 {len(syms)} 个")
    try:
        res = subprocess.run(["rustfilt"], input="\n".join(syms),
                             capture_output=True, text=True)
        demangled = res.stdout.splitlines()
    except FileNotFoundError:
        print("[-] 未安装 rustfilt: cargo install rustfilt")
        demangled = [s for s in syms]
    pairs = list(zip(syms, demangled))
    for m, d in pairs[:30]:
        print(f"   {d}")
    return pairs

# ---------- 3) 生成 IDA 重命名脚本 ----------
def gen_ida_script(pairs, out="apply_rust_syms.py"):
    with open(out, "w") as f:
        f.write("import idc, idaapi\n")
        for mangled, demangled in pairs:
            short = demangled.split("::h")[0].replace("::", "_")[:40]
            if not short or not short.isidentifier():
                continue
            f.write(f"try:\n"
                    f"    ea = idc.get_name_ea_simple('{mangled}')\n"
                    f"    if ea != idaapi.BADADDR: idc.set_name(ea, 'rs_{short}', idc.SN_NOWARN)\n"
                    f"except Exception: pass\n")
    print("[+] 已生成", out, "（IDA: File -> Script File 执行）")

# ---------- 4) 结构体布局助手 ----------
RUST_LAYOUTS = {
    "String": [("ptr", 8), ("cap", 8), ("len", 8)],
    "Vec":    [("ptr", 8), ("cap", 8), ("len", 8)],
    "&str":   [("ptr", 8), ("len", 8)],
    "Result": [("tag", 8), ("payload", "max(Ok,E)")],
    "Option": [("tag", 8), ("payload", "T")],
    "Box":    [("ptr", 8)],
    "Rc":     [("ptr", 8)],   # -> {strong, weak, value}
    "Arc":    [("ptr", 8)],
}

def layout(name):
    print(f"{name}: " + ", ".join(f"{n}({sz})" for n, sz in RUST_LAYOUTS.get(name, [])))

# ---------- 5) 反汇编里找 panic 分支（= unwrap 失败路径） ----------
def find_unwraps(path):
    out = subprocess.run(["objdump", "-d", path], capture_output=True, text=True).stdout
    n = len(re.findall(r"call.*(core9panicking|rust_begin_unwind)", out))
    print(f"[*] panic 分支调用点 {n} 处（多为 unwrap/expect）")

if __name__ == "__main__":
    if is_rust(BIN):
        pairs = rustfilt_all(BIN)
        gen_ida_script(pairs)
        find_unwraps(BIN)
    for t in ("String", "Vec", "Result", "Option"):
        layout(t)
```

快速反混淆单条命令：

```bash
# 在线版也可以直接把符号贴进去：demangler.com
echo "_ZN4core3fmt9Formatter3pad17h8a5e2c1d9f0b7a6cE" | rustfilt
# 输出：core::fmt::Formatter::pad::h8a5e2c1d9f0b7a6c
objdump -d ./chall | rustfilt | less      # 直接看可读反汇编
```

## 五、常见坑 / 变体

- **hash 后缀不一致**：同一函数在不同 crate 编译会得到不同 hash，匹配时要去掉 `::h<16hex>`。
- **单态化导致同名多份**：`Vec<u8>` 与 `Vec<u32>` 的 `push` 是两个函数，名字只差类型参数。
- **`Result` tag 偏移**：不是总在 0，小类型会被 niche 优化（`Option<NonZeroU32>` 用 0 表示 None）。
- **内联 `unwrap`**：看不到独立函数调用，只能认 `call core::panicking::panic` 的分支。
- **`panic=abort`**：没有 unwind 路径，逻辑里 `unwrap` 直接 `abort`，分析要关注 `abort` 而非 `panic_fmt`。
- **release 优化**：边界检查被消除后逻辑变化大，优先拿 debug 版或对照 `-C opt-level`。
- **`std` 静态链接**：`core`/`std` 前三个字母可作快速过滤，跳过它们专注用户代码。

## 六、参考来源

- [CTF-Wiki: Rust 逆向入门](https://ctf-wiki.org/reverse/language/rust/introduction/)
- [rust-lang/rustc-demangle](https://github.com/rust-lang/rustc-demangle)
- [rustc-demangle crate 文档](https://docs.rs/rustc-demangle/latest/rustc_demangle/)
- [Rust Nomicon（内存布局与 ABI）](https://doc.rust-lang.org/nomicon/)
- [CTF-Wiki: 语言相关逆向总览](https://ctf-wiki.org/reverse/language/introduction/)
- [Ghidra 官方（多架构反编译）](https://ghidra.re/)
