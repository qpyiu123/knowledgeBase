---
title: LuaJIT 字节码与手游脚本逆向（lj_bc 还原）
category: reverse
tags: [luajit, lj_bc, 手游, cocos, 字节码]
signals: [文件头是 1b4c4a（1b 4c 4a）, 出现 LuaJIT 2.0 或 LuaJIT 2.1 字样, 手游包里有 libcocos2dlua.so 或 libluajit.so, assets 目录下大量 .lua 但是二进制, 游戏目录有 .luac 或 .luajit, 报错提示 "cannot load incompatible bytecode", 题面提示「LuaJIT」「手游」「热更新」, 有 socket 通信或是 Unity 外挂脚本, 反编译 luac 工具全部失败]
difficulty: hard
source: "luajit-decompiler / LjTools / LuaJIT 源码"
tools: [python, luajit, ida]
updated: 2026-10-22
---

## 一、识别信号（题面长什么样）

- 文件头 `\x1bLJ`（hex `1b4c4a`），第 4 字节通常是 `\x02`（LuaJIT 2.0）或 `\x01`（2.1 早期）。
- 手游 APK 里 `assets/`、`res/` 下有 `.lua` / `.luac` / `.luac.enc`。
- `lib/arm64-v8a/` 下有 `libcocos2dlua.so`、`libluajit.so`、`libxlua.so`。
- 直接用 `unluac` / `luadec` 全部报错（因为指令集不同）。
- 题面提示：`LuaJIT`、`手游`、`脚本`、`热更新`、`bytecode`。
- 数据段里有 `BC_`、`lj_` 前缀符号（来自 LuaJIT 内部）。
- 有网络协议或滑块验证码逻辑写在 Lua 里。

## 二、原理

### 1. 为什么普通 luac 工具失败

LuaJIT **不使用标准 Lua 虚拟机指令集**，而是自己的 **lj_bc**（bytecode，单字节 opcode + 8/16/32 位操作数）。`unluac` 这类工具只认 Lua 5.x 的 `Instruction` 格式，所以必然失败。

LuaJIT 字节码结构（`lj_bcdump.c`）：

```
Header: \x1b LJ \x02 \x?? len ... flags(uleb128) [dict(字符串字典)]  ← 2.1 有 dict
块: PROTOS | STRINGS | NUMBERS | CHUNKS | ... 
Proto: flags | args | framesize | sizebc | sizekgc | sizekn | sizept
```

### 2. opcode 数量与版本

- LuaJIT 2.0：`BC__MAX = 0x60`（96 条）
- LuaJIT 2.1：`BC__MAX = 0x61` / 较新的 2.1 到 `0x62`
- **不同版本的 opcode 编号可能不同**，必须用**匹配版本**的反编译器。

### 3. 常见保护

| 手段 | 应对 |
|---|---|
| 字节码 XOR/加密 | 从 `libluajit.so` 里找自定义 `lj_bcread` 补丁 |
| opcode 表重排 | 在 `lj_bc_mode[]` / `lj_bc_names[]` 里还原映射 |
| 字符串表加密 | 运行时 hook `lj_str_new` |
| 魔数改掉 | 手工改回 `1b 4c 4a 02` |

## 三、解题步骤

1. **确认版本**：`xxd -l 8`，看第 4 字节；再看手游里的 `libluajit.so` 版本字符串 `LuaJIT 2.1.0-beta3`。
2. **选工具**：
   - LuaJIT 2.0 → `lj_bcdump` + `luajit-decompiler`（Dr-MTN）
   - LuaJIT 2.1 → `luajit-decompiler` 的 2.1 分支，或 `LjTools`
3. **跑反编译**：`python ljd/main.py -f target.luac`。
4. **失败时**：从 `libluajit.so` 里导出 opcode 表（`lj_bc_mode` 符号或 `BCDEF` 宏表），按重排顺序调整反编译器的 opcode 常量。
5. **静态读逻辑**：找 `TG_` 指令（数值比较/跳转）与常量池 `KN`。
6. **动态验证**：用同版本 `luajit` 加载，或在 Android 上 Frida hook `lj_bc_read`。

