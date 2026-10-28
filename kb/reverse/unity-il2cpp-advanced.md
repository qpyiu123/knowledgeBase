---
title: Unity il2cpp 进阶（global-metadata.dat 还原与 Il2CppDumper 全流程）
category: reverse
tags: [unity, il2cpp, il2cppdumper, il2cppinspector, metadata]
signals: [APK 里有 libil2cpp.so 且伴随 global-metadata.dat, PC 游戏有 GameAssembly.dll 与 global-metadata.dat, 用 dnSpy 打开只看到 Assembly-CSharp 的空壳, 报错 "Unable to resolve" 或 "metadata version mismatch", 字符串里有 il2cpp 但代码逻辑看不到, 题面提示「Unity」「il2cpp」, 存在 Il2CppDumper 或 script.json, 游戏目录有 unity default resources, assembly-CSharp.dll 只有 3KB]
difficulty: hard
source: "Perfare/Il2CppDumper / katboi01/Il2CppInspector"
tools: [il2cppdumper, il2cppinspector, ida, ghidra]
updated: 2026-10-22
---

## 一、识别信号（题面长什么样）

- APK 的 `lib/arm64-v8a/libil2cpp.so`（几 MB~几十 MB），旁边还有 `assets/bin/Data/Managed/Metadata/global-metadata.dat`。
- PC/Windows 游戏目录下有 `GameAssembly.dll` + `<Game>_Data/il2cpp_data/Metadata/global-metadata.dat`。
- `dnSpy` 打开 `Assembly-CSharp.dll` 只有几百字节的 `DummyDll`（空壳）。
- 字符串里有 `il2cpp_init`、`mscorlib.dll`、`UnityEngine.CoreModule.dll`。
- 题面提示：`Unity`、`il2cpp`、`il2cppdumper`、`metadata`。
- Il2CppDumper 输出 `dump.cs`、`script.json`、`il2cpp.h`、`stringliteral.json`。
- 有 `global-metadata.dat` 被加密（头部 magic 不是 `AFC1D57F`）的迹象。

## 二、原理

### 1. IL2CPP 是什么

Unity 把 C# 的 IL **AOT 编译成 C++**，再编译成原生 `.so`/`.dll`。于是：

- 代码在 `libil2cpp.so`（原生机器码）
- 元数据（类名、方法名、字段名、字符串）在 `global-metadata.dat`
- 两个文件是**分离**的，必须**配对**才能还原出 `dump.cs`

### 2. global-metadata.dat 的结构（关键）

```
Magic: 0xFAB11BAF （小端字节：AF 1B B1 FA）
version: u32（常见 24 / 27 / 29 / 31）
...
stringLiteralOffset, stringLiteralCount      ← 字符串字面量
stringOffset, stringCount                    ← 字符串表
eventsOffset / methodsOffset / fieldsOffset  ← 各元数据表
typeDefinitionsOffset                        ← 类定义
imagesOffset / assembliesOffset
```

**版本号极度重要**：Il2CppDumper 按 version 决定表结构；改版本号会解析出乱码。

### 3. Il2CppDumper 的工作流

```
libil2cpp.so  ──读 CodeRegistration / MetadataRegistration（由 il2cpp_codegen_initialize 定位）
              ──枚举 MethodInfo[]、Il2CppCodeGenModule[]
global-metadata.dat ──解析 TypeDefinition / MethodDefinition / FieldDefinition
                     ──合并 → dump.cs + script.json
```

### 4. 加密对抗

- **metadata 加密**：头部 magic 被改（不是 `AF 1B B1 FA`）、XOR 全表、加密前 0x100 字节。
- **header 结构改变**（如把字符串表挪位）→ 需要手工修 header 再 dump。
- 常见处理：搜索内存中解密后的 `global-metadata.dat`（它必须在运行时被解密加载）。

## 三、解题步骤

1. **配对文件**：`libil2cpp.so` + `global-metadata.dat`（版本必须来自同一构建）。
2. **跑 Il2CppDumper**：
   ```
   Il2CppDumper.exe libil2cpp.so global-metadata.dat output/
   ```
3. **看 `dump.cs`**：搜 `Flag`、`Check`、`Game`、`Verify` 类，找 `Class$$Method`。
4. **找地址**：在 `script.json` 里按方法名查 `Address`（RVA）。
5. **IDA 导入**：`File → Script file → il2cppdumper 的 il2cpp_header.py` 或 `ghidra_with_struct.py`。
6. **`stringliteral.json`**：所有 UI 文本都被反查，flag 格式可能直接出现。
7. **加密场景**：Frida 在 `il2cpp_init` 后 dump 内存里的 metadata（在 `libil2cpp.so` 的 `MetadataLoader::LoadMetadataFile` 之后）。

