---
title: "2022 N1CTF WriteUp By EDISEC"
category: web
tags: ["N1CTF 2022", "web", "N1CTF", "struts2", "WEB-INF", "mtime"]
signals: ["N1CTF 2022 2022", "N1CTF", "struts2", "WEB-INF", "mtime", "md5", "cmd-trace", "WallPaper", "knapsack-LLL", "lfi", "web_unknown", "lattice", "crypto_rsa", "LFI"]
difficulty: hard
source: "https://www.ctfiot.com/71976.html"
tools: ["C", "x86/x64"]
origin: des-import
origin_kind: cards
updated: 2026-10-24
---
# 2022 N1CTF WriteUp By EDISEC

> 赛事：N1CTF 2022 2022 | 方向：web | 难度：hard | 工具：C、x86/x64

## 一句话总结

N1CTF 2022：struts2 LFI + cmd 痕迹 md5 + knapsack lattice + ECDLP

## 攻击链

1. Web Easy_S2: struts2 WEB-INF/classes/com.mycompany.helloword.action/struts.xml + .do 后缀
2. Misc just_find_flag: cmd 痕迹 ''C:\Program Files (x86)\Windows NT\Accessories\flag.zip'' → md5(0d3ba7db468bdbd4f93a88c97ba7bef1) 是密码
3. Crypto Ezdlp: knapsack lattice 攻击 m = matrix(ZZ, len(l), len(l)+1) → LLL 短向量 → GCD 找 n 因子
4. q = 12980311456459934558628309999285260982188754011593109633858685687007370476504059552729490523256867881534711749584157463076269599380216374688443704196597025947 (130-bit)
5. ECDLP: F=GF(q), g=F(0x10001), y 已知 → discrete_log(y, g) 还原 a → flag

## 关键 payload

```
md5('C:\Program Files (x86)\Windows NT\Accessories\flag.zip') = 0d3ba7db468bdbd4f93a88c97ba7bef1
```

## 经验教训

cmd 痕迹 = 取证金矿；knapsack lattice 是经典格密码；ECDLP 130-bit 可用 Pohlig-Hellman

## 标签

N1CTF、struts2、WEB-INF、mtime、md5、cmd-trace、WallPaper、knapsack-LLL、discrete_log、GF(q)、ECDLP、DLP

## 参考来源

- https://www.ctfiot.com/71976.html
- 原文件：2022N1CTF-WriteUp_By_EDISEC.full.md
