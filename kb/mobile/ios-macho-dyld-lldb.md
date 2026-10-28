---
title: iOS 进阶（Mach-O、dyld 注入、LLDB 调试与砸壳）
category: mobile
tags: [ios, macho, dyld, lldb, class-dump, frida-ios-dump]
signals: [附件是一个 Mach-O 二进制或者 IPA, 题目说这是砸壳后的 ipa 可以直接反编译, 需要注入 dylib 绕过某个校验, 应用是 Swift 写的符号表被 strip 了, 题目要求用 lldb 断点停在某个函数, 二进制里有 __objc_classname 段能 dump 出全部类名]
difficulty: hard
source: "Apple dyld 开源文档 / LLDB 官方文档 / OWASP MASTG iOS 逆向章节"
tools: [lldb, class-dump, ipsw, frida, frida-ios-dump, Hopper, IDA, optool]
updated: 2026-10-22
exec_yaml: ok
---

## 一、识别信号（题面长什么样）

- 附件是 `.ipa`（其实是 zip，里面有 `Payload/App.app/App`）或直接一个无扩展名的 Mach-O。
- `file App` 输出 `Mach-O 64-bit arm64 executable` 或 `bundle`。
- 题目提示"已砸壳"，说明可以直接看真实代码。
- 二进制里 `strings` 有大量 Objective-C 类名与方法名（`__objc_methname` 段）。
- 校验逻辑在 `-[Class verify:]` 这类方法里。
- 需要"注入一个 dylib"或"重签名后安装"。

## 二、原理

**Mach-O 结构**：`Header`（magic `0xfeedfacf` 64 位）→ `Load Commands`（`LC_SEGMENT_64`、`LC_LOAD_DYLIB`、`LC_ENCRYPTION_INFO_64`、`LC_CODE_SIGNATURE`）→ `Sections`（`__TEXT.__text`、`__TEXT.__cstring`、`__DATA.__objc_classlist`）。

- **`LC_ENCRYPTION_INFO_64`**：表示 App 被 FairPlay 加密，`cryptid=1` 表示未解密；砸壳就是把这段解出来回写为 0。
- **Objective-C 运行时元数据**：类、方法、属性名全部明文存储在 `__objc_*` 段，即使 strip 了符号也拿得到。
- **dyld 注入**：`DYLD_INSERT_LIBRARIES` 只对未启用 hardened runtime 的二进制有效；签名后注入的做法是直接加 `LC_LOAD_DYLIB` 命令（`optool install -c load -p @executable_path/x.dylib -t App`），再重签名。
- **LLDB 调试**：`debugserver` 在设备上跑，LLDB 通过 `process connect connect://...` 附加；越狱设备可直接 `frida -U`。

## 三、操作步骤

1. **判加密**：`otool -l App | grep -A4 LC_ENCRYPTION_INFO`，`cryptid 1` 需先砸壳。
2. **砸壳**：`frida-ios-dump -o out.ipa <bundleid>`（需越狱设备）或 `ipsw` 提 `dyld_shared_cache`。
3. **静态分析**：`class-dump` 出头文件；Hopper/IDA 打开看 `-[verify:]`。
4. **找逻辑**：`strings -a App | grep -i flag`，再用 `__objc_methname` 与 xref 定位。
5. **动态验证**：LLDB 下断点 `b -[Demo verify:]`，看参数寄存器 `x0/x1/x2`（arm64）。
6. **注入 hook**：用 `optool`/`insert_dylib` 加 `LC_LOAD_DYLIB`，或用 `frida` 直接 hook（更省事）。

## 四、命令 / 脚本

