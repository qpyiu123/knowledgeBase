---
title: "NewStar CTF 2024 / Simple_Shellcode"
category: pwn
tags: ["NewStar CTF 2024", "Simple_Shellcode", "pwn", "官方资料", "docs/wp/2024/week5/pwn/simple_shellcode.md", "origin_tag:imported_cats"]
signals: ["NewStar CTF 2024", "Simple_Shellcode", "pwn"]
difficulty: medium
source: "https://github.com/pj-newstar/wiki-docs/blob/1a0f2ba21a30f950276396118b315eef0328371c/docs/wp/2024/week5/pwn/simple_shellcode.md"
tools: []
origin: imported_cats
origin_id: "official-f51fb1c1c8fed3f2d7231d"
origin_domain: "pwn"
origin_family: "official_event_archive"
origin_event: "NewStar CTF 2024"
origin_year: 2024
origin_license: "MIT"
origin_attribution: ""
origin_verification: "official_source_not_reproduced"
origin_content_sha256: "e4948a0ac253ee177ae081b53b30755b98c1551de5c3ef7f429d62eb61a35750"
origin_body_sha256: d697b68a652f3db3a3995824a467657c86e8e48bab04788f28a74dfbfd4940c0
origin_title: "NewStar CTF 2024 / Simple_Shellcode"
origin_meta:
  asset_refs: [{"downloaded_bytes": 2351989, "kind": "image", "local_path": "62_官方赛事题库/objects/4716e8d0387a3055533bfceaa739ba74ba046d9eacf9ac2d13c5f6576417a15c.blob", "owner_id": "official-f51fb1c1c8fed3f2d7231d", "policy": "reference_only_no_execution", "relative_path": "docs/assets/images/wp/2024/week5/simple_shellcode_1.png", "sha256": "4716e8d0387a3055533bfceaa739ba74ba046d9eacf9ac2d13c5f6576417a15c", "source_url": "https://github.com/pj-newstar/wiki-docs/blob/1a0f2ba21a30f950276396118b315eef0328371c/docs/assets/images/wp/2024/week5/simple_shellcode_1.png"}]
  basis: "original_prose_not_runtime_verified"
  challenge_key: "newstar:docs/wp/2024/week5/pwn/simple_shellcode"
  chunk_ids: [9858, 9859]
  content_sha256: "e4948a0ac253ee177ae081b53b30755b98c1551de5c3ef7f429d62eb61a35750"
  domain: "pwn"
  domain_basis: "repository_path"
  event: "NewStar CTF 2024"
  external_links_not_followed: 0
  id: "official-f51fb1c1c8fed3f2d7231d"
  kind: "official_wp_prose"
  language: "zh"
  license: "MIT"
  local_path: "62_官方赛事题库/objects/a6904f6840c628030ac198ae9258aa2306789e7f18eac855ffb95c8734b8a308.blob"
  official_evidence: "https://newstar.wiki/wp/2024/"
  original_path: "docs/wp/2024/week5/pwn/simple_shellcode.md"
  revision: "1a0f2ba21a30f950276396118b315eef0328371c"
  scope_note: "官方发布来源的说明正文；代码单独索引，未运行或分析。按文件收录，不把多份文件算作多道题。图片及附件下载状态见清单；仅按路径/原题分类标方向，binary 等跨方向资料留待分类。"
  source_family: "official_event_archive"
  source_url: "https://github.com/pj-newstar/wiki-docs/blob/1a0f2ba21a30f950276396118b315eef0328371c/docs/wp/2024/week5/pwn/simple_shellcode.md"
  tags: ["NewStar CTF 2024", "Simple_Shellcode", "pwn", "官方资料", "docs/wp/2024/week5/pwn/simple_shellcode.md"]
  title: "NewStar CTF 2024 / Simple_Shellcode"
  verification_status: "official_source_not_reproduced"
  year: 2024
updated: 2026-10-31
---
# NewStar CTF 2024 / Simple_Shellcode

> 本文由授权中文赛事 WP 正文导入（阶段 1，仅散文，代码段未导入）。
>
> - 来源：https://github.com/pj-newstar/wiki-docs/blob/1a0f2ba21a30f950276396118b315eef0328371c/docs/wp/2024/week5/pwn/simple_shellcode.md
> - 许可：MIT
> - 署名：（未提供）
> - 文档族：official_event_archive
> - 赛事：NewStar CTF 2024
> - 年份：2024
> - 核验状态：official_source_not_reproduced
> - 正文 sha256：e4948a0ac253ee177ae081b53b30755b98c1551de5c3ef7f429d62eb61a35750
> - 导入 ID：official-f51fb1c1c8fed3f2d7231d
> - 原 domain：pwn
> - 本地快照：62_官方赛事题库/objects/a6904f6840c628030ac198ae9258aa2306789e7f18eac855ffb95c8734b8a308.blob
> - 源修订：1a0f2ba21a30f950276396118b315eef0328371c
> - 收录说明：官方发布来源的说明正文；代码单独索引，未运行或分析。按文件收录，不把多份文件算作多道题。图片及附件下载状态见清单；仅按路径/原题分类标方向，binary 等跨方向资料留待分类。
> - 判定依据：original_prose_not_runtime_verified
> - 附件引用：[{"owner_id": "official-f51fb1c1c8fed3f2d7231d", "relative_path": "docs/assets/images/wp/2024/week5/simple_shellcode_1.png", "local_path": "62_官方赛事题库/objects/4716e8d0387a3055533bfceaa739ba74ba046d9eacf9ac2d13c5f6576417a15c.blob", "downloaded_bytes": 2351989, "source_url": "https://github.com/pj-newstar/wiki-docs/blob/1a0f2ba21a30f950276396118b315eef0328371c/docs/assets/images/wp/2024/week5/simple_shellcode_1.png", "sha256": "4716e8d0387a3055533bfceaa739ba74ba046d9eacf9ac2d13c5f6576417a15c", "kind": "image", "policy": "reference_only_no_execution"}]

> 原文：https://github.com/pj-newstar/wiki-docs/blob/1a0f2ba21a30f950276396118b315eef0328371c/docs/wp/2024/week5/pwn/simple_shellcode.md

## 正文

---
titleTemplate: ":title | WriteUp - NewStar CTF 2024"
---

import Container from '@/components/docs/Container.vue'

## Simple_Shellcode

程序有两个功能

一是输入 shellcode，二是运行 shellcode

其中，`v4` 是用来存储 shellcode 的 `vector`

在输入功能中，一次只能输入 8 个字符

检测功能中，如果检测到 shellcode 含有非字母或数字，就会删掉这段 shellcode

当然，使用 AE64 直接生成 shellcode 也是可以的

通过查看 `erase` 的源码，发现 `erase` 是通过将后面的元素 MOVE 到前面，然后 `--finish` 实现的

而在程序实现的删除算法中，`erase` 后没有将 `i--`，这就会导致，如果 `idx=2` 的元素被删除了，`i++`（`i=3`），而 `erase` 会将后面的元素 MOVE 到前面，原本 `idx=3` 的元素会移动到 `idx=2`，这样会导致原本 `idx=3` 的元素绕过检测

也就是说，我们将会被删除的元素输入两次，即可绕过检测

对于沙箱，洒洒水啦：openat + mmap + writev
