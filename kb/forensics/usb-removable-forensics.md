---
title: USB / 移动存储取证（USBSTOR、挂载记录与文件恢复）
category: forensics
tags: [usb, usbstor, registry, mounteddevices, mobile-storage, removable]
signals: [题目问这台电脑插过什么 U 盘, 附件是一个 Windows 系统的注册表 hive, 题目问文件是从哪个设备拷贝过来的, 要求还原 U 盘序列号或者厂家型号, 给了 setupapi.dev.log 日志, 题目描述里出现 2019 年某天有人接过外接硬盘, 需要找出移动设备的首次接入时间]
difficulty: medium
source: "Windows Registry USBSTOR 取证规范 / Eric Zimmerman 工具集 / DFIR 公开文章"
tools: [python, regripper, registry-explorer, usbforensics, MFTECmd, Timeline-Explorer]
updated: 2026-10-22
exec_yaml: ok
---

## 一、识别信号（题面长什么样）

- 附件里有 `SYSTEM`、`SOFTWARE`、`SAM` 等 hive 文件（无扩展名，`file` 识别为 `MS Windows registry file`）。
- 附件里有 `C:\Windows\INF\setupapi.dev.log`。
- 题目问"设备的序列号""最后一次连接时间""被拷贝走的是哪个文件"。
- 场景描述"公司电脑被插了不明 U 盘""有个文件被拷到移动硬盘"。
- `.vmx` / `.vmdk` / `.qcow2` 里含完整 Windows 分区。
- 题目给出的 flag 形式与设备序列号或 VID/PID 相关。

## 二、原理

**Windows 对 USB 设备的记录散落在至少 5 个位置：**

| 位置 | 内容 | 时间戳 |
| --- | --- | --- |
| `SYSTEM\ControlSet00x\Enum\USBSTOR` | 设备类 PID、序列号（子键） | 无 |
| `SYSTEM\...\Enum\USB` | VID/PID 与 **首次连接时间**（`Properties\{83da6326-...}\0065`） | FILETIME |
| `SYSTEM\MountedDevices` | 卷 GUID ↔ 盘符的二进制映射 | 无 |
| `SOFTWARE\Microsoft\Windows Portable Devices\Devices` | 友好名称 | 无 |
| `NTUSER.DAT\...\MountPoints2` | 用户上下文下的挂载记录（含卷 GUID） | 有 |
| `setupapi.dev.log` | 设备安装全过程与 ANCHOR 时间 | 文本时间 |

- **设备序列号就在键名里**：`USBSTOR\Disk&Ven_SanDisk&Prod_Cruzer&Rev_1.00\4C530001120523123456&0`，最后一段是序列号与实例号。
- **首次连接时间**存放在 `Properties` 下的 GUID 子键：`{83da6326-97a6-4088-9453-a1923f573b29}` 是设备属性集合，`0064`=首次连接、`0065`=最后一次连接、`0066`=最后移除，值是 8 字节 FILETIME。
- **文件来源**：NTFS 的 `$MFT` 里每个文件的 `$FILE_NAME` 与 `$STANDARD_INFORMATION` 时间戳，配合 `USN Journal`（`$UsnJrnl:$J`）可看到"拷贝进/拷贝出"的 `FILE_CREATE`、`CLOSE` 记录。

## 三、操作步骤

1. **定位 hive**：`SAM`/`SYSTEM`/`SOFTWARE` 在 `Windows/System32/config`，用户 hive 在 `Users/<name>/NTUSER.DAT`。
2. **用 RegRipper 或 regipy 批量出 USB 相关报告**。
3. **解析 `USBSTOR`**：列出所有设备型号、序列号。
4. **解析 `USB` 的 Properties**：读出首次/最后连接 FILETIME。
5. **`MountedDevices` ↔ `MountPoints2`**：把卷 GUID 对应到盘符，确认"哪个盘符是那个 U 盘"。
6. **`setupapi.dev.log`**：搜索 `Device Install (Hardware initiated)`，看精确到秒的安装时间与 `{vendor/product}`。
7. **文件层面**：用 `MFTECmd` 输出 `$MFT` 与 `$J`，按时间窗筛选"目标文件拷贝出去"的事件。

