---
title: 反调试与绕过（IsDebuggerPresent / ptrace / TracerPid）
category: reverse
tags: [反调试, IsDebuggerPresent, ptrace, TracerPid, ScyllaHide]
signals: [下断点程序直接退出, 程序跑起来检测到调试器就崩, 单步走两步就跳飞, 进程名带 debug 就报错, 需要绕过硬件断点检测]
difficulty: medium
source: "CTF-Wiki 反调试 / anti-debug.checkpoint.com / al-khaser"
tools: [x64dbg, ScyllaHide, gdb, pwndbg, IDA, Frida]
updated: 2026-10-22
---

## 一、识别信号（题面长什么样）

- 用 x64dbg 打开程序，F9 直接退出（无弹窗）。
- 单步几条指令后 `rip` 跳到随机位置，或进程消失。
- 程序里能看到 `ptrace(PTRACE_TRACEME)`、`IsDebuggerPresent`、`NtQueryInformationProcess` 的导入。
- 用 `strace` 看到程序反复 `open("/proc/self/status")` 并读 `TracerPid`。
- 反汇编里有 `int3`（`0xCC`）扫描代码段的行为（自校验）。

## 二、原理

反调试分两大类：

### 1. Windows（PE）

| 技术 | 检测点 | 绕过 |
|---|---|---|
| `IsDebuggerPresent()` | `PEB.BeingDebugged` | 把返回值 patch 成 0，或 ScyllaHide 插件 |
| `CheckRemoteDebuggerPresent` | `NtQueryInformationProcess` | hook 返回 0 |
| `NtQueryInformationProcess(ProcessDebugPort/Flags/Object)` | `ProcessDebugPort` 非 0 | hook 返回 STATUS_PORT_NOT_SET |
| `NtGlobalFlag` | PEB+0x68 有 `FLG_HEAP_ENABLE_TAIL_CHECK` 等 | 清零 PEB 标志 |
| 堆标志 `ForceFlags` | `Heap->Flags` | ScyllaHide 自动处理 |
| `int3` / `int 2d` 扫描 | 自己的代码段被替换成 `0xCC` | 硬件断点 + 内存断点 |
| 时间检测（`rdtsc`/`GetTickCount`） | 单步耗时 | 跳过或 hook |
| `ZwSetInformationThread(ThreadHideFromDebugger)` | 隐藏线程使调试器收不到事件 | 找到调用点 nop |
| 异常/SEH 检测 | 最后一次异常法 | 异常断点过滤 |
| VEH + 硬件断点检测 | `GetThreadContext` 查看 Dr0-Dr7 | ScyllaHide 清硬件断点 |

### 2. Linux（ELF）

| 技术 | 检测点 | 绕过 |
|---|---|---|
| `ptrace(PTRACE_TRACEME)` | 已被跟踪则返回 -1 | 直接 patch 掉调用 / `LD_PRELOAD` 覆盖 ptrace |
| 读 `/proc/self/status` 的 `TracerPid` | 非 0 即被调试 | hook `fopen`/`open` + 伪造内容 |
| `getppid` 检查父进程名 | 父进程是 gdb | 改父进程名 |
| `/proc/self/cmdline` 含 gdb | 同 | 同上 |
| `raise(SIGTRAP)` | 调试器接住信号即暴露 | `handle SIGTRAP nostop noprint pass` |
| 代码段 CRC 自校验 | 断点会改字节 | 硬件断点 |
| `.init_array` 里注册检测函数 | 启动即检测 | 在 `main` 之前 patch |

## 三、checksec 判读与利用思路

反调试题的核心流程：

1. **定位检测点**：`strings` 找 `"debug"`、`"TracerPid"`、`"ptrace"`；导入表找 `IsDebuggerPresent`。
2. **选择绕过层级**：
   - **静态 patch**：`nop` 掉调用或改条件跳转（最快，但改不到 CRC 自校验的题）。
   - **动态 hook**：ScyllaHide（Windows）/ `LD_PRELOAD`（Linux）/ Frida。
   - **内核级**：隐藏调试器（少数场合）。
3. **验证**：改完后重新单步，确认能走完关键分支。

静态 patch 示例（把 `call IsDebuggerPresent; test al,al; jnz exit` 改成永不跳）：

```asm
; 原： E8 xx xx xx xx       call IsDebuggerPresent
;      84 C0                test al, al
;      75 1A                jnz  exit
; 改： 90 90 90 90 90       nop call
;      B0 00                mov al, 0
;      75 1A  -> EB 1A      jnz 跳转改成 jmp（或 90 90 两字节 nop）
```

## 四、可直接运行的 exp 脚本

### 1. Linux：用 LD_PRELOAD 屏蔽 ptrace 与 TracerPid

