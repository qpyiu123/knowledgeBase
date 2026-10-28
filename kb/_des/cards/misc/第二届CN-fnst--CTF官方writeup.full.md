---
title: "第二届CN-fnst--CTF官方writeup"
category: misc
tags: ["CN-fnst--CTF", "misc", "公益CTF", "Misc", "Misc-crypto", "Web-SSTI"]
signals: ["CN-fnst--CTF 2024", "公益CTF", "Misc", "Misc-crypto", "Web-SSTI", "Web-RCE", "Pwn-stack", "Heap", "Sandbox-shellcode", "ssti", "Flask", "SSTI", "canary", "ROP"]
difficulty: medium
source: "https://www.ctfiot.com/219293.html"
tools: ["Flask"]
origin: des-import
origin_kind: cards
updated: 2026-10-24
---
# 第二届CN-fnst--CTF官方writeup

> 赛事：CN-fnst--CTF 2024 | 方向：misc | 难度：medium | 工具：Flask

## 一句话总结

公益赛事998人注册584队参赛,反作弊在某鱼钓鱼执法+14题覆盖Misc隐写音频四象限二进制/Flask SSTI黑名单绕/canary栈溢出ROP/格式化字符串盖got/seccomp openat shellcode/fastbin free_hook/凯撒+图片隐写/UPX脱壳+XOR爆破/RSA yafu/DP泄露/2331位状态DP

## 攻击链

1. 钓鱼执法反作弊→key.html歌词数字提hex→silenteye音频隐写→二十八星宿四象限→玄武00青龙01白虎10朱雀11二进制解flag→Flask SSTI unicode十六进制属性名绕黑名单→canary+ret2libc栈溢出ROP→fmtstr_payload覆盖got→seccomp openat+read+write shellcode→fastbin attack free_hook→凯撒密码1位移→UPX脱壳+XOR key爆破→RSA yafu分解n→dp泄露构造φ→2331位01序列合法状态DP

## 关键 payload

```
flag{BaguA_M4ster_0v0}|{%print g[''pop''][(''_''*2)|attr("x5fx5faddx5fx5f")(''globals'')...%}|b''a''*(0x8*3-1)+b''Z''+p(canary)+prdi+...+p(0x400737)|fmtstr_payload(8, {elf.got["exit"]: p(elf.sym["main"])})+fmtstr_payload(8, {elf.got["printf"]: p(system)})+b''/bin/sh\x00
```

## 经验教训

1) Flask SSTI WAF可读源文件后用十六进制属性名x5fx5faddx5fx5f绕黑名单(''__add__''→''x5fx5faddx5fx5f''); 2) 栈溢出canary末字节必为\x00爆破1字节绕过; 3) fmtstr_payload(offset, {got: value})两步覆盖exit→main循环+printf→system; 4) seccomp禁execve时用openat+read+write纯汇编ORW; 5) tcache下fake_fast布置后backdoor地址前置; 6) RSA已知dp可直接计算p: e*dp ≡ 1 (mod p-1) → p = e*dp - 1 + k*((e*dp-1)//(k+1))... 7) 二十八星宿四象限编码本质是2bit/字符的二进制编码

## 标签

公益CTF、Misc、Misc-crypto、Web-SSTI、Web-RCE、Pwn-stack、Heap、Sandbox-shellcode、RE-XOR、Crypto-RSA

## 参考来源

- https://www.ctfiot.com/219293.html
- 原文件：第二届CN-fnst--CTF官方writeup.full.md
