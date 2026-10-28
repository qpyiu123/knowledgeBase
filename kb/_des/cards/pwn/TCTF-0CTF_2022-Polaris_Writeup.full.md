---
title: "TCTF/0CTF 2022 - Polaris Writeup"
category: pwn
tags: ["TCTF/0CTF", "pwn", "smooth-prime", "discrete-log", "babyheap-tcache", "ezvm-pwn"]
signals: ["TCTF/0CTF 2022", "smooth-prime", "discrete-log", "babyheap-tcache", "ezvm-pwn", "libc-2.35", "sage", "pwn_unknown", "TCTF", "CTF", "Polaris", "Crypto", "DLP", "Pwn"]
difficulty: hard
source: "https://www.ctfiot.com/58888.html"
tools: ["Sage"]
origin: des-import
origin_kind: cards
updated: 2026-10-24
---
# TCTF/0CTF 2022 - Polaris Writeup

> 赛事：TCTF/0CTF 2022 | 方向：pwn | 难度：hard | 工具：Sage

## 一句话总结

TCTF/0CTF 2022 Polaris：Crypto 光滑数 DLP + Pwn babyheap 2.35 largebin + ezvm 自定义 VM。

## 攻击链

1. 找 magic 满足 magic_num * 2^(384-LEN*8) + i * 2^(384-LEN*8-16) + 1 全小因子
2. 构造 p+1 光滑
3. primitive_root(n+1) 找生成元
4. sha384 primitive_root 哈希为 num2
5. discrete_log 求 e 满足 g^e = num2 mod (n+1)
6. 输出 P, E, data
7. flag: Hope_you_can_solve_by_smoothness_this_time
8. babyheap: tcache poisoning + largebin attack 拿 libc
9. House of Apple 改 IO_FILE → stack pivot → mprotect RWX → shellcode
10. libc-2.35 IO_validate_vtable 检验 → _IO_wfile_jumps 绕开
11. orw 沙箱读 flag
12. ezvm: 自定义 VM (22/20/21/0/3/9/4/2/1 opcode)
13. 4 阶段 VM 注入 + 内存分配触发 mprotect
14. 偏移 0x2672e0 找 exit_funcs
15. 通过 one_gadget 触发

## 关键 payload

```
n+1 全小因子 (光滑) → Pohlig-Hellman
```

## 经验教训

p+1 光滑时 Pohlig-Hellman 直接降级 DLP；libc-2.35 后 vtable 范围检查使 House of Apple 成为主流绕过。

## 标签

smooth-prime、discrete-log、babyheap-tcache、ezvm-pwn、libc-2.35、sage

## 参考来源

- https://www.ctfiot.com/58888.html
- 原文件：TCTF-0CTF_2022-Polaris_Writeup.full.md
