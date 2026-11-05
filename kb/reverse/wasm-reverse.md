---
title: WebAssembly 逆向（wasm 反编译与还原）
category: reverse
tags: [WebAssembly, wasm, wabt, wasm2wat, 字节码, 栈式虚拟机]
signals: [附件是 .wasm 或 .wat, 文件开头是 \0asm, 网页里 fetch 加载 wasm, 题目用 emscripten 编译, 有一段 base64 的 wasm 内嵌在 js]
difficulty: medium
source: "WebAssembly 官方规范 / wabt / CTF-Wiki RE"
tools: [wabt, wasm2wat, wasm-decompile, wasm2c, wasmtime, jadx, node]
updated: 2026-10-22
api_language: Node.js
api_version: Node.js 22 文档与旧库归档
api_symbols: [Buffer.from, Buffer.readUInt32LE, Buffer.readUInt32BE]
---

## 一、识别信号（题面长什么样）

- 附件里是 `.wasm`，或网页里 `fetch("x.wasm")` 后 `WebAssembly.instantiate`。
- 二进制开头 4 字节是 `\0asm`（`00 61 73 6d`），版本 `01 00 00 00`。
- JS 里有 `_malloc`、`_free`、`ccall`、`Module.HEAPU8` —— emscripten 编译产物。
- 题目是浏览器题（.html + .js + .wasm），flag 校验在 wasm 里。
- `.wasm` 里看不到明文，但 `strings` 能看到 `memory`、`__indirect_function_table`。

## 二、原理

WebAssembly 是**栈式虚拟机**，指令形如：

```wat
;; WAT（文本格式）
(func $check (param $a i32) (result i32)
  local.get $a
  i32.const 0x37
  i32.xor          ;; 栈顶两个值异或
  i32.const 3
  i32.rotl
  local.get 0
  ...)
```

关键结构：

| 结构 | 作用 |
|---|---|
| Type section | 函数签名 |
| Import/Export section | `env.memory`、导出的 `main`/`check` |
| **Code section** | 实际字节码（栈式） |
| **Data section** | 初始化内存的常量数据（常藏 flag / S-box） |
| Table section | 间接调用表（`call_indirect`）|
| Name section | 调试名（发布版常被删）|

emscripten 产物特征：大量 `__emscripten_*` 导入、`memory` 以 `INITIAL_MEMORY` 增长、`_malloc` 导出。

## 三、checksec 判读与利用思路

判读顺序：

```text
1. wasm-objdump -h ./chall.wasm        # 段列表
2. wasm-objdump -x ./chall.wasm        # 导出/导入/函数表（定位 check）
3. wasm2wat ./chall.wasm > chall.wat   # 转可读文本
4. wasm-decompile ./chall.wasm > c.txt # 伪 C，最省事
```

选择工具：

| 需求 | 工具 |
|---|---|
| 快速看伪 C | `wasm-decompile` |
| 精细看指令 | `wasm2wat` + `wasm-objdump -d` |
| 直接跑起来调试 | `wasmtime` / node |
| 转 C 编译后放到 IDA | `wasm2c` |
| 无 exports 的裸 wasm | 手工找 `start` 或从 JS 里找导出 |

## 四、可直接运行的 exp 脚本

```bash
#!/bin/bash
# wasm 一键反编译流水线
set -e
W=${1:-./chall.wasm}
OUT=./wasm_out
mkdir -p "$OUT"

echo "[1] 段结构"
wasm-objdump -h "$W"

echo "[2] 导入/导出（找 check 函数）"
wasm-objdump -x "$W" | grep -E "Export|Import|func\[" | head -60

echo "[3] 文本格式"
wasm2wat --generate-names "$W" -o "$OUT/chall.wat"
wc -l "$OUT/chall.wat"

echo "[4] 伪 C（最易读）"
wasm-decompile "$W" -o "$OUT/chall.dcmp"
head -80 "$OUT/chall.dcmp"

echo "[5] data 段里的可疑常量"
wasm-objdump -s -j Data "$W" | head -40

echo "[6] 用 wasm2c 转 C，喂给 IDA"
wasm2c "$W" -o "$OUT/chall.c"
```

