---
title: "NewStar CTF 2025 / 尤皮·埃克斯历险记（3）"
category: reverse
tags: ["NewStar CTF 2025", "尤皮·埃克斯历险记（3）", "reverse", "官方资料", "docs/wp/2025/week4/reverse/upx-3.md", "origin_tag:imported_cats"]
signals: ["NewStar CTF 2025", "尤皮·埃克斯历险记（3）", "reverse"]
difficulty: medium
source: "https://github.com/pj-newstar/wiki-docs/blob/1a0f2ba21a30f950276396118b315eef0328371c/docs/wp/2025/week4/reverse/upx-3.md"
tools: []
origin: imported_cats
origin_id: "official-988f47b0a97b25f93cc767"
origin_domain: "reverse"
origin_family: "official_event_archive"
origin_event: "NewStar CTF 2025"
origin_year: 2025
origin_license: "MIT"
origin_attribution: ""
origin_verification: "official_source_not_reproduced"
origin_content_sha256: "46be4dee7413a0e557e883b20d933f502314ccca596eac91129f31092e378579"
origin_body_sha256: 1ab86e9d5afb2504a107aaef826aa41d8929f7fe69926c7d1b7b91e90b74a286
origin_title: "NewStar CTF 2025 / 尤皮·埃克斯历险记（3）"
origin_meta:
  asset_refs: []
  basis: "original_prose_not_runtime_verified"
  challenge_key: "newstar:docs/wp/2025/week4/reverse/upx-3"
  chunk_ids: [11381]
  content_sha256: "46be4dee7413a0e557e883b20d933f502314ccca596eac91129f31092e378579"
  domain: "reverse"
  domain_basis: "repository_path"
  event: "NewStar CTF 2025"
  external_links_not_followed: 0
  id: "official-988f47b0a97b25f93cc767"
  kind: "official_wp_prose"
  language: "zh"
  license: "MIT"
  local_path: "62_官方赛事题库/objects/8ec420e900951265c0d084acda161c890303a709cc5d7c2927d1610bab8860fb.blob"
  official_evidence: "https://newstar.wiki/wp/2024/"
  original_path: "docs/wp/2025/week4/reverse/upx-3.md"
  revision: "1a0f2ba21a30f950276396118b315eef0328371c"
  scope_note: "官方发布来源的说明正文；代码单独索引，未运行或分析。按文件收录，不把多份文件算作多道题。图片及附件下载状态见清单；仅按路径/原题分类标方向，binary 等跨方向资料留待分类。"
  source_family: "official_event_archive"
  source_url: "https://github.com/pj-newstar/wiki-docs/blob/1a0f2ba21a30f950276396118b315eef0328371c/docs/wp/2025/week4/reverse/upx-3.md"
  tags: ["NewStar CTF 2025", "尤皮·埃克斯历险记（3）", "reverse", "官方资料", "docs/wp/2025/week4/reverse/upx-3.md"]
  title: "NewStar CTF 2025 / 尤皮·埃克斯历险记（3）"
  verification_status: "official_source_not_reproduced"
  year: 2025
updated: 2026-10-31
---
# NewStar CTF 2025 / 尤皮·埃克斯历险记（3）

> 本文由授权中文赛事 WP 正文导入（阶段 1，仅散文，代码段未导入）。
>
> - 来源：https://github.com/pj-newstar/wiki-docs/blob/1a0f2ba21a30f950276396118b315eef0328371c/docs/wp/2025/week4/reverse/upx-3.md
> - 许可：MIT
> - 署名：（未提供）
> - 文档族：official_event_archive
> - 赛事：NewStar CTF 2025
> - 年份：2025
> - 核验状态：official_source_not_reproduced
> - 正文 sha256：46be4dee7413a0e557e883b20d933f502314ccca596eac91129f31092e378579
> - 导入 ID：official-988f47b0a97b25f93cc767
> - 原 domain：reverse
> - 本地快照：62_官方赛事题库/objects/8ec420e900951265c0d084acda161c890303a709cc5d7c2927d1610bab8860fb.blob
> - 源修订：1a0f2ba21a30f950276396118b315eef0328371c
> - 收录说明：官方发布来源的说明正文；代码单独索引，未运行或分析。按文件收录，不把多份文件算作多道题。图片及附件下载状态见清单；仅按路径/原题分类标方向，binary 等跨方向资料留待分类。
> - 判定依据：original_prose_not_runtime_verified

> 原文：https://github.com/pj-newstar/wiki-docs/blob/1a0f2ba21a30f950276396118b315eef0328371c/docs/wp/2025/week4/reverse/upx-3.md

## 正文

---
titleTemplate: ":title | WriteUp - NewStar CTF 2025"
---

## 尤皮·埃克斯历险记（3）

本题目抹掉了更多的 UPX 特征，可以选择带壳调试/与 week1 的最初版本进行 cmp/scylla 动态调试手动脱壳，这里以带壳调试为例

start 指向 UPX 主函数：

注意到这里有一大段赋予内存执行权限，之后是一个大跳（JUMPOUT)，在这里就跳到了解压后的程序源代码，动态调试在这里下断点来到原程序的start：

这里有result = xxx的就是源程序的main函数：

`sub_7FF63D31154A` 是一个看起来像RC4 KSA初始化的函数：

而其后的“加密函数”`sub_7FF63D311648` 看起来十分诡异：

不仅十分复杂，且变量设置和运算都不合理，甚至最后还出现了main函数，动态调试发现运行到 `sub_7FF63D311648` 中时会触发除零异常，检查汇编：

发现确实存在除零异常，那么这个函数应该是一个垃圾函数，程序中应当有异常处理逻辑来处理这个异常，查看初始化构造函数main_0：

off_7FF63D3153F0指向构造函数表qword_7FF63D3155F0：

查看第一个函数：

发现含有反调试，且含有srand，检查其中的函数：

`0xC0000094` 是除零异常的标识符，说明这里在非调试状态下会注册除以零异常处理的handler，跳转至其中这个每3字节一哈希的加密，之后扫描了垃圾函数 `sub_7FF63D311648`，检索其中的特殊组合[65,66,67,68]并跳转至其后：

发现就是跳到了垃圾函数的结尾，那么也就是说程序中的RC4加密初始化以及密钥均是无效的，真正的加密逻辑是哈希运算，编写脚本解密：

`flag{C4tcH_th3_rUn71m3_3rr0R_0f_d1vId3D_8Y_z3R0}`
