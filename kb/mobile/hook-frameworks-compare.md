---
title: Hook 框架对比（Frida / Xposed / LSPosed / Zygisk）
category: mobile
tags: [frida, xposed, lsposed, magisk, zygisk, hook-framework]
signals: [题目要求在运行时修改某个方法的行为, 应用有反 frida 但是设备已经 root, 需要一个全局持久生效的 hook 而不是一次性脚本, 题目说用 Xposed 模块绕过某个检测, 设备是 Magisk 环境有 Zygisk, 需要 hook 系统层 API 比如 PackageManager]
difficulty: medium
source: "Frida 官方文档 / LSPosed 官方文档 / Magisk 官方文档 / Xposed API 参考"
tools: [frida, objection, lsposed, magisk, zygisk, xposed-api]
updated: 2026-10-22
exec_yaml: ok
---

## 一、识别信号（题面长什么样）

- 题目需要"运行时改返回值"，但应用检测 Frida，`frida-server` 一挂就崩。
- 题目要求 hook 的是**系统层**组件（`PackageManager.getPackageInfo`、`TelephonyManager.getDeviceId`）。
- 设备已 root（Magisk），题目 hint 提到 "Zygisk" 或 "LSPosed"。
- 需要"每次启动都生效"而不是手动 attach。
- 有多个目标方法需要批量 hook，脚本化管理更方便。
- 应用是 Xposed 检测型题（反 Xposed，需隐藏）。

## 二、原理

**Hook 的本质是"在目标函数执行前后插入代码"，不同框架的差异在于注入点与作用域。**

| 框架 | 注入方式 | 作用域 | 对反检测的暴露面 | 适用 |
| --- | --- | --- | --- | --- |
| **Frida**（server/gadget） | 动态注入进程 | 单进程 | `/proc/maps` 有 frida 库、端口 27042、`gum-js-loop` 线程 | 快速调试、CTF 主力 |
| **Xposed**（原版） | 改 `/system` 的 `app_process` | 全系统（Zygote fork） | 改系统分区、Android 9+ 难装 | 老设备 |
| **LSPosed** | Zygisk / Magisk 模块 | 全系统，按作用域管理 | Magisk 模块明显 | 目前主流 |
| **Zygisk 模块** | 在 `zygote` 里加载 native 库 | 全系统 | 需要真 root | 系统级 hook |
| **KernelSU / APatch** | 内核模块 | 系统 | 更隐蔽 | 高级场景 |

**Xposed 的本质**：让 `app_process` 在 zygote 阶段加载模块的 jar，模块在 `IXposedHookLoadPackage` 里挂 `XposedBridge.hookMethod`。所有 fork 出来的应用都带模块代码，所以**不用每次 attach**。

**CTF 取舍**：能过 Frida 就用 Frida（快）；过不了就上 LSPosed（改包/签名都不需要，且全系统生效）；两者都不行才逆向检测逻辑手工 patch。

## 三、操作步骤

1. **判断能否用 Frida**：跑一次 `frida -U -f pkg`，崩了就看 `logcat` 判断是不是反调试。
2. **能用 Frida**：写 `Java.perform` 脚本，`Cls.method.implementation = function(){...}`。
3. **不能用 Frida**：Magisk + Zygisk + LSPosed，写模块 `assets/xposed_init` 注册入口，在 `handleLoadPackage` 里按包名过滤后 hook。
4. **系统 API 层**：hook `PackageManager`、`Signature`、`Settings.Secure`，从根源上伪造环境。
5. **验证**：用 `logcat -s LSPosed` 或 Frida 日志确认 hook 生效。

## 四、命令 / 脚本

```javascript
// Frida 版：批量 hook 常见检测 API + 目标方法
Java.perform(function () {
    // 1) 改 Build 字段
    var VERSION = Java.use('android.os.Build$VERSION');
    VERSION.RELEASE.value = '12';
    Java.use('android.os.Build').MODEL.value = 'Pixel 6';
    // 2) hook 目标类方法
    try {
        var Cls = Java.use('com.ctf.demo.MainActivity');
        Cls.verify.implementation = function (s) {
            console.log('[verify] ' + s);
            return true;
        };
    } catch (e) { console.log('[-] ' + e); }
    console.log('[*] hooks installed');
});
```

