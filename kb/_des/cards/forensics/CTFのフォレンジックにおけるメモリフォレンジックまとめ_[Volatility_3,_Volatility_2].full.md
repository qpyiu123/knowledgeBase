---
title: "CTF のフォレンジックにおけるメモリフォレンジックまとめ [Volatility 3, Volatility 2]"
category: forensics
tags: ["Volatility CTF", "forensics", "日语", "Volatility 3", "Volatility 2", "windows.info"]
signals: ["Volatility CTF 2023", "日语", "Volatility 3", "Volatility 2", "windows.info", "pstree", "netscan", "cmdline", "dumpfiles", "forensic_memory", "Volatility", "Windows", "hashdump", "mutantscan"]
difficulty: medium
source: "https://www.ctfiot.com/165189.html"
tools: ["Volatility"]
origin: des-import
origin_kind: cards
updated: 2026-10-24
---
# CTF のフォレンジックにおけるメモリフォレンジックまとめ [Volatility 3, Volatility 2]

> 赛事：Volatility CTF 2023 | 方向：forensics | 难度：medium | 工具：Volatility

## 一句话总结

Volatility 3 vs 2 内存取证总结 (日语) — Windows 关键命令 pstree+netscan+cmdline+dumpfiles+hashdump+mutantscan + Linux bash+psaux + 自制 profile (module.dwarf+System.map) + JPCERTCC 符号表。

## 攻击链

1. 内存取证标准: Volatility 3 推荐 (v2 v3 是完全不同的工具)
2. OS 识别: strings -n 10 mem.bin | grep "ubuntu" 或 windows.info.Info
3. Windows 关键命令: pstree / netscan / cmdline / dumpfiles / hashdump / mutantscan
4. Linux 关键命令: linux.bash (命令历史) / linux.psaux (ps -aux)
5. 自制 profile: module.dwarf + System.map 打包 zip 放到 plugins/overlays/linux/
6. VirusTotal 验证可疑 IP
7. 进程 dump: vol -f image.raw windows.dumpfiles --pid=1676
8. 即使不用 Volatility, File Carving + strings 也能拿到有用信息

## 关键 payload

```
Volatility 3 推荐 / windows.info / pstree / netscan / cmdline / dumpfiles / hashdump / mutantscan / linux.bash / linux.psaux / JPCERTCC 符号表 / File Carving
```

## 经验教训

Volatility 3 完全替代 2;windows.info 识别 OS;pstree+netscan 是黄金组合;linux.bash+psaux 是基础;符号表可自制 (module.dwarf + System.map)。

## 标签

日语、Volatility 3、Volatility 2、windows.info、pstree、netscan、cmdline、dumpfiles、hashdump、mutantscan、linux.bash、linux.psaux、profile、JPCERTCC符号表、File Carving、strings

## 参考来源

- https://www.ctfiot.com/165189.html
- 原文件：CTFのフォレンジックにおけるメモリフォレンジックまとめ_[Volatility_3,_Volatility_2].full.md
