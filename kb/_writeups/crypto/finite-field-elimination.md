---
title: "Equation 与 myez_encode：先消去一个变量，再验有限域的根"
category: "crypto"
kind: "writeup"
tags: ["有限域", "四次多项式", "消元"]
signals: ["f=13*y²+x*y+5*x", "g=7*y+x²", "因子位于曲线上"]
source: "https://www.ctfplus.cn/problem-detail/2056307377690382336/description"
origin_id: "r67-finite-field-elimination"
relates_to: ["_writeups/crypto/curve-parameters.md", "_writeups/crypto/groebner-composite.md"]
verification: "本机用附件公开数据回验"
---

# Equation 与 myez_encode：先消去一个变量，再验有限域的根

## 先看这一步

有一条式子能直接解出变量，就先用它消元。有限域求根给出候选，再用原式、整除或字节宽度来筛。

**适用时**：域模数是素数；Equation 的 7 可逆，myez_encode 的原因子要在给出的域范围内。

**留意**：加密指数不可逆时，分别在素数域开根并核对每个候选。

## Equation：先解出两个模幂结果

把两段原文升幂后的结果记作 `x`、`y`。由 `g=7y+x²` 得 `y=(g−x²)/7`（模 `p`）。代入 `f=13y²+xy+5x` 并乘 49，得到 `13(g−x²)²+7x(g−x²)+245x−49f=0`。求所有 `x` 根，逐个重建 `y`，再代回两条公开式。

## myez_encode：把因子关系写成四次式

域模数是大写 `P`；小写 `p,q` 是 RSA 因子。把 `q≡p³+ap+b (mod P)` 乘以 `p`，用 `n=pq` 替代，得到 `p⁴+ap²+bp−n≡0 (mod P)`。只有候选 `p` 真能整除 `n`、算出的 `q` 满足原关系，才保留。若 `p` 可以超过 `P`，域根只是余数，不能直接拿它做因子。

## 怎么回验

Equation 找到 2 对满足原式的模幂结果。分别逆 65537 次幂后，只有一对能按 28+28 字节拼接，转换时保留前导零。myez_encode 得到一对因子；原指数为 9，逐个用完整模数核对 3 个根。

## 配套代码

`kb/_code/r67/case_relations.py`。函数接收题目的公开数值；不会运行题目源码。

## 出处

- [Equation](https://www.ctfplus.cn/problem-detail/2056307377690382336/description)：汇编中的 `题目/ctfplus-2056307377690382336/WP.md`。
- myez_encode：汇编中的 `题目/zhejiang-myez_encode/WP.md`。
