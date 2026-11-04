---
title: 方法卡 · RSA padding oracle（parity/LSB 递推、Manger 倍增、同态绕过）
category: crypto
tags: [方法卡, rsa, padding_oracle, lsb_oracle, parity, manger, bleichenbacher, 同态, pkcs1v15]
signals: [服务端对"填充是否合法"返回不同响应, 题目给了解密 oracle 只回一位, 密文可被任意乘同态改造, 响应时间或长度泄露填充信息, e 很小且 n 高于明文若干位, 明文只有几百位、n 有上千位]
difficulty: hard
source: kb/_imported/crypto/RSA.md
tools: [python, 内置脚本]
updated: 2026-11-03
---

# 方法卡 · RSA padding oracle（parity/LSB 递推、Manger 倍增、同态绕过）

## 适用场景

站点或题目只把"填充是否合法"泄露出来，却把明文锁在密文里。典型形态有三种：
parity/LSB oracle（只回"明文是否奇数"）、区间 oracle（只回"明文是否小于阈值 M"）、
以及干脆"只拒绝部分密文"的粗粒度 oracle。三者都靠 RSA 的乘法同态
`c · f^e mod n ↔ m · f mod n`，把一次解密变成一串带噪声的比较。

> 判定信号：交互次数与 n 的位数同一量级（说明信息量来自比较而非穷举）、
> 每次响应的差异很小（一位或一个分支）、密文可以自由乘 `f^e` 而不报错。

## 前置条件

- 能反复查询 oracle，且知道 n、e；不需要 d。
- 关键约束：**倍增后的明文不能绕回 n**。parity 递推和 Manger 都默认
  `T·m < n`，因此要求 `n` 比明文所在区间大若干倍（本卡要求 `2M <= n`，
  M 为判定阈值 2^k_bits）。若 `n` 与 M 同量级，弧线（wrap）会污染每次回答，
  算法会失败——这是本题族最常见的"理论上能打、实际打不动"。
- 明文可以被同态改造后仍被接受（否则先做同态绕过，见第 3 条路径）。

## 步骤

1. **先确认 oracle 语义**。拿一个已知合法密文和几个随机密文各问一次，
   观察响应差异落在哪一位：奇偶、阈值比较、还是"合法/非法"二值。
2. **parity/LSB 路径**（本卡首选，最稳）。令 `S_{k+1} = 2·S_k mod n`，
   `b_k = [2·S_k >= n]`。n 为奇数时 `S_{k+1}` 的奇偶恰好等于 `b_k`，
   于是一次查询拿到一个 wrap 位。展开闭式：

   ```
   2^T·m = n·M + S_T,   M = Σ_{k<T} b_k·2^{T-1-k},   0 <= S_T < n
   ```

   取 `T = n.bit_length()`，则 `m` 落在宽度 n 的窗口
   `[n·M/2^T, (n·M + n)/2^T]` 里，窗口内逐个 `pow(m, e, n) == c` 复验即可。
   **不要**把 wrap 位串直接当 m 的二进制——两者只共享高位。
3. **Manger/区间路径**。oracle 只回"m < M"时：f=2,4,8,… 倍增直到首次
   回答 False，得 `m ∈ [M/f1, M/(f1/2))`；之后每轮以中点取
   `f = M//mid + 1`，回答 True 即 `m <= M//f`，据此缩区间。
   注意可用的 `f` 只有 n 以内那么多个，区间会被"整块阈值"卡住，
   所以 `M` 相对 n 越小越好；卡住时如实报错，不要用暴力扫描兜底。
4. **同态绕过**。若 oracle 直接拒绝目标密文，试 `c·r^e`（r=2,3,…，需
   `gcd(r,n)=1`），解出 `r·m mod n` 后乘 `r^{-1}` 还原。本卡脚本的
   `homomorphic_bypass` 就是这条：它只返回 `pow` 复验通过的结果。
5. **收尾**：任何路径最终都必须 `pow(m, e, n) == c` 复验；不通过就判失败，
   把所有"候选"当结论是本题族里最常见的假绿。

## 脚本

```bash
python kb/_methods/scripts/rsa_padding_oracle.py --selftest
python kb/_methods/scripts/rsa_padding_oracle.py --n 1208925819847725639805843 \
    --e 3 --c 12345 --lsb
```

`parity_oracle_decrypt(n, e, c, oracle, bits=None)`：oracle 接收密文、返回明文最低位。
`manger_decrypt(n, e, c, k_bits, oracle)`：oracle 返回"明文 < 2^k_bits"。
`homomorphic_bypass(n, e, c, decrypt)`：decrypt 抛 ValueError 表示被拒。
`pkcs1v15_valid(m, n)`、`int_root(n, k)`、`inv_d(p, q, e)` 为辅助函数。

## 失效场景

1. **明文所在区间与 n 同量级**：倍增立刻绕回 n，`S_T` 窗口不再包含 m，
   parity 递推会把区间推到错误位置。表现为候选区间落在 m 附近但差几格。
   修法是让题目里的 M（阈值）远小于 n，或改用多 oracle 组合。
2. **oracle 有次数限制或对 f 有白名单**：倍增路径需要 O(log n) 次查询，
   一旦被限流，只能改用同态绕过 + 单次猜测。
3. **响应噪声**：若填充判定有随机延迟/随机失败，"非法"与"合法"混叠，
   先把同一查询重复多次取众数，再进入递推；否则每条错误回答都会污染公式。
4. **oracle 语义与假设不符**：oracle 回的是"解密成功"而不是"明文 < M"
   时，Manger 的倍增阶段永远回答 True（或永远 False），函数会在倍增上限处
   报错——这是设计上的拒绝，不是 bug。
