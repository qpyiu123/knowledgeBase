---
title: "NewStar CTF 2024 / Easy_Shellcode"
category: pwn
tags: ["NewStar CTF 2024", "Easy_Shellcode", "pwn", "官方资料", "docs/wp/2024/week3/pwn/easy-shellcode.md", "origin_tag:imported_cats"]
signals: ["NewStar CTF 2024", "Easy_Shellcode", "pwn"]
difficulty: medium
source: "https://github.com/pj-newstar/wiki-docs/blob/1a0f2ba21a30f950276396118b315eef0328371c/docs/wp/2024/week3/pwn/easy-shellcode.md"
tools: []
origin: imported_cats
origin_id: "official-d661f1c67e776386897a78"
origin_domain: "pwn"
origin_family: "official_event_archive"
origin_event: "NewStar CTF 2024"
origin_year: 2024
origin_license: "MIT"
origin_attribution: ""
origin_verification: "official_source_not_reproduced"
origin_content_sha256: "687ddfdc3694b402f715820434f8e446bf5ed236864a3bc5e611205e528a6a5d"
origin_body_sha256: bf97a79d3dad62cb0af7811dbf1bd33cd90534d3f252c6d5cc08e676146e5cb0
origin_title: "NewStar CTF 2024 / Easy_Shellcode"
origin_meta:
  asset_refs: []
  basis: "original_prose_not_runtime_verified"
  challenge_key: "newstar:docs/wp/2024/week3/pwn/easy-shellcode"
  chunk_ids: [9040]
  content_sha256: "687ddfdc3694b402f715820434f8e446bf5ed236864a3bc5e611205e528a6a5d"
  domain: "pwn"
  domain_basis: "repository_path"
  event: "NewStar CTF 2024"
  external_links_not_followed: 1
  id: "official-d661f1c67e776386897a78"
  kind: "official_wp_prose"
  language: "zh"
  license: "MIT"
  local_path: "62_官方赛事题库/objects/4984ebe8c69ee64950f321548650707b50a38c67874d92ae1b390fb4f8be4bbd.blob"
  official_evidence: "https://newstar.wiki/wp/2024/"
  original_path: "docs/wp/2024/week3/pwn/easy-shellcode.md"
  revision: "1a0f2ba21a30f950276396118b315eef0328371c"
  scope_note: "官方发布来源的说明正文；代码单独索引，未运行或分析。按文件收录，不把多份文件算作多道题。图片及附件下载状态见清单；仅按路径/原题分类标方向，binary 等跨方向资料留待分类。"
  source_family: "official_event_archive"
  source_url: "https://github.com/pj-newstar/wiki-docs/blob/1a0f2ba21a30f950276396118b315eef0328371c/docs/wp/2024/week3/pwn/easy-shellcode.md"
  tags: ["NewStar CTF 2024", "Easy_Shellcode", "pwn", "官方资料", "docs/wp/2024/week3/pwn/easy-shellcode.md"]
  title: "NewStar CTF 2024 / Easy_Shellcode"
  verification_status: "official_source_not_reproduced"
  year: 2024
updated: 2026-10-31
---
# NewStar CTF 2024 / Easy_Shellcode

> 本文由授权中文赛事 WP 正文导入（阶段 1，仅散文，代码段未导入）。
>
> - 来源：https://github.com/pj-newstar/wiki-docs/blob/1a0f2ba21a30f950276396118b315eef0328371c/docs/wp/2024/week3/pwn/easy-shellcode.md
> - 许可：MIT
> - 署名：（未提供）
> - 文档族：official_event_archive
> - 赛事：NewStar CTF 2024
> - 年份：2024
> - 核验状态：official_source_not_reproduced
> - 正文 sha256：687ddfdc3694b402f715820434f8e446bf5ed236864a3bc5e611205e528a6a5d
> - 导入 ID：official-d661f1c67e776386897a78
> - 原 domain：pwn
> - 本地快照：62_官方赛事题库/objects/4984ebe8c69ee64950f321548650707b50a38c67874d92ae1b390fb4f8be4bbd.blob
> - 源修订：1a0f2ba21a30f950276396118b315eef0328371c
> - 收录说明：官方发布来源的说明正文；代码单独索引，未运行或分析。按文件收录，不把多份文件算作多道题。图片及附件下载状态见清单；仅按路径/原题分类标方向，binary 等跨方向资料留待分类。
> - 判定依据：original_prose_not_runtime_verified

> 原文：https://github.com/pj-newstar/wiki-docs/blob/1a0f2ba21a30f950276396118b315eef0328371c/docs/wp/2024/week3/pwn/easy-shellcode.md

## 正文

---
titleTemplate: ":title | WriteUp - NewStar CTF 2024"
---

## Easy_Shellcode

将程序拖入 IDA 分析，发现程序有一个名为 `sandbox` 的函数，通过 `seccomp-tools dump ./pwn`，可得出程序的沙箱规则

可以发现，程序禁用了 `execve` 和 `execveat`，不能直接 get shell，需要通过 ORW<span data-desc>（open read write）</span>来得到 flag

同时，程序也禁用了常规的 `open` `read` `write`，需要我们找到他们的替代品

- 对于 `open`，我们可以选择使用 `openat` 或者 `openat2`<span data-desc>（本题已禁用）</span>
- 对于 `read`，我们可以选择使用 `readv`、`preadv`、`preadv2`<span data-desc>（本题可用）</span>，`pread64` 或者 `mmap`<span data-desc>（本题可用）</span>
- 对于 `write`，我们可以选择使用 `writev`<span data-desc>（本题可用）</span>，`sendfile`<span data-desc>（本题可用，且能省略`read`）</span>等

注意在使用 shellcraft 时需恢复 `rsp` 寄存器

::: tip
有关沙箱 ORW 的学习资料可参见该文章：[seccomp 学习（2）](https://blog.csdn.net/qq_54218833/article/details/134205383)
:::
