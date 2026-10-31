---
title: "NewStar CTF 2025 / CBC 之舞"
category: crypto
tags: ["NewStar CTF 2025", "CBC 之舞", "crypto", "官方资料", "docs/wp/2025/week3/crypto/cbc-dance.md", "origin_tag:imported_cats"]
signals: ["NewStar CTF 2025", "CBC 之舞", "crypto"]
difficulty: medium
source: "https://github.com/pj-newstar/wiki-docs/blob/1a0f2ba21a30f950276396118b315eef0328371c/docs/wp/2025/week3/crypto/cbc-dance.md"
tools: []
origin: imported_cats
origin_id: "official-520eded3d58f8ed9a02d92"
origin_domain: "crypto"
origin_family: "official_event_archive"
origin_event: "NewStar CTF 2025"
origin_year: 2025
origin_license: "MIT"
origin_attribution: ""
origin_verification: "official_source_not_reproduced"
origin_content_sha256: "46be4dee7413a0e557e883b20d933f502314ccca596eac91129f31092e378579"
origin_body_sha256: 1b76af3fb37cef73f9ad5d1bd64f89aed5cae81806a714cd36a733465996e649
origin_title: "NewStar CTF 2025 / CBC 之舞"
origin_meta:
  asset_refs: []
  basis: "original_prose_not_runtime_verified"
  challenge_key: "newstar:docs/wp/2025/week3/crypto/cbc-dance"
  chunk_ids: [10885]
  content_sha256: "46be4dee7413a0e557e883b20d933f502314ccca596eac91129f31092e378579"
  domain: "crypto"
  domain_basis: "repository_path"
  event: "NewStar CTF 2025"
  external_links_not_followed: 0
  id: "official-520eded3d58f8ed9a02d92"
  kind: "official_wp_prose"
  language: "zh"
  license: "MIT"
  local_path: "62_官方赛事题库/objects/9c635cbfcf977170ce9d1d70c3952c5f79e3bfadedad4c82b8d4cbfeda80441e.blob"
  official_evidence: "https://newstar.wiki/wp/2024/"
  original_path: "docs/wp/2025/week3/crypto/cbc-dance.md"
  revision: "1a0f2ba21a30f950276396118b315eef0328371c"
  scope_note: "官方发布来源的说明正文；代码单独索引，未运行或分析。按文件收录，不把多份文件算作多道题。图片及附件下载状态见清单；仅按路径/原题分类标方向，binary 等跨方向资料留待分类。"
  source_family: "official_event_archive"
  source_url: "https://github.com/pj-newstar/wiki-docs/blob/1a0f2ba21a30f950276396118b315eef0328371c/docs/wp/2025/week3/crypto/cbc-dance.md"
  tags: ["NewStar CTF 2025", "CBC 之舞", "crypto", "官方资料", "docs/wp/2025/week3/crypto/cbc-dance.md"]
  title: "NewStar CTF 2025 / CBC 之舞"
  verification_status: "official_source_not_reproduced"
  year: 2025
updated: 2026-10-31
---
# NewStar CTF 2025 / CBC 之舞

> 本文由授权中文赛事 WP 正文导入（阶段 1，仅散文，代码段未导入）。
>
> - 来源：https://github.com/pj-newstar/wiki-docs/blob/1a0f2ba21a30f950276396118b315eef0328371c/docs/wp/2025/week3/crypto/cbc-dance.md
> - 许可：MIT
> - 署名：（未提供）
> - 文档族：official_event_archive
> - 赛事：NewStar CTF 2025
> - 年份：2025
> - 核验状态：official_source_not_reproduced
> - 正文 sha256：46be4dee7413a0e557e883b20d933f502314ccca596eac91129f31092e378579
> - 导入 ID：official-520eded3d58f8ed9a02d92
> - 原 domain：crypto
> - 本地快照：62_官方赛事题库/objects/9c635cbfcf977170ce9d1d70c3952c5f79e3bfadedad4c82b8d4cbfeda80441e.blob
> - 源修订：1a0f2ba21a30f950276396118b315eef0328371c
> - 收录说明：官方发布来源的说明正文；代码单独索引，未运行或分析。按文件收录，不把多份文件算作多道题。图片及附件下载状态见清单；仅按路径/原题分类标方向，binary 等跨方向资料留待分类。
> - 判定依据：original_prose_not_runtime_verified

> 原文：https://github.com/pj-newstar/wiki-docs/blob/1a0f2ba21a30f950276396118b315eef0328371c/docs/wp/2025/week3/crypto/cbc-dance.md

## 正文

---
titleTemplate: ":title | WriteUp - NewStar CTF 2025"
---

## CBC 之舞

这道题是一个基于 AES-CBC 模式的加密题目，CBC 是「密码块链接」模式。

其特点是：每个明文块在加密前会先与前一个密文块进行异或（XOR），第一个块则与初始化向量（IV）进行异或。如果密文块顺序被打乱，解密时会导致明文块错位，从而可能泄露信息。

我们已知以下数据：

我们已知以下数据：

值得注意的是，`c1` 是 `c2` 的四个块经过某种置换（permutation）后得到的。

相关代码如下：

观察后不难发现：

观察后不难发现：

即 `perm = [3, 0, 2, 1]`。

CBC 模式中的解密过程为：

利用 CBC 的解密公式，可以建立 `m1` 与 `c1`、`c2` 之间的关系，从而还原 `m2` 的内容。

核心解密公式如下：

而 `AES_Decrypt(c2[i])` 实际上可以表示为 `m1[j] XOR c1[k]` 的形式，通过置换关系可以一一对应。

最终推导出四个 m2 块：

最终推导出四个 m2 块：

完整 EXP：