## 四、可直接运行的脚本

标准流程（Linux/Windows 均可）：

```bash
# 1) 从 APK 抽文件
unzip game.apk 'lib/arm64-v8a/libil2cpp.so' \
               'assets/bin/Data/Managed/Metadata/global-metadata.dat' -d extracted/

# 2) dump
Il2CppDumper extracted/libil2cpp.so \
              extracted/assets/bin/Data/Managed/Metadata/global-metadata.dat \
              output/

# 3) 查看结果
ls output/
# dump.cs  script.json  il2cpp.h  stringliteral.json  dummy.cs
```

快速检索关键类：

```bash
grep -nE "class .*(Flag|Check|Verify|Game|Secret)" output/dump.cs | head -30
grep -n "flag" output/stringliteral.json | head
```

从 `script.json` 拿 RVA：

```python
import json

data = json.load(open("output/script.json", encoding="utf-8"))
for s in data.get("ScriptMethod", []):
    if any(k in s["Name"] for k in ("Check", "Verify", "Flag", "Decrypt")):
        print("%-70s 0x%x" % (s["Name"], s["Address"]))
```

IDA 里自动导入（Il2CppDumper 自带脚本）：

```python
# IDA: File -> Script File -> ida_with_struct.py（配合 il2cpp.h）
# 或使用 il2cpp_header.py（仅导函数名，不需要 struct）
```

检测 metadata 是否被加密：

```python
import struct, sys

b = open(sys.argv[1], "rb").read(16)
magic = struct.unpack("<I", b[:4])[0]
print("magic = 0x%08X (expect 0xFAB11BAF)" % magic)
print("raw   =", b[:8].hex())
if magic != 0xFAB11BAF:
    print("-> metadata 可能被加密/改了 magic，需要解密或修 header")
```

Frida 从内存 dump 解密后的 metadata（Android）：

```javascript
// 在 il2cpp_init 之后，metadata 已被解密到内存
const lib = Process.findModuleByName("libil2cpp.so");
console.log("libil2cpp base:", lib.base);

// 找 MetadataLoader 加载函数的返回值（简化：搜 magic 于可读段）
function scan() {
    Process.enumerateRanges("r--").forEach(r => {
        try {
            const hit = Memory.scanSync(r.base, Math.min(r.size, 0x4000000),
                                        "af 1b b1 fa");
            if (hit.length) {
                console.log("metadata @", hit[0].address, "range", r.base);
                const size = 0x2000000;
                const data = Memory.readByteArray(hit[0].address, size);
                const f = new File("/sdcard/metadata.dat", "wb");
                f.write(data); f.flush(); f.close();
            }
        } catch (e) {}
    });
}
setTimeout(scan, 3000);
```

## 五、常见坑 / 变体

- **metadata 被加密**：`Il2CppDumper` 报 `ERROR: Metadata file supplied is not a valid metadata file` → 先解出 header（magic 改成 `AF 1B B1 FA` 再试），或用运行时 dump。
- **版本不匹配**：`libil2cpp.so` 与 metadata 必须同一构建；混用会得到错误类名。
- **`dump.cs` 里的方法体为空**：那是外壳类型声明，真实逻辑在 `libil2cpp.so` 里，需要 IDA 看 RVA。
- **`script.json` 的 Address 是 RVA 还是 VA**：IL2CppDumper 输出通常是 **VA**（含 image base），IDA 里要减去 base。
- **Unity 版本太新（il2cpp > 29）**：Il2CppDumper 需升级到最新 release。
- **meta 被 patch 过（防止 dump）**：常见做法是 `Il2CppCodeRegistration` 指针加密，需在 IDA 里找解密函数。
- **变体：Il2CppInspector 支持 iOS/PC/多平台**，还能生成 `.cs` 工程。
- **变体：`GameAssembly.dll` 被 Themida 加壳** → 先脱壳再 dump。
- **变体：方法体被混淆（CIL2CPP / Beebyte）** → 名字保持，但有大量跳转，需动态执行。
- **注意**：`dump.cs` 里搜到 `Check` 后别忘了 `MonoBehaviour` 的回调（`Update`/`Start` 调用链）也在 `dump.cs` 里。

## 六、参考来源

- [Perfare/Il2CppDumper](https://github.com/perfare/il2cppdumper)
- [katboi01/Il2CppInspector](https://github.com/djkaty/Il2CppInspector)
- [Il2CppDumper Online](https://il2cppdumper.com/)
- [Unity 官方文档 — IL2CPP](https://docs.unity3d.com/Manual/IL2CPP.html)
- [frida](https://github.com/frida/frida)
- [Ghidra](https://github.com/NationalSecurityAgency/ghidra)
