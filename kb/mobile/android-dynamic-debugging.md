---
title: Android 动态调试（jdwp 附加、smali 插桩、动态修改返回值）
category: mobile
tags: [jdwp, smali, debugging, instrumentation, app-debug, baksmali]
signals: [APK 的 AndroidManifest 里 debuggable 为 true, 题目说直接连 jdwp 端口调试, 要求直接改 smali 让校验函数返回 true, 附件给的是可编辑的 apk 源码结构, 应用崩溃在某个 so 里需要单步, 题目只有一个输入框和一个校验按钮]
difficulty: medium
source: "OWASP MASTG 调试技术 / Android 官方开发者文档（debuggable / jdwp） / baksmali-smali 工具"
tools: [jadx, apktool, jdb, Android Studio, frida, objection, adb]
updated: 2026-10-22
exec_yaml: ok
---

## 一、识别信号（题面长什么样）

- `AndroidManifest.xml` 里 `<application android:debuggable="true">`。
- `adb jdwp` 能列出 PID，说明进程开放在调试端口。
- 题目强调"直接改代码"或"运行时改返回值"。
- 只有一个输入框 + 校验按钮，点确认输出"Wrong"。
- 校验逻辑不复杂（字符串比较、简单哈希），静态看完直接改最省事。
- 应用是重打包后仍然能安装（无签名校验）。

## 二、原理

**Android 的调试面：**

- **JDWP**：Java 调试线协议，`adb forward tcp:8700 jdwp:<pid>` 后可用 `jdb`/Android Studio 附加。
- **ptrace**：native 层调试（gdb/lldb），与 Java 层调试可同时进行。
- **smali 插桩**：`apktool d` 反编译成 smali（Dalvik 汇编），手动改 `if-ne`/`invoke-*` 后 `apktool b` 重打包；签名需自己签（`apksigner`），否则安装失败。
- **绕过校验的两条路**：
  1. **静态改**：把 `check()` 里的 `return 0` 改成 `return 1`，或把比较分支反过来。
  2. **动态改**：Frida hook 返回值（无需重打包，OvErAll 更快）。

**为什么要优先动态**：重打包会破坏签名（若应用有签名校验就装不上），而 Frida 不改包体。

## 三、操作步骤

1. **静态定位校验点**：jadx 搜 `Wrong`、`Toast`、`equals`、按钮 onClick 方法。
2. **确定返回值**：找到返回 boolean/int 的方法，看 `if-eqz`/`if-nez` 的真假分支。
3. **路线 A：smali 插桩**：
   - `apktool d app.apk -o src`
   - 改 `src/smali/<pkg>/XXX.smali` 里的 `const/4 v0, 0x0` → `0x1`，或加 `return v0` 提前返回。
   - `apktool b src -o patched.apk`
   - `keytool` 生成临时 key → `apksigner sign` → `adb install -r`
4. **路线 B：JDWP 附加**：
   - `adb shell am set-debug-app -w <pkg>`（等待调试器）
   - `adb forward tcp:8700 jdwp:<pid>`
   - `jdb -attach localhost:8700`，用 `stop in com.ctf.Demo.check` 下断点。
5. **路线 C：Frida**（最简，见下方脚本）。
6. **验证**：重新点击按钮，看是否输出 flag。

## 四、命令 / 脚本

```bash
# 反编译与重打包
apktool d app.apk -o src
grep -rn 'Wrong\|flag' src/smali | head
# 修改后重打包
apktool b src -o patched.apk
# 生成临时签名
keytool -genkey -v -keystore tmp.keystore -alias ctf -keyalg RSA \
  -keysize 2048 -validity 365 -storepass 123456 -keypass 123456 \
  -dname "CN=ctf, OU=ctf, O=ctf, L=ctf, S=ctf, C=CN"
apksigner sign --ks tmp.keystore --ks-pass pass:123456 --out signed.apk patched.apk
adb install -r signed.apk

# JDWP
adb shell "am set-debug-app -w com.ctf.demo"
adb jdwp
adb forward tcp:8700 jdwp:12345
jdb -attach localhost:8700
# jdb 里的常用命令
# stop in com.ctf.demo.MainActivity.check
# run / cont / locals / print var
```

```smali
# 修改前：校验失败返回 0
.method public static check(Ljava/lang/String;)Z
    .locals 1
    const-string v0, "ctf2024"
    invoke-virtual {p0, v0}, Ljava/lang/String;->equals(Ljava/lang/Object;)Z
    move-result v0
    return v0
.end method

# 修改后：直接返回 true（注意 .locals 不变，且最后的 return 类型要匹配 Z）
.method public static check(Ljava/lang/String;)Z
    .locals 1
    const/4 v0, 0x1
    return v0
.end method
```

```javascript
// Frida：直接改返回值 + 打印入参
Java.perform(function () {
    var Cls = Java.use('com.ctf.demo.MainActivity');
    Cls.check.implementation = function (s) {
        console.log('[check] input =', s);
        var r = this.check(s);
        console.log('[check] original =', r);
        return true;                    // 强制通过
    };
});
```

## 五、常见坑 / 变体

- **重打包后签名校验失败**：应用有 `PackageManager` 签名比对，先 hook `getPackageInfo().signatures` 或直接走 Frida。
- **`debuggable` 为 false**：`am set-debug-app -w` 对 release 包无效，需 Frida 或改 Manifest 重打包（改后同样破坏签名）。
- **smali 的寄存器计数**：加指令后 `.locals` 或 `.registers` 不够会校验失败，`baksmali` 报错——先算好寄存器。
- **JDWP 的端口**：`jdwp:<pid>` 需要 `adb jdwp` 里真有该 PID；被 `ro.debuggable=0` 时不可用。
- **多进程应用**：目标逻辑可能在 `:remote` 进程里，要附加正确 PID。
- **native 校验**：Java 层改完没用，逻辑在 so 里（转 `android-native-jni-reverse`）。
- **变体**：Xposed 模块批量 hook、`objection` 一条命令 `android hooking set return_value`。

## 六、参考来源

- [OWASP MASTG：Android 调试技术（JDWP 与 ptrace）](https://mas.owasp.org/MASTG/techniques/android/MASTG-TECH-0031/)
- [Android 官方：可调试应用与 JDWP](https://developer.android.com/studio/debug)
- [apktool 官方文档（反编译与重打包）](https://github.com/iBotPeaches/Apktool)
- [smali/baksmali 官方仓库](https://github.com/JesusFreke/smali)
- [Objection：Frida 的移动端自动化封装](https://github.com/sensepost/objection)
