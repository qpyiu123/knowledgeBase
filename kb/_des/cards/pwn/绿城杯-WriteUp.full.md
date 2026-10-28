---
title: "绿城杯-WriteUp"
category: pwn
tags: ["绿城杯", "pwn", "off-by-one", "uaf-double-free", "tcache-poisoning", "libc-2.23"]
signals: ["绿城杯 2021", "off-by-one", "uaf-double-free", "tcache-poisoning", "libc-2.23", "one-gadget", "ROP", "ORW", "git-leak", "sqli", "WriteUp", "Web", "warmup", "ezphp"]
difficulty: medium
source: "https://www.ctfiot.com/1058.html"
tools: ["ROP"]
origin: des-import
origin_kind: cards
updated: 2026-10-24
---
# 绿城杯-WriteUp

> 赛事：绿城杯 2021 | 方向：pwn | 难度：medium | 工具：ROP

## 一句话总结

绿城杯WriteUp多方向,Web(warmup ezphp easy_seri)+Pwn(null off-by-one+ezuaf double-free+GreentownNote uaf ORW)。

## 攻击链

1. Web warmup:git信息泄露+SQL注入+eval(system("tac pages/flag.php"))+payload:?link_page=23') or eval(system("tac pages/flag.php"));#
2. Pwn null:off by one+libc-2.23 uaf+tcache攻击+__free_hook=system
3. Pwn ezuaf:double free泄漏cfree后三位+mallochook确定libc 2.23+one_gadget 0x45226
4. Pwn GreentownNote:uaf+堆重叠+tcache bin+__free_hook+open/read/write ORW
5. Web ezphp:phpggc+SQL注入(时间盲注)+AES-CBC解密+RSA低位爆破
6. Web easy_seri:PHP反序列化

## 关键 payload

```
eval(system("tac pages/flag.php")) + one_gadget 0x45226
```

## 经验教训

绿城杯是glibc-2.23时代典型off-by-one+tcache攻击;git信息泄露在Web题中是常见入口;时间盲注+1字节+快速爆破是密码攻击的实用技术。

## 标签

off-by-one、uaf-double-free、tcache-poisoning、libc-2.23、one-gadget、ROP、ORW、git-leak、eval-system、false-file-read

## 参考来源

- https://www.ctfiot.com/1058.html
- 原文件：绿城杯-WriteUp.full.md
