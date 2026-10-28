---
title: "GDG Algiers CTF两道矩阵题wp"
category: crypto
tags: ["GDG Algiers CTF", "crypto", "matrix", "diagonalization", "sagemath", "discrete-log"]
signals: ["GDG Algiers CTF 2022", "matrix", "diagonalization", "sagemath", "discrete-log", "poly", "rsa", "aes-cbc", "lwe", "crypto_rsa", "GDG", "Algiers", "CTF", "DLP"]
difficulty: hard
source: "https://www.ctfiot.com/73582.html"
tools: []
origin: des-import
origin_kind: cards
updated: 2026-10-24
---
# GDG Algiers CTF两道矩阵题wp

> 赛事：GDG Algiers CTF 2022 | 方向：crypto | 难度：hard

## 一句话总结

GDG Algiers CTF 2题：矩阵对角化DLP+多项式LWE

## 攻击链

1. 第1题 the_matrix: 12x12矩阵GF(p)对角化
2. D.diagonalization() + A.inverse() * P * A
3. 取对角元素 vD=[37,31,29,...,3,2] vP=[大数...]
4. discrete_log(vP[11], vD[11]) = K
5. SHA256(K)[:256] 作AES key解iv+ciphertext
6. flag: CyberErudites{Di4g0n4l1zabl3_M4tric3s_d4_b3st}
7. 第2题 franklin-last-words: 多项式3*num^3, 3*num^6
8. v2polyv/v2poly2v映射
9. poly_C*V1[0][0] + poly_y*V1[0][1]
10. 爆破字符32-126
11. flag: CyberErudites{Fr4nkl1n_W3_n33d_an0th3R_S3450N_A54P}

## 关键 payload

```
K = discrete_log(G(vP[11]), G(vD[11]))
```

## 经验教训

矩阵对角化可破解特征值加密；多项式+线性方程组可恢复字符

## 标签

matrix、diagonalization、sagemath、discrete-log、poly、rsa、aes-cbc、lwe

## 参考来源

- https://www.ctfiot.com/73582.html
- 原文件：GDG_Algiers_CTF两道矩阵题wp.full.md
