---
title: "NewStar CTF 2024 / Reread"
category: pwn
tags: ["NewStar CTF 2024", "Reread", "pwn", "官方资料", "docs/wp/2024/week4/pwn/reread.md", "origin_tag:imported_cats"]
signals: ["NewStar CTF 2024", "Reread", "pwn"]
difficulty: medium
source: "https://github.com/pj-newstar/wiki-docs/blob/1a0f2ba21a30f950276396118b315eef0328371c/docs/wp/2024/week4/pwn/reread.md"
tools: []
origin: imported_cats
origin_id: "official-d191013710887be97a5b48"
origin_domain: "pwn"
origin_family: "official_event_archive"
origin_event: "NewStar CTF 2024"
origin_year: 2024
origin_license: "MIT"
origin_attribution: ""
origin_verification: "official_source_not_reproduced"
origin_content_sha256: "687ddfdc3694b402f715820434f8e446bf5ed236864a3bc5e611205e528a6a5d"
origin_body_sha256: 9d73be2446fb75616700e1b83ad9811e6afb8ab005e6ac9d3710d688ec22192c
origin_title: "NewStar CTF 2024 / Reread"
origin_meta:
  asset_refs: [{"downloaded_bytes": 1819024, "kind": "image", "local_path": "62_官方赛事题库/objects/8b7d3befbc4ec7cc19bbefb6e893ed6c055623372e337ae557ea740c753452c9.blob", "owner_id": "official-d191013710887be97a5b48", "policy": "reference_only_no_execution", "relative_path": "docs/assets/images/wp/2024/week4/reread_1.png", "sha256": "8b7d3befbc4ec7cc19bbefb6e893ed6c055623372e337ae557ea740c753452c9", "source_url": "https://github.com/pj-newstar/wiki-docs/blob/1a0f2ba21a30f950276396118b315eef0328371c/docs/assets/images/wp/2024/week4/reread_1.png"}]
  basis: "original_prose_not_runtime_verified"
  challenge_key: "newstar:docs/wp/2024/week4/pwn/reread"
  chunk_ids: [9406]
  content_sha256: "687ddfdc3694b402f715820434f8e446bf5ed236864a3bc5e611205e528a6a5d"
  domain: "pwn"
  domain_basis: "repository_path"
  event: "NewStar CTF 2024"
  external_links_not_followed: 0
  id: "official-d191013710887be97a5b48"
  kind: "official_wp_prose"
  language: "zh"
  license: "MIT"
  local_path: "62_官方赛事题库/objects/133e784715e2a19d0da86161de590568f273ede2c4498f24170616f92a8efdfe.blob"
  official_evidence: "https://newstar.wiki/wp/2024/"
  original_path: "docs/wp/2024/week4/pwn/reread.md"
  revision: "1a0f2ba21a30f950276396118b315eef0328371c"
  scope_note: "官方发布来源的说明正文；代码单独索引，未运行或分析。按文件收录，不把多份文件算作多道题。图片及附件下载状态见清单；仅按路径/原题分类标方向，binary 等跨方向资料留待分类。"
  source_family: "official_event_archive"
  source_url: "https://github.com/pj-newstar/wiki-docs/blob/1a0f2ba21a30f950276396118b315eef0328371c/docs/wp/2024/week4/pwn/reread.md"
  tags: ["NewStar CTF 2024", "Reread", "pwn", "官方资料", "docs/wp/2024/week4/pwn/reread.md"]
  title: "NewStar CTF 2024 / Reread"
  verification_status: "official_source_not_reproduced"
  year: 2024
updated: 2026-10-31
---
# NewStar CTF 2024 / Reread

> 本文由授权中文赛事 WP 正文导入（阶段 1，仅散文，代码段未导入）。
>
> - 来源：https://github.com/pj-newstar/wiki-docs/blob/1a0f2ba21a30f950276396118b315eef0328371c/docs/wp/2024/week4/pwn/reread.md
> - 许可：MIT
> - 署名：（未提供）
> - 文档族：official_event_archive
> - 赛事：NewStar CTF 2024
> - 年份：2024
> - 核验状态：official_source_not_reproduced
> - 正文 sha256：687ddfdc3694b402f715820434f8e446bf5ed236864a3bc5e611205e528a6a5d
> - 导入 ID：official-d191013710887be97a5b48
> - 原 domain：pwn
> - 本地快照：62_官方赛事题库/objects/133e784715e2a19d0da86161de590568f273ede2c4498f24170616f92a8efdfe.blob
> - 源修订：1a0f2ba21a30f950276396118b315eef0328371c
> - 收录说明：官方发布来源的说明正文；代码单独索引，未运行或分析。按文件收录，不把多份文件算作多道题。图片及附件下载状态见清单；仅按路径/原题分类标方向，binary 等跨方向资料留待分类。
> - 判定依据：original_prose_not_runtime_verified
> - 附件引用：[{"owner_id": "official-d191013710887be97a5b48", "relative_path": "docs/assets/images/wp/2024/week4/reread_1.png", "local_path": "62_官方赛事题库/objects/8b7d3befbc4ec7cc19bbefb6e893ed6c055623372e337ae557ea740c753452c9.blob", "downloaded_bytes": 1819024, "source_url": "https://github.com/pj-newstar/wiki-docs/blob/1a0f2ba21a30f950276396118b315eef0328371c/docs/assets/images/wp/2024/week4/reread_1.png", "sha256": "8b7d3befbc4ec7cc19bbefb6e893ed6c055623372e337ae557ea740c753452c9", "kind": "image", "policy": "reference_only_no_execution"}]

> 原文：https://github.com/pj-newstar/wiki-docs/blob/1a0f2ba21a30f950276396118b315eef0328371c/docs/wp/2024/week4/pwn/reread.md

## 正文

---
titleTemplate: ":title | WriteUp - NewStar CTF 2024"
---

## Reread

先查看沙箱

可以看到除了只允许 open、read、write、dup2 四个系统调用外，还增添了一个额外条件，那就是执行 `read` 系统调用时，第一个参数必须是 `0`

查看主要函数 `vuln`，直接一个栈溢出贴脸，但是溢出的长度很短，算上 `rbp` 的话其实只能覆盖范围地址这一个地方

那该怎么办呢

我们来仔细看一下汇编，通过 gdb 动态调试可以知道，其实是 `lea rsi,[rbp]`

然在前面的栈溢出中我们可以控制 rbp，如果把返回地址覆盖成 `4013AC`，那我们就可以向任意地址写入 `0x50` 字节

同时第二次读入的时候，`rbp` 又是可控的，程序也会执行 `leave ret`，如此，便构成了一次巧妙的栈迁移

至于上文 `sandbox` 中设置的 `syscall_read` 的一参必须为 `0` 的问题，可以使用 dup2 系统调用

具体用法为 `dup2(fd,new_fd)`，可以看作 `new_fd` 是 `fd` 的一个拷贝，同时会 `close(fd)`

所以，EXP 如下
