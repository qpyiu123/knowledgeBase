---
title: 方法卡 · ECDSA/EdDSA nonce 重用与偏置 nonce 恢复私钥
category: crypto
tags: [方法卡, ecdsa, nonce, 签名, hnp, 偏置nonce, eddsa, secp256k1]
signals: [两次签名 r 相同, 签名是 (r s) 二元组, k 只有低位随机, nonce 偏置, 源码里 k = getrandbits(128), 签名接口可重复调用, 曲线是 secp256k1, 给了 d 的部分比特]
difficulty: hard
source: kb/crypto/ecdsa-nonce-reuse-lattice.md, kb/crypto/lattice-lll.md
tools: [python, 内置脚本]
updated: 2026-11-03
---

# 方法卡 · ECDSA/EdDSA nonce 重用与偏置 nonce

## 适用场景

题面给出一串签名 `(r, s)`（通常附 `z = H(msg)` 的整数形式）和曲线参数，要求恢复私钥 `d`：

- **nonce 重用**：两条签名的 `r` 一模一样 → 直接消元，一条公式出 `d`，这类题 90% 到这一步就结束。
- **偏置 nonce**：`k` 只有低位随机（`k < 2^bias`、或高位恒为 0、或高位已知），单条不够、多条联立就行——
  这就是隐藏数问题（HNP）。
- **EdDSA**：`S = k_ephemeral + r·s`，重用 ephemeral 同样能解出私钥，`n` 要换成 Ed25519 的阶 `L`。

## 前置条件

- 已知曲线阶 `n`（secp256k1 是常量，Ed25519 的 `L` 与它**不同**，套错就全错）。
- 已知每条签名的 `z`：注意题目可能用 `sha256(msg)` 的高 256 位、可能 `>> 8` 截断，差一位就解不出。
- nonce 重用路径只要 2 条签名；偏置 nonce 路径要 ≥3 条（第 3 条起用于交叉验证，防假阳）。
- 偏置位宽 `bias_bits` 要能从源码里读出来，别猜。

## 步骤

1. 把所有 `(r, s, z)` 收集成列表，先 `Counter(r)` 查重复——有重复立刻走联立。
2. nonce 重用：`k = (z1 - z2)·(s1 - s2)^{-1} mod n`，再 `d = (s1·k - z1)·r^{-1} mod n`。
3. 偏置 nonce：每条签名满足 `k_i = (z_i + r_i·d)·s_i^{-1} mod n`，且 `0 < k_i < 2^bias`。
   - 规模小时（bias ≤ 20 位左右）直接枚举 `k_0`，由 `d = (s_0·k_0 - z_0)·r_0^{-1}` 得候选，
     再用其余签名反解 `k_i` 检查是否都落在界内；
   - 规模大时构造 HNP 格（`u_i = r_i·s_i^{-1}`，`t_i = -z_i·s_i^{-1}`，格上带 `n` 的对角块 + 目标行），
     用 LLL/fpylll 约化，`d ≈ |v[m]|·n/B`；**提取公式必须和构造配套**。
4. 无论哪条路径，最后都用 `Q = d·G` 或"反解出的 k 全部落在界内"复核，然后才去伪造签名。

## 立即可用脚本

`kb/_methods/scripts/ecdsa_nonce_reuse.py`（纯标准库，无 Sage、无网络）：

```bash
# 1) 直接给两条 r 相同的签名
python kb/_methods/scripts/ecdsa_nonce_reuse.py --r <R> --s1 <S1> --z1 <Z1> --s2 <S2> --z2 <Z2>

# 2) 给签名列表（JSON：[{r,s,z},...]），自动先查 r 重复
python kb/_methods/scripts/ecdsa_nonce_reuse.py --sigs sigs.json

# 3) 偏置 nonce：k < 2^20，三条以上签名
python kb/_methods/scripts/ecdsa_nonce_reuse.py --sigs sigs.json --bias-bits 20 --max-k 1048576

# 4) 自检（6 组断言，约 2 秒）
python kb/_methods/scripts/ecdsa_nonce_reuse.py --selftest
```

退出码：`0` 成功；`2` 参数不足/非法；`1` 数据不满足任何一条假设（如实报失败）。

## 失效场景

1. **`s1 == s2` 或 `z1 == z2`**：消息相同或 nonce 是确定性派生的，两式无法消元，脚本报错退出，需要再找一条独立签名。
2. **偏置位宽太大或太小**：`bias_bits` 给小了会退化成"无解"，给大了枚举空间直接爆炸；确定性枚举上限 60 位，超过就必须上 LLL/fpylll（本脚本不含，避免"看着能跑其实解不出"）。
3. **`z` 的截断方式弄错**（高位截断 vs 低 8 位截断 vs `int.from_bytes` 端序）：所有公式都会解出乱码私钥，务必先对齐源码，再用第 3 条签名交叉验证。
4. **曲线阶套错**：Ed25519 用 secp256k1 的 `n`、或反过来，`pow(s, -1, n)` 一步就崩或给出无意义的 `d`。
5. **`s` 与 `n` 不互素**：`pow(s,-1,n)` 抛异常，说明签名数据被篡改，不要强行继续。
6. **只看"解出一个数"就算成功**：多解、假解很常见，必须用 `k` 的界或 `Q == d·G` 复核；脚本里的"防假阳"用例专门钉住这一条。
