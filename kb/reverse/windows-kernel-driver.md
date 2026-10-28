---
title: Windows 内核驱动逆向（DriverEntry、IRP、IOCTL 分析）
category: reverse
tags: [windows, kernel, driver, ioctl, irp]
signals: [文件是 .sys 后缀且 PE 特征为 driver, 存在 DriverEntry 导出或入口, 字符串里有 \\Device\\ 与 \\DosDevices\\ 前缀, 导入表只有 ntoskrnl.exe 与 HAL, 出现 IoCreateDevice 或 IoCreateSymbolicLink, 有 sub_ 函数里大量 switch 比较 IOCTL 码, 导入 IoBuildDeviceIoControlRequest 或 IofCompleteRequest, 字符串里有 ObReferenceObjectByHandle 与 PsLookupProcessByProcessId, 题面给出 .sys 加载器与用户态程序, 设备路径形如 \\\\.\\MyDevice]
difficulty: hard
source: "Microsoft WDK 文档 / matterpreter"
tools: [ida, ghidra, windbg, x64dbg]
updated: 2026-10-22
---

## 一、识别信号（题面长什么样）

- 附件是 `.sys`，PE 特征 `Subsystem: Native (1)`，`Characteristics` 里没有 DLL 位。
- 导入表几乎只有 `ntoskrnl.exe` / `hal.dll`，没有 `kernel32`。
- 字符串里有 `\Device\MyDevice`、`\DosDevices\MyDevice`、`\??\C:\flag`。
- 有个函数里对一个 DWORD 做 `switch`，case 值形如 `0x222000`、`0x80002004`（**IOCTL 码**）。
- 题面附带一个用户态 `.exe` 或提供 `CreateFileW("\\\\.\\MyDevice")` 的调用截图。
- 导入 `PsLookupProcessByProcessId`、`KeStackAttachProcess`、`MmCopyVirtualMemory` → 内存读写型驱动。
- 题面提示：`驱动`、`内核`、`driver`、`IOCTL`、`DeviceIoControl`、`IRP`。
- 校验逻辑出现在 `IRP_MJ_DEVICE_CONTROL` 分支里，`InputBuffer`/`OutputBuffer` 是关键。

## 二、原理

### 1. 驱动的骨架

```c
NTSTATUS DriverEntry(PDRIVER_OBJECT drv, PUNICODE_STRING reg) {
    drv->DriverUnload = Unload;
    drv->MajorFunction[IRP_MJ_CREATE]         = DispatchCreate;
    drv->MajorFunction[IRP_MJ_CLOSE]          = DispatchClose;
    drv->MajorFunction[IRP_MJ_DEVICE_CONTROL] = DispatchIoctl;  // ← 重点
    IoCreateDevice(drv, 0, &devName, FILE_DEVICE_UNKNOWN, 0, FALSE, &devObj);
    IoCreateSymbolicLink(&symLink, &devName);
    return STATUS_SUCCESS;
}
```

用户态通过 `DeviceIoControl(hDev, ioctlCode, in, inLen, out, outLen, ...)` 调进来。

### 2. IRP 结构（逆向时最常碰的字段）

```
_IRP
  +0x000 Type / Size
  +0x018 IoStatus.Status / Information
  +0x050 Tail.Overlay.CurrentStackLocation -> _IO_STACK_LOCATION
_IO_STACK_LOCATION
  +0x000 MajorFunction
  +0x008 Parameters.DeviceIoControl.OutputBufferLength
  +0x010 Parameters.DeviceIoControl.InputBufferLength
  +0x018 Parameters.DeviceIoControl.IoControlCode   ← IOCTL 码
  +0x020 Parameters.DeviceIoControl.Type3InputBuffer
  +0x008 DeviceObject
```

IDA 里常见：`a2->Tail.Overlay.CurrentStackLocation->Parameters.DeviceIoControl.IoControlCode`。

### 3. IOCTL 码的四段结构

```
31      16 15  14 13      2 1 0
[DeviceType][Access][Function][Method]
```

- `Method`（bits 0-1）：0 = BUFFERED（`SystemBuffer`），1 = IN_DIRECT，2 = OUT_DIRECT，3 = NEITHER。
- 所以 `0x222000` = DeviceType `0x22`、Access `0`、Function `0x800`、Method `0`。

## 三、解题步骤

1. **静态确认是驱动**：`file` / `Detect It Easy` 看 `PE32+ executable (native) (DLL)`，`Characteristics` 无 `IMAGE_FILE_DLL` 则是 .sys 入口。
2. **找 `DriverEntry`**：入口点（`AddressOfEntryPoint`）直接被调用；或找 `IoCreateDevice` 的调用者。
3. **找 `MajorFunction[0xE]`**（IRP_MJ_DEVICE_CONTROL）：看 `DriverEntry` 里给 `drv+0x70`（x64 的偏移）赋值的函数。
4. **在 IOCTL handler 里定位 `switch`**：用 IDA 的 `Switch` 视图，导出所有 case 值。
5. **解开每个 case**：读 `+0x18` 的码，再取 `SystemBuffer`（x64 下 `a2->AssociatedIrp.SystemBuffer`，或 `*(QWORD*)(a2+0x18)`）。
6. **构造调用**：用户态 `DeviceIoControl` 的 `dwIoControlCode` 用 IDA 里的常量；`InBuffer` 用结构体偏移。
7. **验证 flag**：对照驱动里比较逻辑（常见 `strcmp` 被内联成逐字节比较）。

