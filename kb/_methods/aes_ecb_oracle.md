---
title: 方法卡 · AES-ECB 选择明文攻击（模式判别 / cut-and-paste / 逐字节恢复）
category: crypto
tags: [方法卡, aes, ecb, 分组密码, 选择明文, cut-and-paste, byte-at-a-time, oracle]
signals: [题目给出 AES 加密服务并允许任意提交明文, 源码里出现 mode=ECB 或 AES.MODE_ECB, 密文里出现重复的 16 字节分组, 明文由固定的 secret 与用户输入拼接后再加密, 输入长度变化时密文按 16 字节整块增长, 允许上传密文并要求其解密结果含特定字段]
difficulty: medium
source: kb/_imported/crypto/AES.md
tools: [python, pycryptodome, 内置脚本]
updated: 2026-11-03
---

# 方法卡 · AES-ECB 选择明文攻击

## 适用场景

服务端用 **ECB 模式** 加密「`prefix | 用户可控 | secret`」这种拼接串，或允许直接上传密文：

- 源码/流量里能看到 `MODE_ECB`、`mode=ECB`、`AES/ECB/PKCS7`；
- 提交长串重复字符（如 64 个 `A`）后密文里出现**完全相同的分组**；
- 输入长度每增加 1 字节，密文按 16 字节整块跳动（分组边界固定）；
- 目标是伪造 `admin=true` / `role=admin` 这类**位于分组边界上**的字段。

## 前置条件

- 至少能拿到「加密结果」（黑盒）。可以加密任意长度输入、并且每次加密用的是**同一密钥**。
- 加密方式是 ECB：分组之间互不影响，等于把分组当成独立的 16 字节码本。
- 需要伪造的字段能在某次输入里被凑到分组边界上（cut-and-paste 的核心前提）。

## 步骤

1. **判模式**：喂 `A`×64 之类的重复串，检查密文里有没有重复分组。有 → ECB；没有不排除 ECB（前缀短、恰好错位），再多试几个长度。
2. **测前缀长度**：把 `A` 串从 1 涨到 16，观察「第一个重复分组」的位置偏移，算出攻击者可控部分的对齐余数 `prefix_len`，这是逐字节恢复的坐标原点。
3. **cut-and-paste 伪造（有字段场景）**：分别提交 `user=x&admin=false` 与 `user=x&admin=true`，把含 `admin=true` 的密文分组替换进原密文对应的位置——不需要密钥，只要字段块对齐。
4. **逐字节恢复（无字段场景）**：每轮喂 `A^(block-1-i)` 把 secret 的第 i+1 字节顶到分组末尾，本地枚举 256 个候选算出「本应出现的分组」，用一次加密请求比对命中。
5. **收尾**：把恢复出的字节拼起来（`--json` 输出），并去掉末尾 PKCS#7 填充；用一次真实解密/回显核对 flag。

## 立即可用脚本

`kb/_methods/scripts/aes_ecb_oracle.py`（纯标准库，自带 FIPS-197 AES-128，不需要 pycryptodome）：

```bash
# 自检（17 组断言：FIPS-197 向量、往返、ECB 判别、块重排、三种前缀下的逐字节恢复、非法输入拒绝）
python kb/_methods/scripts/aes_ecb_oracle.py --selftest

# 演示：本地起一个 prefix|可控|secret 的 ECB oracle，复现到完整 secret
python kb/_methods/scripts/aes_ecb_oracle.py --demo --secret 'flag{d3m0_ecb}' --prefix 'p' --json
```

导出函数：`expand_key`、`encrypt_block`/`decrypt_block`、`ecb_encrypt`/`ecb_decrypt`、`make_oracle(key, prefix, suffix)`、
`detect_mode(enc)`、`find_repeats(ct)`、`ecb_prefix_length(enc)`、`ecb_byte_at_a_time(enc)`。
接远程服务时把 `enc` 换成一个 `bytes -> bytes` 的回调（发请求、收密文）即可，其余逻辑不动。退出码：`0` 成功、`2` 参数不足/非法。

## 失效场景

1. **不是 ECB**：CBC/CTR/GCM 下分组互相依赖，`detect_mode` 会返回 `cbc-like`，本卡全部招式失效（改看 CBC padding oracle / bit-flip）。
2. **每次加密密钥不同**：逐字节恢复依赖「同一密钥可重复观测」，密钥随机则字典比对永远不命中；表现为第 1 个字节就找不到候选。
3. **前缀长度会变**：若服务在明文中塞入时间戳/随机串，对齐余数每一轮都变，`ecb_prefix_length` 会给出漂移值；必须先找到固定前缀或改用对齐探测每轮重算。
4. **secret 含 PKCS#7 样式字节**：恢复末尾会多出填充字节，脚本按 `body[-n:] == bytes([n])*n` 去填充；若 secret 本身以这样的模式结尾会被误删一个分组的尾部。
5. **oracle 限制长度或过滤字符**：脚本用 `\n` 做对齐补位，若服务拒绝换行/非 ASCII，需换成服务允许的字符（如 `=`、`A`），否则 `ecb_byte_at_a_time` 会在第一轮就抛异常（异常原样上抛，不静默降级）。
6. **仅 128 位密钥**：内置 AES 只实现 128-bit 密钥扩展，`expand_key` 对其它长度直接 `ValueError`；遇到 AES-192/256 服务要么换实现，要么只把它当作黑盒 oracle 使用（攻击本身不需要密钥）。
