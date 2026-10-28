---
title: "Sekai CTF ProcessFlipper.sys 驱动漏洞分析与利用"
category: misc
tags: ["Sekai CTF", "misc", "windows-kernel", "eprocess-flip", "kmdf-driver", "token-priv-escalation"]
signals: ["Sekai CTF 2024", "windows-kernel", "eprocess-flip", "kmdf-driver", "token-priv-escalation", "sys", "reverse", "Sekai", "CTF", "ProcessFlipper", "KMDF", "EPROCESS", "SYSTEM", "IDA"]
difficulty: hard
source: "https://www.ctfiot.com/210611.html"
tools: ["C", "IDA"]
origin: des-import
origin_kind: cards
updated: 2026-10-24
---
# Sekai CTF ProcessFlipper.sys 驱动漏洞分析与利用

> 赛事：Sekai CTF 2024 | 方向：misc | 难度：hard | 工具：C、IDA

## 一句话总结

Sekai CTF 2024 ProcessFlipper.sys：KMDF 驱动翻转 EPROCESS 任意位，本地权限提升至 SYSTEM。

## 攻击链

1. IDA 打开 ProcessFlipper.sys KMDF 驱动
2. WdfDriverCreate/WdfBindInfo 入口
3. 两个 IOCTL: 0x222004 (SET) / 0x222008 (CLEAR)
4. 翻转 EPROCESS 内任意位 (offset < 0x5c00 = 0xb80*8)
5. 通过 DiskCounters 字段构造 fake value
6. patch_diskcounter 写 12 bit 触发 token pointer 覆盖
7. NtQuerySystemInformation 遍历进程找目标 PID
8. 改 _TOKEN.privileges.present + privileges.enabled
9. 启用 SeDebugPrivilege 后 OpenSCManager 等
10. 读 C:\flag.txt 完成 System 提权
11. OpenSecurityTraining2 高级 Windbg 课
12. 操作系统置 Test Mode + OSRLoader 加载驱动

## 关键 payload

```
DeviceIoControl(file, IOCTL_PROCESS_SET/CLEAR, &BitToFlip, sizeof(BitToFlip), ...)
```

## 经验教训

任意位翻转即使粒度小，配合 12 bit DiskCounters 构造可定向覆盖 EPROCESS 关键指针。

## 标签

windows-kernel、eprocess-flip、kmdf-driver、token-priv-escalation、sys

## 参考来源

- https://www.ctfiot.com/210611.html
- 原文件：Sekai_CTF_ProcessFlipper.sys_驱动漏洞分析与利用.full.md
