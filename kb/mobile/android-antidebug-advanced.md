---
title: Android 反调试高级（ptrace、/proc 检测、反 Frida）
category: mobile
tags: [anti-debug, ptrace, tracerpid, anti-frida, ptrace-hook, port-scan]
signals: [附加调试器后应用直接退出或者黑屏, 程序在启动时读取 /proc/self/status, so 里有 ptrace 调用和 PTRACE_TRACEME, 检测到了 frida 的线程名或者 27042 端口, 应用在 root 或模拟器上直接闪退, 崩溃日志显示 SIGSEGV 在反调试函数里, 需要先过检测才能 hook]
difficulty: hard
source: "Linux ptrace 系统调用文档 / OWASP MASTG 反调试章节 / Frida 检测与反检测公开研究"
tools: [frida, ida, objection, magisk, zygisk, patch-frida, jadx]
updated: 2026-10-22
exec_yaml: ok
---

## 一、识别信号（题面长什么样）

- 一附加 Frida 或 gdb，应用秒退，`logcat` 里只有 `Fatal signal 11` 而无 Java 异常。
- 题目 hint 写"有反调试，注意过掉"。
- IDA 里能看到 `ptrace` 调用、`/proc/self/status` 字符串、`TracerPid` 字样。
- 字符串里有 `frida`、`gum-js-loop`、`27042`、`gadget`、`linjector`。
- 应用只在真机上跑得起来，模拟器/root 环境直接闪。
- 一段时间的 `sleep` 或"随机延时"后才崩溃。

## 二、原理

**常见反调试/反注入手段，按实现层分：**

| 手法 | 检测点 | 绕过点 |
| --- | --- | --- |
| `ptrace(PTRACE_TRACEME)` 自占用 | 返回值 -1 即已被调试 | Hook `ptrace` 返回 0 |
| `/proc/self/status` 读 `TracerPid` | 非 0 表示被附加 | Hook `open` 或字符串替换 |
| `/proc/self/maps` 扫 `frida`/`gum` | 内存中出现注入库 | 改 frida 名字（`magisk-frida`、patch gadget） |
| `frida-server` 端口 27042/27043 | 连接探测 | 改名端口或用 `frida-gadget` 嵌入 |
| 线程名 `gum-js-loop` / `gmain` / `pool-spawner` | 遍历 `/proc/self/task` | 编译时改线程名（undetected-frida 补丁） |
| `fork()` 后子进程反调试 | fork 前断点失效 | 在子进程里再下断 |
| 时间差检测 | 单步导致耗时异常 | 用 Frida 不改代码、少断点 |
| Signal 处理 / SIGTRAP 劫持 | 收到 SIGTRAP 直接 `exit` | 屏蔽 `exit`/`abort` |

**核心思路：所有"检测"最终都要落到某个系统调用或文件读取上**，因此 Hook 这些原语比逐个打补丁稳。

## 三、操作步骤

1. **先让程序跑起来再说**：不附加任何工具，正常启动一次，记录 UI 行为。
2. **定位检测点**：`strings libx.so | grep -E 'frida|27042|status|TracerPid|maps'`，IDA 找 xref。
3. **优先 Hook 原语**：
   - `ptrace` → 返回 0。
   - `open/openat` + `read` → 对 `/proc/self/status` 把 `TracerPid:\t<非0>` 改成 0。
   - `strstr`/`strcmp` → 对 `frida` 等关键字返回 NULL。
4. **处理端口探测**：Hook `connect` 对 27042/27043 返回 -1。
5. **处理线程名检测**：用打过补丁的 frida-server（改名 `gum-js-loop` → 随机）或 gadget。
6. **验证**：过了检测后再挂业务 hook。

## 四、命令 / 脚本

```bash
# 静态线索
strings lib/arm64-v8a/libx.so | grep -Ei 'frida|gum|27042|TracerPid|/proc/self/status|/proc/self/maps'
jadx -d out app.apk && grep -rn 'frida\|27042' out/ | head
# 端口/进程排查
adb shell "cat /proc/net/tcp | grep -i 69B2"      # 27042 的 16 进制
adb shell "ps -A | grep -i frida"
```