```c
// anti_debug_bypass.c —— gcc -shared -fPIC -o hook.so anti_debug_bypass.c -ldl
#define _GNU_SOURCE
#include <stdio.h>
#include <string.h>
#include <stdlib.h>
#include <dlfcn.h>
#include <sys/ptrace.h>

static long (*real_ptrace)(int, ...) = NULL;

long ptrace(int request, ...) {
    if (!real_ptrace) real_ptrace = dlsym(RTLD_NEXT, "ptrace");
    // 让 PTRACE_TRACEME 总是"成功"
    if (request == PTRACE_TRACEME) return 0;
    return -1;
}

// 伪造 /proc/self/status 里的 TracerPid 为 0
static FILE *(*real_fopen)(const char *, const char *) = NULL;
FILE *fopen(const char *path, const char *mode) {
    if (!real_fopen) real_fopen = dlsym(RTLD_NEXT, "fopen");
    FILE *f = real_fopen(path, mode);
    if (f && strstr(path, "status")) {
        // 简单方案：直接把文件内容读出来替换（仅演示）
        char tmp[4096] = {0};
        size_t n = fread(tmp, 1, sizeof(tmp) - 1, f);
        fclose(f);
        char *p = strstr(tmp, "TracerPid:");
        if (p) { p[10] = '0'; p[11] = '\n'; p[12] = '\0'; }
        FILE *mem = fmemopen(tmp, n, "r");
        return mem;
    }
    return f;
}
```

```bash
gcc -shared -fPIC -o hook.so anti_debug_bypass.c -ldl
LD_PRELOAD=./hook.so gdb ./chall
```

### 2. Frida 版（Android / Linux 通用）

```javascript
// bypass_antidebug.js
Interceptor.attach(Module.findExportByName(null, "ptrace"), {
  onEnter(args) { this.req = args[0].toInt32(); },
  onLeave(retval) { if (this.req === 0) retval.replace(ptr(0)); }
});

// 屏蔽对 /proc/self/status 的读取，把 TracerPid 改成 0
const openPtr = Module.findExportByName(null, "open");
if (openPtr) {
  Interceptor.attach(openPtr, {
    onEnter(args) { this.path = args[0].readCString(); },
    onLeave(retval) { if (this.path && this.path.indexOf("status") >= 0) retval.replace(ptr(-1)); }
  });
}
console.log("[+] anti-debug bypass installed");
```

```bash
frida -U -f com.target.app -l bypass_antidebug.js --no-pause
```

### 3. gdb 侧的配合设置

```bash
gdb -q ./chall \
  -ex "set pagination off" \
  -ex "handle SIGTRAP nostop noprint pass" \
  -ex "catch exec" \
  -ex run
# 若程序读 TracerPid 后退出，直接在那个 fopen 上下断点：
#   b fopen
#   cond 1 *(char**)$rdi != 0
```

### 4. 用 Python 自动定位反调试点

```python
#!/usr/bin/env python3
# 扫描导入表与字符串，输出可能的反调试 API 与对应位置
import sys, subprocess, pathlib

BIN = sys.argv[1] if len(sys.argv) > 1 else "./chall"
KEYWORDS = ["IsDebuggerPresent", "CheckRemoteDebuggerPresent", "NtQueryInformationProcess",
            "ZwSetInformationThread", "OutputDebugString", "ptrace", "TracerPid",
            "NtGlobalFlag", "IsProcessorFeaturePresent"]

def scan(path):
    data = pathlib.Path(path).read_bytes()
    for kw in KEYWORDS:
        idx = data.find(kw.encode())
        if idx >= 0:
            print(f"[+] {kw:28s} @ file offset {idx:#x}")
    out = subprocess.run(["strings", "-a", "-t", "x", path], capture_output=True, text=True).stdout
    for line in out.splitlines():
        low = line.lower()
        if any(k.lower() in low for k in ("debug", "tracerpid", "ptrace", "vmware", "virtualbox")):
            print("   str:", line.strip()[:90])

if __name__ == "__main__":
    scan(BIN)
```

## 五、常见坑 / 变体

- **`int3` 自校验**：下软件断点会改字节，必须用**硬件断点**（x64dbg 的 `r/rw` 或 gdb 的 `hbreak`）。
- **多线程反调试**：一个线程检测到就 `exit`，要在 `ExitProcess`/`exit` 下断点看调用栈。
- **Android 的 `debuggerd`**：`debuggable=false` 时无法 attach，需重打包或 root。

## 六、参考来源

- [CTF-Wiki: 检测调试（Linux）](https://ctf-wiki.org/reverse/platform/linux/detect-dbg/)
- [CTF-Wiki: 检测断点](https://ctf-wiki.org/reverse/platform/linux/detect-bp/)
- [CTF-Wiki: IsDebuggerPresent](https://ctf-wiki.org/reverse/platform/windows/anti-debug/isdebuggerpresent/)
- [CTF-Wiki: NtQueryInformationProcess](https://ctf-wiki.org/reverse/platform/windows/anti-debug/ntqueryinformationprocess/)
- [CTF-Wiki: ZwSetInformationThread](https://ctf-wiki.org/reverse/platform/windows/anti-debug/zwsetinformationthread/)
- [anti-debug.checkpoint.com（反调试技术大全）](https://anti-debug.checkpoint.com/)
- [al-khaser（反反调试测试样本集）](https://github.com/LordNoteworthy/al-khaser)
- [x64dbg ScyllaHide 插件](https://github.com/x64dbg/ScyllaHide)