## 四、命令 / 脚本

```bash
# 用 regipy 快速遍历
pip install regipy
regipy-dump -f SYSTEM -o system_dump.json
regipy-dump -f NTUSER.DAT -o ntuser_dump.json
# RegRipper（Windows 上跑）
rip.exe -r SYSTEM -p usbstor
rip.exe -r SYSTEM -p usbdevices
```

```python
#!/usr/bin/env python3
# 直接解析 SYSTEM hive 里的 USBSTOR / USB 属性时间戳
from Registry import Registry
import datetime

def filetime(v):
    """FILETIME 100ns -> datetime"""
    if isinstance(v, bytes):
        v = int.from_bytes(v, 'little')
    if not v:
        return None
    return datetime.datetime(1601, 1, 1) + datetime.timedelta(microseconds=v // 10)

PROPS = '{83da6326-97a6-4088-9453-a1923f573b29}'
LABEL = {'0064': 'first-connect', '0065': 'last-connect', '0066': 'last-remove'}

reg = Registry.Registry('SYSTEM')
usbstor = reg.open('ControlSet001\\Enum\\USBSTOR')
for dev in usbstor.subkeys():
    print('== %s' % dev.name())
    for inst in dev.subkeys():
        print('   序列号/实例: %s' % inst.name())
        for k in ('FriendlyName', 'DeviceDesc', 'Mfg'):
            try:
                print('   %-12s %s' % (k, inst.value(k).value()))
            except Exception:
                pass

usb = reg.open('ControlSet001\\Enum\\USB')
for vid in usb.subkeys():
    for inst in vid.subkeys():
        try:
            props = inst.open(PROPS)
        except Exception:
            continue
        for sub in props.subkeys():
            if sub.name() in LABEL:
                for val in sub.values():
                    if isinstance(val.value(), (bytes, int)):
                        print('%-14s %-16s %s' % (inst.name(),
                              LABEL[sub.name()], filetime(val.value())))
```

```bash
# setupapi.dev.log 里的 USB 安装事件
grep -n -A6 'Device Install (Hardware initiated)' setupapi.dev.log | grep -iE 'usbstor|usb\\vid' | head -30
# MountedDevices 与 MountPoints2
regipy-dump -f SYSTEM -o sys.json && grep -i -A3 'MountedDevices' sys.json | head -40
```

## 五、常见坑 / 变体

- **ControlSet 编号**：`ControlSet001` 通常对应 `CurrentControlSet`，但系统曾异常启动会有 `002`，要读 `Select\Current` 确认。
- **Properties 是二进制结构**：不是直接 8 字节整数，是 `REG_BINARY` 包着一个小头部（前 8 字节是类型标记），取值时要跳过头部——保险做法是用 regipy 的 typed parser。
- **序列号可以被伪造**：U 盘主控允许量产后改序列号，所以"序列号相同"不等于"同一设备"，需结合 VID/PID。
- **用户在 `USB` 里的子键是 `VID_XXXX&PID_YYYY`**，序列号在更深一层，不要只取第一层。
- **`setupapi.dev.log` 会滚动覆盖**：只保留最近的部分，旧设备事件可能已丢。
- **手机/MTP 设备不走 USBSTOR**：看 `Windows Portable Devices\Devices` 与 `WPDNSE`。
- **虚拟机取证**：把 `.vmdk` 挂载后要按 `\\.\PhysicalDrive` 方式读取原始扇区，别直接看挂载后的文件系统（会改时间戳）。

## 六、参考来源

- [USB Device Forensics：USBSTOR / MountPoints2 / setupapi 全解析](https://elitedigitalforensics.com/usb-device-forensics/)
- [Elcomsoft：Windows 10/11 USB 设备取证（注册表与事件日志）](https://blog.elcomsoft.com/2026/02/usb-device-forensics-on-windows-10-and-11/)
- [Eric Zimmerman 工具集（含 MFTECmd、PECmd、注册表工具）](https://ericzimmerman.github.io/)
- [regipy 文档（Python 注册表解析）](https://github.com/mkorman90/regipy)
- [RegRipper 插件说明（usbstor / usbdevices）](https://github.com/keydet89/RegRipper3.0)
