---
title: "2023 强网杯 WriteUp by Arr3stY0u"
category: misc
tags: ["强网杯 2023", "misc", "RSA_p5", "sage_nth_root", "AES-CFB", "pyModeS"]
signals: ["强网杯 2023 2023", "RSA_p5", "sage_nth_root", "AES-CFB", "pyModeS", "ADS-B", "XTEA", "FSB", "LD_PRELOAD hook", "crypto_rsa", "RSA", "BSGS", "LD_PRELOAD", "phoenixAES"]
difficulty: hard
source: "https://www.ctfiot.com/152049.html"
tools: ["GDB", "Sage"]
origin: des-import
origin_kind: cards
updated: 2026-10-24
---
# 2023 强网杯 WriteUp by Arr3stY0u

> 赛事：强网杯 2023 2023 | 方向：misc | 难度：hard | 工具：GDB、Sage

## 一句话总结

12+ 道题：RSA p^5+BSGS+ADS-B+pyModeS+XTEA+VM+LD_PRELOAD+phoenixAES+ARC4+ISIS 论文题。

## 攻击链

1. not only rsa: n=p^5, e=641747, sage Mod(c,n).nth_root(e, all=True) 找 flag
2. discrete_log: g=5 mod p, c 走 bsgs+padding 反推
3. babyrsa: p,q 共 100 bit kbits 共享，attack2 LLL 攻击 + 二次丢番图方程
4. Speed up: 2^27! 各位数求和
5. 石头剪刀布: AI 学习模式，固定套路试探
6. QAM 流量: wav 4-ary QAM 解调，2-bit/样点映射
7. rockyou AES-CFB: EVP_BytesToKey 派生 key，密文开 HTTP header 检索
8. pyModeS: 1090ES ADS-B 报文 tell() 解析航班号
9. aes_keyschedule: 末轮 key 反推 AES-128 完整 key schedule
10. rc4_license: ARC4("WelcomeToQWB2023") 解密 License.dat
11. fancy: LD_PRELOAD hook clock_gettime + 4-bit 拆分密文爆破
12. 0xGame QAM: scipy 读 wav, -3/-1/1/3 → 00/01/10/11
13. VMP VM: ida 模拟执行 sar/shl/add/cmp VM 指令
14. XTEA 32 轮加密: pwndbg 搜 key 内存，XOR + bswap 解密
15. 论文题 ISIS: fpylll BKZ + g6k Siever 解 SIS 短向量

## 关键 payload

```
n = p^5, e = 641747, c (qwb RSA)
```

## 经验教训

RSA p^5 用 sage nth_root 一步搞定；AES 末轮 key 已知反推完整 key schedule；XTEA 32 轮是入门题标配。

## 标签

RSA_p5、sage_nth_root、AES-CFB、pyModeS、ADS-B、XTEA、FSB、LD_PRELOAD hook、phoenixAES、ARC4、fpylll、ISIS

## 参考来源

- https://www.ctfiot.com/152049.html
- 原文件：2023_强网杯_writeup_by_Arr3stY0u.full.md
