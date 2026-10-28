---
title: Frida Hook 实战（脱壳 / root 检测绕过 / 函数替换）
category: mobile
tags: [Frida, hook, 脱壳, root检测, frida-server, Interceptor]
signals: [需要在运行时改函数返回值, 应用有 root/simulator 检测, 需要 dump 内存里的 dex, 静态分析看到加密但跑起来能出明文, 需要打印 native 函数的参数]
difficulty: medium
source: "Frida 官方文档 / OWASP MASTG / HackTricks Frida"
tools: [frida, frida-tools, frida-server, objection, adb, root设备]
updated: 2026-10-22
---

## 一、识别信号（题面长什么样）

- 静态分析发现关键函数返回值决定分支，直接改代码不方便（有校验/加固）。
- App 一启动就检测 root/模拟器，直接退出。
- 加了壳，`classes.dex` 是空壳，需要运行时 dump 出真实 dex。
- native 层函数参数是加密的，需要 hook 看明文。
- 需要在不改 APK 的情况下验证假设（「猜这段逻辑是 AES」）。

## 二、原理

Frida 注入原理：

```text
PC ──frida CLI──> frida-server(Android, 需 root) ──ptrace/zygote──> App 进程
                                                       │
                                         加载 frida-agent.so
                                                       │
                                         执行你的 JS，提供 Interceptor
```

核心 JS API：

| API | 作用 |
|---|---|
| `Java.perform(fn)` | 在 ART 就绪后执行（Java hook 必须包在里） |
| `Java.use("类名")` | 拿到类，`.implementation` 覆盖方法 |
| `Java.enumerateLoadedClasses` | 枚举已加载类（找混淆类名） |
| `Interceptor.attach(addr, cb)` | native hook，`onEnter`/`onLeave` |
| `Interceptor.replace(addr, cb)` | 完整替换函数（不含原逻辑） |
| `Module.findExportByName` | 找 so 导出符号地址 |
| `Module.getBaseAddress` | so 基址（算偏移） |
| `Process.enumerateModules()` | 列出所有 so |
| `Memory.readByteArray / readCString` | 读内存 |
| `NativeFunction(addr, ret, args)` | 调任意函数 |
| `send/recv` | JS 与 Python 侧通信 |

## 三、checksec 判读与利用思路

动态分析前置检查：

| 检查 | 方法 | 不满足时 |
|---|---|---|
| 是否有 root | `adb shell su -c id` | 用模拟器（AOSP/Genymotion）|
| 是否能 attach | `frida-ps -U` 能列出进程 | 检查 frida-server 架构与版本 |
| 是否 debuggable | `apkanalyzer manifest print` 看 | 重打包加 `android:debuggable="true"` |
| 加固类型 | `unzip -l` 看 so | 先脱壳（frida-dexdump） |

## 四、可直接运行的 exp 脚本

### 1. 环境准备

```bash
# 版本必须与 frida CLI 一致！
pip install frida-tools
FRIDA_VER=$(frida --version)
ARCH=$(adb shell getprop ro.product.cpu.abi | tr -d '\r')   # arm64-v8a
adb push frida-server-$FRIDA_VER-android-$ARCH /data/local/tmp/frida-server
adb shell "su -c 'chmod 755 /data/local/tmp/frida-server'"
adb shell "su -c '/data/local/tmp/frida-server &'"
frida-ps -U            # 能列出进程即成功
frida-ps -Uai          # 列出已安装应用与包名
```

### 2. root 检测绕过（通用 JS）

```javascript
// bypass_root.js —— frida -U -f com.example.chall -l bypass_root.js --no-pause
Java.perform(function () {
  // 1) RootBeer 与常见自定义检测
  var classes = ["com.scottyab.rootbeer.RootBeer", "com.example.chall.RootCheck"];
  Java.enumerateLoadedClasses({
    onMatch: function (name) {
      if (!classes.some(function (c) { return name.indexOf(c) >= 0; })) return;
      try {
        var C = Java.use(name);
        C.$ownMembers.forEach(function (m) {
          if (m.constructor.name !== "Method") return;
          if (/isRoot|isRooted|isDeviceRooted|checkRoot/i.test(m.name)) {
            try {
              m.implementation = function () {
                console.log("[+] hooked " + name + "." + m.name);
                return m.returnType.className === "boolean" ? false : null;
              };
            } catch (e) {}
          }
        });
      } catch (e) {}
    },
    onComplete: function () {}
  });

  // 2) 文件存在性检测（su / busybox / Magisk）
  var File = Java.use("java.io.File");
  File.exists.implementation = function () {
    var p = this.getAbsolutePath();
    if (/\/su$|busybox|magisk|superuser|daemonsu/.test(p)) {
      console.log("[-] hide file: " + p);
      return false;
    }
    return this.exists();
  };

  console.log("[+] root bypass installed");
});
```

