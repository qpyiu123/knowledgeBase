---
title: "NewStar CTF 2024 / No_Output"
category: pwn
tags: ["NewStar CTF 2024", "No_Output", "pwn", "官方资料", "docs/wp/2024/week5/pwn/no_output.md", "origin_tag:imported_cats"]
signals: ["NewStar CTF 2024", "No_Output", "pwn"]
difficulty: medium
source: "https://github.com/pj-newstar/wiki-docs/blob/1a0f2ba21a30f950276396118b315eef0328371c/docs/wp/2024/week5/pwn/no_output.md"
tools: []
origin: imported_cats
origin_id: "official-cb856f0cd8ff04eeb6a787"
origin_domain: "pwn"
origin_family: "official_event_archive"
origin_event: "NewStar CTF 2024"
origin_year: 2024
origin_license: "MIT"
origin_attribution: ""
origin_verification: "official_source_not_reproduced"
origin_content_sha256: "687ddfdc3694b402f715820434f8e446bf5ed236864a3bc5e611205e528a6a5d"
origin_body_sha256: 3c597cdf5aa6eb174686dee918a0d117d12d12a6dd8dd0ee24e5024f4679ae5d
origin_title: "NewStar CTF 2024 / No_Output"
origin_meta:
  asset_refs: []
  basis: "original_prose_not_runtime_verified"
  challenge_key: "newstar:docs/wp/2024/week5/pwn/no_output"
  chunk_ids: [9852]
  content_sha256: "687ddfdc3694b402f715820434f8e446bf5ed236864a3bc5e611205e528a6a5d"
  domain: "pwn"
  domain_basis: "repository_path"
  event: "NewStar CTF 2024"
  external_links_not_followed: 0
  id: "official-cb856f0cd8ff04eeb6a787"
  kind: "official_wp_prose"
  language: "zh"
  license: "MIT"
  local_path: "62_官方赛事题库/objects/67b9466998e6dd37808f3ba8a20f682f5ca6bd781963a3b91e287e2a7460d799.blob"
  official_evidence: "https://newstar.wiki/wp/2024/"
  original_path: "docs/wp/2024/week5/pwn/no_output.md"
  revision: "1a0f2ba21a30f950276396118b315eef0328371c"
  scope_note: "官方发布来源的说明正文；代码单独索引，未运行或分析。按文件收录，不把多份文件算作多道题。图片及附件下载状态见清单；仅按路径/原题分类标方向，binary 等跨方向资料留待分类。"
  source_family: "official_event_archive"
  source_url: "https://github.com/pj-newstar/wiki-docs/blob/1a0f2ba21a30f950276396118b315eef0328371c/docs/wp/2024/week5/pwn/no_output.md"
  tags: ["NewStar CTF 2024", "No_Output", "pwn", "官方资料", "docs/wp/2024/week5/pwn/no_output.md"]
  title: "NewStar CTF 2024 / No_Output"
  verification_status: "official_source_not_reproduced"
  year: 2024
updated: 2026-10-31
---
# NewStar CTF 2024 / No_Output

> 本文由授权中文赛事 WP 正文导入（阶段 1，仅散文，代码段未导入）。
>
> - 来源：https://github.com/pj-newstar/wiki-docs/blob/1a0f2ba21a30f950276396118b315eef0328371c/docs/wp/2024/week5/pwn/no_output.md
> - 许可：MIT
> - 署名：（未提供）
> - 文档族：official_event_archive
> - 赛事：NewStar CTF 2024
> - 年份：2024
> - 核验状态：official_source_not_reproduced
> - 正文 sha256：687ddfdc3694b402f715820434f8e446bf5ed236864a3bc5e611205e528a6a5d
> - 导入 ID：official-cb856f0cd8ff04eeb6a787
> - 原 domain：pwn
> - 本地快照：62_官方赛事题库/objects/67b9466998e6dd37808f3ba8a20f682f5ca6bd781963a3b91e287e2a7460d799.blob
> - 源修订：1a0f2ba21a30f950276396118b315eef0328371c
> - 收录说明：官方发布来源的说明正文；代码单独索引，未运行或分析。按文件收录，不把多份文件算作多道题。图片及附件下载状态见清单；仅按路径/原题分类标方向，binary 等跨方向资料留待分类。
> - 判定依据：original_prose_not_runtime_verified

> 原文：https://github.com/pj-newstar/wiki-docs/blob/1a0f2ba21a30f950276396118b315eef0328371c/docs/wp/2024/week5/pwn/no_output.md

## 正文

---
titleTemplate: ":title | WriteUp - NewStar CTF 2024"
---

## No_Output

程序是无沙箱的 shellcode，但关闭了 `0` `1` `2` 描述符，即关闭了标准输入，标准输出和标准错误输出

本题的解法也有很多，由于靶机是出网的，我们可以选择直接连上一个公网的服务器，使用 `send` 将 flag 发送到服务器上

`connect` 的参数可以写一个 C 语言的 demo，编译后动调将内存复制出来

也可以使用两个进程，使用一个去 ptrace 另一个，直接修改他的程序段内存，将 `close012` 给 nop 掉<span data-desc>（靶机的 pid 初始都是一样的）</span>

当然，也可以使用侧信道爆破
