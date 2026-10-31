---
title: "加法密码"
category: crypto
tags: ["crypto", "helloctf", "hc-skill", "additive-cipher.md", "AES", "隐写", "origin_tag:imported_cats"]
signals: ["crypto", "helloctf", "hc-skill"]
difficulty: medium
source: "https://github.com/ProbiusOfficial/Hello-CTF/blob/8e9d6396a0d1ccc1f606810d575d1abb3dd567de/docs/hc-skill/crypto/additive-cipher.md"
tools: []
origin: imported_cats
origin_id: "helloctf-06fa192bb5a2f5"
origin_domain: "crypto"
origin_family: "helloctf"
origin_event: ""
origin_year: ""
origin_license: "CC-BY-SA-4.0"
origin_attribution: "ProbiusOfficial/Hello-CTF contributors; original at https://github.com/ProbiusOfficial/Hello-CTF/blob/8e9d6396a0d1ccc1f606810d575d1abb3dd567de/docs/hc-skill/crypto/additive-cipher.md"
origin_verification: "source_document_not_reproduced"
origin_content_sha256: "c0aadff3f5a138f9d1a737cbf938468fd989c2e39168b282e1b2c91466438b66"
origin_body_sha256: 5c5f9305c1e5143d5ab16c17cad12f648054e1585640eddc1dfeef0b8d53623d
origin_title: "加法密码"
origin_meta:
  asset_refs: []
  attribution: "ProbiusOfficial/Hello-CTF contributors; original at https://github.com/ProbiusOfficial/Hello-CTF/blob/8e9d6396a0d1ccc1f606810d575d1abb3dd567de/docs/hc-skill/crypto/additive-cipher.md"
  basis: "original_prose_not_runtime_verified"
  chunk_ids: [4610]
  content_sha256: "c0aadff3f5a138f9d1a737cbf938468fd989c2e39168b282e1b2c91466438b66"
  domain: "crypto"
  fetched_at_utc: "2026-10-22T17:55:10.129698+00:00"
  id: "helloctf-06fa192bb5a2f5"
  kind: "licensed_chinese_reference"
  language: "zh"
  license: "CC-BY-SA-4.0"
  license_local_path: "61_中文赛事资料/来源与许可/helloctf/LICENSE.txt"
  local_path: "61_中文赛事资料/开源正文快照/helloctf/docs/hc-skill/crypto/additive-cipher.md"
  response_sha256: "23bb73509db0a9434aebb65e5431d59db43b971a982cd792eb87aec5ccfac717"
  scope_note: "开源中文文档正文。原作者与版本已保留；检索正文省略代码块、缩进代码和图片，完整 Markdown 另存；未复现。"
  source_family: "helloctf"
  source_revision: "8e9d6396a0d1ccc1f606810d575d1abb3dd567de"
  source_url: "https://github.com/ProbiusOfficial/Hello-CTF/blob/8e9d6396a0d1ccc1f606810d575d1abb3dd567de/docs/hc-skill/crypto/additive-cipher.md"
  tags: ["crypto", "helloctf", "hc-skill", "crypto", "additive-cipher.md", "AES", "隐写"]
  title: "加法密码"
  verification_status: "source_document_not_reproduced"
  year: ""
updated: 2026-10-31
---
# 加法密码

> 本文由授权中文赛事 WP 正文导入（阶段 1，仅散文，代码段未导入）。
>
> - 来源：https://github.com/ProbiusOfficial/Hello-CTF/blob/8e9d6396a0d1ccc1f606810d575d1abb3dd567de/docs/hc-skill/crypto/additive-cipher.md
> - 许可：CC-BY-SA-4.0
> - 署名：ProbiusOfficial/Hello-CTF contributors; original at https://github.com/ProbiusOfficial/Hello-CTF/blob/8e9d6396a0d1ccc1f606810d575d1abb3dd567de/docs/hc-skill/crypto/additive-cipher.md
> - 文档族：helloctf
> - 赛事：（无）
> - 年份：（无）
> - 核验状态：source_document_not_reproduced
> - 正文 sha256：c0aadff3f5a138f9d1a737cbf938468fd989c2e39168b282e1b2c91466438b66
> - 导入 ID：helloctf-06fa192bb5a2f5
> - 原 domain：crypto
> - 许可文件：61_中文赛事资料/来源与许可/helloctf/LICENSE.txt
> - 本地快照：61_中文赛事资料/开源正文快照/helloctf/docs/hc-skill/crypto/additive-cipher.md
> - 源修订：8e9d6396a0d1ccc1f606810d575d1abb3dd567de
> - 抓取时间：2026-10-22T17:55:10.129698+00:00
> - 收录说明：开源中文文档正文。原作者与版本已保留；检索正文省略代码块、缩进代码和图片，完整 Markdown 另存；未复现。
> - 判定依据：original_prose_not_runtime_verified

> 原文：https://github.com/ProbiusOfficial/Hello-CTF/blob/8e9d6396a0d1ccc1f606810d575d1abb3dd567de/docs/hc-skill/crypto/additive-cipher.md

## 正文

---
comments: true
---

## 加法密码

> CRYPTO · 知识域。移位类替换:凯撒、ROT13、ASCII 移位。标签:**凯撒密码**、**ROT13**、**ASCII移位**。

## 触发特征

- 明文形似英文但整体"错位";`flag` 变成 `synt`(ROT13)。
- 提示"shift/caesar/位移"。

## 凯撒密码

- 暴力 26 个移位逐一输出,肉眼或词频选正确项。
- 密钥空间小到可以全试;非字母字符通常保留原样。
- 变体:ATBASH(倒序表,属单表但常一起考)、凯撒对 ASCII 全集移位(含符号)。

## ROT13

- 自逆变换(加密=解密);识别最快:字符串里 `n` 多半是 `a`。
- 变体:ROT5(数字)、ROT18(ROT13+ROT5)、ROT47(ASCII 33-126)。

## ASCII移位

- 对整段 ASCII(含标点/数字)统一加 n;解法:`for n in range(128): ''.join(chr((ord(c)+n)%128))`。
- 逐字符不同偏移(如 +i 或斐波那契偏移)→ 找已知明文(`flag{`、`CTF`)差分出偏移序列。
- 图片化变体:像素行/列按 strip 偏移做凯撒,对比原图读出偏移量即 ASCII(BSIDSSF 2026)。

## 转向

- 移位+多表轮换 → [多表替换](polyalphabetic.md);移位藏在图片里 → [Misc-图片隐写](../misc/image-stego.md)
