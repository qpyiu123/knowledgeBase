---
title: "解析2025强网拟态决赛easyre"
category: reverse
tags: ["强网拟态 2025 决赛 easyre", "reverse", "signal-handler", "setjmp-longjmp", "SIGSEGV", "control-flow-obfuscation"]
signals: ["强网拟态 2025 决赛 easyre 2025", "signal-handler", "setjmp-longjmp", "SIGSEGV", "control-flow-obfuscation", "TEA-decrypt", "signal-based-vm", "exception-based-cf", "x86-pe32", "reverse", "easyre", "PE32", "Windows", "signal"]
difficulty: medium
source: "https://www.ctfiot.com/286199.html"
tools: ["x86/x64"]
origin: des-import
origin_kind: cards
updated: 2026-10-24
---
# 解析2025强网拟态决赛easyre

> 赛事：强网拟态 2025 决赛 easyre 2025 | 方向：reverse | 难度：medium | 工具：x86/x64

## 一句话总结

强网拟态2025决赛easyre逆向,PE32+Windows+signal(SIGSEGV)+setjmp/longjmp控制流混淆+异常处理触发跳转+TEA解密(delta补码0x61C88647+sum初值0xC6EF3720+32轮Feistel+32字符flag)。

## 攻击链

1. 文件:PE32+ x86-64 stripped to external PDB Windows 10 sections
2. 关键字符串:Input flag / Wrong flag! Try again. / Success / Wrong length! Hint: 32 chars.
3. 信号:SIGSEGV(11)访问违例+SIGILL非法指令+SIGFPE浮点异常+SIGINT中断
4. 控制流混淆:
5. 1. signal(SIGSEGV, handler)注册信号处理函数
6. 2. setjmp保存当前执行上下文
7. 3. mov dword [0], eax触发SIGSEGV(向地址0写入)
8. 4. 操作系统捕获异常调用处理函数
9. 5. handler通过longjmp跳转回setjmp位置
10. 正常控制流被异常处理打断,静态分析工具难跟踪
11. 关键逻辑隐藏在异常处理函数中,不在主执行流
12. TEA算法识别:
13. delta补码0x61C88647(标准TEA的delta补码)
14. sum初值=delta*32=0xC6EF3720
15. 位运算模式(左移4位+右移5位+异或+add+32轮)
16. Feistel结构(两个32位变量交替运算)
17. 解密步骤:
18. 1. 检查signal函数导入
19. 2. 定位signal调用位置
20. 3. 识别异常触发点(向地址0写入)
21. 4. 找到异常处理函数
22. 5. 识别密钥读取位置
23. 6. 提取原始密钥数据+计算变换后的实际密钥
24. 7. 提取密文(8个32位整数=4组64位)
25. 8. 标准TEA解密
26. 9. 小端序转换ASCII字符(每4字节反转)
27. 10. 拼接得flag

## 关键 payload

```
0x9E3779B9 + 0x61C88647 + signal(SIGSEGV, handler)
```

## 经验教训

signal(SIGSEGV)+setjmp/longjmp是控制流混淆的经典手法;TEA特征常量0x9E3779B9+0xC6EF3720+0x61C88647快速识别;密钥常在异常处理函数中计算,需从handler提取。

## 标签

signal-handler、setjmp-longjmp、SIGSEGV、control-flow-obfuscation、TEA-decrypt、signal-based-vm、exception-based-cf、x86-pe32、32-char-flag、wchar-key

## 参考来源

- https://www.ctfiot.com/286199.html
- 原文件：解析2025强网拟态决赛easyre.full.md