## 四、可直接运行的脚本

识别 LuaJIT 版本与头部：

```python
import sys

b = open(sys.argv[1], "rb").read()
print("magic:", b[:3])
print("version byte:", hex(b[3]), "flags:", hex(b[4]) if len(b) > 4 else "?")

# LuaJIT 2.0: \x1bLJ\x02 ; 2.1: \x1bLJ\x01 或 \x02 + 不同 flags
if b[:3] == b"\x1bLJ":
    if b[3] == 0x02:
        print("-> likely LuaJIT 2.0.x")
    else:
        print("-> likely LuaJIT 2.1 or custom")
```

批量从 APK 里抽 Lua 脚本：

```python
import zipfile, os, sys

apk = sys.argv[1]
out = "extracted"
os.makedirs(out, exist_ok=True)

with zipfile.ZipFile(apk) as z:
    for n in z.namelist():
        if n.endswith((".lua", ".luac")) or "lua" in n.lower() and n.endswith(".lua"):
            data = z.read(n)
            p = os.path.join(out, n.replace("/", "_"))
            open(p, "wb").write(data)
            print("%-60s %6d bytes  head=%s" % (n, len(data), data[:4].hex()))
```

从 `libluajit.so` 里找 opcode 名字表（用于确认 opcode 顺序）：

```python
import re

data = open("libluajit.so", "rb").read()
# lj_bc_names / BCDEF 生成的字符串块通常连续出现
names = re.findall(rb"(?:[A-Z]{2,3}\x00){10,}", data)
print("candidate opcode name tables:", len(names))
for chunk in names[:3]:
    print([s.decode() for s in chunk.split(b"\x00") if s][:40])
```

用 LuaJIT 本地跑字节码（验证解密后的脚本）：

```bash
luajit -b input.lua output.luac     # 编译
luajit output.luac                  # 执行
luajit -bl output.luac              # 列出字节码指令
```

`luajit -bl` 的反汇编输出识别：

```
0001    KSHORT   0 0
0002    TGETS    1 0 "os"       ← 表操作
0003    TSETS    1 1 "execute"
0004    KSTR     2 "id"        ← 字符串常量
0005    CALLM    1 0 2          ← 方法调用
```

## 五、常见坑 / 变体

- **版本不匹配反编译乱码**：`lj_bc` 2.0 与 2.1 差异巨大，先确认再选工具。
- **`luajit -b` 需要同版本**：文档说 "LuaJIT 2.1 的字节码不能跨 patch 版本"，实际上**跨小版本也不保证**。
- **防 dump**：`lj_bcwrite` 被 hook 掉时无法 `string.dump`，只能静态解。
- **加密的 `.luac`**：常见 4 字节密钥 XOR；用已知明文（`\x1bLJ`）反推密钥。
- **变体：Cocos2d-x Lua** —— 用 `xxtea` 加密 `.lua`，密钥在 `AppDelegate.cpp` 的 `setXXTEAKeyAndSign`。
- **变体：Tolua/XLua（Unity）** —— 字节码常在 `Assets/StreamingAssets`，入口由 C# 调 `luaL_dofile`。
- **变体：protobuf/Lua 热点热更** —— 再看 `libxlua.so` 里的 `luaopen_xlua`。
- **变体：游戏内脚本（FNV/JIT 混淆）** —— `lj_trace` 会 JIT，静态分析仍可行。
- **注意**：手游逆向涉及版权，仅限 CTF 授权题目。

## 六、参考来源

- [LuaJIT 官方文档](https://luajit.org/)
- [luajit-decompiler](https://github.com/Dr-MTN/luajit-decompiler)
- [LjTools](https://github.com/rochus-keller/LjTools)
- [LuaJIT Decompiler Online](https://www.decompiler.com/luajit)
- [LuaJIT 源码 lj_bc.h](https://github.com/LuaJIT/LuaJIT/blob/v2.1/src/lj_bc.h)
- [frida](https://github.com/frida/frida)