### 3. 脱壳（frida-dexdump）

```bash
pip install frida-dexdump
frida-dexdump -U -f com.example.chall -d 5     # -d 等待秒数，应对延迟解密
# 产出 classes*.dex，之后用 jadx 打开
```

### 4. Java 层方法替换（打印参数 + 改返回值）

```javascript
// hook_java.js
Java.perform(function () {
  var Checker = Java.use("com.example.chall.Checker");
  Checker.check.overload("java.lang.String").implementation = function (input) {
    console.log("[*] check(" + input + ")");
    var r = this.check(input);      // 先跑原逻辑
    console.log("[*] -> " + r);
    return true;                    // 强制通过
  };
});
```

### 5. native 层 hook（打印参数 + 改返回值）

```javascript
// hook_native.js
var lib = Process.findModuleByName("libnative.so");

// 已知偏移（IDA 里看到 0x1A2C）→ 直接 attach 并改返回值
var addr = lib.base.add(0x1A2C);
Interceptor.attach(addr, {
  onEnter: function (args) {
    console.log("[*] arg0 = " + args[0]);
    console.log("[*] arg1 = " + Memory.readCString(args[1]));
    this.buf = args[1];
  },
  onLeave: function (retval) {
    console.log("[*] ret = " + retval);
    retval.replace(ptr(1));         // 强制返回 1（成功）
  }
});
```

### 6. Python 侧自动化

```python
#!/usr/bin/env python3
# auto_hook.py —— frida Python 绑定：spawn + load JS + 批量试参数
import frida, time
device = frida.get_usb_device(timeout=10)
pid = device.spawn(["com.example.chall"])
session = device.attach(pid)
script = session.create_script(open("hook_java.js").read())
script.on("message", lambda m, d: print("[js]", m.get("payload", m)))
script.load(); device.resume(pid); time.sleep(1.5)
for cand in ("test", "flag", "admin"):
    script.post({"type": "try", "value": cand}); time.sleep(0.3)
```

## 五、常见坑 / 变体

- **frida-server 版本不匹配**：CLI 与 server 必须完全同版本，否则 `Failed to spawn: unable to find process`。
- **反 Frida 检测**：扫 `/proc/self/maps` 找 `frida-agent`、检测 27042 端口、`pthread_create` 特征。用 `frida-server -l 0.0.0.0:1234` 换端口 + 改 lib 名；或改用 Xposed。
- **`Java.perform` 太早**：挂在 `Application.attachBaseContext` 前会失败，用 `--no-pause` + `setImmediate`。
- **加固壳的类找不到**：类名被加密，先脱壳或用 `Java.enumerateLoadedClasses` 枚举后发现。
- **`Interceptor.attach` 崩进程**：hook 点不是函数入口（跳进了指令中间），确认偏移正确。

## 六、参考来源

- [Frida 官方文档](https://frida.re/docs/home/)
- [Frida JavaScript API（Interceptor/Memory/Module）](https://frida.re/docs/javascript-api/)
- [Frida 函数 hook 指南](https://frida.re/docs/functions/)
- [Frida Android 支持说明](https://frida.re/docs/android/)
- [OWASP MASTG: Bypassing Root Detection](https://mas.owasp.org/MASTG/techniques/android/MASTG-TECH-0144/)
- [objection（Frida 封装，`android root disable` 一行搞定）](https://github.com/sensepost/objection)
- [HackTricks: Frida Tutorial](https://book.hacktricks.wiki/en/mobile-pentesting/android-app-pentesting/frida-tutorial/index.html)
- [Frida CodeShare 社区脚本集](https://codeshare.frida.re/@ravanmalik13/)