```bash
# 结构
file Payload/Demo.app/Demo
otool -l Payload/Demo.app/Demo | grep -A4 -E 'LC_ENCRYPTION_INFO|LC_LOAD_DYLIB|LC_CODE_SIGNATURE'
otool -hv Payload/Demo.app/Demo
# 元数据
class-dump -H Payload/Demo.app/Demo -o headers/
strings -a Payload/Demo.app/Demo | grep -iE 'flag|key|verify|check'
nm -gU Payload/Demo.app/Demo | head -20        # 导出的符号（Swift 会是 mangled）
# 砸壳
frida-ios-dump -o out.ipa com.ctf.demo
# 重签名安装（实验环境）
codesign -f -s "Apple Development: XXXX" Payload/Demo.app
xcrun simctl install booted Payload/Demo.app

# LLDB 附加
lldb
(lldb) process connect connect://<device-ip>:1234
(lldb) image list -o -f | head
(lldb) b -[Demo verify:]
(lldb) c
(lldb) register read x0 x1 x2
(lldb) po (char*)$x2
```

```bash
# 注入 dylib：optool 加 LC_LOAD_DYLIB
../optool install -c load -p "@executable_path/hook.dylib" -t Payload/Demo.app/Demo
cp hook.dylib Payload/Demo.app/
codesign -f -s - --deep Payload/Demo.app
zip -qr patched.ipa Payload
```

```objectivec
// hook.m —— 编译成 dylib 后注入，用 constructor 在启动时替换方法
#import <Foundation/Foundation.h>
#import <objc/runtime.h>

__attribute__((constructor))
static void init_hook(void) {
    NSLog(@"[hook] dylib loaded");
    Class cls = objc_getClass("Demo");
    SEL sel = sel_registerName("verify:");
    Method m = class_getInstanceMethod(cls, sel);
    if (!m) { NSLog(@"[hook] method not found"); return; }
    IMP orig = method_getImplementation(m);
    IMP repl = imp_implementationWithBlock(^BOOL(id _self, NSString *s) {
        NSLog(@"[hook] verify input = %@", s);
        return YES;                     // 强制通过
    });
    method_setImplementation(m, repl);
}
```

```bash
# 编译与注入
xcrun --sdk iphoneos clang -arch arm64 -dynamiclib -o hook.dylib hook.m \
  -framework Foundation -isysroot "$(xcrun --sdk iphoneos --show-sdk-path)"
```

## 五、常见坑 / 变体

- **`LC_ENCRYPTION_INFO` 不是 `_64` 后缀**：arm64 上用的是 `_64` 变体，grep 时两种都要试。
- **Swift 的方法名 mangled**：`class-dump` 对 Swift 支持差，用 `swift-demangle` 或 IDA 的 demangler。
- **hardened runtime**：`DYLD_INSERT_LIBRARIES` 直接被忽略，必须改 `LC_LOAD_DYLIB` 并重签名（且 `codesign` 必须带 `--entitlements`）。
- **`__objc_methname` 在 `__TEXT`**：字符串扫描要看 `__cstring` 与 `__objc_methname` 两处。
- **LLDB 下断点用符号名**：strip 过的二进制只能用地址下断（`br s -a 0x100004a20`），配合 `image list -o -f` 计算 ASLR 偏移。
- **砸壳工具依赖越狱**：没有越狱设备时只能拿 `dyld_shared_cache` 里的系统库，或做静态分析。
- **变体**：iOS 的 Swift 反混淆（`SwiftShield` 加过密的）、Flutter/Unity 的 iOS 包（主逻辑在 `App.framework`/`UnityFramework`）。

## 六、参考来源

- [Apple dyld 开源代码（Mach-O 加载与 LC_LOAD_DYLIB）](https://github.com/apple-oss-distributions/dyld)
- [OWASP MASTG：iOS 逆向与 Mach-O 分析](https://mas.owasp.org/MASTG/techniques/ios/MASTG-TECH-0058/)
- [DYLD_INSERT_LIBRARIES 注入深入解析（含 hardened runtime 限制）](https://theevilbit.github.io/posts/dyld_insert_libraries_dylib_injection_in_macos_osx_deep_dive/)
- [LLDB 官方文档（process connect、断点与寄存器）](https://lldb.llvm.org/use/map.html)
- [class-dump 工具仓库](https://github.com/nygard/class-dump)
