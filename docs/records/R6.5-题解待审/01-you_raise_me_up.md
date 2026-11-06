# you_raise_me_up：从模幂结果还原指数

网鼎杯 2020 青龙组 · 密码学 · 2026-11-06 在 [DASCTF 练习页](https://ctf2.dasctf.com/dashboard/practice/b9bbb32f-f186-458f-b90b-12440c0f6aea?tab=challenges&challenge=5ee6edd2-4fc9-46c9-b6b1-44e5fa5ca197) 提交，站点显示回答正确。

## 先看未知量在哪

打开压缩包里的 Python 文件，读取注释中给出的底数和结果。题目要找的是指数：已知奇数底数 `g` 和余数 `c`，找 `x` 使 `g**x % (2**512) == c`。这叫离散对数：在取余的情况下反过来找指数。

## 从模 2 算起

在模 2 下，奇数的任意次幂都是 1。先记指数代表 `x=0`、周期 `order=1`。每把模数翻倍，检查 `g**order` 在新模数下是否仍等于 1：

- 仍等于 1，周期不变，核对原来的 `x` 即可。
- 不等于 1，周期翻倍。上一步只知道指数余数，所以新的一位只有两种：`x` 或 `x+order`，保留与 `c` 匹配的那个。

```python
def solve(g, c, bits):
    assert g % 2 == c % 2 == 1
    x, order = 0, 1
    for i in range(2, bits + 1):
        modulus = 1 << i
        if pow(g, order, modulus) != 1:
            if pow(g, x, modulus) != c % modulus:
                x += order
            order *= 2
        assert pow(g, x, modulus) == c % modulus
    return x.to_bytes((x.bit_length() + 7) // 8, "big")
```

本题算出的周期是 `2**510`，最小非负指数转成大端字节后就是可提交答案。大端的意思是把最高位字节放在最前面。验证时用完整的 `2**512` 回算，不能只在较小模数下检查。

参考：[参赛者的离散对数解法](https://www.cnblogs.com/vict0r/p/13298370.html)。本文用逐位还原的方法复现，不需要运行题目源码。
