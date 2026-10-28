---
title: "记一次某部内存取证比赛writeup"
category: forensics
tags: ["某部内存取证比赛", "forensics", "volatility", "winxp", "imageinfo", "pstree"]
signals: ["某部内存取证比赛 2023", "volatility", "winxp", "imageinfo", "pstree", "pslist", "memdump", "dlllist", "malfind", "forensic_memory", "volatility2", "WinXPSP3x86", "dump", "SAM"]
difficulty: medium
source: "https://www.ctfiot.com/131729.html"
tools: []
origin: des-import
origin_kind: cards
updated: 2026-10-24
---
# 记一次某部内存取证比赛writeup

> 赛事：某部内存取证比赛 2023 | 方向：forensics | 难度：medium

## 一句话总结

某部内存取证比赛WP,volatility2全套命令实战:WinXPSP3x86镜像+进程树+进程dump+注册表蜂巢+SAM hashdump+Winlogon最后登录用户+AES解密+matplotlib数据绘图。

## 攻击链

1. volatility2 imageinfo确认winxp.raw为WinXPSP3x86
2. pstree/pslist查运行进程
3. memdump/procdump/dlldump导出PID=324进程及所有DLL
4. getsids/dlllist/threads/malfind深挖进程痕迹
5. hivelist查注册表蜂巢位置
6. hivedump导出SAM,hashdump -y system -s SAM取账号Hash
7. printkey查SOFTWARE\Microsoft\Windows NT\CurrentVersion\Winlogon最后登录用户
8. 拿到key=Th1s_1s_K3y00000+iv=1234567890123456
9. AES/CBC解密jfXvUoypb8p3zvmPks8kJ5Kt0vmEw0xUZyRGOicraY4=得flag
10. hint.txt数据用matplotlib作图显示图像(可能是字符画或图片)

## 关键 payload

```
key=Th1s_1s_K3y00000 iv=1234567890123456
```

## 经验教训

volatility2是Windows内存取证必备工具,常用命令组合:imageinfo→pstree→pslist→memdump→hivelist→hashdump→printkey,matplotlib散点图作图是hint可视化的简单方法。

## 标签

volatility、winxp、imageinfo、pstree、pslist、memdump、dlllist、malfind、hivelist、hashdump、TrueCrypt、matplotlib、hint-plot

## 参考来源

- https://www.ctfiot.com/131729.html
- 原文件：记一次某部内存取证比赛writeup.full.md
