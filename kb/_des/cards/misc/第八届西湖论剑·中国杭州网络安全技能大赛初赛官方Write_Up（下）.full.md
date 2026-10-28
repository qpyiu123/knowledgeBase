---
title: "第八届西湖论剑·中国杭州网络安全技能大赛初赛官方Write Up(下)"
category: misc
tags: ["西湖论剑", "misc", "Disk取证-compressed", "Zstandard", "COM_UnMunge2解码", "AES-CBC+HMAC"]
signals: ["西湖论剑 2025", "Disk取证-compressed", "Zstandard", "COM_UnMunge2解码", "AES-CBC+HMAC", "PWN-babytrace", "Heaven's door-32/64切换+proc-mem,Vpwn-栈溢出-edit高地址,RE-BitDance位重排", "shellcode", "MISC", "img", "RSA", "AES-CBC", "HMAC", "COM_UnMunge2"]
difficulty: hard
source: "https://www.ctfiot.com/226338.html"
tools: []
origin: des-import
origin_kind: cards
updated: 2026-10-24
---
# 第八届西湖论剑·中国杭州网络安全技能大赛初赛官方Write Up(下)

> 赛事：西湖论剑 2025 | 方向：misc | 难度：hard

## 一句话总结

第八届西湖论剑下半:MISC糟糕的磁盘(5张img合并)→RSA+AES-CBC+HMAC+COM_UnMunge2解码UDP stream→secret.pcapng|PWN-babytrace(int3+pop rax+add rsp,0x78 ret读/flag)+Heaven's door(32/64切换+open /proc/pid/mem+lseek+write)+Vpwn(StackVector.edit高32/低32写64位ROP)|RE-BitDance(767位BitDanceDecode box位重排)

## 攻击链

1. MISC-糟糕的磁盘: img1-5 gSoNiXLC/uGZ85OzT/m8X4exzG/Fsiq6lKn/suPVGqm6顺序合并|CSCS: 5张img合并+RSA+已知p/q(差6)+AES-CBC+HMAC-SHA256+COM_UnMunge2(XOR+LongSwap+表)→secret.pcapng|Heaven''s door: i386 32位shellcode + retfq切64位 + open /proc/{pid}/mem + lseek + write madain_heaven|BitDance: 767位BitDanceDecode box[223,64,650,...]位重排|新CSCS: AES-128-CBC(b''abcdefghijklmnop'') + HMAC验证|PWN-babytrace: int3(0x1723F8)+pop rax链+add rsp,0x78 ret + read /flag|Vpwn: StackVector.show+edit索引18-25写32位+32位高地址拼64位ROP

## 关键 payload

```
img1..5 合并|sha256(AES_key + HMAC_key) = hashlib.sha256(raw_aes_keys).digest()|int3+pop rax(0x1723F8)+call j_strncmp+setz al+jmp add rsp,8 ret|rop_chain=p64(rdi)+p64(0)+p64(rsi)+p64(write_able)+p64(rdx)+p64(8)+p64(read)+...+p64(int3)+p64(stack+0x200)|bit_box[223,64,650,471,493,580,763,459,754,349,...] 767位|edit(18, pop_rdi&0xffffffff) edit(19, (pop_rdi>>32)&0xffff)
```

## 经验教训

1) 磁盘取证合并:多img按特定顺序(gSoNiXLC等)合并为完整磁盘; 2) COM_UnMunge2算法:=XOR seq→_LongSwap(c)→XOR ~seq→4字节内j循环表mungify_table2; 3) Heaven's door:32位shellcode入口+retfq+CS 0x33切换64位+open /proc/{pid}/mem+lseek(SEEK_SET,made_in_heaven)+write shellcode; 4) babytrace:libc-2.35 int3+pop rax+add rsp,0x78 ret; 5) Vpwn:StackVector 64位地址分两次写(低32+高32)+edit(18..25)对应位置; 6) BitDance:BitDanceDecode用box[223,64,650,...]做位重排,cipher[0]>>7取srcBit,循环count=len*8次

## 标签

Disk取证-compressed、Zstandard、COM_UnMunge2解码、AES-CBC+HMAC、PWN-babytrace、Heaven's door-32/64切换+proc-mem,Vpwn-栈溢出-edit高地址,RE-BitDance位重排

## 参考来源

- https://www.ctfiot.com/226338.html
- 原文件：第八届西湖论剑·中国杭州网络安全技能大赛初赛官方Write_Up（下）.full.md
