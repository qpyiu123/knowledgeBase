---
title: Lua / Python 脚本保护与字节码还原（Luac 反编译、混淆 Lua）
category: reverse
tags: [lua, luac, 字节码, 反编译, 脚本保护]
signals: [附件以 1b4c7561 开头（Lua 字节码魔数）, 文件出现 Lua 5.1 或 Lua 5.3 字样, 脚本被封装进 exe 且字符串里有 lua_pcall, 混淆后的变量名形如 O0O0O / lIll, 存在 loadstring 或 load 动态执行, 有 .luac 或 .lua 但是在文本编辑器里是乱码, 题面提示「Lua」「脚本」「字节码」, 脚本里出现 getfenv/setfenv 操作, 程序目录里有 lua54.dll 或 lua51.dll]
difficulty: medium
source: "lua.org / luadec / unluac"
tools: [unluac, luadec, python, lua]
updated: 2026-10-22
---

## 一、识别信号（题面长什么样）

- 文件头 `\x1bLua`（hex `1b4c7561`），第 5 字节是版本（`0x51` = 5.1，`0x53` = 5.3，`0x54` = 5.4）。
- 附件是 `.luac` / `.lua`，但 `cat` 出来全是二进制。
- exe 里有 `lua_pcall`、`luaL_loadbuffer`、`luaL_loadstring` 导入 → 内嵌 Lua 引擎。
- 混淆后的 Lua 名如 `local O0O00O0 = ...`、`local lIIlI1 = ...`（变量名无意义）。
- 字符串被 `\99\111\114\111\110\97` 这种十进制转义拆开。
- 题面提示：`Lua`、`脚本`、`字节码`、`Luac`、`loadstring`。
- 有 `.lua` 被加密后存进资源段，运行时解密加载。

## 二、原理

### 1. Lua 字节码结构

```
Header（12 字节，5.1）
  \x1bLua | version | format | endianness | sizeof(int) | sizeof(size_t) | sizeof(Instruction) | sizeof(lua_Number) | integral flag
Function（递归）
  source | linedefined | lastlinedefined | nups | numparams | is_vararg | maxstacksize
  code[] | constants[] | upvalues[] | protos[] | debug info
```

`luac -l -l file.luac` 可以直接反汇编出每条指令（需**同版本** Lua）。

### 2. 常见保护手段

| 手段 | 表象 | 应对 |
|---|---|---|
| **魔数改掉** | 头不是 `1b4c7561` | 改回魔数或用 `unluac` 忽略 |
| **版本号改掉** | 头部 version 字段与真实不符 | 改回 `0x51/0x53/0x54` |
| **字节码 XOR/RC4** | 密文看不出来 | 从宿主程序里找解密函数 |
| **字符串加密** | 常量表都是乱码 | 在运行时 `string.dump` 出来 |
| **opcode 重排** | 指令反编译出错误结果 | 需要根据重排表还原 |
| **变量名混淆** | `O0O0` 风格 | 交给 `unluac` 直接得源码，名字无所谓 |

### 3. `string.dump` 的威力

如果能**执行**这段 Lua（在程序里），一句 `io.write(loadstring("..."))` 或 hook `lua_load` 就能把解密后的字节码 dump 出来，比硬啃解密算法省事。

## 三、解题步骤

1. **看头部**：`xxd -l 16 file.luac`，确认版本与魔数。
2. **直接反编译**：`java -jar unluac.jar file.luac > out.lua`；失败则用 `luadec`（5.1 专用）。
3. **魔数/版本被改**：用 `HxD` 改回 `1b 4c 75 61 51 00 ...`，再试。
4. **混淆变量名**：`unluac` 输出后直接读逻辑，别管名字。
5. **字符串加密**：找 `\x5c\x64` 十进制转义或 `string.char(...)` 调用；写个小 Lua 脚本解。
6. **跑起来 dump**：用 `luajit`/`lua` 加 `-e` 执行 `loadstring`，或在宿主程序 Frida hook `lua_load`。
7. **对照逻辑**：找 `if` 里的比较常量，直接推 flag。

## 四、可直接运行的脚本

判定文件类型与版本：

```python
import sys

data = open(sys.argv[1], "rb").read()
if data[:4] == b"\x1bLua":
    ver = data[4]
    print("Lua bytecode, version 0x%02x (%s)" % (ver, {0x51: "5.1", 0x53: "5.3", 0x54: "5.4"}.get(ver, "?")))
    print("format:", data[5], "endian:", data[6], "int size:", data[7], "size_t:", data[8])
else:
    print("not raw lua bytecode, head:", data[:16].hex())
```

