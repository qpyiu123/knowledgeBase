---
title: iOS 逆向入门（ptrace 反调试 / class-dump / Frida）
category: mobile
tags: [iOS, ptrace, class-dump, Frida, IPA, arm64]
signals: [附件是 .ipa 或解密后的 Mach-O, 需要在越狱设备上跑, 有 LC_ENCRYPTION_INFO 加密段, 需要 dump Objective-C 类结构, 题目是 iOS 平台的 app]
difficulty: medium
source: "OWASP MASTG iOS / Frida iOS 文档 / 经典 iOS 逆向流程"
tools: [Frida, class-dump, Hopper, IDA, ios-deploy, frida-ios-dump, ldid, otool]
updated: 2026-10-22
---

## 一、识别信号（题面长什么样）

- 附件是 `.ipa`（本质是 zip），解压后是 `Payload/App.app/App`（Mach-O arm64）。
- `otool -l App | grep -A4 LC_ENCRYPTION_INFO` 显示 `cryptid 1`（App Store 加密）。
- 题目要求「在越狱设备上运行」或「先用 Frida 跑起来」。
- 有 `Info.plist`、`_CodeSignature`、`Frameworks/*.dylib`（Swift/RN/Flutter 应用）。
- 反编译后大量 `objc_msgSend`，类名与方法名以 `-[Class method]` 形式出现。

## 二、原理

iOS 应用（Mach-O）关键结构：

| 结构 | 作用 |
|---|---|
| `LC_ENCRYPTION_INFO(_64)` | App Store 加密段，`cryptid=1` 需解密才能静态分析 |
| `__TEXT,__objc_classname` | Objective-C 类名 |
| `__TEXT,__objc_methname` | 方法名 |
| `__DATA,__objc_classlist` | 类列表（class-dump 的数据源）|
| `LC_LOAD_DYLIB` | 依赖库（越狱后 hook 点）|

**iOS 反调试**：
- `ptrace(PT_DENY_ATTACH, 0, 0, 0)`：让调试器无法 attach。
- `sysctl` 检查 `kinfo_proc.kp_proc.p_flag & P_TRACED`。
- `getppid` 检查父进程是否为 `launchd`。
- 越狱检测：`/Applications/Cydia.app`、`/bin/bash`、`fork()` 是否成功、`cydia://` URL scheme。

**越狱环境**：`frida-server` 通过 `frida-ios-dump` 或 `ios-deploy` 安装，attach 无需重打包。

## 三、checksec 判读与利用思路

判读流程：

```text
1. unzip -l x.ipa                 # 看结构
2. otool -l App | grep -A4 -i crypt   # cryptid 是否为 1
3. file App                        # Mach-O 64-bit arm64
4. lipo -info App                  # 是否 fat（同时含 armv7/arm64）
5. class-dump App > classes.h      # 出类头文件
```

| 现象 | 处理 |
|---|---|
| `cryptid 1` | 需在越狱设备上 dump 解密后的可执行文件 |
| 全是 `objc_msgSend` | 需要 class-dump + IDA 的 ObjC 插件 |
| 有 `ptrace` 调用 | 先 patch 或 Frida hook |
| Swift 应用 | 符号 mangled，用 `swift-demangle` |
| Flutter/RN | 逻辑在 `App.framework`/`Hermes` 字节码里 |

## 四、可直接运行的 exp 脚本

### 1. 基础侦察

```bash
#!/bin/bash
# iOS ipa 侦察
IPA=${1:-./chall.ipa}
OUT=./ios_out
rm -rf "$OUT"; mkdir -p "$OUT"
unzip -o -q "$IPA" -d "$OUT/raw"
APP=$(find "$OUT/raw/Payload" -maxdepth 1 -name "*.app" | head -1)
BIN="$APP/$(defaults read "$APP/Info.plist" CFBundleExecutable 2>/dev/null || basename "$APP" .app)"
echo "[*] app=$APP"; echo "[*] bin=$BIN"

file "$BIN"
lipo -info "$BIN" 2>/dev/null || true
# 加密判定
otool -l "$BIN" | grep -A4 -i "LC_ENCRYPTION_INFO" || echo "[*] 无加密段（可能已解密）"
# 依赖与反调试线索
otool -L "$BIN" | head -20
strings -a "$BIN" | grep -iE "ptrace|PT_DENY_ATTACH|sysctl|Cydia|substrate|frida" | head -20
```

### 2. 解密（class-dump 前置）

```bash
# 越狱设备上：frida-ios-dump 直接拉取解密后的 Mach-O
pip install frida-tools
git clone https://github.com/AloneMonkey/frida-ios-dump
cd frida-ios-dump && pip install -r requirements.txt
./dump.py com.example.chall
# 产出 com.example.chall.ipa（已解密）

# 或用 Clutch（越狱设备）
Clutch -i
Clutch -d com.example.chall
```

### 3. class-dump 出类头文件

