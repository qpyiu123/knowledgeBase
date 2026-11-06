# Factorize：两个素数为什么能从平方根附近分开

0x41414141 CTF 2021 · 密码学 · 原题附件在 [第二轮清单](../../../eval/r65_real_cases.json)的 `rsa-shared-prime-prefix`。本地复现了归档里的固定数据。

生成程序给两个 1024 位素数用同一段高 512 位，分别随机填低位。关键线索是差值小。令 `a=(p+q)//2`、`b=(p-q)//2`，就有 `n=a*a-b*b`。从向上取整的平方根试起，如果 `a*a-n` 正好是一个平方，便能拆出两个因子。

```python
from math import isqrt
a = isqrt(n) + 1
b2 = a * a - n
b = isqrt(b2)
assert b * b == b2
p, q = a - b, a + b
assert p * q == n
```

在本题第一步就成功了。遇到另一题时，先估计差值；需要试的次数大约是 `(p-q)**2 / (8*sqrt(n))`。没有相近的证据，就不要让这个循环一直跑。解密用公钥指数 65537，最后按公开密文回验。

参考：[主办方赛事回顾](https://offshift.io/blog/2021-02-11-the-offshift-0x41414141-ctf-in-review/)、[题目归档](https://pwn.college/ctf-archive/0x41414141ctf2021/)。本文验证的是归档原附件，不使用重托管环境产生的新数据。
