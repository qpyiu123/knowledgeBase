---
title: "GoldenYear"
category: crypto
tags: [UCATFLAGS 2024, wp prose]
signals: [GoldenYear]
difficulty: medium
source: "https://github.com/UCAS-CTF/UCATFLAGS-WP/blob/b1e667240041738bf1361b555b162b5713be315c/wp/crypto/GoldenYear-wp.md"
tools: []
origin: imported
origin_id: official-a820e64e0051a83cd54812
origin_sha256: 390e798dc2b2bcbfb18ca045f2bd48e5a689cacda0c7fa112fd86c3d863084b0
origin_event: "UCATFLAGS 2024"
origin_kind: wp_prose
license: "not_declared"
updated: 2026-10-23
---
# UCATFLAGS 2024 / GoldenYear

> 来源：UCATFLAGS 2024  |  类型：wp_prose  |  https://github.com/UCAS-CTF/UCATFLAGS-WP/blob/b1e667240041738bf1361b555b162b5713be315c/wp/crypto/GoldenYear-wp.md

### 题目源码


### 解题思路

#### ***Point 1***：椭圆曲线基本常识

关注到代码片段：

此处素数模3是一个十分重要的提示，根据有限域上椭圆曲线点群的相关结论，如果素数 $p \equiv 2  \pmod{3}$ ，那么 $ \mathbb{F}_p $ 上形如 $ y^2 = x^3 + C $ 的椭圆曲线的阶一定满足 $ \lvert E(\mathbb{F}_p)\rvert = p + 1 $ 。因此上述代码一定满足下列条件：


证明 $p \equiv 2 \pmod{3}$ 的情况：    
根据熟知的有限域上椭圆曲线点的计算公式（公式依据就是遍历每个 $ x $ ，计算 $ y $ 可以开平方的数量）：    

$$ 
\begin{aligned}
\#E(\mathbb{F}_p) &= 1 + \sum\limits_{k\in\mathbb{F}_p} \left(\left(\dfrac{k^3+c}{p}\right) + 1\right) \\    
&= p + 1 + \sum\limits_{k\in\mathbb{F}_p} \left(\dfrac{k^3+c}{p}\right) \\ 
&= p + 1 + \sum\limits_{k\in\mathbb{F}_p} \left(\dfrac{k}{p}\right) \\ 
&= p + 1 \end{aligned}
$$ 

注：
1. 考虑 $ p \equiv 2\pmod{3} $，不考虑$k = 0$ ，由于 $ k_1 ^ 3 + c = k_2 ^ 3 + c $ $ \Leftrightarrow $ $ k_1 ^ 3 = k_2 ^ 3 $ ，而 $ p - 1 \equiv 1\pmod{3} $ ，根据费马小定理 $ k_1 ^ {p-1} = k_2^{p-1} = 1 $ ，那么 $ k_1 ^ 3 + c = k_2 ^ 3 + c $ $ \Leftrightarrow $ $ k_1^{3\cdot \frac{p-2}{3}} = k_2^{3\cdot \frac{p-2}{3}} $ $ \Leftrightarrow $ $ k_1 = k_2 $ 。因此 $ k^3+c $ 恰好构成 $ p $ 的一个完全剩余系。（听起来高级一点的说法就是 $ x \mapsto x^3 + c $ 为 $ \mathbb{F}_p^{*} $ 上的一个内自同构）    

2. 二次剩余和二次非剩余的数量相等；$0$ 的勒让德符号值为 $0$。

#### ***Point 2***：广度优先搜索+爆破

记 $p_H$ 和 $q_H$ 分别表示 `Happy_2024` 和 `Haqqy_2024` ，$n_H$ 表示 `Hanny_2024` ，另外记 $a$ 和 $b$ 分别表示 `p` 和 `q`     
$p_H, q_H$ 在十进制下可以被写成如下形式：    

$$
\begin{aligned}
p_H &= a_0 + a_1 10 + a_2 10^2 + \cdots \\
q_H &= b_0 + b_1 10 + b_2 10^2 + \cdots
\end{aligned}
$$

记 `f = lambda x: bytes_to_long(str(x).encode())` 为 $f$ 因此 $f(x)$ 就可以写成：

$$ f(x) = (48 + x_0) + (48 + x_1) 256 + (48 + x_2) 256^2 + \cdots $$

根据上一条对于有限域上椭圆曲线点群阶的讨论，不妨设 `Exuberant_p.order() == Happy_2024 + 1` ，记 $ n_g $ 表示这里的 `gift1 = f(Exuberant_p.order() + q) * f(Haqqy_2024 + p)` ，那么就有：

$$
\begin{aligned}
n_H &= p_H \cdot q_H \\
n_g &= f(p_H + 1 + b)\cdot f(q_H + a) \\
\end{aligned}
$$

考虑 $ n_H \equiv (\sum\limits_{j=0}^{i-1} p_j 10^j) \cdot (\sum\limits_{j=0}^{i-1} q_j 10^j) \pmod{10^i} $ 以及 $ n_g \equiv (\sum\limits_{j=0}^{i-1} (48+p_j') 256^j) \cdot (\sum\limits_{j=0}^{i-1} (48+q_j') 256^j) \pmod{256^i} $ 从低到高逐数位恢复即可。    

这里可以使用递推或者递归实现，但是递归实现小心爆栈。

#### ***Point 3***：小密钥空间


根据上述代码可知，列表 `Goldbach_christian` 空间是很小的，因此枚举即可

> 至此已经可以求出两个素数了，下面先给出一部分代码。


#### ***Point 4***：数论变换

这一部分是一个简单的数论变换。记 $p_H$ 和 $q_H$ 分别表示 `Happy_2024` 和 `Haqqy_2024` ，$n_H$ 表示 `Hanny_2024` ，另外记 $\omega_p$ 和 $\omega_q$ 分别表示 `Exuberant_p` 和 `Exuberant_q` ，这些变量现在都已经是已知的了    
那么根据代码片段：
可以整理得到如下表达式：    

$$
c \equiv (p_H \cdot m + \omega_p)^{q_H} + (q_H \cdot m + \omega_q)^{p_H} \pmod{n_H}
$$

注意到 $n_H = p_H \cdot q_H$ ，那么根据费马小定理可以得到如下方程组：    

$$
\begin{cases}
c \equiv \omega_p^{q_H} + q_H \cdot m + \omega_q & \pmod{p_H} \\
c \equiv p_H \cdot m + \omega_p + \omega_q^{p_H} & \pmod{q_H} \\
\end{cases}
$$    

从而有：

$$
\begin{cases}
m_p \equiv q_H ^ {-1} \cdot(c - \omega_p^{q_H} - \omega_q) & \pmod{p_H} \\
m_q \equiv p_H ^ {-1} \cdot(c - \omega_p - \omega_q^{p_H}) & \pmod{q_H} \\
\end{cases}
$$    

最后利用中国剩余定理即可恢复 $m$ 。

这里主要注意一点是前面解出来的小 `p` 和小 `q` 可能顺序不对应，调整一下就好了：


### 完整解题代码