```bash
class-dump -H "$BIN" -o "$OUT/headers"     # 导出所有 .h
ls "$OUT/headers" | head
grep -rn "check\|verify\|flag" "$OUT/headers" | head -20
# Swift 类用 swift-demangle 处理符号
nm -gU "$BIN" | xcrun swift-demangle | grep -i "check" | head
```

### 4. Frida 绕过 ptrace 与越狱检测

```javascript
// ios_bypass.js —— frida -U -f com.example.chall -l ios_bypass.js --no-pause
// 1) 屏蔽 ptrace(PT_DENY_ATTACH)
var ptracePtr = Module.findExportByName(null, "ptrace");
if (ptracePtr) {
  Interceptor.replace(ptracePtr, new NativeCallback(function (req, pid, addr, data) {
    return 0;    // 直接返回成功，不真正调用
  }, 'int', ['int', 'int', 'pointer', 'int']));
  console.log("[+] ptrace disabled");
}

// 2) 越狱检测：文件是否存在
Interceptor.attach(Module.findExportByName(null, "access"), {
  onEnter: function (args) {
    try {
      var path = args[0].readCString();
      this.jailbreak = path && /Cydia|substrate|bash$|ssh$|apt$/.test(path);
      if (this.jailbreak) console.log("[-] hide jailbreak path: " + path);
    } catch (e) {}
  },
  onLeave: function (ret) {
    if (this.jailbreak) ret.replace(ptr(-1));   // -1 = 不存在
  }
});

// 3) Objective-C 方法替换（需 ObjC Runtime）
if (ObjC.available) {
  var cls = "Checker";
  if (ObjC.classes[cls]) {
    var m = ObjC.classes[cls]["- check:"];
    if (m) {
      Interceptor.attach(m.implementation, {
        onEnter: function (args) { console.log("[*] check: " + new ObjC.Object(args[2]).toString()); },
        onLeave: function (ret) { console.log("[*] -> " + ret); ret.replace(ptr(1)); }
      });
    }
  }
}
```

### 5. iOS Frida 环境

```bash
# 越狱设备：Cydia/Sileo 安装 Frida，或手动装 frida-server
frida-ps -U                     # 列进程
frida -U -f com.example.chall -l ios_bypass.js --no-pause
# 列 ObjC 类
frida -U com.example.chall -e 'ObjC.classes' 
```

### 4. Python 辅助：检查 cryptid 与导出符号

```python
#!/usr/bin/env python3
# 快速判断 Mach-O 是否加密、是否含反调试符号（无需 Xcode）
import pathlib, struct, sys

BIN = pathlib.Path(sys.argv[1] if len(sys.argv) > 1 else "./App")
data = BIN.read_bytes()
print("[*] magic:", data[:4].hex(), "size:", len(data))

# LC_ENCRYPTION_INFO_64 = 0x2C，cryptid 在命令后第 16 字节
MAGIC_64 = struct.unpack("<I", data[:4])[0]
print("[*] is arm64:", MAGIC_64 == 0xFEEDFACF)
for kw in (b"ptrace", b"PT_DENY_ATTACH", b"sysctl", b"Cydia", b"substrate", b"frida"):
    idx = data.find(kw)
    if idx >= 0:
        print(f"[+] {kw.decode():16s} @ {idx:#x}")
idx = data.find(b"__TEXT")
print("[*] 有 __TEXT 段:", idx >= 0)
```

## 五、常见坑 / 变体

- **`cryptid 1` 未解密**：静态看到的代码是加密的乱码，必须先 dump（`frida-ios-dump`/`Clutch`）。
- **沙盒限制**：未越狱设备上 `frida-server` 无法运行，只能走重签名注入（更麻烦）。
- **Swift 应用**：`class-dump` 看不到 Swift 类，需 `swift-demangle` + Hopper/IDA 的 Swift 支持。
- **Flutter 应用**：逻辑在 `App.framework/App`（AOT 快照），需 `reFlutter` 或 blutter。
- **RN 应用**：逻辑在 `main.jsbundle`（可读），或 Hermes 字节码（需 hermes-dec）。

## 六、参考来源

- [OWASP MASTG: iOS 逆向与测试指南](https://mas.owasp.org/MASTG/techniques/ios/MASTG-TECH-0085/)
- [Frida 官方文档（iOS 支持）](https://frida.re/docs/ios/)
- [Frida JavaScript API（ObjC 与 Interceptor）](https://frida.re/docs/javascript-api/)
- [AloneMonkey/frida-ios-dump](https://github.com/AloneMonkey/frida-ios-dump)
- [KJCracks/Clutch（解密工具）](https://github.com/KJCracks/Clutch)
- [nygard/class-dump](https://github.com/nygard/class-dump)
- [HackTricks: iOS Pentesting](https://book.hacktricks.wiki/en/mobile-pentesting/ios-pentesting/index.html)
- [0xdea/frida-scripts（常用 iOS hook 脚本集）](https://github.com/0xdea/frida-scripts)