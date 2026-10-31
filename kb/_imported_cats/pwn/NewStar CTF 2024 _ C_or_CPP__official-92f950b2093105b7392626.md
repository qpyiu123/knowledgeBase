---
title: "NewStar CTF 2024 / C_or_CPP"
category: pwn
tags: ["NewStar CTF 2024", "C_or_CPP", "pwn", "官方资料", "docs/wp/2024/week5/pwn/c_or_cpp.md", "origin_tag:imported_cats"]
signals: ["NewStar CTF 2024", "C_or_CPP", "pwn"]
difficulty: medium
source: "https://github.com/pj-newstar/wiki-docs/blob/1a0f2ba21a30f950276396118b315eef0328371c/docs/wp/2024/week5/pwn/c_or_cpp.md"
tools: []
origin: imported_cats
origin_id: "official-92f950b2093105b7392626"
origin_domain: "pwn"
origin_family: "official_event_archive"
origin_event: "NewStar CTF 2024"
origin_year: 2024
origin_license: "MIT"
origin_attribution: ""
origin_verification: "official_source_not_reproduced"
origin_content_sha256: "e4948a0ac253ee177ae081b53b30755b98c1551de5c3ef7f429d62eb61a35750"
origin_body_sha256: be9be9f48640eb6700787bcf1155b8003a10137a0dfbf0bc7bae3087282e9415
origin_title: "NewStar CTF 2024 / C_or_CPP"
origin_meta:
  asset_refs: [{"downloaded_bytes": 85461, "kind": "image", "local_path": "62_官方赛事题库/objects/ba797c551678b73e8e15d587e360360e7727b2e9544583546b296aaff0f0e635.blob", "owner_id": "official-92f950b2093105b7392626", "policy": "reference_only_no_execution", "relative_path": "docs/assets/images/wp/2024/week5/c_or_cpp_1.png", "sha256": "ba797c551678b73e8e15d587e360360e7727b2e9544583546b296aaff0f0e635", "source_url": "https://github.com/pj-newstar/wiki-docs/blob/1a0f2ba21a30f950276396118b315eef0328371c/docs/assets/images/wp/2024/week5/c_or_cpp_1.png"}]
  basis: "original_prose_not_runtime_verified"
  challenge_key: "newstar:docs/wp/2024/week5/pwn/c_or_cpp"
  chunk_ids: [9796, 9797]
  content_sha256: "e4948a0ac253ee177ae081b53b30755b98c1551de5c3ef7f429d62eb61a35750"
  domain: "pwn"
  domain_basis: "repository_path"
  event: "NewStar CTF 2024"
  external_links_not_followed: 0
  id: "official-92f950b2093105b7392626"
  kind: "official_wp_prose"
  language: "zh"
  license: "MIT"
  local_path: "62_官方赛事题库/objects/c9940e5c63b35e1f010f13fe384d9ccfe09cd75de409b5a08a2235adb2c75ea8.blob"
  official_evidence: "https://newstar.wiki/wp/2024/"
  original_path: "docs/wp/2024/week5/pwn/c_or_cpp.md"
  revision: "1a0f2ba21a30f950276396118b315eef0328371c"
  scope_note: "官方发布来源的说明正文；代码单独索引，未运行或分析。按文件收录，不把多份文件算作多道题。图片及附件下载状态见清单；仅按路径/原题分类标方向，binary 等跨方向资料留待分类。"
  source_family: "official_event_archive"
  source_url: "https://github.com/pj-newstar/wiki-docs/blob/1a0f2ba21a30f950276396118b315eef0328371c/docs/wp/2024/week5/pwn/c_or_cpp.md"
  tags: ["NewStar CTF 2024", "C_or_CPP", "pwn", "官方资料", "docs/wp/2024/week5/pwn/c_or_cpp.md"]
  title: "NewStar CTF 2024 / C_or_CPP"
  verification_status: "official_source_not_reproduced"
  year: 2024
updated: 2026-10-31
---
# NewStar CTF 2024 / C_or_CPP

> 本文由授权中文赛事 WP 正文导入（阶段 1，仅散文，代码段未导入）。
>
> - 来源：https://github.com/pj-newstar/wiki-docs/blob/1a0f2ba21a30f950276396118b315eef0328371c/docs/wp/2024/week5/pwn/c_or_cpp.md
> - 许可：MIT
> - 署名：（未提供）
> - 文档族：official_event_archive
> - 赛事：NewStar CTF 2024
> - 年份：2024
> - 核验状态：official_source_not_reproduced
> - 正文 sha256：e4948a0ac253ee177ae081b53b30755b98c1551de5c3ef7f429d62eb61a35750
> - 导入 ID：official-92f950b2093105b7392626
> - 原 domain：pwn
> - 本地快照：62_官方赛事题库/objects/c9940e5c63b35e1f010f13fe384d9ccfe09cd75de409b5a08a2235adb2c75ea8.blob
> - 源修订：1a0f2ba21a30f950276396118b315eef0328371c
> - 收录说明：官方发布来源的说明正文；代码单独索引，未运行或分析。按文件收录，不把多份文件算作多道题。图片及附件下载状态见清单；仅按路径/原题分类标方向，binary 等跨方向资料留待分类。
> - 判定依据：original_prose_not_runtime_verified
> - 附件引用：[{"owner_id": "official-92f950b2093105b7392626", "relative_path": "docs/assets/images/wp/2024/week5/c_or_cpp_1.png", "local_path": "62_官方赛事题库/objects/ba797c551678b73e8e15d587e360360e7727b2e9544583546b296aaff0f0e635.blob", "downloaded_bytes": 85461, "source_url": "https://github.com/pj-newstar/wiki-docs/blob/1a0f2ba21a30f950276396118b315eef0328371c/docs/assets/images/wp/2024/week5/c_or_cpp_1.png", "sha256": "ba797c551678b73e8e15d587e360360e7727b2e9544583546b296aaff0f0e635", "kind": "image", "policy": "reference_only_no_execution"}]

> 原文：https://github.com/pj-newstar/wiki-docs/blob/1a0f2ba21a30f950276396118b315eef0328371c/docs/wp/2024/week5/pwn/c_or_cpp.md

## 正文

---
titleTemplate: ":title | WriteUp - NewStar CTF 2024"
---

import Container from '@/components/docs/Container.vue'

## C_or_CPP

首先拖入 IDA 分析，这是一个用 C 和 CPP 来实现相同操作对比的程序

题目存在两个漏洞

一个是位于功能 2 里面的

一个是位于功能 2 里面的

一个是位于功能 5 里面的

第一个漏洞首先 read 了 `0x50` 个字符，乍一看可能没有发现溢出，但结合上后面的 `printf("%s")`，即可实现泄露地址

`printf("%s")` 会一直输出直到遇到 `\x00`

第二个漏洞先使用 `cin` 输入了字符串，再将它 memcpy 到 `dest` 字符串中，而 `dest` 是存放在栈上的，因此存在栈溢出

因为程序是使用 `g++` 编译的，相对可用的 gadget 会相当少，所以靠第一次泄露的地址，用 libc 的 gadget 来实现 ROP
