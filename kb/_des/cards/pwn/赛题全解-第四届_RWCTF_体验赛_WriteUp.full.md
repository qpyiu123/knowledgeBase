---
title: "赛题全解|第四届 RWCTF 体验赛 WriteUp"
category: pwn
tags: ["第四届 Real World CTF 体验赛", "pwn", "Java-Processor", "Annotation-Processing", "SNMP-aarch64", "kernel-UAF"]
signals: ["第四届 Real World CTF 体验赛 2022", "Java-Processor", "Annotation-Processing", "SNMP-aarch64", "kernel-UAF", "Docker-escape", "lvm-vm", "CAP_DAC_OVERRIDE", "QEMU-RTOS", "pwn_unknown", "Real", "World", "CTF", "Java"]
difficulty: hard
source: "https://www.ctfiot.com/24814.html"
tools: ["Java"]
origin: des-import
origin_kind: cards
updated: 2026-10-24
---
# 赛题全解|第四届 RWCTF 体验赛 WriteUp

> 赛事：第四届 Real World CTF 体验赛 2022 | 方向：pwn | 难度：hard | 工具：Java

## 一句话总结

第四届Real World CTF体验赛赛题全解,涵盖Java Processor注解处理+SNMP aarch64 PWN+kernel UAF+Docker逃逸+lvm VM+CAP_DAC_OVERRIDE+Log4j JNDI+Redis+H2 RCE。

## 攻击链

1. Secured Java: 扩展javax.annotation.processing.AbstractProcessor+读取flag+打包为jar(META-INF/services)+远程发送
2. Remote Debugger: 39支战队解出(简单Java JDWP调试)
3. Be-an-IoT-Hacker: SNMP SET OID 1.3.6.1.4.1.23333.1.0写入aarch64 shellcode+反弹shell
4. Digging into Kernel: kmem_cache_create("lalala", 192, 0, 0, 0)+xkmod_ioctl三命令(alloc/rd/wt)+fork子进程+UAF改cred.uid=0提权
5. Be-a-Docker-Escaper: docker -m 128m挂载docker.sock+privileged+挂载/dev/sda1读宿主机flag
6. Be-a-VM-Escaper: 自定义lvm VM(PUSH/POP/ADD/SUB/IFEQ/JMP等)+libc-2.31栈地址计算+ret+system(/bin/sh)
7. Phonograph: CAP_DAC_OVERRIDE capability读/records+CVE-2016-1247 /etc/ld.so.preload提权
8. the REAL Menu Challenge: QEMU vexpress-a9 + 0x600104D0栈溢出+shellcode(ldr r0 flag; ldr pc puts)
9. 1log4flag: Log4j2 RCE+${j${::-n}di:${::-l}dap://...}绕字符串检查+su18/JNDI工具
10. 2Be-a-Database-Hacker: Redis未授权+写公钥或定时任务反弹+H2数据库CREATE ALIAS SHELLEXEC执行whoami

## 关键 payload

```
Log4j2 ${j${::-n}di:ldap://} + H2 CREATE ALIAS SHELLEXEC
```

## 经验教训

Real World CTF体验赛质量顶级,涵盖IOT/内核/容器/VM/CAP/JNDI/Redis/H2等真实场景;Log4j2字符串绕过${j${::-n}di:${::-l}dap}是2022热点;H2数据库CREATE ALIAS是Web Java常见反序列化路径。

## 标签

Java-Processor、Annotation-Processing、SNMP-aarch64、kernel-UAF、Docker-escape、lvm-vm、CAP_DAC_OVERRIDE、QEMU-RTOS、Log4j-JNDI、Redis-unauth、H2-Database、phpMyAdmin、Pentest-Pivoting

## 参考来源

- https://www.ctfiot.com/24814.html
- 原文件：赛题全解-第四届_RWCTF_体验赛_WriteUp.full.md
