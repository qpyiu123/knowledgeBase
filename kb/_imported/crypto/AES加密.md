---
title: "AES加密"
category: crypto
tags: [licensed chinese reference]
signals: [AES加密]
difficulty: medium
source: "https://github.com/ProbiusOfficial/Hello-CTF/blob/8e9d6396a0d1ccc1f606810d575d1abb3dd567de/docs/hc-skill/crypto/aes.md"
tools: []
origin: imported
origin_id: helloctf-6c6abba5da1098
origin_sha256: 1e04d149407913043f255bda6eb8baf19fd015eb968538c9ef1a62265ae72bf0
origin_event: ""
origin_kind: licensed_chinese_reference
license: "CC-BY-SA-4.0"
updated: 2026-10-23
---
# AES加密

> 来源：https://github.com/ProbiusOfficial/Hello-CTF/blob/8e9d6396a0d1ccc1f606810d575d1abb3dd567de/docs/hc-skill/crypto/aes.md

---
comments: true
---

# AES加密

> CRYPTO · 知识域。AES 四种模式与实现层攻击。标签:**CBC**、**ECB**、**OFB**、**CFB**。

## 触发特征

- 16 字节块、模式提示、加解密 oracle(服务端返回 padding 错误/解密结果)。

## ECB

- **模式识别**:重复明文块 → 重复密文块;加密图片可见轮廓(像素级 ECB 去重视觉还原,BackdoorCTF 2017)。
- **逐字节选择明文**:受控前缀 + 目标逐字节入同一块,256 查询/字节恢复(ABCTF 2016;工具 FeatherDuster `ecb_cpa_decrypt`)。
- **块剪切粘贴**:重排/复制密文块伪造字段(`is_admin:true` 块注入)。

## CBC

- **位翻转**:改前一块密文翻转下一块明文对应位(无 MAC 时直接改 cookie 权限位,Google CTF 2016)。
- **IV 伪造 + 块截断**:XOR IV 改块 0;MAC 嵌在密文流内时截尾块绕过完整性(0CTF 2017)。
- **padding oracle**:字节级改前块测 padding → 逐字节恢复解密中间态(~4096 查询/块,PadBuster);进阶链:padding oracle 解密 + CBC 位翻转注命令实现 RCE(BSIDSSF 2017)。
- **错误消息 oracle**:服务端把解密字节回显在报错里 → 零块学习中间态逐块伪造密文(Nuit du Hack CTF 2018)。
- **UnicodeDecodeError 侧信道**:解码错误位置泄露字节信息(2017 CTF)。
- **块边界对齐去 nonce**:按块边界对齐让 CBC 退化成 ECB 类比较(2018 CTF 变体)。

## OFB

- 密钥流独立于密文:RNG 状态可逆时**反向运行**恢复前序密钥流(BSIDSSF 2026)。
- 密钥流重复(计数器/IV 复用)→ 多次一密;DES 弱密钥下 OFB 周期 2(Boston Key Party 2016)。

## CFB

- CFB-8 静态 IV:16 字节已知明文后可重建内部状态继续加密/解密(2017 CTF)。
- **时间种子 IV**:IV 来自时间戳 PRNG → 枚举种子恢复 IV → 位翻转(CFB IV 恢复,2017)。

## 实现/密钥层

- **S 盒魔改**:非双射(`len(set(sbox))<256`)→ 4097 次查询恢复密钥(2016)。
- **字节清零 oracle**:密钥槽索引整数溢出 → 逐字节清零暴力(256 次/字节,共 4096,Confidence CTF 2017)。
- **密钥派生弱**:`SHA256(pubkey)⊕seed`(BSIDSSF 2026);密钥短(≤4 字节)直接爆。
- **GCM nonce 复用**:CTR 密钥流复用 + GHASH 认证密钥多项式恢复(nonce-disrespect)。
- **缩减轮 AES**:4 轮积分(square attack):256 明文 λ 集,末轮密钥字节 XOR 和=0 区分器猜密钥(0CTF 2016);简化 Ascon 差分同思路。
- **密钥流协议复合**:AES-CTR + CRC32 GF(2) 线性签名伪造(2018)。
- `GF(2)` 消元:线性哈希(XOR+旋转)直接高斯消元。

## 工具速查


## 转向

- 密钥/IV 来自 PRNG → [LCG](lcg.md)/[MT19937](mt19937.md);DES 专属 → [DES](des.md)

## 例题

### Padding Oracle 逐字节解密

服务端告知 padding 是否合法时,改前块逐字节恢复中间值(约 4096 次/块):


工具:PadBuster、`padding-oracle` 库。进阶组合:解密 + CBC 位翻转注命令(BSIDSSF 2017)。

### ECB 逐字节选择明文(ABCTF 2016)

服务端加密 `user_input || secret`,ECB 同块同密文——控制前缀长度把 secret 逐字节推进块尾比对:


 FeatherDuster 的 `cryptanalib.ecb_cpa_decrypt()` 可全自动。成本:每字节 ≤256 次查询。

### GCM nonce 复用(forbidden attack)

同 nonce 两次 = CTR 密钥流复用 + GHASH 认证密钥可恢复,明文与认证同时崩:


工具:[nonce-disrespect](https://github.com/nonce-disrespect/nonce-disrespect) 全自动。另:nonce 只有 1-4 字节且密钥已知时直接暴力枚举 nonce。

### ECB 剪切粘贴伪造会话(NDH Quals 2016)

JSON 会话按 ECB 加密、`is_admin: false` 跨块可预测:先用重复注册名(如 `'A'*64`)确认 ECB(出现重复密文块)→ 变长探测块边界 → 用空格 padding 把 `true` 对齐到块首 → 拼接密文块完成伪造。JSON 忽略空白是关键配合。
