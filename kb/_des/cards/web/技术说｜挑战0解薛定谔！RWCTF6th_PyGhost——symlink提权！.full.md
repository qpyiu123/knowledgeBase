---
title: "RWCTF6th PyGhost - Windows LPE symlink提权(0解薛定谔题)"
category: web
tags: ["RealWorldCTF 6th(0解薛定谔赛题)", "web", "LPE", "Local_Privilege_Escalation", "Windows", "PyInstaller"]
signals: ["RealWorldCTF 6th(0解薛定谔赛题) 2024", "LPE", "Local_Privilege_Escalation", "Windows", "PyInstaller", "symlink", "named_pipe", "matplotlib", "os.scandir", "web_unknown", "RWCTF6th", "PyGhost", "rmtree_unsafe", "TOCTOU"]
difficulty: hard
source: "https://www.ctfiot.com/169214.html"
tools: ["C"]
origin: des-import
origin_kind: cards
updated: 2026-10-24
---
# RWCTF6th PyGhost - Windows LPE symlink提权(0解薛定谔题)

> 赛事：RealWorldCTF 6th(0解薛定谔赛题) 2024 | 方向：web | 难度：hard | 工具：C

## 一句话总结

RWCTF6th PyGhost 0解薛定谔题:Windows服务matplotlib+PyInstaller _rmtree_unsafe symlink TOCTOU LPE。

## 攻击链

1. Windows服务以ctf低权限运行(RWCTFService+SMWinservice+named pipe) → 接收png/jpg/svg/pdf指令生成matplotlib图存C:\Windows\Temp\res.X.png → 0解赛题利用matplotlib临时文件可预测目录+PyInstaller的_rmtree_unsafe已知漏洞:scandir+is_dir但is_symlink被catch后continue → TOCTOU+symlink替换 → 提权

## 关键 payload

```
PyInstaller _rmtree_unsafe+symlink TOCTOU + matplotlib C:\Windows\Temp + named pipe + os.scandir
```

## 经验教训

0解薛定谔题特点:必须有历史漏洞背景知识+Windows特性;PyInstaller的_rmtree_unsafe:os.scandir+entry.is_dir(follow_symlinks=False)但is_symlink被catch后continue是race;matplotlib写C:\Windows\Temp可预测目录+Windows named pipe ACL;Windows service低权限运行需提权;挑战时间3分钟+只3次机会。

## 标签

LPE、Local_Privilege_Escalation、Windows、PyInstaller、symlink、named_pipe、matplotlib、os.scandir、_rmtree_unsafe、is_symlink、0解、薛定谔题、RWCTF、ctf低权限、nt_authority_system、服务权限

## 参考来源

- https://www.ctfiot.com/169214.html
- 原文件：技术说｜挑战0解薛定谔！RWCTF6th_PyGhost——symlink提权！.full.md
