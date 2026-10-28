---
title: Flutter / Dart AOT 逆向（libapp.so 与 Blutter）
category: reverse
tags: [flutter, dart, aot, libapp, blutter]
signals: [APK 的 lib 目录下有 libapp.so 且体积超过 5MB, 没有 libflutter_engine.so 只有 libflutter.so, 程序 UI 有 Flutter 的 Material 控件风格, 反编译 dex 只看到 MainActivity 与 FlutterActivity, assets 里没有 Flutter 业务代码, 题面提示「Flutter」「Dart」, libapp.so 字符串里有 _kDartVmSnapshotData, 存在 dart:ffi 与 isolate 相关符号, 使用 frida hook Java 层拿不到校验逻辑]
difficulty: hard
source: "worawit/blutter / Flutter 官方"
tools: [blutter, ida, python, frida]
updated: 2026-10-22
---

## 一、识别信号（题面长什么样）

- `lib/arm64-v8a/libapp.so` 几 MB 到几十 MB，`libflutter.so` 也很大。
- `classes.dex` 里几乎只有 `FlutterActivity`、`io.flutter.embedding.*`，找不到业务逻辑。
- `res/` 下有 `flutter_assets/`，`kernel_blob.bin` 在 **debug 构建**里才存在（release 被 AOT 成 `libapp.so`）。
- 字符串里有 `_kDartVmSnapshotData`、`_kDartIsolateSnapshotInstructions`、`dart:core`。
- 题面提示：`Flutter`、`Dart`、`libapp.so`、`AOT`、`Blutter`。
- Frida 只能 hook Java 层（如 `MainActivity`），拿不到 check 逻辑。
- 有 `.dill` 文件（未 AOT 的 kernel snapshot，能被 `dart` 直接反编译）。

## 二、原理

### 1. Flutter 的编译链

```
Dart 源码 --(dart compile kernel)--> kernel snapshot (dill)
          --(gen_snapshot)--> libapp.so (AOT 机器码 + Dart 对象快照)
```

- `libapp.so` = **AOT 编译后的机器码**，没有 Java 字节码。
- 快照里有 `DartVmSnapshotData`、`DartIsolateSnapshotData`（对象池、字符串、类信息）。
- 函数名以 `Symbol` 形式保留在快照的 `CodeSourceMap`/`ObjectPool` 里（**部分版本会 strip**）。

### 2. Blutter 做的事

1. 解析 `libflutter.so` 找到 Dart VM 版本与 `Dart_*` 函数地址。
2. 用 Dart VM 的 **`dart::Snapshot` 反序列化逻辑**读取 `libapp.so` 的 isolate snapshot。
3. 恢复所有 class / function 的名字与地址。
4. 输出：
   - `asm/`（每个函数一个 `.asm` 伪汇编）
   - `pp.txt`（对象池内容→可读字符串）
   - `ida_script/`（IDA 用的符号导入脚本，含函数名与类型）

### 3. 为什么必须配对应版本 libflutter.so

Blutter 需要 `dart::Snapshot::kMagicValue` 和对象布局，版本不对就解析失败。一般 `flutter --version` 或 `strings libflutter.so | grep "Dart VM version"` 可查。

## 三、解题步骤

1. **确认 Flutter**：看 dex 与 `libapp.so`。
2. **取版本**：`strings libapp.so | grep -m1 "Dart VM"`；或用 Blutter 自带探测。
3. **准备 libflutter.so**：`flutter_tools` 的 `bin/cache/artifacts/engine/android-arm64-release/` 里对应版本；Blutter 支持自动下载。
4. **跑 Blutter**：`python3 blutter.py <libapp.so 目录> <output 目录>`。
5. **看 `pp.txt`**：常量和字符串都在里面，flag 校验的关键字符串常在此。
6. **看 `asm/`**：搜索 `main`、`check`、`verify`、`XOR` 相关函数名，IDA 用 `ida_script` 导入。
7. **动态验证**：Frida hook `dart` 函数（需要计算真实地址），或在 `libapp.so` 导出函数上下断。

