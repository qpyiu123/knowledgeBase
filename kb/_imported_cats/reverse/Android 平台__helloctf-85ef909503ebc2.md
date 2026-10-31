---
title: "Android 平台"
category: reverse
tags: ["reverse", "helloctf", "hc-reverse", "Android.md", "origin_tag:imported_cats"]
signals: ["reverse", "helloctf", "hc-reverse"]
difficulty: medium
source: "https://github.com/ProbiusOfficial/Hello-CTF/blob/8e9d6396a0d1ccc1f606810d575d1abb3dd567de/docs/hc-reverse/Android.md"
tools: []
origin: imported_cats
origin_id: "helloctf-85ef909503ebc2"
origin_domain: "reverse"
origin_family: "helloctf"
origin_event: ""
origin_year: ""
origin_license: "CC-BY-SA-4.0"
origin_attribution: "ProbiusOfficial/Hello-CTF contributors; original at https://github.com/ProbiusOfficial/Hello-CTF/blob/8e9d6396a0d1ccc1f606810d575d1abb3dd567de/docs/hc-reverse/Android.md"
origin_verification: "source_document_not_reproduced"
origin_content_sha256: "304fc5c5de70061befcf917ba7d3cd3576e23130b53411a31069953e69b2f686"
origin_body_sha256: 481181eea8151adcaefa85d9e00cf944ff68f35357f6b49e635fab5f8c927dc7
origin_title: "Android 平台"
origin_meta:
  asset_refs: []
  attribution: "ProbiusOfficial/Hello-CTF contributors; original at https://github.com/ProbiusOfficial/Hello-CTF/blob/8e9d6396a0d1ccc1f606810d575d1abb3dd567de/docs/hc-reverse/Android.md"
  basis: "original_prose_not_runtime_verified"
  chunk_ids: [4659]
  content_sha256: "304fc5c5de70061befcf917ba7d3cd3576e23130b53411a31069953e69b2f686"
  domain: "reverse"
  fetched_at_utc: "2026-10-22T17:55:11.323038+00:00"
  id: "helloctf-85ef909503ebc2"
  kind: "licensed_chinese_reference"
  language: "zh"
  license: "CC-BY-SA-4.0"
  license_local_path: "61_中文赛事资料/来源与许可/helloctf/LICENSE.txt"
  local_path: "61_中文赛事资料/开源正文快照/helloctf/docs/hc-reverse/Android.md"
  response_sha256: "1e0555d68336a928409df30a00c9b059a4e5f9a49bec72a7677fd5c06fe5ab55"
  scope_note: "开源中文文档正文。原作者与版本已保留；检索正文省略代码块、缩进代码和图片，完整 Markdown 另存；未复现。"
  source_family: "helloctf"
  source_revision: "8e9d6396a0d1ccc1f606810d575d1abb3dd567de"
  source_url: "https://github.com/ProbiusOfficial/Hello-CTF/blob/8e9d6396a0d1ccc1f606810d575d1abb3dd567de/docs/hc-reverse/Android.md"
  tags: ["reverse", "helloctf", "hc-reverse", "Android.md"]
  title: "Android 平台"
  verification_status: "source_document_not_reproduced"
  year: ""
updated: 2026-10-31
---
# Android 平台

> 本文由授权中文赛事 WP 正文导入（阶段 1，仅散文，代码段未导入）。
>
> - 来源：https://github.com/ProbiusOfficial/Hello-CTF/blob/8e9d6396a0d1ccc1f606810d575d1abb3dd567de/docs/hc-reverse/Android.md
> - 许可：CC-BY-SA-4.0
> - 署名：ProbiusOfficial/Hello-CTF contributors; original at https://github.com/ProbiusOfficial/Hello-CTF/blob/8e9d6396a0d1ccc1f606810d575d1abb3dd567de/docs/hc-reverse/Android.md
> - 文档族：helloctf
> - 赛事：（无）
> - 年份：（无）
> - 核验状态：source_document_not_reproduced
> - 正文 sha256：304fc5c5de70061befcf917ba7d3cd3576e23130b53411a31069953e69b2f686
> - 导入 ID：helloctf-85ef909503ebc2
> - 原 domain：reverse
> - 许可文件：61_中文赛事资料/来源与许可/helloctf/LICENSE.txt
> - 本地快照：61_中文赛事资料/开源正文快照/helloctf/docs/hc-reverse/Android.md
> - 源修订：8e9d6396a0d1ccc1f606810d575d1abb3dd567de
> - 抓取时间：2026-10-22T17:55:11.323038+00:00
> - 收录说明：开源中文文档正文。原作者与版本已保留；检索正文省略代码块、缩进代码和图片，完整 Markdown 另存；未复现。
> - 判定依据：original_prose_not_runtime_verified

> 原文：https://github.com/ProbiusOfficial/Hello-CTF/blob/8e9d6396a0d1ccc1f606810d575d1abb3dd567de/docs/hc-reverse/Android.md

## Android 平台

本章节内容施工中，后续将补充完整的 Android 平台逆向分析指南。

## 预计内容目录

- 环境搭建
  - 常用操作系统与工具链
  - 模拟器 / 真机调试环境
- 常见逆向工具
  - APK 反编译与重打包（如 JADX、apktool 等）
  - 动态调试与 Hook（如 Frida、Xposed 等）
- Android 应用基本结构
  - APK 文件结构与打包流程
  - DEX / OAT / ART 基础
- 静态分析流程示例
- 动态分析与调试示例
- 常见保护与对抗（壳、混淆、反调试等）
- 实战案例与练习思路

## 参考资料（预备）

- Android 官方文档（架构与应用打包流程）
- 常见逆向工具文档：JADX、apktool、Frida、Xposed 等
- 经典 Android 逆向分析书籍与博客文章
