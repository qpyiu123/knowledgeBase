---
title: "ACTF 2026 WriteUp By F1ux"
category: crypto
tags: ["ACTF", "crypto", "inverse pow", "128-bit定点扫描", "Decimal高精度", "pydoc.builtin不拦截"]
signals: ["ACTF 2026", "inverse pow", "128-bit定点扫描", "Decimal高精度", "pydoc.builtin不拦截", "help('secret')泄flag", "低指数RSA广播", "QuadraticField虚数域", "max_order", "crypto_rsa", "ACTF", "Crypto", "inverse_pow", "jail"]
difficulty: hard
source: "https://www.ctfiot.com/307824.html"
tools: ["C", "Python", "Sage"]
origin: des-import
origin_kind: cards
updated: 2026-10-24
---
# ACTF 2026 WriteUp By F1ux

> 赛事：ACTF 2026 | 方向：crypto | 难度：hard | 工具：C、Python、Sage

## 一句话总结

ACTF 2026 — 5 道 Crypto (inverse_pow + jail help('secret') + 低指 RSA 广播 + QuadraticField+decimal sqrt + TenSEAL CKKS 同态 rank) + Misc Farthest2026 DOSEMU2 DJ64 loader + SUID cat。

## 攻击链

1. Crypto1 inverse_pow: 128-bit 定点 C helper 扫描 + Decimal Python 复核
2. Crypto2 jail: eval 没禁 builtins, help(''secret'') 触发 pydoc DATA 区打印 secret.py FLAG
3. Crypto3 低指数 RSA 广播: Pand√ra 给 Sage, 反推 p ≡ 3 mod 4
4. Crypto4: QuadraticField(-p, ''w'') + max_order OK, Oq = K.order([1, (Δq+q*K.gen())/2])
5. 输出 (A>>360, B, decimal_part_of_sqrt(p*q^2)) 反推 45 字节 token
6. Crypto5 Arrange in Ascending: TenSEAL CKKS 加密 128 元素 Base, 同态计算 rank
7. round(answer[i]) == sorted(Base).index(Base[i]) → 用 Galois key 旋转
8. rank = #j < i + (#j > i, sign 区分) - 1, 加法+密文乘密文+rescale
9. Misc Farthest2026: DOSEMU2 DOS 环境 cat 加 SUID, dos 不可直接读 /flag
10. 走 DJ64 loader: 构造 R.COM 调 int 0e6h al=60h ah=01h dx=0005h
11. 改 R.ELF 为 fake MZ 头 (0x86=STFLG1_NO32PL|SHM_EXCL|SHM_NEW_NS)
12. dj64init_once() 内 fork+execve /usr/bin/cat /flag 重定向到 /home/dos/.dosemu/drive_c/OUT.TXT
13. VNC 上传: copy con A.TXT (hex) + g.com decoder + R.ELF

## 关键 payload

```
TenSEAL CKKS rank 同态 / QuadraticField + decimal sqrt 反推 / DJ64 STFLG1_NO32PL|SHM_EXCL|SHM_NEW_NS / SUID cat / DOSEMU2
```

## 经验教训

pydoc DATA 区会打印模块源 (help('secret') 非预期读 flag);TenSEAL CKKS 即使无 secret key 也可同态计算（仅用 public+galois）;DOSEMU2 DJ64 loader 是非预期 host exec 入口;STFLG1_NO32PL+SHM_NEW_NS 组合是关键。

## 标签

inverse pow、128-bit定点扫描、Decimal高精度、pydoc.builtin不拦截、help('secret')泄flag、低指数RSA广播、QuadraticField虚数域、max_order、decimal_part_of_sqrt、TenSEAL CKKS、同态计算rank、Galois key旋转、sign近似、DOSEMU2、DJ64 loader、comcom64 stubless、STFLG1_NO32PL|SHM_EXCL|SHM_NEW_NS、VNC上傳hex+decoder、/usr/bin/cat SUID

## 参考来源

- https://www.ctfiot.com/307824.html
- 原文件：ACTF2026_WriteUp_By_F1ux.full.md
