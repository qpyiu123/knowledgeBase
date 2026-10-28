---
title: Android native 逆向（.so 的 IDA 分析、JNI 静态与动态注册）
category: mobile
tags: [native, jni, so, register-natives, ida, unidbg]
signals: [lib 目录下有 libnative.so 或 libcore.so, Java 层方法声明为 native 没有任何实现, 关键算法都在 native 层实现, 用 jadx 搜索 System.loadLibrary 发现加载了多个 so, java 层 native 方法名与 so 里导出的符号对不上, so 文件被 strip 过没有符号表, 程序用 jni 把参数转成 byte 数组传给 native]
difficulty: hard
source: "Oracle JNI 规范 / OWASP MASTG 的 native 分析方法 / 逆向 JNI 动态注册公开研究"
tools: [ida, ghidra, jadx, apktool, frida, readelf, nm, objdump, r2, unidbg]
updated: 2026-10-22
exec_yaml: ok
---

## 一、识别信号（题面长什么样）

- `jadx` 里看到 `public static native String check(String s);`，方法体不存在。
- `System.loadLibrary("native-lib")` 或 `System.load("/data/.../libx.so")`。
- `unzip -l app.apk` 有 `lib/arm64-v8a/*.so`，几个 so 之间有依赖（`libx.so` 又加载别的）。
- `readelf -s libx.so | grep Java_` 只有一个 `JNI_OnLoad`，说明用**动态注册**。
- 方法名是 `a`、`b`、`c` 混淆过的，Map 不到 `Java_<package>_<class>_<method>`。
- so 很大（几 MB），但 Java 层只调用一两个方法 → 大部分逻辑在 native。

## 二、原理

**JNI 两种注册方式：**

1. **静态注册**：native 方法名必须严格符合 `Java_<包名>_<类名>_<方法名>`（`_` 转 `_1`、`/` 转 `_`）。所以 `readelf -s` 能直接搜到 `Java_com_ctf_demo_MainActivity_check`。
2. **动态注册**：在 `JNI_OnLoad` 里调用 `env->RegisterNatives(clazz, methods, n)`，`JNINativeMethod { const char* name; const char* signature; void* fnPtr; }` 表把 Java 名字映射到任意地址。**符号表里只有 `JNI_OnLoad`**。

**逆向动态注册的三板斧：**

- 在 `JNI_OnLoad` 里找 `RegisterNatives` 的调用点，读出那张 `JNINativeMethod` 数组（名字字符串 + 函数指针）。
- 在运行时用 Frida Hook `RegisterNatives` 直接打印映射。
- 用 unidbg 做"模拟执行"：不启动 Android，直接加载 so 跑 native 方法，绕过反调试。

**JNI 调用约定要点（ARM64）**：`JNIEnv*` 是第一个参数，`jobject/jclass` 第二个，之后才是 Java 参数；`jstring` 是句柄，要 `GetStringUTFChars` 才能取内容。

## 三、操作步骤

1. **Java 侧定位入口**：jadx 搜 `native` 与 `loadLibrary`，列出所有 native 方法与声明类。
2. **确认注册方式**：`readelf -sW libx.so | grep -E 'Java_|JNI_OnLoad'`。
3. **静态注册**：直接按符号名跳到函数，看参数处理。
4. **动态注册**：
   - IDA 打开，找 `JNI_OnLoad`（一般是从 `JNI_OnLoad` 导出符号定位），回溯到 `RegisterNatives` 的调用；
   - 读 `JNINativeMethod` 数组的三元组（名字、签名、指针），把指针重命名。
5. **交叉验证**：Frida Hook `RegisterNatives` 打印运行时真实映射（能拿到被混淆的名字）。
6. **分析算法**：搜字符串、常量表（TEA/AES S 盒）、`memcmp` 调用点。
7. **动态调参**：用 Frida 直接调用目标方法，喂输入观察输出。

## 四、命令 / 脚本

```bash
# 快速判定注册方式
readelf -sW lib/arm64-v8a/libnative.so | grep -E 'Java_|JNI_OnLoad|RegisterNatives'
nm -D --defined-only lib/arm64-v8a/libnative.so | head -30
strings -n 6 lib/arm64-v8a/libnative.so | grep -iE 'flag|key|check|decrypt'
# apktool 看 Java 声明
apktool d app.apk -o app_src && grep -rn 'native ' app_src/smali | head
# 检测混淆与壳
readelf -d lib/arm64-v8a/libnative.so | grep NEEDED
```

