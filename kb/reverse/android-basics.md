---
title: Android APK 逆向与 native so 分析
category: reverse
tags: [Android, APK, so, JNI, jadx, IDA, arm64]
signals: [附件是 .apk, 有 lib/arm64-v8a/*.so, Java 层逻辑很少, 校验在 native 层, 题面说 flag 在 so 里]
difficulty: medium
source: "CTF-Wiki Android 逆向 / MASTG / jadx 与 apktool 文档"
tools: [jadx, apktool, IDA, Ghidra, apkanalyzer, adb, unzip, readelf]
updated: 2026-10-22
---

## 一、识别信号（题面长什么样）

- 附件是一个 `.apk`（本质是 zip）。
- `unzip -l` 显示 `lib/arm64-v8a/libnative.so`、`classes.dex`。
- Java 层只有 `System.loadLibrary("native")` 和 `native` 方法声明，核心逻辑全在 so。
- 反编译 Java 看到 `native boolean check(String s);` 这种声明。
- 题目提示「静态注册」或「动态注册（JNI_OnLoad）」。

## 二、原理

APK 结构：

```text
AndroidManifest.xml   (二进制 AXML，需 apktool 解)
classes.dex            (Dalvik 字节码)
classes2.dex ...
lib/arm64-v8a/*.so     (native 库，arm64)
lib/armeabi-v7a/*.so   (arm32)
resources.arsc         (资源索引)
assets/                (任意文件，常藏 flag / 加密数据)
META-INF/              (签名)
```

**JNI 两条注册路径**：

1. **静态注册**：Java 的 `native void foo()` 对应 so 里 `Java_<包名>_<类名>_<方法名>`，符号名可直接搜。
2. **动态注册**：`JNI_OnLoad` 里调用 `RegisterNatives(env, clazz, gMethods, n)`，`gMethods` 数组里才有符号名与函数指针。必须先在 so 里找 `JNI_OnLoad`，再解析数组。

**架构判断**：用 IDA 分析 so 时要选对 `arm64-v8a` / `ARM Little-endian`，否则反汇编全乱。

## 三、checksec 判读与利用思路

流程：

```text
1. unzip -l chall.apk                 # 看结构，找 so 与 assets
2. apktool d chall.apk -o out          # 反编译资源与 smali
3. jadx -d jadx_out chall.apk          # Java 源码级还原
4. grep -r "loadLibrary\|native "      # 找 native 入口
5. 把 so 拖进 IDA/Ghidra，选 arm64
6. 静态注册：搜 Java_ 前缀；动态注册：找 JNI_OnLoad -> RegisterNatives 数组
```

so 的判读要点：

| 现象 | 含义 |
|---|---|
| `.init_array` 有函数 | 可能在 `main` 之前解密数据 |
| 有 `JNI_OnLoad` | 动态注册，顺着 `RegisterNatives` 找 |
| 大量 NEON 指令（`ld1/eor3`） | SIMD 加密/校验 |
| 有 `atexit` 注册 | 退出时校验/吐 flag |
| `.text` 熵高 | 可能加了壳或 SMC |

## 四、可直接运行的 exp 脚本

```bash
#!/bin/bash
# apk 一键侦察（Linux/macOS/bash）
set -e
APK=${1:-./chall.apk}
OUT=./apk_out
rm -rf "$OUT"; mkdir -p "$OUT"

echo "[1] 文件类型与包名"
file "$APK"
apkanalyzer manifest print "$APK" 2>/dev/null | grep -E "package=|android:name=" | head -20

echo "[2] 解包"
unzip -o -q "$APK" -d "$OUT/raw"
find "$OUT/raw/lib" -name "*.so" 2>/dev/null | while read -r so; do
  echo "  so: $so  arch=$(readelf -h "$so" | awk -F: '/Machine/{print $2}')"
done

echo "[3] dex 反编译（jadx）"
jadx -q -d "$OUT/java" --show-bad-code "$APK"

echo "[4] 资源与 smali（apktool）"
apktool d -f -q -o "$OUT/smali" "$APK"

echo "[5] 找 native 入口"
grep -rn "loadLibrary" "$OUT/java" | head -10
grep -rn "native " "$OUT/java" | head -10

echo "[6] so 里的 JNI 符号"
for so in $(find "$OUT/raw/lib" -name "*.so" 2>/dev/null); do
  echo "--- $so"
  readelf -sW --dyn-syms "$so" 2>/dev/null | grep -E "Java_|JNI_OnLoad|RegisterNatives" | head -20
  strings -a "$so" | grep -iE "flag|check|key|encrypt" | head -10
done
```

```python
#!/usr/bin/env python3
# 解析动态注册的 gMethods 数组（静态分析 or Frida 辅助）
# gMethods 结构：{name: const char*, signature: const char*, fnPtr: void*}
import struct, sys

def parse_gmethods(buf, base_addr, ptr_size=8, count=8):
    """buf: so 中 gMethods 处的原始字节；base_addr: 该处在内存中的地址"""
    out = []
    for i in range(count):
        off = i * 3 * ptr_size
        name_p  = struct.unpack_from("<Q" if ptr_size == 8 else "<I", buf, off)[0]
        sig_p   = struct.unpack_from("<Q" if ptr_size == 8 else "<I", buf, off + ptr_size)[0]
        fn_p    = struct.unpack_from("<Q" if ptr_size == 8 else "<I", buf, off + 2 * ptr_size)[0]
        if name_p == 0 and fn_p == 0:
            break
        out.append((hex(name_p), hex(sig_p), hex(fn_p)))
    return out

if __name__ == "__main__":
    # 占位：从 IDA 里 dump gMethods 的 8*3*8 字节后传入
    raw = bytes.fromhex("00" * 8 * 3 * 4)
    for row in parse_gmethods(raw, 0x0):
        print(row)
```

Frida 侧确认动态注册（设备已 root）：

```javascript
// 打印所有 RegisterNatives 注册的方法名与地址
const symbols = Process.enumerateModules().filter(m => /libnative|\.so$/.test(m.name));
const rn = Module.findExportByName(null, "RegisterNatives");
if (rn) {
  Interceptor.attach(rn, {
    onEnter(args) {
      const clazz = args[1], methods = args[2], n = args[3].toInt32();
      for (let i = 0; i < n; i++) {
        const p = methods.add(i * 3 * Process.pointerSize);
        const name = p.readPointer().readCString();
        const sig  = p.add(Process.pointerSize).readPointer().readCString();
        const fn   = p.add(2 * Process.pointerSize).readPointer();
        console.log(`[+] ${name}${sig} @ ${fn} (${DebugSymbol.fromAddress(fn)})`);
      }
    }
  });
}
```

## 五、常见坑 / 变体

- **`unzip` 不完整**：部分 APK 用 zipalign 或 `resources.arsc` 压缩异常，`apktool` 会优先处理，先用 `unzip -o` 再 `apktool`。
- **打包加壳（梆梆/爱加密）**：`classes.dex` 很小且是壳，需脱壳（Frida `frida-dexdump`）。
- **so 架构选错**：`arm64-v8a` 与 `armeabi-v7a` 都可能有，先确认题目跑哪一个（`AndroidManifest` 的 `abiFilters`）。
- **Thumb 模式**：arm32 so 中函数可能是 Thumb（奇数地址），IDA 需 `Alt+G` 切换。
- **静态注册符号被 strip**：`.dynsym` 里没有 `Java_`，则一定是动态注册，找 `JNI_OnLoad`。
- **`assets` 里有加密资源**：先看 Java 层怎么解密（`AES`/`XXTEA` 常见），再解 resources。
- **64 位 only**：x86 模拟器装不上，用 arm64 的 Android 11+ 镜像或真机。

## 六、参考来源

- [CTF-Wiki: Android 逆向基本介绍](https://ctf-wiki.org/android/basic_reverse/overview/)
- [CTF-Wiki: Android 关键代码定位](https://ctf-wiki.org/android/basic_reverse/android_code_location/)
- [CTF-Wiki: 静态分析原生层程序](https://ctf-wiki.org/android/basic_reverse/static/so-example/)
- [CTF-Wiki: so 介绍](https://ctf-wiki.org/android/basic_operating_mechanism/native_layer/so/)
- [jadx 官方仓库](https://github.com/skylot/jadx)
- [apktool 官方文档](https://apktool.org/docs/install)
- [HackTricks: Reversing Native Libraries](https://book.hacktricks.wiki/en/mobile-pentesting/android-app-pentesting/reversing-native-libraries.html)
- [OWASP MASTG Android 平台概览](https://mas.owasp.org/MASTG/0x05a-Platform-Overview/)
