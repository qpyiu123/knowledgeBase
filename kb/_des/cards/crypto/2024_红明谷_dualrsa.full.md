---
title: "红明谷 2024/dualrsa"
category: crypto
tags: ["红明谷", "crypto", "RSA", "eval", "LSB Oracle", "gmpy2.iroot"]
signals: ["红明谷 2024", "RSA", "eval", "LSB Oracle", "gmpy2.iroot", "双层 RSA", "整数根求解", "crypto_rsa", "lsb_oracle", "rce", "RCE", "LSB", "Oracle", "flag"]
difficulty: hard
source: "https://www.ctfiot.com/172261.html"
tools: ["Python", "gmpy2"]
origin: des-import
origin_kind: cards
updated: 2026-10-24
---
# 红明谷 2024/dualrsa

> 赛事：红明谷 2024 | 方向：crypto | 难度：hard | 工具：Python、gmpy2

## 一句话总结

83 次方根求 RCE 字符串 + eval 触发 + LSB Oracle 还原 flag

## 攻击链

1. 审计 RSASystem 类发现 encrypt/decrypt 接受字符串
2. encrypt/decrypt 内部 try: pow(eval(m), e, n) 存在 eval 漏洞
3. eval 被限制，只能短字符串触发
4. 构造 b"__import__('os').system('ls')" + \xff 填充到 512 字节
5. 走 83 次方根（外层 RSA e=83）求 m
6. 提交 m 让服务端 encrypt 后转字符串触发 eval
7. 利用 LSB Oracle（选项 3 + decrypt）逐字节还原 flag

## 关键 payload

```
rce = b"__import__('os').system('ls')" + b'\xff' * (512 - len(rce)); m = gmpy2.iroot(bytes_to_long(rce), 83)[0]
```

## 经验教训

RSA 加密函数中 eval 漏洞用 iroot 求整数根构造可执行 Python 字节；LSB Oracle 配合多步签名链路还原明文

## 标签

RSA、eval、LSB Oracle、gmpy2.iroot、双层 RSA、整数根求解

## 参考来源

- https://www.ctfiot.com/172261.html
- 原文件：2024_红明谷_dualrsa.full.md
