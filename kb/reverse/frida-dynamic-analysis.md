---
title: Frida 动态分析二进制（native hook、trace、内存 dump）
category: reverse
tags: [frida, hook, trace, dump, dynamic]
signals: [需要在不改文件的情况下观察函数参数与返回值, 程序有强完整性校验无法直接 patch, 目标是 APK / iOS / 桌面原生程序, 需要 dump 解密后的内存数据, 有 frida-server 需在设备上跑, 题面提示「动态」「hook」, 校验逻辑在 native 层而 Java 层是空壳, 需要 trace 某个函数的所有调用, 存在 JNI 与 System.loadLibrary]
difficulty: medium
source: "frida 官方文档 / Frida JavaScript API"
tools: [frida, python, adb, gdb]
updated: 2026-10-22
---

## 一、识别信号（题面长什么样）

- 校验逻辑被封在 `.so` 里，静态反编译看不懂（VM / 混淆）。
- 程序启动时检测调试器/内存完整性，直接 patch 会崩。
- 题目提供 APK（有 native lib），或有 iOS/Mach-O 文件。
- 需要"看运行时某个函数收到的参数"、"把解密后的明文内存 dump 出来"。
- 题面提示：`Frida`、`hook`、`动态`、`trace`、`dump`、`frida-server`。
- 附件里有 `frida-server` 或 `frida-gadget.so`。
- 明文只在运行时出现一次（用完即清），静态搜不到。

## 二、原理

### 1. Frida 的三个角色

| 角色 | 作用 |
|---|---|
| **frida-server**（Android/越狱 iOS） | 在目标进程注入 agent |
| **frida-gadget.so** | 作为库被 `System.loadLibrary` 加载（免 root） |
| **frida CLI / Python API** | 发起脚本 |

### 2. Attach vs Spawn

- `frida -U -f com.target.app`：**spawn**，在最早期注入，能拦 `System.loadLibrary` 与 `JNI_OnLoad`。
- `frida -U com.target.app`：**attach**，程序已运行，只能拦后面的调用。
- 逆向一般用 **spawn** + `setTimeout(main, 0)` 保证早于业务代码。

### 3. 核心 API

| API | 作用 |
|---|---|
| `Interceptor.attach(ptr, callbacks)` | 在函数入口/返回处回调 |
| `Interceptor.replace(ptr, cb)` | 替换整个函数 |
| `Stalker.follow(threadId)` | 指令级 trace |
| `Memory.scan(addr, size, pattern)` | 内存搜索 |
| `Process.enumerateModules()` | 模块基址 |
| `Module.findExportByName("libc.so", "strcmp")` | 找导出 |
| `NativeFunction` | 自己调用 native 函数 |

### 4. 常见用途

- **trace 参数**：`onEnter` 里读 `args[0..3]`，打印 `readUtf8String`。
- **dump 解密后内存**：hook 解密函数返回处，读输出 buffer。
- **绕过反调试**：hook `ptrace`、`fopen("/proc/self/status")` 返回假值。
- **动态调用**：`NativeFunction` 直接调校验函数暴力枚举。

## 三、解题步骤

1. **准备设备/环境**：root 安卓机 + `frida-server`（匹配 `frida` 版本），或 `frida-gadget` 注入桌面程序。
2. **列出模块**：`frida -U -f pkg -l list.js` 看 `libX.so` 的基址与导出。
3. **hook 关键函数**：找 `strcmp`、`memcmp`、`System.loadLibrary`、自定义 `JNI_OnLoad`。
4. **拿到参数**：`onEnter` 打印，配合 `Thread.backtrace` 定位调用者。
5. **dump 内存**：`Memory.readByteArray` + `File.write`。
6. **trace 全流程**：`Stalker` 跟一个线程，导出 `trace` 给 IDA 分析。
7. **验证**：拿到明文/密钥后回到静态分析交叉验证。

## 四、可直接运行的脚本

列出模块与导出：

```javascript
// list_modules.js
Process.enumerateModules().forEach(m => {
  console.log(m.name, m.base, m.size);
  if (m.name.includes("target")) {
    m.enumerateExports().forEach(e => console.log("  ", e.name, e.address));
  }
});
```

hook `strcmp`/`memcmp` 看比较内容：

