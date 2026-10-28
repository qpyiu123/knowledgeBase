---
title: "解析2025强网杯tradre"
category: reverse
tags: ["强网杯 2025 tradre", "reverse", "control-flow-obfuscation", "basic-block", "state-transition", "alarm-bypass"]
signals: ["强网杯 2025 tradre 2025", "control-flow-obfuscation", "basic-block", "state-transition", "alarm-bypass", "signal-SIGCHLD", "AES-modified", "S-box-XOR", "fork-anti-debug", "reverse", "tradre", "Full", "RELRO", "Canary"]
difficulty: hard
source: "https://www.ctfiot.com/275554.html"
tools: []
origin: des-import
origin_kind: cards
updated: 2026-10-24
---
# 解析2025强网杯tradre

> 赛事：强网杯 2025 tradre 2025 | 方向：reverse | 难度：hard

## 一句话总结

强网杯2025 tradre逆向,Full RELRO+Canary+NX+No PIE+控制流平坦化(182基本块+176状态转移)+fork()反调试+alarm(60)修补(mod $60, %edi→$0, %edi)+AES-128(固定seed+32字节XOR密钥循环混淆S盒)。

## 攻击链

1. ELF 64位LSB+Full RELRO+Canary+NX+No PIE
2. 大小:29160字节+入口0x400910+代码段0x400000-0x405288
3. 数据段:0x605d58-0x608160
4. 基本块结构体:0x606AC0
5. 转储大小:16318字节+182个基本块+176种状态转移函数
6. improved_dump.bin:5792字节+181/181非空基本块
7. 恢复代码大小:1882字节+生成反汇编代码:555行
8. 修补位置:文件偏移0x47eb
9. 修补内容:mov $60, %edi → mov $0, %edi (alarm(60)→alarm(0))
10. 生成:minimal_patch_tradre
11. 反调试:fork()+alarm(60)+signal(SIGCHLD)
12. 加密:固定seed+rand()+AES-128(16字节密钥)+32字节XOR密钥循环混淆256字节S盒
13. 三重XOR:随机数 ^ XOR密钥 ^ 原始字节
14. 密文:3136323964353231323863613339356534663661306663393837313261336531 / ASCII:1629d52128ca395e4f6a0fc98712a3e1
15. 信号:SIGCHLD(监控子进程)+SIGTRAP(处理int3断点)+SIGALRM(60秒超时)
16. 状态转移:0x0(JMP)+0x401CA6(JLE)+0x401D22(JNE)+0x401D5B(JE)+0x401DCD(JNS)+0x401F0C(JG)+0x401C31(JL)+0x401EB4(CALL)+0x401EA5(EXT)+0x401E96(RET)

## 关键 payload

```
minimal_patch_tradre (alarm(60)→alarm(0))
```

## 经验教训

tradre是2025强网杯控制流混淆+多反调试+魔改AES的高级题;alarm(60)单点patch是绕过60秒超时的标准方法;S盒三重XOR(随机数^XOR密钥^原始字节)需要从已知seed爆破。

## 标签

control-flow-obfuscation、basic-block、state-transition、alarm-bypass、signal-SIGCHLD、AES-modified、S-box-XOR、fork-anti-debug、minimal-patch、dispatcher

## 参考来源

- https://www.ctfiot.com/275554.html
- 原文件：解析2025强网杯tradre.full.md
