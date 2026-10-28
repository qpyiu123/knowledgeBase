---
title: .NET / C# 逆向（dnSpyEx / ILSpy）与 Unity il2cpp
category: reverse
tags: [.NET, C#, dnSpy, ILSpy, Unity, il2cpp, 元数据]
signals: [文件是 .NET 程序集, 有 mscoree.dll 导入或 CLR 头, Unity 游戏里有 GameAssembly.dll 与 global-metadata.dat, 反编译能看到完整 C# 源码, 方法名带 unreadable 前缀, 有 ConfuserEx 特征]
difficulty: easy
source: "CTF-Wiki Dnspy / .NET 官方文档 / Il2CppDumper"
tools: [dnSpyEx, ILSpy, monodis, de4dot, Il2CppDumper, IDA, Ghidra, Frida]
updated: 2026-10-22
---

## 一、识别信号（题面长什么样）

- 附件是 `.exe`/`.dll`，`strings` 里有 `_CorExeMain`、`mscoree.dll`。
- file 命令显示 `PE32 executable (console) Intel 80386 Mono/.Net assembly`。
- Unity 游戏目录里有 `GameAssembly.dll` + `*_Data/il2cpp_data/Metadata/global-metadata.dat`。
- 反编译工具能直接给出接近原始 C# 的代码（`.NET` 保留 IL 元数据）。
- 命名空间/类名清晰（`FlagChecker`、`Decrypt`）。

## 二、原理

.NET 程序编译成 **CIL（中间语言）**，运行时由 CLR/JIT 编译。IL 元数据保留了类名、方法名、字段名、类型签名，因此反编译质量极高（接近源码）。

| 形态 | 特征 | 工具 |
|---|---|---|
| .NET Framework / .NET Core | `mscoree.dll`、CLR 头 | dnSpyEx / ILSpy |
| .NET Native / AOT | 无 IL，纯 native | IDA + 符号恢复 |
| Unity Mono | `MonoBleedingEdge` + `Assembly-CSharp.dll` | dnSpyEx 直接开 |
| Unity il2cpp | `GameAssembly.dll` + `global-metadata.dat` | Il2CppDumper 生成 dummy dll |

**Unity il2cpp**：C# 被 AOT 编译成 C++ 再编译成 native，IL 没了，但 `global-metadata.dat` 保留了**所有类型、方法名与地址映射**。`Il2CppDumper` 解析该文件，生成：
- `dump.cs`：类型与方法签名
- `DummyDll/`：假 IL 元数据，可直接拖进 dnSpyEx 看结构
- `il2cpp.h`：给 IDA 的符号脚本

**常见混淆**：`ConfuserEx`、`Eazfuscator`、`Obfuscar`。特征：控制流平坦化、字符串加密、方法代理（proxy calls）。

## 三、checksec 判读与利用思路

判读流程：

```text
1. file ./chall.exe                                  # 看是否 .NET
2. python3 -c "import pefile; pe=pefile.PE('chall.exe'); print(pe.OPTIONAL_HEADER.DATA_DIRECTORY[14])"
   # DATA_DIRECTORY[14] = CLR 目录，Header 非 0 即 .NET
3. 是 Unity？ ls 有 GameAssembly.dll / Assembly-CSharp.dll / global-metadata.dat
4. 是否混淆？ dnSpyEx 里看方法名是否为 unreadableXXXX / 是否大量 switch
```

工具选择：

| 场景 | 首选 |
|---|---|
| 直接看源码 | dnSpyEx（可断点调试） |
| 导出可编译工程 | ILSpy |
| 混淆还原 | de4dot / de4dot-cex |
| il2cpp | Il2CppDumper + IDA/Ghidra + Frida |

## 四、可直接运行的 exp 脚本

```python
#!/usr/bin/env python3
# .NET / Unity 程序类型判定 + 元数据快速提取
import sys, struct, re, subprocess, pathlib

PATH = sys.argv[1] if len(sys.argv) > 1 else "./chall.exe"

def is_dotnet(path):
    """读 PE 的 DataDirectory[14]（CLR）判断是否为 .NET"""
    try:
        import pefile
    except ImportError:
        print("[-] pip install pefile"); return False
    pe = pefile.PE(path)
    try:
        d = pe.OPTIONAL_HEADER.DATA_DIRECTORY[14]
        print(f"[*] CLR Directory: VA={d.VirtualAddress:#x} Size={d.Size:#x}")
        return d.VirtualAddress != 0 and d.Size != 0
    except Exception:
        return False

def unity_kind(dirpath):
    p = pathlib.Path(dirpath)
    if (p / "GameAssembly.dll").exists():
        print("[*] 检测到 il2cpp：GameAssembly.dll")
    if (p / "*_Data").exists() is False:
        for d in p.glob("*_Data"):
            meta = d / "il2cpp_data" / "Metadata" / "global-metadata.dat"
            if meta.exists():
                print(f"[*] il2cpp metadata: {meta}")
            if (d / "Managed").exists():
                print(f"[*] Mono 托管程序集: {d / 'Managed' / 'Assembly-CSharp.dll'}")

def dump_strings_from_metadata(path):
    """il2cpp metadata 里直接 grep 可疑字符串（不解就不是加密的）"""
    data = pathlib.Path(path).read_bytes()
    hits = re.findall(rb"[\x20-\x7e]{6,}", data)
    key = [h for h in hits if any(k in h.lower() for k in
           (b"flag", b"check", b"decrypt", b"key", b"correct", b"wrong"))]
    for h in key[:40]:
        print("   ", h[:100])
    return key

def rundll(path, method="Main", args=[]):
    """如果程序集有入口，直接跑（仅本地授权靶场）"""
    cmd = ["dotnet", path] + args
    try:
        out = subprocess.run(cmd, capture_output=True, text=True, timeout=10)
        print(out.stdout[:2000]); print(out.stderr[:500])
    except FileNotFoundError:
        print("[-] 需要 dotnet runtime")

if __name__ == "__main__":
    if PATH.endswith(".exe") or PATH.endswith(".dll"):
        if is_dotnet(PATH):
            print("[+] 是 .NET 程序集，可直接拖进 dnSpyEx / ILSpy")
        else:
            print("[*] 非 .NET，可能是 .NET Native/AOT 或普通 PE")
    elif pathlib.Path(PATH).is_dir():
        unity_kind(PATH)
    elif PATH.endswith("global-metadata.dat"):
        dump_strings_from_metadata(PATH)
```

il2cpp 完整流程：

```bash
# 1) dump 类型与方法
Il2CppDumper GameAssembly.dll global-metadata.dat ./il2cpp_out
# 产出：dump.cs / DummyDll/ / il2cpp.h / script.py

# 2) 在 IDA 里跑 script.py 恢复函数名
#    IDA: File -> Script File -> il2cpp_out/script.py

# 3) 只想看 C# 结构：DummyDll 拖进 dnSpyEx
# 4) 需要运行时改逻辑：Frida hook libil2cpp.so 的 offset
frida-trace -U -f com.game.app -I "libil2cpp.so" -i "*Check*"
```

Mono 游戏（最简单）：

```bash
# 直接打开 Assembly-CSharp.dll，dnSpyEx 里 F5 出源码，Ctrl+G 跳转，F9 下断点运行
dnSpy.exe "$GAME_DIR/${GAME}_Data/Managed/Assembly-CSharp.dll"
```

## 五、常见坑 / 变体

- **程序集被混淆**：方法名变成 `\u0001` 或 `unreadable_xxx`，用 `de4dot` 先清洗（对 ConfuserEx 有效）。
- **`ConfuserEx` 的 anti-tamper**：改字节后会校验，先脱掉 anti-tamper 再改。
- **il2cpp 的 metadata 被加密**：`global-metadata.dat` 头部 magic 不是 `0xFAB11BAF` 说明被改，需找 `il2cpp_init` 动态还原后的内存 dump。
- **Unity 版本与 Dumper 不匹配**：新版 il2cpp（2021+）结构有变，用 `Perfare/Il2CppDumper` 最新版或 `Zygisk-Il2CppDumper` 在设备上 dump。
- **.NET Native/AOT**：无 IL，只能按 native 逆向，工具链回到 IDA + 符号猜测。
- **`Assembly-CSharp.dll` 不存在**：可能用了 Addressables / HybridCLR 热更新，逻辑在 `StreamingAssets` 的 dll 里。
- **dnSpyEx 打不开**：dnSpy 原版已归档，用社区维护的 `dnSpyEx` 分叉。

## 六、参考来源

- [CTF-Wiki: dnSpy](https://ctf-wiki.org/reverse/tools/static-analyze/dnspy/)
- [dnSpyEx（社区维护版 dnSpy）](https://github.com/dnSpyEx/dnSpy)
- [ILSpy（.NET 反编译器）](https://github.com/icsharpcode/ILSpy)
- [de4dot（.NET 混淆还原）](https://github.com/0xd4d/de4dot)
- [monodis（Mono 程序集反汇编）](https://www.mono-project.com/docs/tools+libraries/tools/monodis/)
- [Perfare/Il2CppDumper](https://github.com/Perfare/Il2CppDumper)
- [Zygisk-Il2CppDumper（设备端 dump）](https://github.com/Perfare/Zygisk-Il2CppDumper)
- [.NET 程序集官方文档](https://learn.microsoft.com/en-us/dotnet/standard/assembly/)
