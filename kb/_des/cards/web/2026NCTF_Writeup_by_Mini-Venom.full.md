---
title: "2026 NCTF Writeup by Mini-Venom（Blind SSTI + 连分数 Wiener 攻击）"
category: web
tags: ["2026 NCTF", "web", "NCTF 2026", "BlindSSTIExploit 时延盲注", "cycler.__init__.__globals__.os.popen sleep 5", "字符集 {}_- + ascii + digits"]
signals: ["2026 NCTF 2026", "NCTF 2026", "BlindSSTIExploit 时延盲注", "cycler.__init__.__globals__.os.popen sleep 5", "字符集 {}_- + ascii + digits", "N-RustPICA SPA js 源码泄露", "/api/admin/templates/review-flow", "anime_admin/purestream 凭据", "连分数 e/N^6 展开 收敛分母 d", "ssti", "crypto_rsa", "web_unknown", "jwt", "NCTF"]
difficulty: hard
source: "https://www.ctfiot.com/304798.html"
tools: ["C"]
origin: des-import
origin_kind: cards
updated: 2026-10-24
---
# 2026 NCTF Writeup by Mini-Venom（Blind SSTI + 连分数 Wiener 攻击）

> 赛事：2026 NCTF 2026 | 方向：web | 难度：hard | 工具：C

## 一句话总结

2026 NCTF Web: Blind SSTI 时延盲注 + N-RustPICA js 源码泄露 + Wiener 攻击 + GAME 五子棋协议走棋拿 flag。

## 攻击链

1. Blind SSTI: cycler.__init__.__globals__.os.popen(''sleep 5'').read() → 时延判 RCE
2. find_flag_path: test -f /flag && sleep delay
3. get_length: [ $(wc -c < /flag) -eq N ] && sleep delay
4. extract_char: [ "$(cut -c POS /flag)" = ''C'' ] && sleep delay
5. N-RustPICA: js 源码泄露 /api/admin/templates/review-flow 接口
6. anime_admin / purestream 凭据
7. 读取 N, e, c → 连分数 e/N^6 展开 → 收敛分母 d
8. 验证 pow(pow(2, e, N), d, N) == 2 → d 正确
9. m = c^d mod N
10. GAME 协议 Magic=0x47414D45 → 五子棋协议
11. 7 选 7: payload = "%d,%d" 走棋
12. 5 选 5: 随机匹配对手 → 赢了 N 次 拿 flag

## 关键 payload

```
Wiener 攻击：e/N^6 连分数展开 → 收敛分母 d
```

## 经验教训

Blind SSTI 时延盲注模板: `sleep N` 判 RCE → find_flag_path → wc -c 算长度 → cut -c 提字符；RSA Wiener 攻击 `e/N^k` 连分数展开（k=6 是 N-RustPICA 变种）。

## 标签

NCTF 2026、BlindSSTIExploit 时延盲注、cycler.__init__.__globals__.os.popen sleep 5、字符集 {}_- + ascii + digits、N-RustPICA SPA js 源码泄露、/api/admin/templates/review-flow、anime_admin/purestream 凭据、连分数 e/N^6 展开 收敛分母 d、Wiener 攻击 RSA 小 d、GAME 协议 Magic 0x47414D45

## 参考来源

- https://www.ctfiot.com/304798.html
- 原文件：2026NCTF_Writeup_by_Mini-Venom.full.md
