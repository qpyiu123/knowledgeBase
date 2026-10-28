---
title: "THJCC CTF 2026 (部分)"
category: web
tags: ["THJCC CTF", "web", "powershell-ransomware", "aes-cbc", "office2john", "sstv"]
signals: ["THJCC CTF 2026", "powershell-ransomware", "aes-cbc", "office2john", "sstv", "ssrf-whois", "php-write-race", "crypto_oracle", "THJCC", "CTF", "Misc", "Crypto", "Web", "Reverse"]
difficulty: medium
source: "https://www.ctfiot.com/300512.html"
tools: ["C", "PHP"]
origin: des-import
origin_kind: cards
updated: 2026-10-24
---
# THJCC CTF 2026 (部分)

> 赛事：THJCC CTF 2026 | 方向：web | 难度：medium | 工具：C、PHP

## 一句话总结

THJCC CTF 2026 多类 (Misc/Crypto/Web/Reverse/Forensics)：勒索软件 AES 解密 + WhoIS SSRF + 竞争写 WebShell + VM 字节码。

## 攻击链

1. PowerShell Ransomware: key = MD5(UnixTime) + AES-128-CBC + PKCS7
2. header 8 byte unix_time + 16 byte IV + 密文
3. 还原脚本：hashlib.md5(str(unix_time).encode())
4. flag.txt.lock 拿回 flag.txt
5. THJCC{L1nK_R4Ns0mWar3_😭😭😭😭}
6. SSTV 解码：Martin M1 + Robot36
7. POST n=777 拿 THJCC{LUcKy_sEVen_af41404df16be1ff}
8. Apache download.php 路径穿越 ?file=../../../flag.txt
9. PHP 文件写入竞争：php://filter/write=convert.iconv.UTF-16LE.UTF-8/
10. 多 writer+reader 线程 + 0.67s 内必须访问
11. type juggling: 0 == ''admin'' 弱类型比较
12. login.php 接受 '0' 用户名 → indexController 中 foreach 弱比较通过
13. SSRF via whois -h/-p：手工构造 HTTP 请求到 /flag
14. TOTP 硬编码密钥 XOR 解码：Jl5cLlcsI10sKCYhLS40IykpMyQnIF8wIjEtPTM6OzI= ^ 'thjcc
15. Custom C++ Reverse: 42 次循环 XOR key=b"Th1s_1s_th3_k3y
16. Custom VM 4 寄存器 11 指令 (1:mov_imm, 2:read_input, 3:mov_reg, 4:add_reg, 5:add_imm, 6:xor_imm, 7:rol, 8:and_imm, 9:cmp_eq)

## 关键 payload

```
THJCC{L1nK_R4Ns0mWar3_😭😭😭😭}
```

## 经验教训

PowerShell 勒索软件使用 MD5(时间戳) 作 key 时，时间窗口可爆破；AES-CBC + 头部保存时间 + IV 是常见 pattern。

## 标签

powershell-ransomware、aes-cbc、office2john、sstv、ssrf-whois、php-write-race

## 参考来源

- https://www.ctfiot.com/300512.html
- 原文件：THJCC_CTF_2026（部分）.full.md
