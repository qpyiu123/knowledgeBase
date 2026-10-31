---
title: "NewStar CTF 2025 / 尤皮·埃克斯历险记（1）"
category: reverse
tags: ["NewStar CTF 2025", "尤皮·埃克斯历险记（1）", "reverse", "官方资料", "docs/wp/2025/week2/reverse/upx-1.md", "origin_tag:imported_cats"]
signals: ["NewStar CTF 2025", "尤皮·埃克斯历险记（1）", "reverse"]
difficulty: medium
source: "https://github.com/pj-newstar/wiki-docs/blob/1a0f2ba21a30f950276396118b315eef0328371c/docs/wp/2025/week2/reverse/upx-1.md"
tools: []
origin: imported_cats
origin_id: "official-20d7fbc8ed6946a8f47698"
origin_domain: "reverse"
origin_family: "official_event_archive"
origin_event: "NewStar CTF 2025"
origin_year: 2025
origin_license: "MIT"
origin_attribution: ""
origin_verification: "official_source_not_reproduced"
origin_content_sha256: "3505c69bd87af33f36578bb0699417dda5647a640603bba828608be30f9ca761"
origin_body_sha256: 3faa031acb21a184ac06ccb9d9c0640d03e9b88a768e33d94ac824088b633628
origin_title: "NewStar CTF 2025 / 尤皮·埃克斯历险记（1）"
origin_meta:
  asset_refs: []
  basis: "original_prose_not_runtime_verified"
  challenge_key: "newstar:docs/wp/2025/week2/reverse/upx-1"
  chunk_ids: [10775, 10776]
  content_sha256: "3505c69bd87af33f36578bb0699417dda5647a640603bba828608be30f9ca761"
  domain: "reverse"
  domain_basis: "repository_path"
  event: "NewStar CTF 2025"
  external_links_not_followed: 0
  id: "official-20d7fbc8ed6946a8f47698"
  kind: "official_wp_prose"
  language: "zh"
  license: "MIT"
  local_path: "62_官方赛事题库/objects/8e195228f919729978a49cd9adce994f0f8f6b3a6f8d421a1f810fb876efe01b.blob"
  official_evidence: "https://newstar.wiki/wp/2024/"
  original_path: "docs/wp/2025/week2/reverse/upx-1.md"
  revision: "1a0f2ba21a30f950276396118b315eef0328371c"
  scope_note: "官方发布来源的说明正文；代码单独索引，未运行或分析。按文件收录，不把多份文件算作多道题。图片及附件下载状态见清单；仅按路径/原题分类标方向，binary 等跨方向资料留待分类。"
  source_family: "official_event_archive"
  source_url: "https://github.com/pj-newstar/wiki-docs/blob/1a0f2ba21a30f950276396118b315eef0328371c/docs/wp/2025/week2/reverse/upx-1.md"
  tags: ["NewStar CTF 2025", "尤皮·埃克斯历险记（1）", "reverse", "官方资料", "docs/wp/2025/week2/reverse/upx-1.md"]
  title: "NewStar CTF 2025 / 尤皮·埃克斯历险记（1）"
  verification_status: "official_source_not_reproduced"
  year: 2025
updated: 2026-10-31
---
# NewStar CTF 2025 / 尤皮·埃克斯历险记（1）

> 本文由授权中文赛事 WP 正文导入（阶段 1，仅散文，代码段未导入）。
>
> - 来源：https://github.com/pj-newstar/wiki-docs/blob/1a0f2ba21a30f950276396118b315eef0328371c/docs/wp/2025/week2/reverse/upx-1.md
> - 许可：MIT
> - 署名：（未提供）
> - 文档族：official_event_archive
> - 赛事：NewStar CTF 2025
> - 年份：2025
> - 核验状态：official_source_not_reproduced
> - 正文 sha256：3505c69bd87af33f36578bb0699417dda5647a640603bba828608be30f9ca761
> - 导入 ID：official-20d7fbc8ed6946a8f47698
> - 原 domain：reverse
> - 本地快照：62_官方赛事题库/objects/8e195228f919729978a49cd9adce994f0f8f6b3a6f8d421a1f810fb876efe01b.blob
> - 源修订：1a0f2ba21a30f950276396118b315eef0328371c
> - 收录说明：官方发布来源的说明正文；代码单独索引，未运行或分析。按文件收录，不把多份文件算作多道题。图片及附件下载状态见清单；仅按路径/原题分类标方向，binary 等跨方向资料留待分类。
> - 判定依据：original_prose_not_runtime_verified

> 原文：https://github.com/pj-newstar/wiki-docs/blob/1a0f2ba21a30f950276396118b315eef0328371c/docs/wp/2025/week2/reverse/upx-1.md

## 正文

---
titleTemplate: ":title | WriteUp - NewStar CTF 2025"
---

import Container from '@/components/docs/Container.vue'

## 尤皮·埃克斯历险记（1）

本题考查 UPX 脱壳及反调试。

将 exe 拖入 IDA 之后发现主函数不见了，程序只有一两个函数，再用 DIE 或者 exeinfope 查壳，发现有 UPX 壳。

`upx -d` 可以脱壳。

`upx -d` 可以脱壳。

脱壳后查看主函数：

发现给出了密文，还有一个 `encrypt` 函数：

是一个凯撒密码的变体：

是一个凯撒密码的变体：

1. 如果字符是数字，那么反转其在 0~9 之间的顺序（也就是 `0x69-C`），0 ↔ 9，1 ↔ 8，...

2. 如果是字母，反转其在字母表中的顺序并切换大小写（也就是 `0xBB-C`），A ↔ z，b ↔ Y，...

而主函数后面逻辑中的 `IsDebuggerPresent` 函数是**反调试**函数，当存在调试器时返回真，否则为假。

由于题目正常运行时肯定不存在调试器，所以这里一定会按假的分支走<span data-desc>（也就是异或 `0x3C`）</span>，接下来动态调试，在 `std::string::string((std::string *)v11);` 这一行下断点，提取前面的密文`69736668474A09747E63550A790A75546A636A09547E636A5164757E777B04057141`。

在 cyberchef fromhex 后异或 `0x3C` 后得到 `UOZT{v5HB_i6E6IhV_V5hB_VmXIBKG89M}`，然后编写一个简单的 python 脚本即可恢复 flag：

flag 为：`flag{E4sy_R3v3rSe_e4Sy_eNcrypt10n}`。
