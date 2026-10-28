---
title: "2024 巅峰极客挑战赛-初赛 Write_up"
category: web
tags: ["巅峰极客", "web", "FastAPI 内存马", "exec 模块注入", "symlink TOCTOU 竞争", "ECDSA 线性组合 nonce 恢复"]
signals: ["巅峰极客 2024", "FastAPI 内存马", "exec 模块注入", "symlink TOCTOU 竞争", "ECDSA 线性组合 nonce 恢复", "RSA 多 k 爆破", "哈希流密码", "symlink 抢占", "ssti", "rce", "ecdsa", "crypto_rsa", "FastAPI", "symlink"]
difficulty: hard
source: "https://www.ctfiot.com/200261.html"
tools: []
origin: des-import
origin_kind: cards
updated: 2026-10-24
---
# 2024 巅峰极客挑战赛-初赛 Write_up

> 赛事：巅峰极客 2024 | 方向：web | 难度：hard

## 一句话总结

FastAPI 内存马 + symlink TOCTOU + ECDSA 线性组合 + 多 k 爆破 + 哈希流密码逐位爆破。

## 攻击链

1. 1. EncirclingGame: FastAPI 内存马 exec() + app.add_api_route /x → /x?x=cat /flag / 2. GoldenHornKing: ssti 无回显 → FastAPI 内存马 add_api_route / 3. sandbox: symlink 竞速 - 20 线程 symlink /usr/bin/mkdir → /sandbox/12345678/phpcode → 改写 phpcode 为 /bin/sh → 执行反弹 / 4. backdoorplus: ECDSA z = (k1 - w*t)*G + (-a*k1 - b)*Y → k1G 已知 → 推 z.x() → k2 = sha1(z.x()) → 99 次 next_prime 拿 p / 5. cipher: hash+XOR 流密码 → 已知 64 字节块加密 3 字符 (前 2 + 新 1) → 逐位爆破

## 关键 payload

```
app.__init__.__globals__['__builtins__']['exec'](code) ; symlink("/usr/bin/mkdir", "/sandbox/.../phpcode") ; z = k1G - w*G - a*x*k1G - b*x*G ; k2 = int(sha1(str(z[0])).hexdigest(), 16) ; next_prime x99
```

## 经验教训

ECDSA nonce k 线性组合时已签名点线性组合 → 还原私钥；symlink 攻击通过并发改写 phpcode 路径。

## 标签

FastAPI 内存马、exec 模块注入、symlink TOCTOU 竞争、ECDSA 线性组合 nonce 恢复、RSA 多 k 爆破、哈希流密码、symlink 抢占

## 参考来源

- https://www.ctfiot.com/200261.html
- 原文件：2024巅峰极客挑战赛-初赛Write_up.full.md
