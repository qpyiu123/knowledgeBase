# ez_raabin：先用已知的第三个因子

本地密码题。原附件见 [第二轮清单](../../../eval/r65_real_cases.json)的 `rabin-eight`。本机得到两条模根候选，其中一条是 39 字节明文，并通过完整模数回验。

题目给 `n=p*q*r`、`hint=p*q` 和 `C=m**8 % n`。不用先分解 `hint`：直接算 `r=n//hint`。原附件里这个结果是 512 位素数，且 `r % 4 == 3`。

对这种素数，平方根候选可用 `pow(v,(r+1)//4,r)` 得到。每次有正负两个候选；必须平方回验，因为不是每个数都有平方根。八次幂连续开三次平方即可：

```python
values = {C % r}
for _ in range(3):
    next_values = set()
    for v in values:
        t = pow(v, (r+1)//4, r)
        for x in (t, (-t) % r):
            if x*x % r == v:
                next_values.add(x)
    values = next_values
```

算到的是明文模 `r` 的余数。如果实际明文够短，就可以直接把这些余数当作整数候选；若长度超过素数范围，还要找其他信息。本题逐个检查文本格式，再计算 `pow(x,8,n)`，只有一个候选与完整密文一致。
