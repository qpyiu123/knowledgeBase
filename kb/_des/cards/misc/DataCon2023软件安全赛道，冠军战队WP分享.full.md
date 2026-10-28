---
title: "DataCon2023软件安全赛道，冠军战队WP分享"
category: misc
tags: ["DataCon 2023", "misc", "metasploit", "cobaltstrike", "shellcode", "shikata_ga_nai"]
signals: ["DataCon 2023 2023", "metasploit", "cobaltstrike", "shellcode", "shikata_ga_nai", "upx", "stager", "smc", "x86-x64", "misc_unknown", "DataCon2023", "Metasploit", "CobaltStrike", "UPX"]
difficulty: hard
source: "https://www.ctfiot.com/150561.html"
tools: ["x86/x64"]
origin: des-import
origin_kind: cards
updated: 2026-10-24
---
# DataCon2023软件安全赛道，冠军战队WP分享

> 赛事：DataCon 2023 2023 | 方向：misc | 难度：hard | 工具：x86/x64

## 一句话总结

DataCon2023软件安全：Metasploit/CobaltStrike shellcode stager分析

## 攻击链

1. 200个Metasploit/CobaltStrike PE样本
2. 6个UPX壳：upx -d脱壳
3. 无Encoder: hash(0x6B8029 WSAStartup)+call ebp
4. IP/端口加载: 32位 0x80BEA8C0→C0A8BE80→192.168.190.128 0x33050002→1331
5. 64位: 0x5c110002→0x115c→4444
6. shikata_ga_nai: 内存特征 xd9x74x24xf4 (fnstenv)
7. fcmovu st,st(1)+fnstenv byte[esp-0Ch]+xor+loop SMC
8. 上百轮自修改解密

## 关键 payload

```
ida_search.find_binary(0, 0xffffffffffffffff, '29 80 6B 00', 16, idc.SEARCH_DOWN)
```

## 经验教训

shikata_ga_nai内存特征xd9x74x24xf4是fnstenv指令

## 标签

metasploit、cobaltstrike、shellcode、shikata_ga_nai、upx、stager、smc、x86-x64

## 参考来源

- https://www.ctfiot.com/150561.html
- 原文件：DataCon2023软件安全赛道，冠军战队WP分享.full.md
