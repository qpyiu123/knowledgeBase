---
title: "Social Engineering To Solve A Crypto Challenge – LakeCTF 2022"
category: crypto
tags: ["LakeCTF", "crypto", "pgp-rsa", "protonmail-lookup", "social-engineering", "key-recovery"]
signals: ["LakeCTF 2022", "pgp-rsa", "protonmail-lookup", "social-engineering", "key-recovery", "crypto_rsa", "LakeCTF", "Crypto", "ProtonMail", "API", "PGP", "epfl-ctf-admin2", "protonmail", "com"]
difficulty: medium
source: "https://www.ctfiot.com/59629.html"
tools: []
origin: des-import
origin_kind: cards
updated: 2026-10-24
---
# Social Engineering To Solve A Crypto Challenge – LakeCTF 2022

> 赛事：LakeCTF 2022 | 方向：crypto | 难度：medium

## 一句话总结

LakeCTF 2022 社工 + Crypto：通过 ProtonMail API 公开查询接口拿到 PGP 公钥用于后续攻击。

## 攻击链

1. 知道收件人 epfl-ctf-admin2 @protonmail.com
2. 调 ProtonMail API https://api.protonmail.ch/pks/lookup?op=get&search={user}@protonmail.com
3. 下载公钥 pub
4. gpg --list-packets --verbose 解析公钥
5. 拿到 sub key packet v4 algo 1 (RSA)
6. e = 010001 (标准 65537)
7. n = 0x B1CF59A37A81DA78...DC3
8. 检查 n 是否可分解 (FactorDB)
9. 假定 n 是 1024-bit 标准 RSA 但因 social 攻击已知部分信息
10. 攻击者拿到 mail 转发后尝试用 admin 凭据重发
11. social engineering 拿私钥 → 离线解密 PGP

## 关键 payload

```
requests.get("https://api.protonmail.ch/pks/lookup?op=get&search=epfl-ctf-admin2@protonmail.com")
```

## 经验教训

任何 PGP 公钥服务器都允许陌生人拉取目标公钥；私钥安全完全依赖持有者。

## 标签

pgp-rsa、protonmail-lookup、social-engineering、key-recovery

## 参考来源

- https://www.ctfiot.com/59629.html
- 原文件：Social_Engineering_To_Solve_A_Crypto_Challenge_–_LakeCTF_2022.full.md
