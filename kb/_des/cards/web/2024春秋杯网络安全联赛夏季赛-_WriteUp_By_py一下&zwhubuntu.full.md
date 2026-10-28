---
title: "2024 春秋杯夏季赛 WP（py一下&zwhubuntu 视角：Hijack / ezecc / Signatrue / 2024happy）"
category: web
tags: ["2024 春秋杯网络安全联赛夏季赛", "web", "ENV/DIFF/FILE/FUN POP 链", "Hijack LD_PRELOAD 绕 disable_functions", "brother 反弹 MySQL udf", "ezecc ECC 256bit p=gcd 求曲线参数+爆破 k"]
signals: ["2024 春秋杯网络安全联赛夏季赛 2024", "ENV/DIFF/FILE/FUN POP 链", "Hijack LD_PRELOAD 绕 disable_functions", "brother 反弹 MySQL udf", "ezecc ECC 256bit p=gcd 求曲线参数+爆破 k", "Signatrue DSA LCG nonce 复用 HNP 格", "2024happy N^2+2024 Coppersmith + HSSP 正交格", "deserialize", "sqli", "rce", "ecdsa", "crypto", "web", "Hijack"]
difficulty: hard
source: "https://www.ctfiot.com/193435.html"
tools: []
origin: des-import
origin_kind: cards
updated: 2026-10-24
---
# 2024 春秋杯夏季赛 WP（py一下&zwhubuntu 视角：Hijack / ezecc / Signatrue / 2024happy）

> 赛事：2024 春秋杯网络安全联赛夏季赛 2024 | 方向：web | 难度：hard

## 一句话总结

春秋杯夏季赛三大 crypto + 一 web：Hijack LD_PRELOAD + ezecc gcd 求 ECC 曲线 + Signatrue DSA nonce 复用 HNP 格 + 2024happy N^2 Coppersmith + HSSP 正交格；全是密码学与 POP 链硬菜。

## 攻击链

1. Hijack: ENV.__toString → putenv LD_PRELOAD + system
2. 拿 shell → 找 mysql 凭据 → udf 提权
3. ezecc: 已知 a,b, K=(G=k*G 公开) → p = gcd(f1, f2) 求曲线素数
4. k 私钥 < 1e6 爆破 → m = C1 - k*C2, cipher_left/invert(m[0])%p = flag 前半
5. Signatrue: DSA 8 次签名, 同 nonce 复用 → HNP 格 A=R[i]*s0/(r0*S[i]), B=(r0*H[i]-R[i]*h0)/(r0*S[i])
6. 构造 Ge = [q*I; A; B; 0 0 K 1]，BKZ-30 → 还原 d, 重签 admin
7. pass_proof 爆破 2^19 大小写
8. 2024happy: N=n^2+2024, hint=(3^2022 p^2 + 5^2022 q^2) mod N, Coppersmith 还原 p,q
9. 4x4 LLL 矩阵 [[1,0,Ta*2^pbit,0],[0,1,Tb*2^qbit,0],[0,0,TN,0],[0,0,T*hh,N]] 找 p,q
10. AES-CBC key 解出 (key=mylove_in_summer)
11. HSSP part2: 31 个 As, 80 维 binary vectors xs, M=256bit, B=As*xs % M
12. find_ortho_fp kernel_LLL → recoverBinary all_ones {-1,0,1} → 求 As
13. AES IV=sha256(sum(As)).digest()[:16]

## 关键 payload

```
p = gcd(G[0]^3 + a*G[0] + b - G[1]^2, c1[0]^3 + a*c1[0] + b - c1[1]^2)
```

## 经验教训

ezecc 的关键观察是 "K = (..., 4359... : 4359...) K = (G, kG)，求 p 时所有点代入曲线方程再 gcd" 一步出 p；Signatrue 用 A,B 矩阵构造 LLL 求 d 是教科书 HNP；2024happy 把 RSA 与 HSSP 拼接是密码学综合题经典套路。

## 标签

ENV/DIFF/FILE/FUN POP 链、Hijack LD_PRELOAD 绕 disable_functions、brother 反弹 MySQL udf、ezecc ECC 256bit p=gcd 求曲线参数+爆破 k、Signatrue DSA LCG nonce 复用 HNP 格、2024happy N^2+2024 Coppersmith + HSSP 正交格

## 参考来源

- https://www.ctfiot.com/193435.html
- 原文件：2024春秋杯网络安全联赛夏季赛-_WriteUp_By_py一下&zwhubuntu.full.md
