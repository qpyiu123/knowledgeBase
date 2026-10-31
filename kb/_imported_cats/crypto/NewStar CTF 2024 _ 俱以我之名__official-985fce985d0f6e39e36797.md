---
title: "NewStar CTF 2024 / 俱以我之名"
category: crypto
tags: ["NewStar CTF 2024", "俱以我之名", "crypto", "官方资料", "docs/wp/2024/week4/crypto/wiener.md", "origin_tag:imported_cats"]
signals: ["NewStar CTF 2024", "俱以我之名", "crypto"]
difficulty: medium
source: "https://github.com/pj-newstar/wiki-docs/blob/1a0f2ba21a30f950276396118b315eef0328371c/docs/wp/2024/week4/crypto/wiener.md"
tools: []
origin: imported_cats
origin_id: "official-985fce985d0f6e39e36797"
origin_domain: "crypto"
origin_family: "official_event_archive"
origin_event: "NewStar CTF 2024"
origin_year: 2024
origin_license: "MIT"
origin_attribution: ""
origin_verification: "official_source_not_reproduced"
origin_content_sha256: "687ddfdc3694b402f715820434f8e446bf5ed236864a3bc5e611205e528a6a5d"
origin_body_sha256: 1737b81b4b5236dcf582ae3baf7bed11e13e02f6b2b1821c7928a298cf5ac1f2
origin_title: "NewStar CTF 2024 / 俱以我之名"
origin_meta:
  asset_refs: []
  basis: "original_prose_not_runtime_verified"
  challenge_key: "newstar:docs/wp/2024/week4/crypto/wiener"
  chunk_ids: [9255]
  content_sha256: "687ddfdc3694b402f715820434f8e446bf5ed236864a3bc5e611205e528a6a5d"
  domain: "crypto"
  domain_basis: "repository_path"
  event: "NewStar CTF 2024"
  external_links_not_followed: 2
  id: "official-985fce985d0f6e39e36797"
  kind: "official_wp_prose"
  language: "zh"
  license: "MIT"
  local_path: "62_官方赛事题库/objects/e09100d63918f45e840b04ef5a9b2d36dc473af675b85eff13c15ef7dc78464c.blob"
  official_evidence: "https://newstar.wiki/wp/2024/"
  original_path: "docs/wp/2024/week4/crypto/wiener.md"
  revision: "1a0f2ba21a30f950276396118b315eef0328371c"
  scope_note: "官方发布来源的说明正文；代码单独索引，未运行或分析。按文件收录，不把多份文件算作多道题。图片及附件下载状态见清单；仅按路径/原题分类标方向，binary 等跨方向资料留待分类。"
  source_family: "official_event_archive"
  source_url: "https://github.com/pj-newstar/wiki-docs/blob/1a0f2ba21a30f950276396118b315eef0328371c/docs/wp/2024/week4/crypto/wiener.md"
  tags: ["NewStar CTF 2024", "俱以我之名", "crypto", "官方资料", "docs/wp/2024/week4/crypto/wiener.md"]
  title: "NewStar CTF 2024 / 俱以我之名"
  verification_status: "official_source_not_reproduced"
  year: 2024
updated: 2026-10-31
---
# NewStar CTF 2024 / 俱以我之名

> 本文由授权中文赛事 WP 正文导入（阶段 1，仅散文，代码段未导入）。
>
> - 来源：https://github.com/pj-newstar/wiki-docs/blob/1a0f2ba21a30f950276396118b315eef0328371c/docs/wp/2024/week4/crypto/wiener.md
> - 许可：MIT
> - 署名：（未提供）
> - 文档族：official_event_archive
> - 赛事：NewStar CTF 2024
> - 年份：2024
> - 核验状态：official_source_not_reproduced
> - 正文 sha256：687ddfdc3694b402f715820434f8e446bf5ed236864a3bc5e611205e528a6a5d
> - 导入 ID：official-985fce985d0f6e39e36797
> - 原 domain：crypto
> - 本地快照：62_官方赛事题库/objects/e09100d63918f45e840b04ef5a9b2d36dc473af675b85eff13c15ef7dc78464c.blob
> - 源修订：1a0f2ba21a30f950276396118b315eef0328371c
> - 收录说明：官方发布来源的说明正文；代码单独索引，未运行或分析。按文件收录，不把多份文件算作多道题。图片及附件下载状态见清单；仅按路径/原题分类标方向，binary 等跨方向资料留待分类。
> - 判定依据：original_prose_not_runtime_verified

> 原文：https://github.com/pj-newstar/wiki-docs/blob/1a0f2ba21a30f950276396118b315eef0328371c/docs/wp/2024/week4/crypto/wiener.md

## 正文

---
titleTemplate: ":title | WriteUp - NewStar CTF 2024"
---

## 俱以我之名

[参考文档](/guide/2024/week4.html#俱以我之名)中的「我是谁」、俱以我之名是维娜的技能，所以我们可以试图将 RSA 和「维娜」作为关键词搜索，出题人尝试了一下，是可以搜到的，于是展开学习。

维纳攻击思想，原理可以参照 Xenny 师傅的文章学习：[wiener 攻击](https://www.nssctf.cn/note/set/8)。

详细证明可以看维基百科：[Wiener's attack](https://en.wikipedia.org/wiki/Wiener%27s_attack).

我们可以借助连分数来分解 $p$ 和 $q$ 来对 RSA 打真伤。

在这里我们有

$$
\begin{gather}
\mathrm{Golden\_Oath} = (p-114)(p-514)(p+114)(p+514)(q-1919)(q-810)(q+1919)(q+810) \approx N^4
\\
\frac{y}{\mathrm{Golden\_Oath}} \approx \frac{k}{x}
\end{gather}
$$

至此，$\mathrm{Golden\_Oath}$、$n$ 以及它们和 $p$、$q$ 关系均已知，利用两个等式解个二元方程即可。

这里我们使用 `sympy` 库解方程

分解出 $p$ 和 $q$ 我们就成功对 RSA 打出了最真实的伤害，然后常规流程抬走
