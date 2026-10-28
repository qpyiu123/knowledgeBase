---
title: "2025 年广西网络与信息安全职业技能竞赛 WriteUP"
category: misc
tags: ["2025 广西网络与信息安全职业技能竞赛", "misc", "Wireshark", "7-bit-decoder", "SpamMimic", "libc-2.35"]
signals: ["2025 广西网络与信息安全职业技能竞赛 2025", "Wireshark", "7-bit-decoder", "SpamMimic", "libc-2.35", "gets", "openat", "PHP-act动态函数", "Spring-aop", "stego_traffic", "reverse", "ret2libc", "rce", "pwn"]
difficulty: hard
source: "https://www.ctfiot.com/281909.html"
tools: ["Java", "PHP", "Spring", "Wireshark"]
origin: des-import
origin_kind: cards
updated: 2026-10-24
---
# 2025 年广西网络与信息安全职业技能竞赛 WriteUP

> 赛事：2025 广西网络与信息安全职业技能竞赛 2025 | 方向：misc | 难度：hard | 工具：Java、PHP、Spring、Wireshark

## 一句话总结

广西职业技能赛 8 大题：流量+密码+re+pwn+web+java

## 攻击链

1. Misc EasyShark: Wireshark 找 hint → 7-bit ASCII 解码 SpamMimic → flag
2. Crypto hint7-bit: 6664666C6E5F5F6C616974744067666868677B5F33677D59755F693072 (hex → spam)
3. Reverse sub_7FF603145E00: 提取函数 get2gets
4. PWN glibc2.35: cyclic(0x38) + gets + puts leak libc 0x28c0 → system + ''/bin/sh'' 字符串改造
5. PWN shellcode: openat(-100, ''flag'') + mmap(0x1337000) + writev 读 flag
6. Web easyphp: act() 动态调函数 + sha256 已知 → 文件名 + start_lineno + ''$'' + rtd_key_counter
7. ezphp: ?pw=1&act=%00util_handler_9x/var/www/html/index.php:18$0 → exit 链触发
8. popparser: PHP-Parser 反序列化触发 fOpYG::__destruct → 6 段 chain → system(''cat /fla?'')
9. Spring Java 17 反序列化: Spring AOP + TemplatesImpl + POJONode + EventListenerList + UndoManager + javassist

## 关键 payload

```
Spring AOP JDK17 反序列化: TemplatesImpl + POJONode + EventListenerList + UndoManager
```

## 经验教训

Java 17+ 反序列化要靠 Spring AOP 跨 Module 反射；PHP act() 链很新颖

## 标签

Wireshark、7-bit-decoder、SpamMimic、libc-2.35、gets、openat、PHP-act动态函数、Spring-aop、JDK17、POJONode、TemplatesImpl、JDK17反序列化、跨Module反射

## 参考来源

- https://www.ctfiot.com/281909.html
- 原文件：2025年广西网络与信息安全职业技能竞赛WriteUP.full.md
