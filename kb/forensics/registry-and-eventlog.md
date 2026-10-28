---
title: Windows 取证（注册表 / EVTX 事件日志）
category: forensics
tags: [windows, 注册表, evtx, 事件日志, hive, 登录记录]
signals: [附件是 NTUSER.DAT 或 SYSTEM, 附件是 evtx 日志, 题目问谁登录过, 需要找 U 盘插拔记录, 需要还原程序执行记录, 需要看远程登录 IP]
difficulty: medium
source: "Eric Zimmerman 工具文档 / Registry Explorer 指南 / Microsoft EVTX 格式说明"
tools: [RegistryExplorer, regripper, python-registry, evtx_dump, EvtxECmd, TimelineExplorer, vol3]
updated: 2026-10-22
---

## 一、识别信号（题面长什么样）

- 附件是 `NTUSER.DAT`、`SYSTEM`、`SOFTWARE`、`SAM`、`SECURITY` 等 hive 文件。
- 附件是 `Security.evtx`、`System.evtx` 等日志，题目问「什么时候登录」「谁登录失败过。
- 题目问「U 盘什么时候插过」「某个程序什么时候执行过」。
- 需要从 `Amcache.hve` / `$UsnJrnl` / `Prefetch` 找执行痕迹。

## 二、原理

**注册表** 由多个 **hive** 文件组成，每个 hive 内部是 `regf` 头 + hbin 分配单元 + NK/VK 单元格（key/value）。关键 hive 与路径：

| Hive | 位置 | 取证要点 |
| --- | --- | --- |
| `SYSTEM` | `Windows\System32\config\` | `ControlSet00X\Services`、`USBSTOR`、网络配置 `Interfaces` |
| `SOFTWARE` | 同上 | 已安装软件、`Run` 键持久化 |
| `SAM` | 同上 | 本地账户（可导出哈希） |
| `SECURITY` | 同上 | LSA secrets、缓存凭据 |
| `NTUSER.DAT` | 用户目录根 | `UserAssist`、`TypedPaths`、`RecentDocs`、`RunMRU` |
| `UsrClass.dat` | `AppData\Local\Microsoft\Windows` | ShellBags（文件夹浏览历史） |
| `Amcache.hve` | `Windows\AppCompat\Programs\` | 程序首次执行时间与路径 |

**EVTX**：Windows Vista 后的二进制事件日志格式（`ElfFile\0` 魔数），每条记录是 XML 序列化后的 BinXML。关键事件 ID：

| ID | 日志 | 含义 |
| --- | --- | --- |
| 4624 | Security | 登录成功（含 Logon Type 2/3/10） |
| 4625 | Security | 登录失败 |
| 4634 | Security | 注销 |
| 4648 | Security | 显式凭据登录（runas） |
| 4672 | Security | 授予特殊权限（管理员登录） |
| 4688 | Security | 进程创建（需开启审计） |
| 1102 | Security | 日志被清除（反取证） |
| 7045 | System | 新服务安装（常见持久化） |
| 1001 | Microsoft-Windows-WER | 程序崩溃报告 |

## 三、操作步骤

1. **判 hive 类型**：`file NTUSER.DAT` 应报 `MS Windows registry file`，或看头 4 字节 `regf`。
2. **用 RegRipper 一把梭**：`rip.pl -r NTUSER.DAT -f ntuser`，输出几十个插件结果。
3. **Registry Explorer 交互**：加载 hive → 内置 `Bookmarks` 直接跳到关键路径。
4. **EVTX**：`EvtxECmd` 转 CSV，或 `python-evtx` 还原 XML。
5. **拼时间线**：把注册表时间、EVTX 时间、文件系统 MACB 时间统一成 UTC 排序。
6. **交叉验证**：注册表说"程序 X 在 10:00 执行"、EVTX 4688 应吻合。

## 四、命令/脚本

### 注册表 hive 定位与拷贝

```bash
# 取证副本（在活系统上先拷贝，不能直接读）
cp /mnt/c/Windows/System32/config/SYSTEM ./SYSTEM
cp /mnt/c/Windows/System32/config/SOFTWARE ./SOFTWARE
cp /mnt/c/Users/USER/NTUSER.DAT ./NTUSER.DAT
# 判断类型
xxd -l 8 NTUSER.DAT      # 应看到 72 65 67 66 ("regf")
```

### RegRipper

```bash
git clone https://github.com/keydet89/RegRipper3.0
perl rip.pl -r NTUSER.DAT -f ntuser > ntuser.txt      # 自动插件集
perl rip.pl -r SYSTEM -f system > system.txt
perl rip.pl -r SAM -f sam > sam.txt
perl rip.pl -r SOFTWARE -f software > software.txt
grep -iE 'usb|run|runonce|lnk' ntuser.txt | head -20
```

### 用 python-registry 精确查键值

```python
#!/usr/bin/env python3
# reg_query.py —— 读取 hive 内任意路径，并打印值
from Registry import Registry
import sys
hive, path = sys.argv[1], sys.argv[2]
reg = Registry.Registry(hive)
k = reg.open(path)
print('key:', k.path(), 'last_write:', k.timestamp())
for v in k.values():
    print(' -', v.name(), '=', repr(v.value()))
