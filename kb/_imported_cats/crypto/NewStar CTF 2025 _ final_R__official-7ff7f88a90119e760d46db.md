---
title: "NewStar CTF 2025 / final_R"
category: crypto
tags: ["NewStar CTF 2025", "final_R", "crypto", "官方资料", "docs/wp/2025/extras/crypto/final-r.md", "origin_tag:imported_cats"]
signals: ["NewStar CTF 2025", "final_R", "crypto"]
difficulty: medium
source: "https://github.com/pj-newstar/wiki-docs/blob/1a0f2ba21a30f950276396118b315eef0328371c/docs/wp/2025/extras/crypto/final-r.md"
tools: []
origin: imported_cats
origin_id: "official-7ff7f88a90119e760d46db"
origin_domain: "crypto"
origin_family: "official_event_archive"
origin_event: "NewStar CTF 2025"
origin_year: 2025
origin_license: "MIT"
origin_attribution: ""
origin_verification: "official_source_not_reproduced"
origin_content_sha256: "46be4dee7413a0e557e883b20d933f502314ccca596eac91129f31092e378579"
origin_body_sha256: de4910f16ab7e19cdf8f9deb2a5896832a8350d6613c5a546a36383935e0ae0d
origin_title: "NewStar CTF 2025 / final_R"
origin_meta:
  asset_refs: []
  basis: "original_prose_not_runtime_verified"
  challenge_key: "newstar:docs/wp/2025/extras/crypto/final-r"
  chunk_ids: [10019]
  content_sha256: "46be4dee7413a0e557e883b20d933f502314ccca596eac91129f31092e378579"
  domain: "crypto"
  domain_basis: "repository_path"
  event: "NewStar CTF 2025"
  external_links_not_followed: 0
  id: "official-7ff7f88a90119e760d46db"
  kind: "official_wp_prose"
  language: "zh"
  license: "MIT"
  local_path: "62_官方赛事题库/objects/9747b614a2d3ee70fe92b5207d884a16599e1d636d368c976a1948c44bf27cae.blob"
  official_evidence: "https://newstar.wiki/wp/2024/"
  original_path: "docs/wp/2025/extras/crypto/final-r.md"
  revision: "1a0f2ba21a30f950276396118b315eef0328371c"
  scope_note: "官方发布来源的说明正文；代码单独索引，未运行或分析。按文件收录，不把多份文件算作多道题。图片及附件下载状态见清单；仅按路径/原题分类标方向，binary 等跨方向资料留待分类。"
  source_family: "official_event_archive"
  source_url: "https://github.com/pj-newstar/wiki-docs/blob/1a0f2ba21a30f950276396118b315eef0328371c/docs/wp/2025/extras/crypto/final-r.md"
  tags: ["NewStar CTF 2025", "final_R", "crypto", "官方资料", "docs/wp/2025/extras/crypto/final-r.md"]
  title: "NewStar CTF 2025 / final_R"
  verification_status: "official_source_not_reproduced"
  year: 2025
updated: 2026-10-31
---
# NewStar CTF 2025 / final_R

> 本文由授权中文赛事 WP 正文导入（阶段 1，仅散文，代码段未导入）。
>
> - 来源：https://github.com/pj-newstar/wiki-docs/blob/1a0f2ba21a30f950276396118b315eef0328371c/docs/wp/2025/extras/crypto/final-r.md
> - 许可：MIT
> - 署名：（未提供）
> - 文档族：official_event_archive
> - 赛事：NewStar CTF 2025
> - 年份：2025
> - 核验状态：official_source_not_reproduced
> - 正文 sha256：46be4dee7413a0e557e883b20d933f502314ccca596eac91129f31092e378579
> - 导入 ID：official-7ff7f88a90119e760d46db
> - 原 domain：crypto
> - 本地快照：62_官方赛事题库/objects/9747b614a2d3ee70fe92b5207d884a16599e1d636d368c976a1948c44bf27cae.blob
> - 源修订：1a0f2ba21a30f950276396118b315eef0328371c
> - 收录说明：官方发布来源的说明正文；代码单独索引，未运行或分析。按文件收录，不把多份文件算作多道题。图片及附件下载状态见清单；仅按路径/原题分类标方向，binary 等跨方向资料留待分类。
> - 判定依据：original_prose_not_runtime_verified

> 原文：https://github.com/pj-newstar/wiki-docs/blob/1a0f2ba21a30f950276396118b315eef0328371c/docs/wp/2025/extras/crypto/final-r.md

## 正文

---
titleTemplate: ":title | WriteUp - NewStar CTF 2025"
---

## final_R

神秘一行 python

解释：FLAG 转为$\mathbb{GF}(2^7)$上的（$59$维）向量（通过对每个字符使用 ord()，值 $x$ 代表 $a^x$ ,$a$ 是生成元）. 然后该向量对自己做循环卷积。结果向量（的值$a^x\in \mathbb{GF}(2^7)$转为$x$，）输出为字节形式。

你当然可以直接解卷积。

你当然可以直接解卷积。

商环 $\mathbb{F}[x]/(x^n-1)$ 和向量空间 $\mathrm{F}^n$ 有一一对应关系：
$r(x)=\sum_i a_ix^{i}\in \mathbb{F}[x]/(x^n-1) \rightarrow (\cdots,a_i,\cdots)\in \mathbb{F}^n$
多项式加法对应向量加法
多项式乘法对应向量的循环卷积。

所以本题其实就是求一个多项式的平方根。
怎么求呢？

非常简单，直接列出来观察就行。因为$\mathbb{GF}(2^7)$ 特征是 $2$ ，所以没有交叉项。直接对应系数相等求解就可以了。
