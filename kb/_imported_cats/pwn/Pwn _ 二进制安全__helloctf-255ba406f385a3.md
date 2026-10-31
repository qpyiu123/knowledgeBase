---
title: "Pwn | 二进制安全"
category: pwn
tags: ["pwn", "helloctf", "hc-pwn", "index.md", "ROP", "栈", "origin_tag:imported_cats"]
signals: ["pwn", "helloctf", "hc-pwn"]
difficulty: medium
source: "https://github.com/ProbiusOfficial/Hello-CTF/blob/8e9d6396a0d1ccc1f606810d575d1abb3dd567de/docs/hc-pwn/index.md"
tools: []
origin: imported_cats
origin_id: "helloctf-255ba406f385a3"
origin_domain: "pwn"
origin_family: "helloctf"
origin_event: ""
origin_year: ""
origin_license: "CC-BY-SA-4.0"
origin_attribution: "ProbiusOfficial/Hello-CTF contributors; original at https://github.com/ProbiusOfficial/Hello-CTF/blob/8e9d6396a0d1ccc1f606810d575d1abb3dd567de/docs/hc-pwn/index.md"
origin_verification: "source_document_not_reproduced"
origin_content_sha256: "48023fc8c3b61986c888af92ce14287eaa877eec2a7097a7a3d0bec8c1db8fd9"
origin_body_sha256: ad976e9a39e5f4c6addb47f5292041f05dd5cc20dac382aa2b3a23d88561f95c
origin_title: "Pwn | 二进制安全"
origin_meta:
  asset_refs: []
  attribution: "ProbiusOfficial/Hello-CTF contributors; original at https://github.com/ProbiusOfficial/Hello-CTF/blob/8e9d6396a0d1ccc1f606810d575d1abb3dd567de/docs/hc-pwn/index.md"
  basis: "original_prose_not_runtime_verified"
  chunk_ids: [4278]
  content_sha256: "48023fc8c3b61986c888af92ce14287eaa877eec2a7097a7a3d0bec8c1db8fd9"
  domain: "pwn"
  fetched_at_utc: "2026-10-22T17:54:55.095412+00:00"
  id: "helloctf-255ba406f385a3"
  kind: "licensed_chinese_reference"
  language: "zh"
  license: "CC-BY-SA-4.0"
  license_local_path: "61_中文赛事资料/来源与许可/helloctf/LICENSE.txt"
  local_path: "61_中文赛事资料/开源正文快照/helloctf/docs/hc-pwn/index.md"
  response_sha256: "bbcd56bf9b96fdc668f86ccad6e5628cb8789c5c5f74f90d23745558f5a7602e"
  scope_note: "开源中文文档正文。原作者与版本已保留；检索正文省略代码块、缩进代码和图片，完整 Markdown 另存；未复现。"
  source_family: "helloctf"
  source_revision: "8e9d6396a0d1ccc1f606810d575d1abb3dd567de"
  source_url: "https://github.com/ProbiusOfficial/Hello-CTF/blob/8e9d6396a0d1ccc1f606810d575d1abb3dd567de/docs/hc-pwn/index.md"
  tags: ["pwn", "helloctf", "hc-pwn", "index.md", "ROP", "栈"]
  title: "Pwn | 二进制安全"
  verification_status: "source_document_not_reproduced"
  year: ""
updated: 2026-10-31
---
# Pwn | 二进制安全

> 本文由授权中文赛事 WP 正文导入（阶段 1，仅散文，代码段未导入）。
>
> - 来源：https://github.com/ProbiusOfficial/Hello-CTF/blob/8e9d6396a0d1ccc1f606810d575d1abb3dd567de/docs/hc-pwn/index.md
> - 许可：CC-BY-SA-4.0
> - 署名：ProbiusOfficial/Hello-CTF contributors; original at https://github.com/ProbiusOfficial/Hello-CTF/blob/8e9d6396a0d1ccc1f606810d575d1abb3dd567de/docs/hc-pwn/index.md
> - 文档族：helloctf
> - 赛事：（无）
> - 年份：（无）
> - 核验状态：source_document_not_reproduced
> - 正文 sha256：48023fc8c3b61986c888af92ce14287eaa877eec2a7097a7a3d0bec8c1db8fd9
> - 导入 ID：helloctf-255ba406f385a3
> - 原 domain：pwn
> - 许可文件：61_中文赛事资料/来源与许可/helloctf/LICENSE.txt
> - 本地快照：61_中文赛事资料/开源正文快照/helloctf/docs/hc-pwn/index.md
> - 源修订：8e9d6396a0d1ccc1f606810d575d1abb3dd567de
> - 抓取时间：2026-10-22T17:54:55.095412+00:00
> - 收录说明：开源中文文档正文。原作者与版本已保留；检索正文省略代码块、缩进代码和图片，完整 Markdown 另存；未复现。
> - 判定依据：original_prose_not_runtime_verified

> 原文：https://github.com/ProbiusOfficial/Hello-CTF/blob/8e9d6396a0d1ccc1f606810d575d1abb3dd567de/docs/hc-pwn/index.md

## 正文

---
comments: true

## 内容导读

- **环境与基础**：WSL2 下的环境配置、x86 汇编语言、常见保护机制（ Canary / NX / PIE / RELRO ）。
- **栈溢出**：栈上数组越界与栈溢出——Pwn 的第一个漏洞类型。
- **ROP 利用**：ROP 入门、常见 ROP 技巧、ROP 进阶。

Pwn 入门周期较长，建议配合 hc-start 中推荐的平台与题单同步刷题。
