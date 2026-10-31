---
title: "NewStar CTF 2024 / EZ_fmt"
category: pwn
tags: ["NewStar CTF 2024", "EZ_fmt", "pwn", "官方资料", "docs/wp/2024/week2/pwn/ez-fmt.md", "origin_tag:imported_cats"]
signals: ["NewStar CTF 2024", "EZ_fmt", "pwn"]
difficulty: medium
source: "https://github.com/pj-newstar/wiki-docs/blob/1a0f2ba21a30f950276396118b315eef0328371c/docs/wp/2024/week2/pwn/ez-fmt.md"
tools: []
origin: imported_cats
origin_id: "official-694fc373ce2daa217a80e8"
origin_domain: "pwn"
origin_family: "official_event_archive"
origin_event: "NewStar CTF 2024"
origin_year: 2024
origin_license: "MIT"
origin_attribution: ""
origin_verification: "official_source_not_reproduced"
origin_content_sha256: "687ddfdc3694b402f715820434f8e446bf5ed236864a3bc5e611205e528a6a5d"
origin_body_sha256: c1904e5d7ebc8301fb2b66b0f00a38ae1aaa79d5432637d699529a7d93fbe118
origin_title: "NewStar CTF 2024 / EZ_fmt"
origin_meta:
  asset_refs: [{"downloaded_bytes": 39538, "kind": "image", "local_path": "62_官方赛事题库/objects/375f2ad71e5b0e3cd3f20d568cbba982541159f5bc698f11a95fb33e5315474f.blob", "owner_id": "official-694fc373ce2daa217a80e8", "policy": "reference_only_no_execution", "relative_path": "docs/assets/images/wp/2024/week2/ez-fmt_1.png", "sha256": "375f2ad71e5b0e3cd3f20d568cbba982541159f5bc698f11a95fb33e5315474f", "source_url": "https://github.com/pj-newstar/wiki-docs/blob/1a0f2ba21a30f950276396118b315eef0328371c/docs/assets/images/wp/2024/week2/ez-fmt_1.png"}, {"downloaded_bytes": 672748, "kind": "image", "local_path": "62_官方赛事题库/objects/acba10c04159cffc797126717b43e907cddf78d9775544a552d920c95df4a07a.blob", "owner_id": "official-694fc373ce2daa217a80e8", "policy": "reference_only_no_execution", "relative_path": "docs/assets/images/wp/2024/week2/ez-fmt_2.png", "sha256": "acba10c04159cffc797126717b43e907cddf78d9775544a552d920c95df4a07a", "source_url": "https://github.com/pj-newstar/wiki-docs/blob/1a0f2ba21a30f950276396118b315eef0328371c/docs/assets/images/wp/2024/week2/ez-fmt_2.png"}]
  basis: "original_prose_not_runtime_verified"
  challenge_key: "newstar:docs/wp/2024/week2/pwn/ez-fmt"
  chunk_ids: [8794]
  content_sha256: "687ddfdc3694b402f715820434f8e446bf5ed236864a3bc5e611205e528a6a5d"
  domain: "pwn"
  domain_basis: "repository_path"
  event: "NewStar CTF 2024"
  external_links_not_followed: 0
  id: "official-694fc373ce2daa217a80e8"
  kind: "official_wp_prose"
  language: "zh"
  license: "MIT"
  local_path: "62_官方赛事题库/objects/1323fcb1445283e07a147b6b96e3aaf32a035f5dbc0467cd0b9a7bef7e3b19c5.blob"
  official_evidence: "https://newstar.wiki/wp/2024/"
  original_path: "docs/wp/2024/week2/pwn/ez-fmt.md"
  revision: "1a0f2ba21a30f950276396118b315eef0328371c"
  scope_note: "官方发布来源的说明正文；代码单独索引，未运行或分析。按文件收录，不把多份文件算作多道题。图片及附件下载状态见清单；仅按路径/原题分类标方向，binary 等跨方向资料留待分类。"
  source_family: "official_event_archive"
  source_url: "https://github.com/pj-newstar/wiki-docs/blob/1a0f2ba21a30f950276396118b315eef0328371c/docs/wp/2024/week2/pwn/ez-fmt.md"
  tags: ["NewStar CTF 2024", "EZ_fmt", "pwn", "官方资料", "docs/wp/2024/week2/pwn/ez-fmt.md"]
  title: "NewStar CTF 2024 / EZ_fmt"
  verification_status: "official_source_not_reproduced"
  year: 2024