```javascript
// hook RegisterNatives：打印所有动态注册的映射
var RegisterNatives = null;
var libart = Module.findExportByName(null, '_ZN3art3JNI15RegisterNativesEP7_JNIEnvP7_jclassPK15JNINativeMethodi');
if (libart) {
    Interceptor.attach(libart, {
        onEnter: function (args) {
            var env = args[0], clazz = args[1], methods = args[2], n = args[3].toInt32();
            console.log('[RegisterNatives] n=' + n);
            for (var i = 0; i < n; i++) {
                var name = methods.add(i * Process.pointerSize * 3).readPointer();
                var sig = methods.add(i * Process.pointerSize * 3 + Process.pointerSize).readPointer();
                var fn = methods.add(i * Process.pointerSize * 3 + 2 * Process.pointerSize).readPointer();
                console.log('  ' + name.readCString() + ' ' + sig.readCString() +
                            ' -> ' + fn + ' (' + (fn.sub(Module.findBaseAddress('libnative.so') || fn)) + ')');
            }
        }
    });
} else {
    console.log('[-] 未找到 art::JNI::RegisterNatives，尝试 libdvm 或换 API 版本');
}
```

```python
#!/usr/bin/env python3
# 从 so 里静态找 JNINativeMethod 三元组（适用于未加壳、字符串明文的 so）
import re, struct, sys

def find_triples(path):
    d = open(path, 'rb').read()
    base = 0
    for m in re.finditer(rb'(Java_[A-Za-z0-9_]+|\b[a-zA-Z]{1,3}\b)\x00'
                         rb'(\([^)]*\)[A-Za-z\[;/I-Z]+)\x00', d):
        name, sig = m.group(1), m.group(2)
        if not sig.startswith(b'('):
            continue
        print('@%#x name=%-20s sig=%-30s' % (m.start(), name.decode(), sig.decode()))

if __name__ == '__main__':
    find_triples(sys.argv[1])
```

```java
// unidbg 直接调用 native 方法（绕过 Android 环境）
Emulator<?> emu = AndroidEmulatorBuilder.for64Bit().build();
Memory memory = emu.getMemory();
Module module = emu.loadLibrary("libnative", handle);
// 打印所有导出符号，按 Java_ 前缀找静态注册
for (Symbol symbol : module.getSymbols()) {
    if (symbol.getName().startsWith("Java_")) System.out.println(symbol.getName());
}
// 对已知偏移直接调用
Number ret = module.callFunction(emulator, 0x1234, arg1, arg2);
```

## 五、常见坑 / 变体

- **`_1` 转义**：Java 包名里带下划线时，符号里变成 `_1`，搜索时要还原。
- **`RegisterNatives` 的符号因 ART 版本而变**：不同 Android 版本 mangled name 不同，Hook 前先 `Module.enumerateSymbols` 搜 `RegisterNatives`。
- **`JNI_OnLoad` 被混淆**：有些壳把 `JNI_OnLoad` 改成自己导出的 `JNI_OnLoad` 加壳入口，真正的注册在第二层 so 里。
- **参数类型**：`char*` 不是 `jstring`，`env->NewStringUTF` 返回的句柄不能当 C 字符串直接读。
- **so 被 strip**：没有局部符号，只能靠字符串 xref 与 `RegisterNatives` 数组反推。
- **Frida 与 ART JIT 冲突**：在某些机器上 Hook 后目标会崩，改用 unidbg 静态跑。
- **变体**：Unity 的 `libil2cpp.so`（见 `dotnet-unity-il2cpp`）、Flutter 的 `libapp.so`（Dart AOT）、TFLite 模型里藏逻辑。

## 六、参考来源

- [Oracle JNI 规范（RegisterNatives 与命名规则）](https://docs.oracle.com/en/java/javase/21/docs/specs/jni/design.html)
- [OWASP MASTG：Android 原生代码逆向（JNI 与 so 分析）](https://mas.owasp.org/MASTG/techniques/android/MASTG-TECH-0044/)
- [Tracing JNI Functions：动态注册与地址计算实战](https://valsamaras.medium.com/tracing-jni-functions-75b04bee7c58)
- [unidbg 官方仓库（模拟执行 so）](https://github.com/zhkl0228/unidbg)
- [Ghidra 官方文档（反编译与符号恢复）](https://ghidra.re/)