```python
#!/usr/bin/env python3
# 用 Python 直接跑 wasm 校验函数（wasmtime-py），暴力/符号化前的快速验证
import sys
try:
    from wasmtime import Store, Module, Instance, Engine
except ImportError:
    sys.exit("pip install wasmtime")

WASM = sys.argv[1] if len(sys.argv) > 1 else "./chall.wasm"
engine = Engine()
store = Store(engine)
module = Module.from_file(engine, WASM)
exports = {}

def host_print(x):
    print("print:", x)

# emscripten 产物常需要几个 env 导入，按需补桩
try:
    instance = Instance(store, module, [])
except Exception as e:
    print("[!] 导入缺失:", e)
    print("[!] 用 wasm-objdump -x 看 Import 段，手工补桩")
    raise SystemExit(1)

mem = instance.exports["memory"] if "memory" in dir(instance.exports) else None
check = instance.exports["check"] if "check" in dir(instance.exports) else None
if check is None:
    print("[!] 没有 check 导出，用 wasm-objdump -x 查导出名")
else:
    for i in range(0x20, 0x7f):
        try:
            r = check(store, i)
            if r:
                print(f"[+] input {i:#x} -> {r}")
        except Exception:
            pass
```

在 Node 里 hook wasm 的导出（无头运行）：

```javascript
// run_wasm.js —— node run_wasm.js
const fs = require("fs");
const buf = fs.readFileSync("./chall.wasm");
const mod = new WebAssembly.Module(buf);
const env = {
  memory: new WebAssembly.Memory({ initial: 256 }),
  emscripten_notify_memory_growth: () => {},
  abort: () => { throw new Error("abort"); },
};
const inst = new WebAssembly.Instance(mod, { env });
const ex = inst.exports;
console.log("exports:", Object.keys(ex));
// 若导出 check(charPtr) -> int，把输入写进内存再调用
if (ex.check && ex.memory) {
  const mem = new Uint8Array(ex.memory.buffer);
  const ptr = 0x1000;
  const input = Buffer.from("test_input\0");
  mem.set(input, ptr);
  console.log("check result =", ex.check(ptr));
}
```

## 五、常见坑 / 变体

- **无 name section**：发布版删了函数名，`wasm2wat` 输出 `(func $0)`，需靠调用关系定位。
- **wasm 被 base64 内嵌**：JS 里 `atob("AGFzbQ...")`，先解密再存成 `.wasm`。
- **自定义段藏数据**：`wasm-objdump -h` 会显示 `Custom`，string/flag 可能在里面。
- **`memory` 导入缺失**：不补 `env.memory` 实例化直接报错。
- **`call_indirect` 表**：间接调用看 `table` 段，函数索引要交叉 `elem` 段。
- **多线程 wasm**：`shared memory` 需要 `WebAssembly.Memory({shared: true})`，node 需开 `--experimental-wasm-threads`。
- **`wasm2c` 输出巨大**：配合 `wasm2wat` 的 `--generate-names` 用名字过滤，只看核心函数。

## 六、参考来源

- [CTF-Wiki: 逆向工程总览](https://ctf-wiki.org/reverse/introduction/)
- [WebAssembly 官方网站](https://webassembly.org/)
- [wabt（WebAssembly Binary Toolkit）](https://github.com/WebAssembly/wabt)
- [wasmtime 运行时](https://github.com/bytecodealliance/wasmtime)
- [Binaryen（wasm 优化与工具）](https://github.com/WebAssembly/binaryen)
- [wasm3 轻量解释器](https://github.com/wasm3/wasm3)

# Node.js 字节读取速查

## Buffer.from

把字符串按给定编码转成字节；字符串形式默认 UTF-8。十六进制文本应指定 hex，Base64 文本应指定 base64。再用 toString 指定输出如何解释，避免把文本编码和整数大小端混为一谈。

```javascript
// Buffer.from(string[, encoding])
const bytes = Buffer.from('4142', 'hex');
console.log(bytes.toString('utf8')); // AB
```

来源：[Node.js 22 Buffer.from](https://nodejs.org/docs/latest-v22.x/api/buffer.html#static-method-bufferfromstring-encoding)，结合旧库 node-buffer 归档核对。

## Buffer.readUInt32LE

从 offset 开始读取四个字节，按小端序解释为无符号 32 位整数，返回 JavaScript number。确保 offset 到末尾至少有四字节；越界时检查数据长度与偏移来源。

```javascript
// buf.readUInt32LE([offset])
Buffer.from('01000000', 'hex').readUInt32LE(0); // 1
```

来源：[Node.js 22 readUInt32LE](https://nodejs.org/docs/latest-v22.x/api/buffer.html#bufreaduint32leoffset)。

## Buffer.readUInt32BE

从 offset 开始读取四个字节，按大端序解释为无符号 32 位整数。与小端版本读取范围一致，差别是字节解释顺序。

```javascript
// buf.readUInt32BE([offset])
Buffer.from('00000001', 'hex').readUInt32BE(0); // 1
```

来源：[Node.js 22 readUInt32BE](https://nodejs.org/docs/latest-v22.x/api/buffer.html#bufreaduint32beoffset)。
