---
title: "解析2025强网拟态Icall"
category: reverse
tags: ["强网拟态 2025 Icall", "reverse", "anti-debug", "prctl-tracer", "proc-status", "pthread-create"]
signals: ["强网拟态 2025 Icall 2025", "anti-debug", "prctl-tracer", "proc-status", "pthread-create", "self-kill", "custom-RC4", "affine-cipher", "prctl-bypass", "reverse", "Icall", "pthread_create", "prctl", "TracerPid"]
difficulty: hard
source: "https://www.ctfiot.com/277428.html"
tools: ["GDB", "x86/x64"]
origin: des-import
origin_kind: cards
updated: 2026-10-24
---
# 解析2025强网拟态Icall

> 赛事：强网拟态 2025 Icall 2025 | 方向：reverse | 难度：hard | 工具：GDB、x86/x64

## 一句话总结

强网拟态2025 Icall多层加密+反调试对抗,pthread_create+prctl监控+TracerPid检测+kill自杀,绕反调试后三轮加密(多轮RC4+仿射+Enc1yp7)逐层解密。

## 攻击链

1. ELF 64位 LSB, x86-64, dynamically linked, stripped
2. 关键符号:pthread_create/prctl/getpid+kill
3. 多线程反调试:
4. 主线程init阶段创建监控线程
5. 子线程prctl(PR_SET_PTRACER, ...)+读/proc/self/status检查TracerPid
6. TracerPid!=0 → kill自杀
7. 绕反调试:GDB return命令直接跳过函数(动态) / Hook prctl系统调用 / 修改二进制NOP掉
8. 三轮加密:r0uNd_Rc4(多轮RC4)+Aff1ne(仿射密码)+Enc1yp7(混淆名)
9. 三轮循环次数:0x0C(12)+0x1E(30)+0x2A(42)
10. 字符类型不同参数:
11. 数字0-9:模数10,乘数7,加数11,逆元3
12. 大写A-Z:模数26,乘数17,加数11,逆元15
13. 小写a-z:模数26,乘数17,加数11,逆元15
14. 自定义S-box+多轮PRGA+CFB链式XOR

## 关键 payload

```
r0uNd_Rc4 + Aff1ne + Enc1yp7
```

## 经验教训

多线程反调试(子线程prctl+TracerPid检测)比单线程更难绕过;GDB的return命令是动态绕反调试最灵活的方法;多轮RC4+仿射+混淆函数名是常见组合加密模式。

## 标签

anti-debug、prctl-tracer、proc-status、pthread-create、self-kill、custom-RC4、affine-cipher、prctl-bypass、GDB-return、multi-round

## 参考来源

- https://www.ctfiot.com/277428.html
- 原文件：解析2025强网拟态Icall.full.md