修复常见篡改（魔数被改）：

```python
data = bytearray(open("x.luac", "rb").read())
data[0:4] = b"\x1bLua"
data[4] = 0x51          # 强制当 5.1 处理
open("fixed.luac", "wb").write(data)
```

Lua 5.3+ 上提取常量表（不依赖反编译器）：

```python
import struct, io

class Reader:
    def __init__(self, b): self.b, self.i = b, 0
    def u8(self):  v = self.b[self.i]; self.i += 1; return v
    def u32(self): v = struct.unpack_from("<I", self.b, self.i)[0]; self.i += 4; return v
    def u64(self): v = struct.unpack_from("<Q", self.b, self.i)[0]; self.i += 8; return v
    def num(self): v = struct.unpack_from("<d", self.b, self.i)[0]; self.i += 8; return v
    def i64(self): v = struct.unpack_from("<q", self.b, self.i)[0]; self.i += 8; return v
    def str_(self):
        n = self.u8()
        if n == 0: return None
        if n == 0xFF: n = self.u64()
        s = self.b[self.i:self.i + n - 1]; self.i += n
        return s.decode("utf-8", "replace")

def skip_function(r, version=0x53):
    r.str_(); r.u32(); r.u32(); r.u8(); r.u8(); r.u8(); r.u8()   # source, linedefined...
    ncode = r.u32(); r.i += ncode * 4                             # code
    nk = r.u32()
    for _ in range(nk):
        t = r.u8()
        if t == 0 or t == 1: r.u8()          # nil / boolean
        elif t == 3: r.num()                  # float
        elif t == 19: r.i64()                 # integer (5.3)
        elif t in (4,): r.str_()              # short string
        elif t == 20: r.str_()                # long string
        else: raise Exception("unknown const type %d at %d" % (t, r.i))
    nup = r.u32()
    for _ in range(nup): r.u16() if False else (r.u8(), r.u8())
    nprotos = r.u32()
    for _ in range(nprotos): skip_function(r, version)

data = open("x.luac", "rb").read()
r = Reader(data)
r.i = 12
if data[4] == 0x53:
    r.u8()   # sizeupvalues
skip_function(r)
print("done, parsed ok")
```

用 `luac` 反汇编（需要对应版本 Lua）：

```bash
luac -l -l -p out.luac        # 列出所有指令与常量
```

Frida hook `lua_load`（从宿主程序 dump 明文脚本）：

```javascript
// hook lua_load 的 Lua 5.4 签名：lua_load(L, reader, data, chunkname, mode)
const lua = Module.findBaseAddress("lua54.dll");
Interceptor.attach(lua.add(0x12345), {   // 偏移需按版本计算
  onEnter(args) { this.L = args[0]; this.name = args[3].readUtf8String(); },
  onLeave(retval) { console.log("loaded chunk:", this.name); }
});
```

## 五、常见坑 / 变体

- **版本不匹配**：`unluac` 需要与字节码同版本的解析器，5.1 的 `.luac` 在 5.4 下会崩 → 安装 `lua5.1`、`lua5.3` 分别试。
- **自定义 `lua_State`**：程序把 Lua 嵌进 C++，`loadstring` 被改名为 `L`，但行为一致。
- **字符串混淆用 `string.char` 拼**：静态看不到，用 `load` + `print` 让 Lua 自己解。
- **opcode 重排**：需要在宿主程序里找 `luaP_opmodes` 表或 opcode 名表还原映射。
- **`luac -s` 去调试信息**：变量名全丢，但逻辑仍在。
- **变体：LuaJIT**（见 `luajit-bytecode.md`），`1b4c4a` 头。
- **变体：Android 里的 Lua**（Cocos2d-x / XLua）→ `libcocos2dlua.so` + `assets/` 的 `.luac`。
- **变体：py2exe / PyInstaller 打包 Python** —— 见 `pyc-reverse.md`，不要混。
- **变体：Lua 混淆器（如 LuaObfuscator）** —— 生成大量 `goto`/`while true` 状态机，交给 `unluac` 往往失败，需要用 `f-strings` 风格静态执行。

## 六、参考来源

- [Lua 官方文档 — Bytecode](https://www.lua.org/manual/5.4/)
- [lua/lua](https://github.com/lua/lua)
- [unluac — Lua decompiler](https://github.com/Jeong-Min-Cho/unluac)
- [luadec](https://github.com/viruscamp/luadec)
- [LuaJIT Decompiler](https://github.com/Dr-MTN/luajit-decompiler)
- [LjTools](https://github.com/rochus-keller/LjTools)