```

```bash
python reg_query.py NTUSER.DAT 'Software\Microsoft\Windows\CurrentVersion\Explorer\RunMRU'
python reg_query.py SYSTEM 'ControlSet001\Enum\USBSTOR'
python reg_query.py NTUSER.DAT 'Software\Microsoft\Windows\CurrentVersion\Explorer\TypedPaths'
```

### 常见取证键位速查

```bash
# 用户最近运行（GUI 程序 + 次数 + 最后时间）
python reg_query.py NTUSER.DAT 'Software\Microsoft\Windows\CurrentVersion\Explorer\UserAssist\{ROT13-GUID}\Count'
# 最近打开文档
python reg_query.py NTUSER.DAT 'Software\Microsoft\Windows\CurrentVersion\Explorer\RecentDocs'
# U 盘历史
python reg_query.py SYSTEM 'ControlSet001\Enum\USBSTOR'
# 自动启动项（持久化）
python reg_query.py NTUSER.DAT 'Software\Microsoft\Windows\CurrentVersion\Run'
python reg_query.py SOFTWARE 'Microsoft\Windows\CurrentVersion\Run'
# 映射过的网络驱动器
python reg_query.py NTUSER.DAT 'Network'
# 网络接口（含最后连接的 SSID）
python reg_query.py SOFTWARE 'Microsoft\Windows NT\CurrentVersion\NetworkList\Profiles'
```

### EVTX 解析

```bash
pip install python-evtx
python -m Evtx.Evtx Security.evtx > /dev/null    # 简单校验
evtx_dump -o jsonl Security.evtx | head -3        # evtx_dump (Rust 工具)
# EvtxECmd（Windows 端，输出 CSV）
EvtxECmd.exe -f Security.evtx --csv . --csvf sec.csv
```

```python
#!/usr/bin/env python3
# evtx_filter.py —— 按事件 ID 过滤 EVTX 并打印关键字段
import sys, re
from Evtx.Evtx import Evtx
from Evtx.Views import evtx_file_xml_view
from xml.etree import ElementTree as ET

want = set(sys.argv[2].split(',')) if len(sys.argv) > 2 else {'4624', '4625', '4688'}
with Evtx(sys.argv[1]) as evtx:
    for xml, _ in evtx_file_xml_view(evtx.get_file_header()):
        try:
            root = ET.fromstring(xml)
        except ET.ParseError:
            continue
        ns = {'e': 'http://schemas.microsoft.com/win/2004/08/events/event'}
        eid = root.findtext('.//e:EventID', '', ns)
        if eid not in want:
            continue
        data = {d.get('Name'): (d.text or '') for d in root.iter(
            '{http://schemas.microsoft.com/win/2004/08/events/event}Data')}
        print(eid, root.findtext('.//e:TimeCreated', '', ns),
              data.get('TargetUserName') or data.get('SubjectUserName'),
              data.get('IpAddress'), data.get('CommandLine'))
```

```bash
python evtx_filter.py Security.evtx 4624,4625 | head -30
```

### 一键 grep（不装工具时）

```bash
strings -el Security.evtx | grep -iE 'logon|4624|flag' | head
# 找被清除日志（1102）
strings -el Security.evtx | grep -c '1102'
```

## 五、常见坑 / 变体

- **hive 正被占用**：活系统上直接读会失败，用 `reg save HKLM\SYSTEM d:\SYSTEM.hiv` 或卷影副本。
- **时间戳是 local time**：注册表 `last_write` 是 UTC，EVTX `SystemTime` 是 UTC，题面若给北京时间要换算。
- **UsrClass.dat 的 ShowBags** 能看出用户浏览过哪些文件夹（含已删除路径）。
- **EVTX 被截断**：`evtx_dump` 会报错但通常仍能 dump 出前面的记录。
- **日志被清（1102）**：题目会问"什么时候被清"，答案就在这条记录里。
- **RDP 登录**：4624 的 `Logon Type 10`，配合 `IpAddress` 字段。
- **与内存取证交叉**：hive 在内存里也有缓存，`hivelist` 能找到已卸载的 hive。

## 六、参考来源

- [RegRipper 官方仓库与插件说明](https://github.com/keydet89/RegRipper3.0)
- [python-registry 文档](https://github.com/williballenthin/python-registry)
- [python-evtx（EVTX 解析）](https://github.com/williballenthin/python-evtx)
- [Eric Zimmerman 工具集（EvtxECmd/Registry Explorer）](https://ericzimmerman.github.io/)
- [Microsoft 安全事件 4624/4625 文档](https://learn.microsoft.com/en-us/windows/security/threat-protection/auditing/event-4624)
- [CTF Wiki - 取证隐写前置技术](https://ctf-wiki.org/misc/prefix/)