```java
// LSPosed 模块主入口：AndroidManifest 声明 xposedmodule，assets/xposed_init 写类名
package com.ctf.mod;

import de.robv.android.xposed.IXposedHookLoadPackage;
import de.robv.android.xposed.XC_MethodHook;
import de.robv.android.xposed.XposedBridge;
import de.robv.android.xposed.XposedHelpers;
import de.robv.android.xposed.callbacks.XC_LoadPackage.LoadPackageParam;

public class HookEntry implements IXposedHookLoadPackage {
    private static final String TARGET = "com.ctf.demo";

    @Override
    public void handleLoadPackage(LoadPackageParam lpparam) {
        if (!lpparam.packageName.equals(TARGET)) return;
        XposedBridge.log("[ctf] loaded in " + lpparam.packageName);

        // hook 目标方法：强制返回 true
        XposedHelpers.findAndHookMethod(
            "com.ctf.demo.MainActivity", lpparam.classLoader,
            "verify", String.class,
            new XC_MethodHook() {
                @Override
                protected void beforeHookedMethod(MethodHookParam param) {
                    XposedBridge.log("[ctf] verify arg = " + param.args[0]);
                    param.setResult(true);
                }
            });

        // hook 系统 API：去掉签名校验
        XposedHelpers.findAndHookMethod(
            "android.content.pm.PackageManager", lpparam.classLoader,
            "getPackageInfo", String.class, int.class,
            new XC_MethodHook() {
                @Override
                protected void afterHookedMethod(MethodHookParam param) {
                    // 可替换 signatures 字段
                }
            });
    }
}
```

```bash
# LSPosed 模块最小工程（gradle 出 apk）
# 1) AndroidManifest.xml 里加：
#    <meta-data android:name="xposedmodule" android:value="true"/>
#    <meta-data android:name="xposeddescription" android:value="ctf hook"/>
#    <meta-data android:name="xposedminversion" android:value="93"/>
# 2) assets/xposed_init 内容：com.ctf.mod.HookEntry
# 3) 编译后在 LSPosed 管理器里启用，勾选作用域为 com.ctf.demo
./gradlew assembleRelease
adb install -r app-release.apk

# Frida 侧的环境准备
adb shell "su -c 'setenforce 0'"
adb shell "su -c '/data/local/tmp/frida-server &'"
frida-ps -U | head
```

## 五、常见坑 / 变体

- **`XposedHelpers.findAndHookMethod` 参数类型必须完全匹配**：`String.class`、`int.class` 写错就抛 `NoSuchMethodError`。
- **LSPosed 的作用域**：不勾目标包名模块不会加载，是新手最常见的"hook 没生效"原因。
- **Frida 与 Magisk 冲突**：某些系统上 `frida-server` 需要 `setenforce 0` 或改名为非 `frida` 的字符串。
- **反射/hidden API**：Android 9+ 对 `android.os.ServiceManager` 等有 hidden API 限制，需 `XposedHelpers.callStaticMethod` 绕。
- **多进程**：`handleLoadPackage` 对每个进程都会调用，要按 `processName` 过滤。
- **Xposed 检测**：应用会查 `StackTraceElement` 里有没有 xposed 类名、或用 `ClassLoader` 找模块类，需清理栈。
- **变体**：`objection` 的 `android hooking` 命令（基于 Frida 的简化封装）、`Pine` 框架、iOS 的 `Substrate/Substitute`。

## 六、参考来源

- [Frida 官方文档（JavaScript API 与 Java bridge）](https://frida.re/docs/javascript-api/)
- [LSPosed 官方仓库与使用说明](https://github.com/lsposed/lsposed)
- [LSPosed 与 Xposed 的关系与差异（社区讨论）](https://www.reddit.com/r/Magisk/comments/1ppkpeo/what_exactly_is_xposed_and_lsposed/)
- [Magisk 官方文档（Zygisk 与模块机制）](https://topjohnwu.github.io/Magisk/)
- [Xposed API 参考（XC_MethodHook 与 XposedHelpers）](https://api.xposed.info/reference/packages.html)
