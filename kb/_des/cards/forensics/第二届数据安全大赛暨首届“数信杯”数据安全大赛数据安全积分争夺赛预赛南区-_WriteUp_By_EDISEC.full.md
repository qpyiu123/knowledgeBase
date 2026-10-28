---
title: "第二届数据安全大赛暨首届\"数信杯\"数据安全大赛数据安全积分争夺赛预赛南区- WriteUp By EDISEC"
category: forensics
tags: ["数信杯数据安全大赛", "forensics", "应急响应", "内存取证", "Volatility", "Win7SP1x64"]
signals: ["数信杯数据安全大赛 2023", "应急响应", "内存取证", "Volatility", "Win7SP1x64", "SQL盲注", "SSRF", "RC4", "TEA", "forensic_memory", "volatility", "SQL", "like", "binary"]
difficulty: medium
source: "https://www.ctfiot.com/173946.html"
tools: ["Volatility", "binwalk"]
origin: des-import
origin_kind: cards
updated: 2026-10-24
---
# 第二届数据安全大赛暨首届"数信杯"数据安全大赛数据安全积分争夺赛预赛南区- WriteUp By EDISEC

> 赛事：数信杯数据安全大赛 2023 | 方向：forensics | 难度：medium | 工具：Volatility、binwalk

## 一句话总结

6道数据安全题涵盖内存取证(Win7SP1x64 volatility全流程)+SQL盲注双写绕(like binary逐位爆)+Download.php SSRF(#截断)+binwalk音频隐写+RC4+TEA(delta=555885348),末尾EDI招新招re/crypto/pwn方向

## 攻击链

1. 数据分析-不安全的U盘1: volatility_2.6_win64_standalone -f 1.raw --profile=Win7SP1x64 printkey→hashdump→lsadump→cmdline→netscan→filescan grep .toml→获取hahaha123/AcroRd32/192.168.31.238:4444/118.180.126.13:6770/attacker.toml|网站数据绝对安全1/2: livwdaw+EccpSOIlRPolP936707|Bitcoin: transferFrom|Web-justsoso: 双写绕SQL注入 aandnd/passwoorrd+binary like+md5+Download.php?img=http://127.0.0.1/flag.php%23 SSRF|Misc-Magic Audio: binwalk→菜就多练密码解zip→flag|Re-rrrrcccc: SMC+RC4+Whatareyourencryption&decryptionbasics+三段XOR|drink tea: TEA delta=555885348

## 关键 payload

```
volatility...hashdump|hahaha123|flag{49059213-a7e2-4e39-b179-953ae9641063}|flag{61909dd6f4120aac7edb9193491fd83e}|flag{d3db69a34a51d7e1d23d621590827c01}|flag{acb8739759dc496ccc945703037e037f}
```

## 经验教训

1) Volatility内存取证全流程:printkey→hashdump→lsadump→cmdline→netscan→filescan grep; 2) SQL盲注双写绕:aandnd(aand and)/passwoorrd(or)/-- '1闭合; 3) like binary逐字符二分爆; 4) Download.php?img=http://127.0.0.1/flag.php%23用#截断本地路径; 5) RC4加密存在SMC自修改; 6) TEA delta可魔改为任意值(本题555885348=0x21212124),需从IDA反编译识别; 7) binwalk提取嵌入文件+已知密码解zip是音频隐写经典套路

## 标签

应急响应、内存取证、Volatility、Win7SP1x64、SQL盲注、SSRF、RC4、TEA、Crypto、EDI招新

## 参考来源

- https://www.ctfiot.com/173946.html
- 原文件：第二届数据安全大赛暨首届“数信杯”数据安全大赛数据安全积分争夺赛预赛南区-_WriteUp_By_EDISEC.full.md
