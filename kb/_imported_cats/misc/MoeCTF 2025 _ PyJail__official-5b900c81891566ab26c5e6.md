---
title: "MoeCTF 2025 / PyJail"
category: misc
tags: ["MoeCTF 2025", "PyJail", "misc", "官方资料", "challenges/Misc/pyjail/README.md", "origin_tag:imported_cats"]
signals: ["MoeCTF 2025", "PyJail", "misc"]
difficulty: medium
source: "https://github.com/XDSEC/MoeCTF_2025/blob/da9e708029f4666da270064c5776ddd29c61dd6f/challenges/Misc/pyjail/README.md"
tools: []
origin: imported_cats
origin_id: "official-5b900c81891566ab26c5e6"
origin_domain: "misc"
origin_family: "official_event_archive"
origin_event: "MoeCTF 2025"
origin_year: 2025
origin_license: "not_declared"
origin_attribution: ""
origin_verification: "official_source_not_reproduced"
origin_content_sha256: "d564946082a28b6e07d43f0d79cdae7bc7703c01c050faf13d1131101d7eb627"
origin_body_sha256: 1da27f7f4b469371de0afc3423bec3a4519382ddd53e89ac810afd9aab2958a1
origin_title: "MoeCTF 2025 / PyJail"
origin_meta:
  asset_refs: []
  basis: "original_prose_not_runtime_verified"
  challenge_key: "moectf2025:challenges/Misc/pyjail"
  chunk_ids: [8232, 8233]
  content_sha256: "d564946082a28b6e07d43f0d79cdae7bc7703c01c050faf13d1131101d7eb627"
  domain: "misc"
  domain_basis: "repository_path"
  event: "MoeCTF 2025"
  external_links_not_followed: 0
  id: "official-5b900c81891566ab26c5e6"
  kind: "official_challenge_document"
  language: "zh"
  license: "not_declared"
  local_path: "62_官方赛事题库/objects/026dcfbb1812f9850e1a11abb713c9bf710ad1029784c7d99f4a29caf62f3bab.blob"
  official_evidence: "https://github.com/XDSEC/MoeCTF_2025"
  original_path: "challenges/Misc/pyjail/README.md"
  revision: "da9e708029f4666da270064c5776ddd29c61dd6f"
  scope_note: "官方发布来源的说明正文；代码单独索引，未运行或分析。按文件收录，不把多份文件算作多道题。图片及附件下载状态见清单；仅按路径/原题分类标方向，binary 等跨方向资料留待分类。"
  source_family: "official_event_archive"
  source_url: "https://github.com/XDSEC/MoeCTF_2025/blob/da9e708029f4666da270064c5776ddd29c61dd6f/challenges/Misc/pyjail/README.md"
  tags: ["MoeCTF 2025", "PyJail", "misc", "官方资料", "challenges/Misc/pyjail/README.md"]
  title: "MoeCTF 2025 / PyJail"
  verification_status: "official_source_not_reproduced"
  year: 2025
updated: 2026-10-31
---
# MoeCTF 2025 / PyJail

> 本文由授权中文赛事 WP 正文导入（阶段 1，仅散文，代码段未导入）。
>
> - 来源：https://github.com/XDSEC/MoeCTF_2025/blob/da9e708029f4666da270064c5776ddd29c61dd6f/challenges/Misc/pyjail/README.md
> - 许可：not_declared
> - 署名：（未提供）
> - 文档族：official_event_archive
> - 赛事：MoeCTF 2025
> - 年份：2025
> - 核验状态：official_source_not_reproduced
> - 正文 sha256：d564946082a28b6e07d43f0d79cdae7bc7703c01c050faf13d1131101d7eb627
> - 导入 ID：official-5b900c81891566ab26c5e6
> - 原 domain：misc
> - 本地快照：62_官方赛事题库/objects/026dcfbb1812f9850e1a11abb713c9bf710ad1029784c7d99f4a29caf62f3bab.blob
> - 源修订：da9e708029f4666da270064c5776ddd29c61dd6f
> - 收录说明：官方发布来源的说明正文；代码单独索引，未运行或分析。按文件收录，不把多份文件算作多道题。图片及附件下载状态见清单；仅按路径/原题分类标方向，binary 等跨方向资料留待分类。
> - 判定依据：original_prose_not_runtime_verified

> 原文：https://github.com/XDSEC/MoeCTF_2025/blob/da9e708029f4666da270064c5776ddd29c61dd6f/challenges/Misc/pyjail/README.md

## 题目部署方式

每个题目目录（0-6）都包含独立的 Docker 环境配置，部署方式如下：

进入对应题目目录，使用 Docker 构建并运行：

## 文件说明

- **chall.py**: 题目核心代码，包含沙箱限制和检查逻辑
- **main.py**: 题目入口文件
- **Dockerfile**: Docker 镜像构建配置
- **wrapper.sh**: 容器启动脚本

## 致谢

本题目中的 `jail-template` 目录并非我所写，来自 **XDSEC 22 届前辈鲤唐可可**，在此表示感谢！🙏
