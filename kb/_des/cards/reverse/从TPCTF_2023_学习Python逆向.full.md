---
title: "从TPCTF 2023学习Python逆向"
category: reverse
tags: ["TPCTF 2023", "reverse", "Python逆向", "AES", "Cython", "IDA重建"]
signals: ["TPCTF 2023 2023", "Python逆向", "AES", "Cython", "IDA重建", "PyObject", "big num", "HITPCTF", "pycdc", "reverse", "TPCTF", "nanoPyEnc", "AES-ECB", "maze"]
difficulty: medium
source: "https://www.ctfiot.com/149063.html"
tools: ["IDA", "Python"]
origin: des-import
origin_kind: cards
updated: 2026-10-24
---
# 从TPCTF 2023学习Python逆向

> 赛事：TPCTF 2023 2023 | 方向：reverse | 难度：medium | 工具：IDA、Python

## 一句话总结

TPCTF 2023 nanoPyEnc AES-ECB + maze Cython 编译产物 IDA 符号重建。

## 攻击链

1. nanoPyEnc: enc 列表 48 字节先 XOR 1 再 AES-ECB 解密 key=''2033-05-18_03:33
2. maze: Cython 编译产物 IDA base=0x44960 重建 PyObject*/PyTypeObject* 数组
3. create_qword + SetType + set_name 还原符号 ys, ns
4. 还原 MazeLang 类 (TWF6ZUxhbmc) 含 add_function/cell/step/get_pos/op/__init__/__repr__
5. 还原 check c29sdmU(SvL6VEBRwx) 比对 33 字节
6. 反变换 aW5pdF9zZWNyZXQ 走 EqdU3uQNCi 33 元素排列置换 c2VjcmV0
7. key='HITPCTF' XOR c2VjcmV0[i] 取后 33 字节

## 关键 payload

```
HITPCTF XOR c2VjcmV0[i] 33 字节解
```

## 经验教训

Python 字节码逆向先识别编译方式 (CPython .pyc, Cython, PyInstaller, Nuitka)，Cython 编译产物的 PyObject 数组可通过 IDA Python 重建；AES-ECB 短密钥直接字典/已知时间戳爆破。

## 标签

Python逆向、AES、Cython、IDA重建、PyObject、big num、HITPCTF、pycdc、maze

## 参考来源

- https://www.ctfiot.com/149063.html
- 原文件：从TPCTF_2023_学习Python逆向.full.md
