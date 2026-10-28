---
title: "固件安全的隐忧：UEFI漏洞的持续威胁与修复之路"
category: misc
tags: ["Binarly UEFI 漏洞研究", "misc", "Binarly", "UEFI固件", "AMI UsbRt", "SMM漏洞"]
signals: ["Binarly UEFI 漏洞研究 2025", "Binarly", "UEFI固件", "AMI UsbRt", "SMM漏洞", "CVE-2022-24419", "CVE-2022-24420", "CVE-2022-24421", "SMM_Code_Chk_En", "misc_unknown", "UEFI", "AMI", "UsbRt", "CRC32"]
difficulty: hard
source: "https://www.ctfiot.com/237369.html"
tools: ["ROP"]
origin: des-import
origin_kind: cards
updated: 2026-10-24
---
# 固件安全的隐忧：UEFI漏洞的持续威胁与修复之路

> 赛事：Binarly UEFI 漏洞研究 2025 | 方向：misc | 难度：hard | 工具：ROP

## 一句话总结

Binarly UEFI 固件安全研究：AMI UsbRt 7 年漏洞未修复 + CRC32 欺骗 + SMM ROP 链 + FwHunt 大规模检测。

## 攻击链

1. Binarly 团队 1 年披露 42 个高严重性 UEFI 漏洞
2. AMI UsbRt (INTEL-SA-00057) 7 年漏洞仍未修复
3. gUsbData 结构 30+ 字段，代码复杂难维护
4. CVE-2017-5721 → CVE-2020-12301 CRC32 欺骗绕过
5. ValidateUsbData() CRC32 校验可被 CRC32 强制攻击绕过
6. CVE-2020-12301 利用：控制 struct_ptr + gUsbData
7. SMM_Code_Chk_En 缓解 (Intel Kabylake+)
8. SMM 公开 ROP 链: SetJump 抓寄存器 + CopyMem 链
9. 戴尔 3 个新 UsbRt 变种 (BRLY-2021-043/045, BRLY-2022-004)
10. 戴尔 DSA-2022-053 三个月响应
11. Binarly FwHunt + LVFS 协作大规模检测

## 关键 payload

```
AMI UsbRt gUsbData 30+ 字段 + CRC32 欺骗 + SMM ROP 链 + FwHunt 检测
```

## 经验教训

AMI UsbRt 是 7 年老漏洞 (gUsbData 30+ 字段), CRC32 验证可被欺骗绕过, SMM_Code_Chk_En 仅 Kabylake+ 支持, ROP 链利用 SMM 是核心攻击面。

## 标签

Binarly、UEFI固件、AMI UsbRt、SMM漏洞、CVE-2022-24419、CVE-2022-24420、CVE-2022-24421、SMM_Code_Chk_En、ROP链、FwHunt

## 参考来源

- https://www.ctfiot.com/237369.html
- 原文件：固件安全的隐忧：UEFI漏洞的持续威胁与修复之路.full.md
