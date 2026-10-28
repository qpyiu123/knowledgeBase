---
title: "基于volatility2构建新版本内核profile指南"
category: forensics
tags: ["内存取证通用指南", "forensics", "volatility2", "内存取证", "Linux_profile", "dwarf"]
signals: ["内存取证通用指南 2022", "volatility2", "内存取证", "Linux_profile", "dwarf", "System.map", "banners.Banners", "linux_enumerate_files", "linux_find_file", "forensic_memory", "profile", "make", "dwarfdump", "zip"]
difficulty: medium
source: "https://www.ctfiot.com/70385.html"
tools: ["x86/x64"]
origin: des-import
origin_kind: cards
updated: 2026-10-24
---
# 基于volatility2构建新版本内核profile指南

> 赛事：内存取证通用指南 2022 | 方向：forensics | 难度：medium | 工具：x86/x64

## 一句话总结

跳跳糖投稿2022:volatility2自定义内核profile三步走(make dwarfdump+zip+plugins/linux)。

## 攻击链

1. strings 1.mem grep "Linux version"确定内核版本 → sudo apt install linux-headers-$(uname -r) build-essential dwarfdump → volatility/tools/linux目录make → zip压缩module.dwarf+System.map → mv到volatility/plugins/linux/ → vol2 -f 1.mem --profile=LinuxUbuntu1804-5_4_0-84x64 加载 → linux_enumerate_files | grep shadow → linux_find_file -O shadow.txt恢复

## 关键 payload

```
module.dwarf + System.map + zip打包 = LinuxUbuntu1804-5_4_0-84x64 profile
```

## 经验教训

volatility2不支持新内核时必须自建profile:同版本kernel headers+dwarfdump生成module.dwarf + 同版本/boot/System.map → zip压缩命名Linux<distro><version>x64 → 放入plugins/linux/;常用linux_*插件100+:bash_history/enumerate_files/find_file/pslist/lsmod/arp/ifconfig/检查rootkit系列(check_idt/check_syscall/check_modules)。

## 标签

volatility2、内存取证、Linux_profile、dwarf、System.map、banners.Banners、linux_enumerate_files、linux_find_file、linux_bash、蓝帽杯、dwarfdump、内核取证

## 参考来源

- https://www.ctfiot.com/70385.html
- 原文件：如何基于volatility2构建“新”版本内核的profile.full.md
