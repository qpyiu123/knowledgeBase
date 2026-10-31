---
title: "NewStar CTF 2024 / MakeHero"
category: pwn
tags: ["NewStar CTF 2024", "MakeHero", "pwn", "官方资料", "docs/wp/2024/week4/pwn/makehero.md", "origin_tag:imported_cats"]
signals: ["NewStar CTF 2024", "MakeHero", "pwn"]
difficulty: medium
source: "https://github.com/pj-newstar/wiki-docs/blob/1a0f2ba21a30f950276396118b315eef0328371c/docs/wp/2024/week4/pwn/makehero.md"
tools: []
origin: imported_cats
origin_id: "official-7d0825de5d6261c6235e4a"
origin_domain: "pwn"
origin_family: "official_event_archive"
origin_event: "NewStar CTF 2024"
origin_year: 2024
origin_license: "MIT"
origin_attribution: ""
origin_verification: "official_source_not_reproduced"
origin_content_sha256: "687ddfdc3694b402f715820434f8e446bf5ed236864a3bc5e611205e528a6a5d"
origin_body_sha256: 8a3f83c0a549817714d4279bce99da69185f0eb3c6ddcf625a5c4101dfca0616
origin_title: "NewStar CTF 2024 / MakeHero"
origin_meta:
  asset_refs: [{"downloaded_bytes": 4254, "kind": "image", "local_path": "62_官方赛事题库/objects/d9b32bf29d59b57bd575edfe9839d3e1da6cceff86afd62856a8cfd87b499a09.blob", "owner_id": "official-7d0825de5d6261c6235e4a", "policy": "reference_only_no_execution", "relative_path": "docs/assets/images/wp/2024/week4/makehero_1.png", "sha256": "d9b32bf29d59b57bd575edfe9839d3e1da6cceff86afd62856a8cfd87b499a09", "source_url": "https://github.com/pj-newstar/wiki-docs/blob/1a0f2ba21a30f950276396118b315eef0328371c/docs/assets/images/wp/2024/week4/makehero_1.png"}, {"downloaded_bytes": 15672, "kind": "image", "local_path": "62_官方赛事题库/objects/75dc41f7ea0f456a2595a7ad7a07004d98578601627062f4b6bcc7fe5441c41e.blob", "owner_id": "official-7d0825de5d6261c6235e4a", "policy": "reference_only_no_execution", "relative_path": "docs/assets/images/wp/2024/week4/makehero_2.png", "sha256": "75dc41f7ea0f456a2595a7ad7a07004d98578601627062f4b6bcc7fe5441c41e", "source_url": "https://github.com/pj-newstar/wiki-docs/blob/1a0f2ba21a30f950276396118b315eef0328371c/docs/assets/images/wp/2024/week4/makehero_2.png"}, {"downloaded_bytes": 23729, "kind": "image", "local_path": "62_官方赛事题库/objects/1b9d83c2a5cb5c940eab3c1a4a92145fe569981f436c49af89d35c9e09e3c6e9.blob", "owner_id": "official-7d0825de5d6261c6235e4a", "policy": "reference_only_no_execution", "relative_path": "docs/assets/images/wp/2024/week4/makehero_3.png", "sha256": "1b9d83c2a5cb5c940eab3c1a4a92145fe569981f436c49af89d35c9e09e3c6e9", "source_url": "https://github.com/pj-newstar/wiki-docs/blob/1a0f2ba21a30f950276396118b315eef0328371c/docs/assets/images/wp/2024/week4/makehero_3.png"}, {"downloaded_bytes": 7540, "kind": "image", "local_path": "62_官方赛事题库/objects/1514c7775e4ab26d9071cf350817190a4c6868157c83cf6d29ce6d7f29eb96c6.blob", "owner_id": "official-7d0825de5d6261c6235e4a", "policy": "reference_only_no_execution", "relative_path": "docs/assets/images/wp/2024/week4/makehero_4.png", "sha256": "1514c7775e4ab26d9071cf350817190a4c6868157c83cf6d29ce6d7f29eb96c6", "source_url": "https://github.com/pj-newstar/wiki-docs/blob/1a0f2ba21a30f950276396118b315eef0328371c/docs/assets/images/wp/2024/week4/makehero_4.png"}, {"downloaded_bytes": 7590, "kind": "image", "local_path": "62_官方赛事题库/objects/54ec6641b59e403fab5d7c79a251392247d01cf7dc21f774c3808cd7682ea123.blob", "owner_id": "official-7d0825de5d6261c6235e4a", "policy": "reference_only_no_execution", "relative_path": "docs/assets/images/wp/2024/week4/makehero_5.png", "sha256": "54ec6641b59e403fab5d7c79a251392247d01cf7dc21f774c3808cd7682ea123", "source_url": "https://github.com/pj-newstar/wiki-docs/blob/1a0f2ba21a30f950276396118b315eef0328371c/docs/assets/images/wp/2024/week4/makehero_5.png"}, {"downloaded_bytes": 571, "kind": "image", "local_path": "62_官方赛事题库/objects/a1b22b1c65378a877826c2e317af6e2edbd73ec29207c8871aa3a9db7011f275.blob", "owner_id": "official-7d0825de5d6261c6235e4a", "policy": "reference_only_no_execution", "relative_path": "docs/assets/images/wp/2024/week4/makehero_6.png", "sha256": "a1b22b1c65378a877826c2e317af6e2edbd73ec29207c8871aa3a9db7011f275", "source_url": "https://github.com/pj-newstar/wiki-docs/blob/1a0f2ba21a30f950276396118b315eef0328371c/docs/assets/images/wp/2024/week4/makehero_6.png"}, {"downloaded_bytes": 4986, "kind": "image", "local_path": "62_官方赛事题库/objects/63ba3b8f0041421d2baf8f5d9113a14ea48bca952c541e0ea0d15c1db9e8bf19.blob", "owner_id": "official-7d0825de5d6261c6235e4a", "policy": "reference_only_no_execution", "relative_path": "docs/assets/images/wp/2024/week4/makehero_7.png", "sha256": "63ba3b8f0041421d2baf8f5d9113a14ea48bca952c541e0ea0d15c1db9e8bf19", "source_url": "https://github.com/pj-newstar/wiki-docs/blob/1a0f2ba21a30f950276396118b315eef0328371c/docs/assets/images/wp/2024/week4/makehero_7.png"}]
  basis: "original_prose_not_runtime_verified"
  challenge_key: "newstar:docs/wp/2024/week4/pwn/makehero"
  chunk_ids: [9364]
  content_sha256: "687ddfdc3694b402f715820434f8e446bf5ed236864a3bc5e611205e528a6a5d"
  domain: "pwn"
  domain_basis: "repository_path"
  event: "NewStar CTF 2024"
  external_links_not_followed: 0
  id: "official-7d0825de5d6261c6235e4a"
  kind: "official_wp_prose"
  language: "zh"
  license: "MIT"
  local_path: "62_官方赛事题库/objects/dbfc3eea7eaccda94b09fa2c73bcf6fbe4ea61f4c43c839f325556e0c197ca86.blob"
  official_evidence: "https://newstar.wiki/wp/2024/"
  original_path: "docs/wp/2024/week4/pwn/makehero.md"
  revision: "1a0f2ba21a30f950276396118b315eef0328371c"
  scope_note: "官方发布来源的说明正文；代码单独索引，未运行或分析。按文件收录，不把多份文件算作多道题。图片及附件下载状态见清单；仅按路径/原题分类标方向，binary 等跨方向资料留待分类。"
  source_family: "official_event_archive"
  source_url: "https://github.com/pj-newstar/wiki-docs/blob/1a0f2ba21a30f950276396118b315eef0328371c/docs/wp/2024/week4/pwn/makehero.md"
  tags: ["NewStar CTF 2024", "MakeHero", "pwn", "官方资料", "docs/wp/2024/week4/pwn/makehero.md"]
  title: "NewStar CTF 2024 / MakeHero"
  verification_status: "official_source_not_reproduced"
  year: 2024