updated: 2026-10-31
---
# NewStar CTF 2024 / EZ_fmt

> 本文由授权中文赛事 WP 正文导入（阶段 1，仅散文，代码段未导入）。
>
> - 来源：https://github.com/pj-newstar/wiki-docs/blob/1a0f2ba21a30f950276396118b315eef0328371c/docs/wp/2024/week2/pwn/ez-fmt.md
> - 许可：MIT
> - 署名：（未提供）
> - 文档族：official_event_archive
> - 赛事：NewStar CTF 2024
> - 年份：2024
> - 核验状态：official_source_not_reproduced
> - 正文 sha256：687ddfdc3694b402f715820434f8e446bf5ed236864a3bc5e611205e528a6a5d
> - 导入 ID：official-694fc373ce2daa217a80e8
> - 原 domain：pwn
> - 本地快照：62_官方赛事题库/objects/1323fcb1445283e07a147b6b96e3aaf32a035f5dbc0467cd0b9a7bef7e3b19c5.blob
> - 源修订：1a0f2ba21a30f950276396118b315eef0328371c
> - 收录说明：官方发布来源的说明正文；代码单独索引，未运行或分析。按文件收录，不把多份文件算作多道题。图片及附件下载状态见清单；仅按路径/原题分类标方向，binary 等跨方向资料留待分类。
> - 判定依据：original_prose_not_runtime_verified
> - 附件引用：[{"owner_id": "official-694fc373ce2daa217a80e8", "relative_path": "docs/assets/images/wp/2024/week2/ez-fmt_1.png", "local_path": "62_官方赛事题库/objects/375f2ad71e5b0e3cd3f20d568cbba982541159f5bc698f11a95fb33e5315474f.blob", "downloaded_bytes": 39538, "source_url": "https://github.com/pj-newstar/wiki-docs/blob/1a0f2ba21a30f950276396118b315eef0328371c/docs/assets/images/wp/2024/week2/ez-fmt_1.png", "sha256": "375f2ad71e5b0e3cd3f20d568cbba982541159f5bc698f11a95fb33e5315474f", "kind": "image", "policy": "reference_only_no_execution"}, {"owner_id": "official-694fc373ce2daa217a80e8", "relative_path": "docs/assets/images/wp/2024/week2/ez-fmt_2.png", "local_path": "62_官方赛事题库/objects/acba10c04159cffc797126717b43e907cddf78d9775544a552d920c95df4a07a.blob", "downloaded_bytes": 672748, "source_url": "https://github.com/pj-newstar/wiki-docs/blob/1a0f2ba21a30f950276396118b315eef0328371c/docs/assets/images/wp/2024/week2/ez-fmt_2.png", "sha256": "acba10c04159cffc797126717b43e907cddf78d9775544a552d920c95df4a07a", "kind": "image", "policy": "reference_only_no_execution"}]

> 原文：https://github.com/pj-newstar/wiki-docs/blob/1a0f2ba21a30f950276396118b315eef0328371c/docs/wp/2024/week2/pwn/ez-fmt.md

## 正文

---
titleTemplate: ":title | WriteUp - NewStar CTF 2024"
---

## EZ_fmt

查看 `vuln` 函数

很经典的格式化字符串，首先确定 offset 为 `8`

根据程序，我们有三次格式化字符串的机会

根据程序，我们有三次格式化字符串的机会

- 第一次泄露 libc
- 第二次改 `printf` GOT 表地址为 `system`
- 第三次输入为 `sh`，构造出 `printf(buf)=system(sh)` 即可

EXP 如下
