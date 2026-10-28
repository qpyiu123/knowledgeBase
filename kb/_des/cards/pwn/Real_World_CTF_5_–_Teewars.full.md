---
title: "Real World CTF 5 - Teewars (Teeworlds) Writeup"
category: pwn
tags: ["Real World CTF 5", "pwn", "teeworlds", "map-file", "cdatafile-format", "zlib"]
signals: ["Real World CTF 5 2022", "teeworlds", "map-file", "cdatafile-format", "zlib", "env-point", "integer-overflow", "rop", "execve", "pwn_unknown", "Real", "World", "CTF", "Teewars"]
difficulty: hard
source: "https://www.ctfiot.com/91481.html"
tools: ["ROP"]
origin: des-import
origin_kind: cards
updated: 2026-10-24
---
# Real World CTF 5 - Teewars (Teeworlds) Writeup

> 赛事：Real World CTF 5 2022 | 方向：pwn | 难度：hard | 工具：ROP

## 一句话总结

Real World CTF 5 Teewars (Teeworlds) 自定义 map 文件 CDataFile 格式 Envelope_Points 整数除法溢出 + 写 ROP 链到 bss 触发 execve /bin/sh -c "cat /home/rwctf/flag"。

## 攻击链

1. Teeworlds (DDNet) 自定义 CDataFile 格式: header(40) + item_types + item_offsets + data_offsets + data_sizes + items + zlib deflate data
2. 头 40 字节: aID[4]="DATA" + Version + Size + Swaplen + NumItemTypes + NumItems + NumRawData + ItemSize + DataSize
3. CDatafileItem m_Type: Version=0/Info=1/Image=2/Envelope=3/Group=4/Layer=5/Envelope_Points=6
4. Envelope_Points 解析: m_Size/sizeof(CEnvPoint) 数组 + POINT_VERSION
5. CEnvPoint m_Time + m_Curvetype + m_aValues[4] 22.10 fixed point
6. 漏洞: envelope channel 数量 + 数组 size 计算溢出
7. 准备 prepared.map 复制 start + 改 num_channels
8. 攻击: 改 0x24c 偏移 4 字节 = (len(rop_chain) + 0x90) / 4 整数除法
9. 复制 items 0x250-0x750+0x90 + ROP chain 覆盖 buffer
10. ROP: pop rdi 0x6c0000 bss + pop rax argv strings + mov [rdi],rax + execve 59
11. 完整 chain: 写 argv[0]="/bin/sh" + argv[1]="-c" + argv[2]="cat /home/rwctf/flag" → execve("/bin/sh", argv, 0)
12. 服务端: rwctf 5 - Teewars 服务器崩溃后 crash 分析

## 关键 payload

```
0x45f135 mov qword ptr [rdi], rax; ret + rop.rax + rop.rdi + rop.rsi + rop.rdx + rop.syscall
```

## 经验教训

自定义二进制文件格式 (CDataFile) 解析时整数除法溢出是经典漏洞 (size/count → 负数 → 后续 memcpy 越界)；Teeworlds/DDNet 引擎 ROP 利用 bss 段写入 argv 是无 shellcode 场景必备。

## 标签

teeworlds、map-file、cdatafile-format、zlib、env-point、integer-overflow、rop、execve、ctf-pwn

## 参考来源

- https://www.ctfiot.com/91481.html
- 原文件：Real_World_CTF_5_–_Teewars.full.md
