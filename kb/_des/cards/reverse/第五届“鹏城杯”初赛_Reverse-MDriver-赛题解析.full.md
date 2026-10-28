---
title: "第五届\"鹏城杯\"初赛 Reverse-MDriver-赛题解析"
category: reverse
tags: ["鹏城杯", "reverse", "Windows驱动", "WFP", "FWPS_CLASSIFY", "MSR"]
signals: ["鹏城杯 2025", "Windows驱动", "WFP", "FWPS_CLASSIFY", "MSR", "KiSystemCall64", "KUSER_SHARED_DATA", "ICMP", "RC4-XOR", "reverse", "callout", "ClassifyFn", "MSR_LSTAR", "Key1"]
difficulty: hard
source: "https://www.ctfiot.com/291134.html"
tools: ["C", "Python"]
origin: des-import
origin_kind: cards
updated: 2026-10-24
---
# 第五届"鹏城杯"初赛 Reverse-MDriver-赛题解析

> 赛事：鹏城杯 2025 | 方向：reverse | 难度：hard | 工具：C、Python

## 一句话总结

鹏城杯2025 WFP callout驱动逆向,ClassifyFn识别WFP过滤ICMP,MSR_LSTAR读KiSystemCall64前4字节作Key1,KUSER_SHARED_DATA.NtSystemRoot="C:\WINDOWS" UTF-16LE异或(~i)生成Key2,密文双key异或解flag,Python SOCK_RAW发ICMP包触发驱动

## 攻击链

1. 1. 识别ClassifyFn为WFP callout驱动函数→rdmsr C0000082获取MSR_LSTAR=fffff801`0c211900→KiSystemCall64前4字节0f 01 f8 65作key1(4字节循环)|2. 读取KUSER_SHARED_DATA.NtSystemRoot="C:\WINDOWS" UTF-16LE 20字节→v4[i]^=(~i)&0xFF 256次异或生成key2|3. 密文v41 20字节cipher=payload[i]=cipher[i]^key2[i]^key1[i%4]|4. 触发: Python socket SOCK_RAW IPPROTO_ICMP发包payload=go_to_find_the_flag!→驱动ICMP包匹配触发

## 关键 payload

```
msr[c0000082] = fffff801`0c211900|0f 01 f8 65(key1)|seed_str="C:\WINDOWS" seed_bytes=seed_str.encode('utf-16le')[:0x14]|v4[i] ^= (~i) & 0xFF for i in range(256)|cipher=[0xD4,0x90,0x60,0xED,...]|key2=[0xBC,0xFE,0xC7,0xFC,...]|p=c^k2^k1|socket.SOCK_RAW socket.IPPROTO_ICMP|flag{Y0r_Ar3_W1nKern3l_Mas7er!*}
```

## 经验教训

1) WFP驱动ClassifyFn签名识别:(const FWPS_INCOMING_VALUES0*, const FWPS_INCOMING_METADATA_VALUES0*, void*, const void*, const FWPS_FILTER1*, UINT64, FWPS_CLASSIFY_OUT0*); 2) MSR C0000082(MSR_LSTAR)读KiSystemCall64前4字节作为密码key1; 3) KUSER_SHARED_DATA.NtSystemRoot(0x30偏移)固定存系统目录"C:\WINDOWS" UTF-16LE格式,加密key素材; 4) Python socket SOCK_RAW IPPROTO_ICMP直接发ICMP包触发驱动callout; 5) 驱动级逆向思路:从filter/classify函数入手定位算法,MSR+共享数据是常见数据源

## 标签

Windows驱动、WFP、FWPS_CLASSIFY、MSR、KiSystemCall64、KUSER_SHARED_DATA、ICMP、RC4-XOR

## 参考来源

- https://www.ctfiot.com/291134.html
- 原文件：第五届“鹏城杯”初赛_Reverse-MDriver-赛题解析.full.md
