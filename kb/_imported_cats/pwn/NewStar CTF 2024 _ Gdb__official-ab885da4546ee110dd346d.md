---
title: "NewStar CTF 2024 / Gdb"
category: pwn
tags: ["NewStar CTF 2024", "Gdb", "pwn", "官方资料", "docs/wp/2024/week1/pwn/gdb.md", "origin_tag:imported_cats"]
signals: ["NewStar CTF 2024", "Gdb", "pwn"]
difficulty: medium
source: "https://github.com/pj-newstar/wiki-docs/blob/1a0f2ba21a30f950276396118b315eef0328371c/docs/wp/2024/week1/pwn/gdb.md"
tools: []
origin: imported_cats
origin_id: "official-ab885da4546ee110dd346d"
origin_domain: "pwn"
origin_family: "official_event_archive"
origin_event: "NewStar CTF 2024"
origin_year: 2024
origin_license: "MIT"
origin_attribution: ""
origin_verification: "official_source_not_reproduced"
origin_content_sha256: "687ddfdc3694b402f715820434f8e446bf5ed236864a3bc5e611205e528a6a5d"
origin_body_sha256: 7d3fe8b87ef5e868a8fe9a5b9cc83ba6241c36671752f4b293aeec7d2183af02
origin_title: "NewStar CTF 2024 / Gdb"
origin_meta:
  asset_refs: [{"downloaded_bytes": 627972, "kind": "image", "local_path": "62_官方赛事题库/objects/e4b4352dc4a165123ece40ef6b2d7bb074b7add17616a87bfef4d3e49f08ec38.blob", "owner_id": "official-ab885da4546ee110dd346d", "policy": "reference_only_no_execution", "relative_path": "docs/assets/images/wp/2024/week1/gdb_1.png", "sha256": "e4b4352dc4a165123ece40ef6b2d7bb074b7add17616a87bfef4d3e49f08ec38", "source_url": "https://github.com/pj-newstar/wiki-docs/blob/1a0f2ba21a30f950276396118b315eef0328371c/docs/assets/images/wp/2024/week1/gdb_1.png"}, {"downloaded_bytes": 43404, "kind": "image", "local_path": "62_官方赛事题库/objects/c1a13f2012cebf759c2b8b9f04341dc95118c422a344600fbf9b6f58fba4210d.blob", "owner_id": "official-ab885da4546ee110dd346d", "policy": "reference_only_no_execution", "relative_path": "docs/assets/images/wp/2024/week1/gdb_2.png", "sha256": "c1a13f2012cebf759c2b8b9f04341dc95118c422a344600fbf9b6f58fba4210d", "source_url": "https://github.com/pj-newstar/wiki-docs/blob/1a0f2ba21a30f950276396118b315eef0328371c/docs/assets/images/wp/2024/week1/gdb_2.png"}]
  basis: "original_prose_not_runtime_verified"
  challenge_key: "newstar:docs/wp/2024/week1/pwn/gdb"
  chunk_ids: [8504]
  content_sha256: "687ddfdc3694b402f715820434f8e446bf5ed236864a3bc5e611205e528a6a5d"
  domain: "pwn"
  domain_basis: "repository_path"
  event: "NewStar CTF 2024"
  external_links_not_followed: 0
  id: "official-ab885da4546ee110dd346d"
  kind: "official_wp_prose"
  language: "zh"
  license: "MIT"
  local_path: "62_官方赛事题库/objects/2fbe4cdf99d7353ce3bfe88b7f59362a6394a1990f93c9c8e7810a11e20546f8.blob"
  official_evidence: "https://newstar.wiki/wp/2024/"
  original_path: "docs/wp/2024/week1/pwn/gdb.md"
  revision: "1a0f2ba21a30f950276396118b315eef0328371c"
  scope_note: "官方发布来源的说明正文；代码单独索引，未运行或分析。按文件收录，不把多份文件算作多道题。图片及附件下载状态见清单；仅按路径/原题分类标方向，binary 等跨方向资料留待分类。"
  source_family: "official_event_archive"
  source_url: "https://github.com/pj-newstar/wiki-docs/blob/1a0f2ba21a30f950276396118b315eef0328371c/docs/wp/2024/week1/pwn/gdb.md"
  tags: ["NewStar CTF 2024", "Gdb", "pwn", "官方资料", "docs/wp/2024/week1/pwn/gdb.md"]
  title: "NewStar CTF 2024 / Gdb"
  verification_status: "official_source_not_reproduced"
  year: 2024
