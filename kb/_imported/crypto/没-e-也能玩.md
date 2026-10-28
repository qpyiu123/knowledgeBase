---
title: "没 e 也能玩"
category: crypto
tags: [NewStar CTF 2024, wp prose]
signals: [没 e 也能玩]
difficulty: medium
source: "https://github.com/pj-newstar/wiki-docs/blob/1a0f2ba21a30f950276396118b315eef0328371c/docs/wp/2024/week5/crypto/noe.md"
tools: []
origin: imported
origin_id: official-268a64fb7d0db5dcec0705
origin_sha256: 550808d524a3cb158a981de90fcd907fc191cd94451fb742990ffd2db04f656a
origin_event: "NewStar CTF 2024"
origin_kind: wp_prose
license: "MIT"
updated: 2026-10-23
---
# NewStar CTF 2024 / 没 e 也能玩

> 来源：NewStar CTF 2024  |  类型：wp_prose  |  https://github.com/pj-newstar/wiki-docs/blob/1a0f2ba21a30f950276396118b315eef0328371c/docs/wp/2024/week5/crypto/noe.md

# 没 e 也能玩

题目如下：


---

从题目中已知条件有 $c$、$p$、$q$、$d_p$、$d_q$，其中 $d_p$ 和 $d_q$ 由以下公式计算：

$$
\begin{gather}
d_p = d \; \mathrm{mod} \; (p-1) \\
d_q = d \; \mathrm{mod} \; (q-1)
\end{gather}
$$

我们知道RSA解密的时候 $m \equiv c^{d} \pmod n$，即 $m = c^{d} +k\times n$，又 $n=p\times q$

所以 $m = c^{d} + k\times p\times q$，两边对 $p$ 和 $q$ 同时取余，得

$$
\begin{gather}
m_{1} \equiv c^{d} \pmod p \qquad (1) \\
m_{2} \equiv c^{d} \pmod q \qquad (2)
\end{gather}
$$

由最开始计算 $d_p$ 和 $d_q$ 的的式子可以假设存在 $k_1$ 和 $k_2$ 使得

$$
\begin{gather}
d = d_{p}+k_{1}\times (p-1)\\  d = d_{q}+k_{2}\times (q-1)
\end{gather}
$$

由费马小定理（对于任意素数 $p$ 和整数 $a\in Z_{p}$，都有 $a^{p}\equiv a \pmod p$），和 $(1)$ 式，可得

$$
m_{1} \equiv c^{d_{p}+k_{1} \times (p-1)} \equiv c^{d_{p}}\times (c^{k_{1}})^{p-1} \equiv c^{d_{p}} \pmod p
$$

$m_{2}$ 同理，所以

$$
\begin{gather}
m_{1} \equiv c^{d_{p}} \pmod p \qquad (3) \\
m_{2} \equiv c^{d_{q}} \pmod q \qquad (4)
\end{gather}
$$

由 $(1)$ 可得 $m_{1}+x\times p=c^{d}$，将其代入 $(2)$ 式可得

$$
x \times p\equiv (m_{2}-m_{1}) \pmod q \qquad (5)
$$

因为 $\mathrm{gcd}(p,q)=1$，所以存在 $p^{\prime}$ 使得

$$
p \times p^{\prime}\equiv 1 \pmod q
$$

给 $(5)$ 式两边同乘 $p^{\prime}$，有

$$
x \equiv p^{\prime}(m_{2}-m_{1}) \pmod q \qquad (6)
$$

将 $(6)$ 式代入 $m_{1}+x \times p=c^{d}$，可得

$$
m_{1}+p\times \left[ p^{\prime}(m_{2}-m_{1}) \; \mathrm{mod} \; q \right] =c^{d}
$$

即

$$
c^{d}=m_{1}+p \times \left[ p^{\prime}(m_{2}-m_{1}) \; \mathrm{mod} \;q \right]
$$

$m_{1}$ 和 $m_{2}$ 可以通过 $(3)$ 式和 $(4)$ 式得到，这样代进上述式子就可以解出 $m$.

题解如下：