updated: 2026-10-31
---
# NewStar CTF 2024 / MakeHero

> 本文由授权中文赛事 WP 正文导入（阶段 1，仅散文，代码段未导入）。
>
> - 来源：https://github.com/pj-newstar/wiki-docs/blob/1a0f2ba21a30f950276396118b315eef0328371c/docs/wp/2024/week4/pwn/makehero.md
> - 许可：MIT
> - 署名：（未提供）
> - 文档族：official_event_archive
> - 赛事：NewStar CTF 2024
> - 年份：2024
> - 核验状态：official_source_not_reproduced
> - 正文 sha256：687ddfdc3694b402f715820434f8e446bf5ed236864a3bc5e611205e528a6a5d
> - 导入 ID：official-7d0825de5d6261c6235e4a
> - 原 domain：pwn
> - 本地快照：62_官方赛事题库/objects/dbfc3eea7eaccda94b09fa2c73bcf6fbe4ea61f4c43c839f325556e0c197ca86.blob
> - 源修订：1a0f2ba21a30f950276396118b315eef0328371c
> - 收录说明：官方发布来源的说明正文；代码单独索引，未运行或分析。按文件收录，不把多份文件算作多道题。图片及附件下载状态见清单；仅按路径/原题分类标方向，binary 等跨方向资料留待分类。
> - 判定依据：original_prose_not_runtime_verified
> - 附件引用：[{"owner_id": "official-7d0825de5d6261c6235e4a", "relative_path": "docs/assets/images/wp/2024/week4/makehero_1.png", "local_path": "62_官方赛事题库/objects/d9b32bf29d59b57bd575edfe9839d3e1da6cceff86afd62856a8cfd87b499a09.blob", "downloaded_bytes": 4254, "source_url": "https://github.com/pj-newstar/wiki-docs/blob/1a0f2ba21a30f950276396118b315eef0328371c/docs/assets/images/wp/2024/week4/makehero_1.png", "sha256": "d9b32bf29d59b57bd575edfe9839d3e1da6cceff86afd62856a8cfd87b499a09", "kind": "image", "policy": "reference_only_no_execution"}, {"owner_id": "official-7d0825de5d6261c6235e4a", "relative_path": "docs/assets/images/wp/2024/week4/makehero_2.png", "local_path": "62_官方赛事题库/objects/75dc41f7ea0f456a2595a7ad7a07004d98578601627062f4b6bcc7fe5441c41e.blob", "downloaded_bytes": 15672, "source_url": "https://github.com/pj-newstar/wiki-docs/blob/1a0f2ba21a30f950276396118b315eef0328371c/docs/assets/images/wp/2024/week4/makehero_2.png", "sha256": "75dc41f7ea0f456a2595a7ad7a07004d98578601627062f4b6bcc7fe5441c41e", "kind": "image", "policy": "reference_only_no_execution"}, {"owner_id": "official-7d0825de5d6261c6235e4a", "relative_path": "docs/assets/images/wp/2024/week4/makehero_3.png", "local_path": "62_官方赛事题库/objects/1b9d83c2a5cb5c940eab3c1a4a92145fe569981f436c49af89d35c9e09e3c6e9.blob", "downloaded_bytes": 23729, "source_url": "https://github.com/pj-newstar/wiki-docs/blob/1a0f2ba21a30f950276396118b315eef0328371c/docs/assets/images/wp/2024/week4/makehero_3.png", "sha256": "1b9d83c2a5cb5c940eab3c1a4a92145fe569981f436c49af89d35c9e09e3c6e9", "kind": "image", "policy": "reference_only_no_execution"}, {"owner_id": "official-7d0825de5d6261c6235e4a", "relative_path": "docs/assets/images/wp/2024/week4/makehero_4.png", "local_path": "62_官方赛事题库/objects/1514c7775e4ab26d9071cf350817190a4c6868157c83cf6d29ce6d7f29eb96c6.blob", "downloaded_bytes": 7540, "source_url": "https://github.com/pj-newstar/wiki-docs/blob/1a0f2ba21a30f950276396118b315eef0328371c/docs/assets/images/wp/2024/week4/makehero_4.png", "sha256": "1514c7775e4ab26d9071cf350817190a4c6868157c83cf6d29ce6d7f29eb96c6", "kind": "image", "policy": "reference_only_no_execution"}, {"owner_id": "official-7d0825de5d6261c6235e4a", "relative_path": "docs/assets/images/wp/2024/week4/makehero_5.png", "local_path": "62_官方赛事题库/objects/54ec6641b59e403fab5d7c79a251392247d01cf7dc21f774c3808cd7682ea123.blob", "downloaded_bytes": 7590, "source_url": "https://github.com/pj-newstar/wiki-docs/blob/1a0f2ba21a30f950276396118b315eef0328371c/docs/assets/images/wp/2024/week4/makehero_5.png", "sha256": "54ec6641b59e403fab5d7c79a251392247d01cf7dc21f774c3808cd7682ea123", "kind": "image", "policy": "reference_only_no_execution"}, {"owner_id": "official-7d0825de5d6261c6235e4a", "relative_path": "docs/assets/images/wp/2024/week4/makehero_6.png", "local_path": "62_官方赛事题库/objects/a1b22b1c65378a877826c2e317af6e2edbd73ec29207c8871aa3a9db7011f275.blob", "downloaded_bytes": 571, "source_url": "https://github.com/pj-newstar/wiki-docs/blob/1a0f2ba21a30f950276396118b315eef0328371c/docs/assets/images/wp/2024/week4/makehero_6.png", "sha256": "a1b22b1c65378a877826c2e317af6e2edbd73ec29207c8871aa3a9db7011f275", "kind": "image", "policy": "reference_only_no_execution"}, {"owner_id": "official-7d0825de5d6261c6235e4a", "relative_path": "docs/assets/images/wp/2024/week4/makehero_7.png", "local_path": "62_官方赛事题库/objects/63ba3b8f0041421d2baf8f5d9113a14ea48bca952c541e0ea0d15c1db9e8bf19.blob", "downloaded_bytes": 4986, "source_url": "https://github.com/pj-newstar/wiki-docs/blob/1a0f2ba21a30f950276396118b315eef0328371c/docs/assets/images/wp/2024/week4/makehero_7.png", "sha256": "63ba3b8f0041421d2baf8f5d9113a14ea48bca952c541e0ea0d15c1db9e8bf19", "kind": "image", "policy": "reference_only_no_execution"}]

