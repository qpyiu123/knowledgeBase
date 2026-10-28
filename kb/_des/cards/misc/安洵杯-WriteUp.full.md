---
title: "安洵杯 WriteUp - ChaMd5 Venom"
category: misc
tags: ["安洵杯", "misc", "ThinkPHP5", "Phar反序列化", "Windows_pipes", "Tupper自指公式"]
signals: ["安洵杯 2021", "ThinkPHP5", "Phar反序列化", "Windows_pipes", "Tupper自指公式", "CRC32反推", "时间盲注", "SSRF", "SemCms", "ssrf", "ChaMd5", "Venom", "Web", "Misc"]
difficulty: hard
source: "https://www.ctfiot.com/13958.html"
tools: ["Python"]
origin: des-import
origin_kind: cards
updated: 2026-10-24
---
# 安洵杯 WriteUp - ChaMd5 Venom

> 赛事：安洵杯 2021 | 方向：misc | 难度：hard | 工具：Python

## 一句话总结

ChaMd5 Venom安洵杯全方向:Web反序列化/Misc CRC32+Tupper/Pwn SROP+chunk合并+FSOP。

## 攻击链

1. Web1:Phar反序列化触发think\process\pipes\Windows→toString→Request::hook→system(cat+/y0u_f0und_It) → Web2:sem-cms时间盲注(sql注入X-Forwarded-For)+Ant_Curl SSRF(http://sem-cms.cn@ip绕过) → Misc1:crc32碰撞6段密码(th1s_I/s_Y0ur/_pa33w/0rd_We/1c0m3...) → Misc2:Tupper自指公式k=1251077...渲染bitmap → Pwn1 ezstack:SROP+canary_leak+elf_base+pop_rdi+binsh → Pwn2 noleak1:chunk_0x100+0x80合并+show泄露libc+__free_hook→system → Pwn3:house of orange+global_max_fast扩展+unsorted_bin attack+_IO_list_all+system

## 关键 payload

```
Phar(thin\process\pipes\Windows) + crc32 reverse + Tupper k=1251077... + SROP canary+elf_base + chunk合并+__free_hook + FSOP _IO_list_all attack
```

## 经验教训

ThinkPHP5 Phar反序列化windows\process\pipes\Windows链触发Request::system;CRC32碰撞用crc32.py reverse已知前4字符反推剩余;时间盲注X-Forwarded-For控制client_ip;http://user@host绕过URL解析;SROP用SigreturnFrame构造所有寄存器;chunk 0xf8+0xf8合并0x100+0x80可泄露unsorted_bin指针;house of orange用top_chunk伪造unsorted_bin触发_IO_list_all。

## 标签

ThinkPHP5、Phar反序列化、Windows_pipes、Tupper自指公式、CRC32反推、时间盲注、SSRF、SemCms、SROP、canary_leak、heap_overflow、global_max_fast、unsorted_bin、FSOP、_IO_list_all、ChaMd5_Venom

## 参考来源

- https://www.ctfiot.com/13958.html
- 原文件：安洵杯-WriteUp.full.md