updated: 2026-10-31
---
# NewStar CTF 2024 / Gdb

> 本文由授权中文赛事 WP 正文导入（阶段 1，仅散文，代码段未导入）。
>
> - 来源：https://github.com/pj-newstar/wiki-docs/blob/1a0f2ba21a30f950276396118b315eef0328371c/docs/wp/2024/week1/pwn/gdb.md
> - 许可：MIT
> - 署名：（未提供）
> - 文档族：official_event_archive
> - 赛事：NewStar CTF 2024
> - 年份：2024
> - 核验状态：official_source_not_reproduced
> - 正文 sha256：687ddfdc3694b402f715820434f8e446bf5ed236864a3bc5e611205e528a6a5d
> - 导入 ID：official-ab885da4546ee110dd346d
> - 原 domain：pwn
> - 本地快照：62_官方赛事题库/objects/2fbe4cdf99d7353ce3bfe88b7f59362a6394a1990f93c9c8e7810a11e20546f8.blob
> - 源修订：1a0f2ba21a30f950276396118b315eef0328371c
> - 收录说明：官方发布来源的说明正文；代码单独索引，未运行或分析。按文件收录，不把多份文件算作多道题。图片及附件下载状态见清单；仅按路径/原题分类标方向，binary 等跨方向资料留待分类。
> - 判定依据：original_prose_not_runtime_verified
> - 附件引用：[{"owner_id": "official-ab885da4546ee110dd346d", "relative_path": "docs/assets/images/wp/2024/week1/gdb_1.png", "local_path": "62_官方赛事题库/objects/e4b4352dc4a165123ece40ef6b2d7bb074b7add17616a87bfef4d3e49f08ec38.blob", "downloaded_bytes": 627972, "source_url": "https://github.com/pj-newstar/wiki-docs/blob/1a0f2ba21a30f950276396118b315eef0328371c/docs/assets/images/wp/2024/week1/gdb_1.png", "sha256": "e4b4352dc4a165123ece40ef6b2d7bb074b7add17616a87bfef4d3e49f08ec38", "kind": "image", "policy": "reference_only_no_execution"}, {"owner_id": "official-ab885da4546ee110dd346d", "relative_path": "docs/assets/images/wp/2024/week1/gdb_2.png", "local_path": "62_官方赛事题库/objects/c1a13f2012cebf759c2b8b9f04341dc95118c422a344600fbf9b6f58fba4210d.blob", "downloaded_bytes": 43404, "source_url": "https://github.com/pj-newstar/wiki-docs/blob/1a0f2ba21a30f950276396118b315eef0328371c/docs/assets/images/wp/2024/week1/gdb_2.png", "sha256": "c1a13f2012cebf759c2b8b9f04341dc95118c422a344600fbf9b6f58fba4210d", "kind": "image", "policy": "reference_only_no_execution"}]

> 原文：https://github.com/pj-newstar/wiki-docs/blob/1a0f2ba21a30f950276396118b315eef0328371c/docs/wp/2024/week1/pwn/gdb.md

## 正文

---
titleTemplate: ":title | WriteUp - NewStar CTF 2024"
---

## Gdb

先拖入 IDA 分析：

可以看到程序逻辑是对一串字符串执行了加密操作，然后需要我们输入加密后的内容

对于加密函数，可以发现完全看不懂<span data-desc>（其实我是故意的🥰）</span>

所以我们选择动调查看加密后的内容

键入 `gdb ./gdb` 并运行，先运行程序，用 `b *$rebase(0x1836)` 下断点（断在call 加密函数处）

运行到加密函数处，可以发现，rdi 寄存器存的是要加密的内容，rsi 存的是加密的 key

先复制下要加密内容的地址

- `0x7fffffffd717`

然后使用 `ni` 指令步进

然后使用 `ni` 指令步进

此时字符串已经完成了加密，我们使用 `tel 0x7fffffffd717` 指令查看字符串的内容

`b'\x5d\x1d\x43\x55\x53\x45\x57\x45'` 便是加密后的内容，使用 Python 脚本发送即可
