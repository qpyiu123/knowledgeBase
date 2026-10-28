---
title: "香港網安奪旗賽HKCERT CTF 2024 Write up（下）"
category: misc
tags: ["HKCERT CTF 2024", "misc", "RSA-LCG", "multiprime-rsa", "pty-disassembly", "Proxy-handler"]
signals: ["HKCERT CTF 2024 2024", "RSA-LCG", "multiprime-rsa", "pty-disassembly", "Proxy-handler", "XOR-stream", "jsc-pyc", "z3-constraint", "pyc-decompile", "crypto_rsa", "HKCERT", "Proxy", "pyc", "seed"]
difficulty: hard
source: "https://www.ctfiot.com/221684.html"
tools: ["Z3"]
origin: des-import
origin_kind: cards
updated: 2026-10-24
---
# 香港網安奪旗賽HKCERT CTF 2024 Write up（下）

> 赛事：HKCERT CTF 2024 2024 | 方向：misc | 难度：hard | 工具：Z3

## 一句话总结

HKCERT 2024下篇涵盖RSA-LCG多线程爆破+几何序列求根+Proxy隐写+数组置换+未知加密z3约束+pyc反编译,密码学综合难度顶级。

## 攻击链

1. 多线程爆破RSA-LCG seed: bits=128 LCG (a,c已知) 生成4个1024位素数p0-p3做multiprime RSA
2. 第二阶段用nth_root(4, all=True)求S0初始种子+反推LCG恢复p0
3. ISA 101 PTY空白字符IFS Proxy隐写通过Proxy has trap触发eval
4. 数组映射XOR: array+array2置换+array3^num→去除x01→还原字节
5. 未知加密算法用z3约束3个未知数(s0+s1+s2=300, 2s0+s1+2s2=496, s0+3s1+s2=508)
6. sser.pyc反编译识别AES-CFB + sha256(nonce+pw)做key+IV

## 关键 payload

```
hkcert24{c0mpu71n9_subs3qu3nc3s_0f_g30m3tr1c_s3qu3nc3s_1s_fun}
```

## 经验教训

LCG生成RSA素数时,若bits小且seed少,可用nth_root或暴力搜索重建;未知加密不要硬逆,先列方程组用SMT求解;pyc反编译在CTF中是必备技能(使用pycdc/pylingual)。

## 标签

RSA-LCG、multiprime-rsa、pty-disassembly、Proxy-handler、XOR-stream、jsc-pyc、z3-constraint、pyc-decompile、SMT、weak-encryption

## 参考来源

- https://www.ctfiot.com/221684.html
- 原文件：香港網安奪旗賽HKCERT_CTF_2024_Write_up（下）.full.md