```javascript
// hook_strcmp.js
const strcmp = Module.findExportByName(null, "strcmp");
Interceptor.attach(strcmp, {
  onEnter(args) {
    this.a = args[0].readUtf8String();
    this.b = args[1].readUtf8String();
  },
  onLeave(retval) {
    if (this.a && this.b)
      console.log("[strcmp]", JSON.stringify(this.a), "vs", JSON.stringify(this.b),
                  "=>", retval.toInt32());
  }
});

const memcmp = Module.findExportByName(null, "memcmp");
Interceptor.attach(memcmp, {
  onEnter(args) {
    this.a = args[0]; this.b = args[1]; this.n = args[2].toInt32();
  },
  onLeave(retval) {
    if (this.n > 0 && this.n < 64)
      console.log("[memcmp]", this.n, retval.toInt32(),
                  hexdump(this.a, {length: this.n}), hexdump(this.b, {length: this.n}));
  }
});
```

python 版本（自动化跑多组输入）：

```python
import frida, sys

JS = """
const strcmp = Module.findExportByName(null, "strcmp");
Interceptor.attach(strcmp, {
  onEnter(args) { this.a = args[0].readUtf8String(); this.b = args[1].readUtf8String(); },
  onLeave(ret) { console.log(JSON.stringify([this.a, this.b, ret.toInt32()])); }
});
"""

def on_message(msg, data):
    if msg["type"] == "send":
        print("MSG", msg["payload"])
    elif msg["type"] == "error":
        print("ERR", msg["stack"])

session = frida.attach("target.exe")            # 或 frida.spawn + resume
script = session.create_script(JS)
script.on("message", on_message)
script.load()
sys.stdin.read()
```

内存 dump（在某函数返回处抓 buffer）：

```javascript
// dump.js
const base = Process.findModuleByName("libtarget.so").base;
const fn = base.add(0x1234);                    // ← 从 IDA 拿到的偏移

Interceptor.attach(fn, {
  onEnter(args) { this.out = args[1]; },        // 假设 arg1 是输出 buffer
  onLeave(ret) {
    const buf = Memory.readByteArray(this.out, 0x100);
    const f = new File("/sdcard/dumped.bin", "wb");
    f.write(buf); f.flush(); f.close();
    console.log("dumped to /sdcard/dumped.bin");
  }
});
```

Frida CLI 常用命令：

```bash
pip install frida-tools                # 安装客户端
frida-ps -U                            # 列出设备进程
frida -U -f com.target.app -l hook_strcmp.js --no-pause     # 注入
adb forward tcp:27042 tcp:27042
adb push frida-server-16.x-android-arm64 /data/local/tmp/frida-server
adb shell "chmod 755 /data/local/tmp/frida-server && su -c '/data/local/tmp/frida-server &'"
```

`frida-trace` 一行看调用：

```bash
frida-trace -U -f com.target.app -i "strcmp" -i "memcmp" -i "malloc"
```

## 五、常见坑 / 变体

- **spawn 太晚**：反调试在 `JNI_OnLoad` 就检测 → 用 `frida -f --no-pause`，并尽早 hook `ptrace`。
- **frida-server 版本不匹配**：`frida --version` 与设备上的 server 必须一致。
- **隐藏 frida 检测**：hook `fopen("/proc/self/maps")`、`pthread_create` 过滤，或读 `frida` 关键字。
- **`Interceptor.attach` 断在 thunk**：某些导入是 PLT 跳板，需跟到真实地址。
- **多线程**：`Stalker.follow(Process.getCurrentThreadId())` 只跟一个线程。
- **变体：Frida Gadget** —— 把 `libgadget.so` 改名 `libX.so`，在 `AndroidManifest` 里 `System.loadLibrary("X")`。
- **变体：iOS** —— `frida -U -f com.app -l script.js`，Mach-O 上 `Module.findExportByName(null, "_strcmp")` 带下划线。
- **变体：Windows** —— `frida -f target.exe -l s.js`，`Module.findExportByName("msvcrt.dll", "strcmp")`。
- **变体：hook Java 层**（`Java.perform`）—— 与已有 `android-basics` 区分，本篇聚焦 native。
- **注意**：Frida 会被某些反作弊检测，CTF 中一般不影响。

## 六、参考来源

- [frida 官方文档](https://frida.re/docs/home/)
- [Frida JavaScript API](https://frida.re/docs/javascript-api/)
- [frida/frida（GitHub）](https://github.com/frida/frida)
- [frida-dexdump](https://github.com/hluwa/frida-dexdump)
- [Hook 原生方法 —— Frida 教程](https://frida.re/docs/android/)
- [Ghidra](https://github.com/NationalSecurityAgency/ghidra)
