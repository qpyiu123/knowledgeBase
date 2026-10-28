---
title: "第三届祥云杯决赛 WriteUp"
category: misc
tags: ["祥云杯", "misc", "SoapClient-SSRF", "XXE", "expect", "mp3-bit"]
signals: ["祥云杯 2020", "SoapClient-SSRF", "XXE", "expect", "mp3-bit", "custom-VM", "OLLVM-flatten", "heap-uaf", "thread-chain", "ssrf", "SoapClient", "SSRF", "mp3", "LSB"]
difficulty: medium
source: "https://www.ctfiot.com/135246.html"
tools: ["OLLVM", "PHP"]
origin: des-import
origin_kind: cards
updated: 2026-10-24
---
# 第三届祥云杯决赛 WriteUp

> 赛事：祥云杯 2020 | 方向：misc | 难度：medium | 工具：OLLVM、PHP

## 一句话总结

祥云杯决赛多方向题集：SoapClient SSRF 登录 + XXE expect + mp3 LSB + 自定义 VM + UAF + 线程环形越界 + XOR 密钥 + ORW。

## 攻击链

1. Web1 message_board 用 SoapClient null+location+uri 构造 SSRF 到 127.0.0.1/index.php?s=login 携带 admin:password + PHPSESSID
2. Web2 babyweb 用 XXE + expect://mv$IFSxx.png$IFSxx.php 触发命令执行
3. Misc1 Twin shadow 按 list.txt 偏移从 mp3 逐字节读 LSB 还原 1.txt
4. PWN1 pwn_ad3 自定义 VM 指令 (push/push_r/pop_r/show/again) + show 泄栈堆 + free_hook 写 system
5. PWN2 sitnote UAF + unlink + edit(8, p64(0x6c1ec8)) 篡 fd + tcache 申请到 free_hook
6. PWN3 message_system 0xf 线程环形链路 + show_idx(9, 0xffffffff) 越界读 0x18 字节泄 libc
7. PWN3 续 edit_idx(9, index=0x100000000-0x10, p64(memcpy)+...+system) 触发 ORW 链
8. PWN4 note XOR 密钥登录 + 0x4e0 chunk 重叠泄漏 + 0x4f2 越界读相邻 chunk key + environ 泄栈
9. PWN4 续 ORW open/read/write 直接读 flag 文件

## 关键 payload

```
SoapClient SSRF 头注入 + XXE expect:// + ORW 链 + UAF tcache + 线程环形越界
```

## 经验教训

SOAP SSRF 头注入（user_agent CRLF）+ expect:// 协议是经典 PHP CTF 套路；多线程链路越界通过环形数据流绕过深度限制。

## 标签

SoapClient-SSRF、XXE、expect、mp3-bit、custom-VM、OLLVM-flatten、heap-uaf、thread-chain、memcpy-redirect、ORW、EDISEC

## 参考来源

- https://www.ctfiot.com/135246.html
- 原文件：第三届“祥云杯”网络安全大赛决赛-WriteUp_By_EDISEC.full.md
