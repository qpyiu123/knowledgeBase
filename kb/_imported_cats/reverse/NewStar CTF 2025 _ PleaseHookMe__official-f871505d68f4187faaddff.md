---
title: "NewStar CTF 2025 / PleaseHookMe"
category: reverse
tags: ["NewStar CTF 2025", "PleaseHookMe", "reverse", "官方资料", "docs/wp/2025/week4/reverse/pleasehookme.md", "origin_tag:imported_cats"]
signals: ["NewStar CTF 2025", "PleaseHookMe", "reverse"]
difficulty: medium
source: "https://github.com/pj-newstar/wiki-docs/blob/1a0f2ba21a30f950276396118b315eef0328371c/docs/wp/2025/week4/reverse/pleasehookme.md"
tools: []
origin: imported_cats
origin_id: "official-f871505d68f4187faaddff"
origin_domain: "reverse"
origin_family: "official_event_archive"
origin_event: "NewStar CTF 2025"
origin_year: 2025
origin_license: "MIT"
origin_attribution: ""
origin_verification: "official_source_not_reproduced"
origin_content_sha256: "46be4dee7413a0e557e883b20d933f502314ccca596eac91129f31092e378579"
origin_body_sha256: 0d68155cbc1287f2934b40f8bccbc31ec9347575c7e41de988753ce596273168
origin_title: "NewStar CTF 2025 / PleaseHookMe"
origin_meta:
  asset_refs: []
  basis: "original_prose_not_runtime_verified"
  challenge_key: "newstar:docs/wp/2025/week4/reverse/pleasehookme"
  chunk_ids: [11374]
  content_sha256: "46be4dee7413a0e557e883b20d933f502314ccca596eac91129f31092e378579"
  domain: "reverse"
  domain_basis: "repository_path"
  event: "NewStar CTF 2025"
  external_links_not_followed: 0
  id: "official-f871505d68f4187faaddff"
  kind: "official_wp_prose"
  language: "zh"
  license: "MIT"
  local_path: "62_官方赛事题库/objects/13769018eb241a14f36677d69414e580042b221a7901eeb8d3a9235e20a0adfb.blob"
  official_evidence: "https://newstar.wiki/wp/2024/"
  original_path: "docs/wp/2025/week4/reverse/pleasehookme.md"
  revision: "1a0f2ba21a30f950276396118b315eef0328371c"
  scope_note: "官方发布来源的说明正文；代码单独索引，未运行或分析。按文件收录，不把多份文件算作多道题。图片及附件下载状态见清单；仅按路径/原题分类标方向，binary 等跨方向资料留待分类。"
  source_family: "official_event_archive"
  source_url: "https://github.com/pj-newstar/wiki-docs/blob/1a0f2ba21a30f950276396118b315eef0328371c/docs/wp/2025/week4/reverse/pleasehookme.md"
  tags: ["NewStar CTF 2025", "PleaseHookMe", "reverse", "官方资料", "docs/wp/2025/week4/reverse/pleasehookme.md"]
  title: "NewStar CTF 2025 / PleaseHookMe"
  verification_status: "official_source_not_reproduced"
  year: 2025
updated: 2026-10-31
---
# NewStar CTF 2025 / PleaseHookMe

> 本文由授权中文赛事 WP 正文导入（阶段 1，仅散文，代码段未导入）。
>
> - 来源：https://github.com/pj-newstar/wiki-docs/blob/1a0f2ba21a30f950276396118b315eef0328371c/docs/wp/2025/week4/reverse/pleasehookme.md
> - 许可：MIT
> - 署名：（未提供）
> - 文档族：official_event_archive
> - 赛事：NewStar CTF 2025
> - 年份：2025
> - 核验状态：official_source_not_reproduced
> - 正文 sha256：46be4dee7413a0e557e883b20d933f502314ccca596eac91129f31092e378579
> - 导入 ID：official-f871505d68f4187faaddff
> - 原 domain：reverse
> - 本地快照：62_官方赛事题库/objects/13769018eb241a14f36677d69414e580042b221a7901eeb8d3a9235e20a0adfb.blob
> - 源修订：1a0f2ba21a30f950276396118b315eef0328371c
> - 收录说明：官方发布来源的说明正文；代码单独索引，未运行或分析。按文件收录，不把多份文件算作多道题。图片及附件下载状态见清单；仅按路径/原题分类标方向，binary 等跨方向资料留待分类。
> - 判定依据：original_prose_not_runtime_verified

> 原文：https://github.com/pj-newstar/wiki-docs/blob/1a0f2ba21a30f950276396118b315eef0328371c/docs/wp/2025/week4/reverse/pleasehookme.md

## 正文

---
titleTemplate: ":title | WriteUp - NewStar CTF 2025"
---

## 分析

打开 `so` 搜索 `Java` ，因为编译器优化的关系，看起来代码有点恐怖。
`veorq_s8` 和 `vqtbl1q_s8` 都是 `ARM64` 的 `Neon` 指令，用来生成密钥，可以看看 `ARM` 的手册，写循环来模拟这个算法。本题更推荐使用 `Frida` `HOOK`

看起来是 `TEA` 系列算法（实际为 `XXTEA`）。`(*(_DWORD *)((unsigned __int64)&v20 & 0xFFFFFFFFFFFFFFF3LL | (4 * ((v10 >> 2) & 3LL)))` 这一处解引用操作是在取 `key`，因此可以使用 Frida 提取该值。

查看汇编可知，向量操作的最后一行会将 `key` 写入内存：

使用 Frida hook，`0xd08` 是指令偏移。

运行 `frida -l .\hook.js -F -U` 附加 App，得到 `key`。

得到密钥后，即可解开后续的 `XXTEA` 加密。
