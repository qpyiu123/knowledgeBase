---
title: "NewStar CTF 2025 / 尤皮·埃克斯历险记（2）"
category: reverse
tags: ["NewStar CTF 2025", "尤皮·埃克斯历险记（2）", "reverse", "官方资料", "docs/wp/2025/week3/reverse/upx-2.md", "origin_tag:imported_cats"]
signals: ["NewStar CTF 2025", "尤皮·埃克斯历险记（2）", "reverse"]
difficulty: medium
source: "https://github.com/pj-newstar/wiki-docs/blob/1a0f2ba21a30f950276396118b315eef0328371c/docs/wp/2025/week3/reverse/upx-2.md"
tools: []
origin: imported_cats
origin_id: "official-2f7af2c933aa8f6604f983"
origin_domain: "reverse"
origin_family: "official_event_archive"
origin_event: "NewStar CTF 2025"
origin_year: 2025
origin_license: "MIT"
origin_attribution: ""
origin_verification: "official_source_not_reproduced"
origin_content_sha256: "46be4dee7413a0e557e883b20d933f502314ccca596eac91129f31092e378579"
origin_body_sha256: f3378903cb7d2cdfcd918415d653f6677585988a586e2b635aa8e40c34de7b5b
origin_title: "NewStar CTF 2025 / 尤皮·埃克斯历险记（2）"
origin_meta:
  asset_refs: []
  basis: "original_prose_not_runtime_verified"
  challenge_key: "newstar:docs/wp/2025/week3/reverse/upx-2"
  chunk_ids: [11110]
  content_sha256: "46be4dee7413a0e557e883b20d933f502314ccca596eac91129f31092e378579"
  domain: "reverse"
  domain_basis: "repository_path"
  event: "NewStar CTF 2025"
  external_links_not_followed: 0
  id: "official-2f7af2c933aa8f6604f983"
  kind: "official_wp_prose"
  language: "zh"
  license: "MIT"
  local_path: "62_官方赛事题库/objects/63e1ac4719585127817f13126979ffc5e6e47574fbd22d35907aecca2d14b8e3.blob"
  official_evidence: "https://newstar.wiki/wp/2024/"
  original_path: "docs/wp/2025/week3/reverse/upx-2.md"
  revision: "1a0f2ba21a30f950276396118b315eef0328371c"
  scope_note: "官方发布来源的说明正文；代码单独索引，未运行或分析。按文件收录，不把多份文件算作多道题。图片及附件下载状态见清单；仅按路径/原题分类标方向，binary 等跨方向资料留待分类。"
  source_family: "official_event_archive"
  source_url: "https://github.com/pj-newstar/wiki-docs/blob/1a0f2ba21a30f950276396118b315eef0328371c/docs/wp/2025/week3/reverse/upx-2.md"
  tags: ["NewStar CTF 2025", "尤皮·埃克斯历险记（2）", "reverse", "官方资料", "docs/wp/2025/week3/reverse/upx-2.md"]
  title: "NewStar CTF 2025 / 尤皮·埃克斯历险记（2）"
  verification_status: "official_source_not_reproduced"
  year: 2025
updated: 2026-10-31
---
# NewStar CTF 2025 / 尤皮·埃克斯历险记（2）

> 本文由授权中文赛事 WP 正文导入（阶段 1，仅散文，代码段未导入）。
>
> - 来源：https://github.com/pj-newstar/wiki-docs/blob/1a0f2ba21a30f950276396118b315eef0328371c/docs/wp/2025/week3/reverse/upx-2.md
> - 许可：MIT
> - 署名：（未提供）
> - 文档族：official_event_archive
> - 赛事：NewStar CTF 2025
> - 年份：2025
> - 核验状态：official_source_not_reproduced
> - 正文 sha256：46be4dee7413a0e557e883b20d933f502314ccca596eac91129f31092e378579
> - 导入 ID：official-2f7af2c933aa8f6604f983
> - 原 domain：reverse
> - 本地快照：62_官方赛事题库/objects/63e1ac4719585127817f13126979ffc5e6e47574fbd22d35907aecca2d14b8e3.blob
> - 源修订：1a0f2ba21a30f950276396118b315eef0328371c
> - 收录说明：官方发布来源的说明正文；代码单独索引，未运行或分析。按文件收录，不把多份文件算作多道题。图片及附件下载状态见清单；仅按路径/原题分类标方向，binary 等跨方向资料留待分类。
> - 判定依据：original_prose_not_runtime_verified

> 原文：https://github.com/pj-newstar/wiki-docs/blob/1a0f2ba21a30f950276396118b315eef0328371c/docs/wp/2025/week3/reverse/upx-2.md

## 正文

---
titleTemplate: ":title | WriteUp - NewStar CTF 2025"
---

## 尤皮·埃克斯历险记（2）

UPX 标识符改了，和正常的相比改了 UPX012!和版本号，改回去就行了，可以和 UPX1 cmp 一下
改完脱壳查看主函数：

FLAG 长度为 48，查看加密函数：

是一个自定义加密，一次加密12字节，其中有多组key和3个iv，查看轮函数：

d810是去不掉这种混淆的，可以把函数复制出来，将含有a的行包裹上printf，这样打印出来的就是按顺序执行的加密：

编写脚本同构加密和解密即可：

`flag{CoN7r0l_F10w_F14t73n1nG_C4N_b3_c0NfU5iNg!!}`
