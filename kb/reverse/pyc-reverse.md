---
title: Python 字节码逆向（pyc / pycdc / decompyle3 差异）
category: reverse
tags: [pyc, 字节码, pycdc, uncompyle6, decompyle3, marshal]
signals: [附件是 .pyc 或 __pycache__, 文件头是 0x55 0x0d 0x0d 0x0a, 只有 pyc 没有源码, 反编译工具报 Unknown opcode, 题目要求还原算法]
difficulty: easy
source: "CTF-Wiki pyc 文件 / CPython 字节码文档 / pycdc / decompyle3"
tools: [python3, dis, pycdc, uncompyle6, decompyle3, xdis, PyLingual]
updated: 2026-10-22
---

## 一、识别信号（题面长什么样）

- 附件是 `chall.pyc` 或 `__pycache__/chall.cpython-311.pyc`。
- 文件头 4 字节是 magic：2.x 常见 `\x03\xf3\r\n`，3.8 是 `\x55\x0d\x0d\x0a`，3.11 `\xa7\x0d\x0d\x0a`。
- 反编译工具报 `Unknown magic number` / `Unsupported Python version`。
- 题目说「只有编译后的文件」「猜猜 exec 里是什么」。
- `.pyc` 里能看到 `marshal` 加载的 code object 嵌套。

## 二、原理

Python 执行流程：`源码 → 编译 → code object（marshal 序列化）→ .pyc 文件`

`.pyc` 结构：

```text
magic(4B) | bit_field(4B, 3.7+) | mtime(4B) | source_size(4B) | marshal(code object)
```

- 前 4 字节 magic 决定 Python 版本，**必须版本完全匹配**才能反序列化。
- `marshal` 格式本身跨版本不稳定，但 code object 字段随版本变化（3.11 引入 `co_exceptiontable`、指令宽度由 2 字节改为 2 字节但 opcode 重排）。
- 3.0~3.10 的 opcode 号相对稳定，3.11/3.12 有较大调整（`PRECALL`、`CACHE` 等）。

**三条工具链差异**：

| 工具 | 支持版本 | 原理 | 优点 | 缺点 |
|---|---|---|---|---|
| `uncompyle6` | 2.7 ~ 3.8 | 语法驱动 AST 重建 | 老版本还原度最高 | 3.9+ 不支持 |
| `decompyle3` | 3.7 ~ 3.8 | uncompyle6 的分支重构 | 3.7/3.8 效果好 | 版本窄 |
| `pycdc` | 2.4 ~ 3.13 | C++ 手写反编译器 | 版本覆盖最广、最快 | 复杂语法可能出错误代码 |
| `dis` 模块 | 全版本 | 官方字节码反汇编 | 永远准确 | 不还原 C 代码 |

## 三、checksec 判读与利用思路

判读 `.pyc`：

```bash
xxd -l 16 ./chall.pyc          # 看 magic 与头部
python3 -c "
import importlib.util
data = open('chall.pyc','rb').read(4)
print('magic:', data.hex(), '-> 需要 Python 3.x')
"
```

magic → 版本速查（部分）：

| magic | 版本 |
|---|---|
| `030df3` (前 2 字节) | 2.7 |
| `420d0d0a` | 3.9 |
| `550d0d0a` | 3.8（题中常见）|
| `550d0d0a` 变体 + `6f0d` | 3.10 |
| `a70d0d0a` | 3.11 |
| `cb0d0d0a` | 3.12 |

处理路线：

1. **版本匹配**：装对应 Python（pyenv/conda），用 `dis` 先看字节码。
2. **反编译**：`pycdc` 兜底，`uncompyle6`/`decompyle3` 针对 3.7/3.8。
3. **魔改 opcode**：题目可能改了 `opcode.py`，需要按改动逆向映射。
4. **加密 pyc**：很多题用自定义 loader 解密后再 exec，要先捉解密后的 code object。

## 四、可直接运行的 exp 脚本