## 四、可直接运行的脚本

解析 .sys 的 IOCTL 常量（IDA 里 Ctrl+F 搜不到的用脚本过一遍）：

```python
# idapython：列出所有 IOCTL 相关 case，并打印结构
import idaapi, idautils, idc

def find_ioctl_handlers():
    for f in idautils.Functions():
        name = idc.get_func_name(f)
        for insn in idautils.FuncItems(f):
            m = idc.print_insn_mnem(insn)
            if m == 'cmp':
                op = idc.print_operand(insn, 1)
                if op.startswith('0') and len(op) >= 6:      # 形如 0x222000
                    print("0x%x %s %s %s" % (insn, name, m, op))

find_ioctl_handlers()
```

用户态触发脚本（配驱动）：

```c
// exploit.c —— 编译：cl exploit.c
#include <windows.h>
#include <stdio.h>

#define IOCTL_CHECK  0x222000     // 从 IDA 里拿到的 case 值

int main(void) {
    HANDLE h = CreateFileA("\\\\.\\MyDevice", GENERIC_READ | GENERIC_WRITE,
                           0, NULL, OPEN_EXISTING, 0, NULL);
    if (h == INVALID_HANDLE_VALUE) { printf("open fail %lu\n", GetLastError()); return 1; }

    char in[64] = {0}, out[64] = {0};
    memcpy(in, "flag{test}", 10);
    DWORD ret = 0;
    BOOL ok = DeviceIoControl(h, IOCTL_CHECK, in, sizeof(in),
                              out, sizeof(out), &ret, NULL);
    printf("ok=%d err=%lu out=%s\n", ok, GetLastError(), out);
    CloseHandle(h);
    return 0;
}
```

Python 版（cffi 或直接 WinDLL）：

```python
import ctypes
from ctypes import wintypes

k32 = ctypes.WinDLL("kernel32", use_last_error=True)
k32.CreateFileA.argtypes = [wintypes.LPCSTR, wintypes.DWORD, wintypes.DWORD,
                            wintypes.LPVOID, wintypes.DWORD, wintypes.DWORD, wintypes.HANDLE]
k32.CreateFileA.restype = wintypes.HANDLE

h = k32.CreateFileA(b"\\\\.\\MyDevice", 0xC0000000, 0, None, 3, 0, None)
buf_in = ctypes.create_string_buffer(b"flag{test}", 64)
buf_out = ctypes.create_string_buffer(64)
ret = wintypes.DWORD(0)
k32.DeviceIoControl(wintypes.HANDLE(h), 0x222000, buf_in, 64, buf_out, 64,
                    ctypes.byref(ret), None)
print(ctypes.get_last_error(), buf_out.value)
```

WinDbg 动态验证（需要测试环境）：

```
0: kd> .reload /f MyDriver.sys
0: kd> lm m MyDriver
0: kd> bp MyDriver!DriverEntry
0: kd> g
# 用户态调用后
0: kd> dt nt!_IRP @rcx
0: kd> dt nt!_IO_STACK_LOCATION poi(@rcx+0x50)
```

## 五、常见坑 / 变体

- **IDA 里 `DriverEntry` 显示为 `start`**：没有导出表，需要看 `AddressOfEntryPoint`。
- **`MajorFunction` 的偏移**：x64 下 `DRIVER_OBJECT.MajorFunction` 从 `+0x70` 开始；x86 是 `+0x38`。
- **`SystemBuffer` 取值**：`Method = BUFFERED` 时是 `Irp->AssociatedIrp.SystemBuffer`；`METHOD_NEITHER` 时要用 `Type3InputBuffer` 并自行 `ProbeForRead`。
- **`DRIVER_OBJECT` 结构偏移随 Windows 版本变**：用 `_DRIVER_OBJECT` 类型加载 `ntoskrnl.pdb` 后再看。
- **变体：WDM vs KMDF** —— KMDF 驱动有 `WdfDriverCreate`，逻辑在 `EvtIoDeviceControl` 回调里。
- **变体：隐藏 IOCTL** —— `switch` 用 `sub` + `ja` 判断范围，IDA 可能识别不出来，需手工看跳转表。
- **变体：数据混淆** —— 比较前做 XOR/ROL，需要从 case 里找常量。
- **变体：`MmCopyVirtualMemory` 读写其他进程** —— 题目常见"读 lsass 里的 flag"。
- **变体：驱动里直接 `ZwOpenFile` 读 `\??\C:\flag`** —— 破解思路是 patch 或伪造参数。

## 六、参考来源

- [Microsoft Learn — Introduction to I/O Control Codes](https://learn.microsoft.com/en-us/windows-hardware/drivers/kernel/introduction-to-i-o-control-codes)
- [Microsoft Learn — IRPs](https://learn.microsoft.com/en-us/windows-hardware/drivers/kernel/irp-major-function-codes)
- [Microsoft Learn — Writing a DriverEntry routine](https://learn.microsoft.com/en-us/windows-hardware/drivers/kernel/writing-a-driverentry-routine)
- [Microsoft Learn — WinDbg 调试器文档](https://learn.microsoft.com/en-us/windows-hardware/drivers/debugger/)
- [Ghidra](https://github.com/NationalSecurityAgency/ghidra)
- [x64dbg](https://github.com/x64dbg/x64dbg)