```javascript
// bypass-anti-debug.js：一把梭的常见检测绕过
Java.perform(function () {});

// 1) ptrace -> 0
var ptrace = Module.findExportByName(null, 'ptrace');
if (ptrace) {
    Interceptor.replace(ptrace, new NativeCallback(function (req, pid, addr, data) {
        console.log('[ptrace] bypass req=' + req);
        return 0;
    }, 'long', ['int', 'int', 'pointer', 'pointer']));
}

// 2) open/openat 后对 /proc/self/status 做路径改写
var openPtr = Module.findExportByName(null, 'open');
if (openPtr) {
    Interceptor.attach(openPtr, {
        onEnter: function (args) {
            var p = args[0].readCString();
            if (p && p.indexOf('/proc/self/status') !== -1) {
                console.log('[open] ' + p);
                args[0] = Memory.allocUtf8String('/proc/self/status_bypass_disabled');
            }
        }
    });
}

// 3) strstr 对 frida 关键字返回 NULL
var strstrPtr = Module.findExportByName(null, 'strstr');
if (strstrPtr) {
    Interceptor.attach(strstrPtr, {
        onEnter: function (args) {
            var h = args[0].readCString(), n = args[1].readCString();
            if (n && /frida|gum|gadget|linjector/i.test(n)) {
                console.log('[strstr] blocked: ' + n);
                this.block = true;
            }
        },
        onLeave: function (retval) {
            if (this.block) retval.replace(ptr(0));
        }
    });
}

// 4) 27042/27043 的 connect 直接失败
var connectPtr = Module.findExportByName(null, 'connect');
if (connectPtr) {
    Interceptor.attach(connectPtr, {
        onEnter: function (args) {
            var sa = args[1];
            try {
                var port = sa.add(2).readU16();
                var portBE = ((port & 0xff) << 8) | ((port >> 8) & 0xff);
                if (portBE === 27042 || portBE === 27043) {
                    console.log('[connect] blocked port ' + portBE);
                    this.block = true;
                }
            } catch (e) {}
        },
        onLeave: function (retval) {
            if (this.block) retval.replace(ptr(-1));
        }
    });
}

// 5) 屏蔽 exit / abort
['exit', 'abort', '_exit'].forEach(function (n) {
    var p = Module.findExportByName(null, n);
    if (p) {
        Interceptor.replace(p, new NativeCallback(function () {
            console.log('[' + n + '] blocked');
        }, 'void', ['int']));
    }
});

console.log('[*] anti-debug bypass loaded');
```

```bash
# 换个名字的 frida-server（编译时改端口与线程名）
# 方式 A：用 undetected-frida 的补丁重新编译
git clone https://github.com/lleroi/undetected-frida.git
# 方式 B：改用 gadget 嵌入到 apk，不走 server
objection patchapk --source app.apk
```

## 五、常见坑 / 变体

- **Hook 太晚**：检测在 `Application.attachBaseContext` 或 `JNI_OnLoad` 里，`-f` 模式要配 `--pause` 或 gadget 从进程启动就注入。
- **`Interceptor.replace` 会破坏调用约定**：`exit` 是 `void(int)`、`ptrace` 是 `long(int,int,ptr,ptr)`，签名写错会直接 SIGSEGV。
- **静态链接的 so**：`ptrace` 不走 PLT 而是直接 syscall（`svc #0`），Hook 不到——此时用 inline hook（`Stalker`）或改 syscall 号。
- **`/proc/self/status` 用 `fopen`**：`fopen` 内部走 `open`，Hook `open` 有效；但个别实现直接 syscall `openat`，需同时 hook `openat`/`__openat`。
- **fork 出子进程检测**：`fork` 后父进程被 Frida 附加，子进程读 `TracerPid` 仍是 0，但子进程会起反调试；需 hook `fork` 在子进程里重装。
- **多个 so 各有检测**：每个 so 单独扫，别只处理主 so。
- **变体**：`seccomp` 限制 `ptrace`、`prctl(PR_SET_DUMPABLE, 0)`、自定义 signal handler 吞 SIGSEGV。

## 六、参考来源

- [Linux man page：ptrace(2)（PTRACE_TRACEME 语义）](https://man7.org/linux/man-pages/man2/ptrace.2.html)
- [OWASP MASTG：Android 反调试与反逆向检测](https://mas.owasp.org/MASTG/techniques/android/MASTG-TECH-0039/)
- [检测进程是否被 GDB 附加（/proc/self/status TracerPid）](https://stackoverflow.com/questions/3596781/how-to-detect-if-the-current-process-is-being-run-by-gdb)
- [undetected-frida：修改线程名绕过检测的补丁集](https://github.com/ultrafunkamsterdam/undetected-frida)
- [Frida 官方文档：Interceptor 与 NativeCallback](https://frida.re/docs/javascript-api/)