## 四、可直接运行的脚本

Blutter 全流程：

```bash
git clone https://github.com/worawit/blutter
cd blutter
pip install -r requirements.txt
python3 blutter.py /path/to/apk_unzipped/lib/arm64-v8a ./out
# 输出目录结构：
#   out/asm/*.asm
#   out/pp.txt
#   out/objs.txt
#   out/ida_script/addNames.py
```

从 APK 里抽取关键文件：

```python
import zipfile, sys

apk = sys.argv[1]
with zipfile.ZipFile(apk) as z:
    for n in z.namelist():
        if n.endswith(("libapp.so", "libflutter.so")):
            open(n.split("/")[-1], "wb").write(z.read(n))
            print("saved", n)
```

在 `pp.txt` 里搜关键字符串：

```bash
grep -nE "flag|check|verify|wrong|correct|key|xor" out/pp.txt | head -50
```

在 `asm/` 里找校验函数（按名字）：

```python
import os, re

for fn in sorted(os.listdir("out/asm")):
    if not fn.endswith(".asm"):
        continue
    txt = open(os.path.join("out/asm", fn), encoding="utf-8", errors="ignore").read()
    if re.search(r"(flag|check|verify|decrypt|validate)", txt, re.I):
        print("==", fn)
        print("\n".join(txt.splitlines()[:40]))
```

Frida hook Dart AOT 函数（拿到地址后）：

```javascript
// 先用 Blutter 输出的 libapp.so 基址 + 函数偏移
const base = Process.findModuleByName("libapp.so").base;
const fn = base.add(0x1a2b3c);          // ← 从 asm 文件里的 offset

Interceptor.attach(fn, {
  onEnter(args) {
    console.log("call at", this.returnAddress);
    // Dart AOT 参数在 x0..x7 (arm64)
  },
  onLeave(ret) {
    console.log("ret =", ret);
  }
});
```

检查 debug 版 kernel_blob（能直接反编译）：

```bash
# debug 构建才有 assets/flutter_assets/kernel_blob.bin
unzip app-debug.apk assets/flutter_assets/kernel_blob.bin
# 用 dartsdk 的 kernel-service 或 visualizer 打开
```

## 五、常见坑 / 变体

- **libflutter.so 版本不匹配**：Blutter 报 `unsupported snapshot` → 从 APK 里抽原始 `libflutter.so` 给 Blutter，别下载错版本。
- **arm64 才有支持**：Blutter 目前主要支持 Android arm64 的 `libapp.so`，arm32 需另想办法。
- **函数名被 strip**：`pp.txt` 仍有字符串；函数名只剩 `sub_xxx`，靠交叉引用整理。
- **deferred libraries** 让函数分散在多个快照 → 输出更多文件。
- **变体：Flutter Windows/Desktop** —— `data/app.so` + `flutter_windows.dll`，Blutter 有社区分支。
- **变体：flutter_secure_storage 里存 key** —— 在 `libapp.so` 中找对应实现。
- **变体：isolate（多线程）** —— 入口在 `dart:isolate` 的 spawn 回调。
- **变体：用 FFI 调 native 加密库** —— 校验在 `.so` 里，Blutter 反向指回去。
- **注意**：release 构建下没有 `kernel_blob.bin`；能拿到 dill 就直接用 `dart` SDK 反编译，比 AOT 容易得多。

## 六、参考来源

- [worawit/blutter — Flutter Application Reverse Engineering Tool](https://github.com/worawit/blutter)
- [Flutter 官方文档 — Build and release an Android app](https://docs.flutter.dev/deployment/android)
- [Dart 官方文档 — dart compile](https://dart.dev/tools/dart-compile)
- [frida](https://github.com/frida/frida)
- [Perfare/Il2CppDumper](https://github.com/perfare/il2cppdumper)
- [Ghidra](https://github.com/NationalSecurityAgency/ghidra)