```python
#!/usr/bin/env python3
# pyc 逆向全套：magic 判定 -> 反汇编 -> 提取嵌套 code object -> 常量 dump
import sys, dis, marshal, importlib.util, types, pathlib

PATH = sys.argv[1] if len(sys.argv) > 1 else "./chall.pyc"

MAGIC_MAP = {
    "030df3": "2.7", "420d0d0a": "3.9", "550d0d0a": "3.8/3.10",
    "610d0d0a": "3.10", "6f0d0d0a": "3.10", "a70d0d0a": "3.11",
    "cb0d0d0a": "3.12", "f30d0d0a": "3.13",
}

def read_header(data):
    magic = data[:4].hex()
    ver = MAGIC_MAP.get(magic, "未知（请用 hexdump 对照 CPython 的 importlib/_bootstrap_external.py）")
    print(f"[*] magic = {magic}  疑似版本 = {ver}")
    return magic, ver

def load_code(path):
    data = pathlib.Path(path).read_bytes()
    read_header(data)
    # 3.7+ 头部：4 magic + 4 flags + 4 mtime + 4 size = 16 字节
    for skip in (16, 12, 8):
        try:
            return marshal.loads(data[skip:])
        except Exception:
            continue
    raise RuntimeError("marshal 解析失败：版本不匹配或文件被加密")

def walk(co, depth=0):
    """递归打印所有 code object（嵌套函数/lambda 都有）"""
    print("  " * depth + f"== {co.co_name} (argcount={co.co_argcount})")
    print("  " * depth + f"   consts: {[c if not isinstance(c, types.CodeType) else '<code %s>' % c.co_name for c in co.co_consts][:20]}")
    print("  " * depth + f"   names: {list(co.co_names)[:20]}")
    for c in co.co_consts:
        if isinstance(c, types.CodeType):
            walk(c, depth + 1)

def dump_opcodes(co, depth=0):
    print("=" * 20, co.co_name)
    dis.dis(co)

def extract_flag_strings(co):
    """把常量里可疑的 bytes/str 全打出来"""
    out = []
    for c in co.co_consts:
        if isinstance(c, (bytes, str)) and c:
            out.append(c)
        elif isinstance(c, types.CodeType):
            out += extract_flag_strings(c)
    return out

if __name__ == "__main__":
    code = load_code(PATH)
    walk(code)
    print("\n[*] 可疑常量:")
    for s in extract_flag_strings(code):
        print("   ", repr(s)[:120])
    print("\n[*] 顶层反汇编（前 80 行）:")
    dis.dis(code)
```

### 魔改 opcode 的处理（题目常见）

```python
#!/usr/bin/env python3
# 题目若改了 opcode.py，用映射表把字节码翻译回标准 opcode
import dis, opcode, types, marshal, pathlib

PATCHED = {           # 假设题目把 BINARY_ADD(23) 与 BINARY_MULTIPLY(20) 换了
    23: "BINARY_MULTIPLY",
    20: "BINARY_ADD",
}

def undo_patch(co):
    new_code = bytearray(co.co_code)
    std = opcode.opmap
    rev = {v: k for k, v in std.items()}
    i = 0
    while i < len(new_code):
        op = new_code[i]
        if op in PATCHED:
            name = PATCHED[op]
            # 双向交换时不动（互换了两次）
            new_code[i] = std[name]
        i += 2        # 3.6+ 指令固定 2 字节（opcode + arg）
    return co.replace(co_code=bytes(new_code))

code = marshal.loads(pathlib.Path("./chall.pyc").read_bytes()[16:])
dis.dis(undo_patch(code))
```

工具链安装与用法：

```bash
pip install uncompyle6 decompyle3 xdis       # 注意：xdis 是它们的依赖
pip install pycdc 2>/dev/null || (git clone https://github.com/zrax/pycdc && cd pycdc && cmake . && make)
pycdc chall.pyc > chall.py
uncompyle6 -o . chall.pyc
decompyle3 chall.pyc
```

## 五、常见坑 / 变体

- **版本强行凑**：3.11 的 pyc 用 3.8 的 Python 解 marshal 会得到乱码或异常，**必须版本匹配**。
- **头部长度差异**：3.3~3.6 是 12 字节，3.7+ 是 16 字节，写死会解错。
- **`uncompyle6` 已停止维护**：3.9+ 一律用 `pycdc` 或 `PyLingual`（在线）。
- **加密 pyc**：`marshal.loads` 失败但 magic 正常 → 内容是自定义加密，找 loader 的 `decrypt` 函数。
- **反编译出错但字节码正确**：以 `dis` 输出为准，反编译器的语法重建可能错。
- **`co_consts` 里藏 flag**：很多题 flag 直接是常量，先 dump 常量再纠结逻辑。
- **嵌套 code object**：lambda/列表推导会生成独立 code，`walk()` 要递归。

## 六、参考来源

- [CTF-Wiki: pyc 文件（magic 与结构）](https://ctf-wiki.org/misc/other/pyc/)
- [CTF-Wiki: Python 逆向入门](https://ctf-wiki.org/reverse/language/python/introduction/)
- [Python 官方 dis 模块文档](https://docs.python.org/3/library/dis.html)
- [CPython 字节码定义（Python/bytecodes.c）](https://github.com/python/cpython/blob/main/Python/bytecodes.c)
- [zrax/pycdc（C++ 反编译器）](https://github.com/zrax/pycdc)
- [rocky/python-decompile3](https://github.com/rocky/python-decompile3)
- [rocky/python-uncompyle6](https://github.com/rocky/python-uncompyle6)
- [rocky/python-xdis（跨版本字节码解析）](https://github.com/rocky/python-xdis)