> 原文：https://github.com/pj-newstar/wiki-docs/blob/1a0f2ba21a30f950276396118b315eef0328371c/docs/wp/2024/week4/pwn/makehero.md

## 正文

---
titleTemplate: ":title | WriteUp - NewStar CTF 2024"
---

## 逆向分析

固定步骤，拖入 IDA 分析

可知，程序实现了通过 `/proc/self/mem` 实现了任意地址的改写

:::tip
程序是通过 `open("/proc/self/mem")` 的方式实现改写，因此无视各地址段的读写权限
:::

程序读入两个数字，`%lx` 是地址，`%hhx` 是要改的字节

其中，程序对 `v6` 的取值做了限制

在 `sub_1430` 函数中，对这几个全局变量做了初始化

结合 gdb 动调时的地址分布，我们可知，`qword_4060` 和 `qword_4068` 是程序 ELF `的地址，qword_4050` 和 `qword_4058` 是程序 libc 的地址

## Pwn it

程序能任意写两次，第一次能改写 ELF，第二次能改写 libc，仅有的两次机会是不足以让我们拿到 flag 的，我们需要通过仅有的两次机会来让我们获得「无限次」的机会

分析发现，程序的退出点在这里

因此我们能否通过修改跳转条件或是其他，来让程序不执行退出呢

我们或许可以通过改 jnz 为其他条件跳转来实现一直执行，也可以让 `v5--` 变为 `v5++` 来实现「无限次」任意写

在这，我选择修改 `--` 为 `++`，就是将 `8D 50 FF` 改为 `8D 50 01`

改完后，我们能一直任意写，剩下的就很多种解法了

改完后，我们能一直任意写，剩下的就很多种解法了

我选择将 exit 处代码改为 shellcode，来 GetShell

这题既能改 ELF，也能改 libc，应该会有很多不一样的解法吧（
