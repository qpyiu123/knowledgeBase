---
title: "磁盤內存分析"
category: misc
tags: ["misc", "ctf-wiki", "zh-tw", "disk-memory", "introduction.md", "ROP", "origin_tag:imported_cats"]
signals: ["misc", "ctf-wiki", "zh-tw"]
difficulty: medium
source: "https://github.com/ctf-wiki/ctf-wiki/blob/e225ddfcd420a7f54a5940f47336ebdf8c29b875/docs/zh-tw/docs/misc/disk-memory/introduction.md"
tools: []
origin: imported_cats
origin_id: "ctf-wiki-bff75e9a57cf9a"
origin_domain: "misc"
origin_family: "ctf-wiki"
origin_event: ""
origin_year: ""
origin_license: "CC-BY-NC-SA-4.0"
origin_attribution: "ctf-wiki/ctf-wiki contributors; original at https://github.com/ctf-wiki/ctf-wiki/blob/e225ddfcd420a7f54a5940f47336ebdf8c29b875/docs/zh-tw/docs/misc/disk-memory/introduction.md"
origin_verification: "source_document_not_reproduced"
origin_content_sha256: "cd899ca5b7d1be770453c6bc4a21f7253fc0c08972ada92d489dbce3e7d50b02"
origin_body_sha256: bf470f737890b8bb4339822a7b813496fea8278150327c1d9120c53593b91b43
origin_title: "磁盤內存分析"
origin_meta:
  asset_refs: []
  attribution: "ctf-wiki/ctf-wiki contributors; original at https://github.com/ctf-wiki/ctf-wiki/blob/e225ddfcd420a7f54a5940f47336ebdf8c29b875/docs/zh-tw/docs/misc/disk-memory/introduction.md"
  basis: "original_prose_not_runtime_verified"
  chunk_ids: [1859]
  content_sha256: "cd899ca5b7d1be770453c6bc4a21f7253fc0c08972ada92d489dbce3e7d50b02"
  domain: "misc"
  fetched_at_utc: "2026-10-22T17:54:02.027946+00:00"
  id: "ctf-wiki-bff75e9a57cf9a"
  kind: "licensed_chinese_reference"
  language: "zh"
  license: "CC-BY-NC-SA-4.0"
  license_local_path: "61_中文赛事资料/来源与许可/ctf-wiki/LICENSE.txt"
  local_path: "61_中文赛事资料/开源正文快照/ctf-wiki/docs/zh-tw/docs/misc/disk-memory/introduction.md"
  response_sha256: "9711143d2e537b04503e5df60a5d2cc21e4302918a18229036bbc5f77a5600f1"
  scope_note: "开源中文文档正文。原作者与版本已保留；检索正文省略代码块、缩进代码和图片，完整 Markdown 另存；未复现。"
  source_family: "ctf-wiki"
  source_revision: "e225ddfcd420a7f54a5940f47336ebdf8c29b875"
  source_url: "https://github.com/ctf-wiki/ctf-wiki/blob/e225ddfcd420a7f54a5940f47336ebdf8c29b875/docs/zh-tw/docs/misc/disk-memory/introduction.md"
  tags: ["misc", "ctf-wiki", "zh-tw", "misc", "disk-memory", "introduction.md", "ROP"]
  title: "磁盤內存分析"
  verification_status: "source_document_not_reproduced"
  year: ""
updated: 2026-10-31
---
# 磁盤內存分析

> 本文由授权中文赛事 WP 正文导入（阶段 1，仅散文，代码段未导入）。
>
> - 来源：https://github.com/ctf-wiki/ctf-wiki/blob/e225ddfcd420a7f54a5940f47336ebdf8c29b875/docs/zh-tw/docs/misc/disk-memory/introduction.md
> - 许可：CC-BY-NC-SA-4.0
> - 署名：ctf-wiki/ctf-wiki contributors; original at https://github.com/ctf-wiki/ctf-wiki/blob/e225ddfcd420a7f54a5940f47336ebdf8c29b875/docs/zh-tw/docs/misc/disk-memory/introduction.md
> - 文档族：ctf-wiki
> - 赛事：（无）
> - 年份：（无）
> - 核验状态：source_document_not_reproduced
> - 正文 sha256：cd899ca5b7d1be770453c6bc4a21f7253fc0c08972ada92d489dbce3e7d50b02
> - 导入 ID：ctf-wiki-bff75e9a57cf9a
> - 原 domain：misc
> - 许可文件：61_中文赛事资料/来源与许可/ctf-wiki/LICENSE.txt
> - 本地快照：61_中文赛事资料/开源正文快照/ctf-wiki/docs/zh-tw/docs/misc/disk-memory/introduction.md
> - 源修订：e225ddfcd420a7f54a5940f47336ebdf8c29b875
> - 抓取时间：2026-10-22T17:54:02.027946+00:00
> - 收录说明：开源中文文档正文。原作者与版本已保留；检索正文省略代码块、缩进代码和图片，完整 Markdown 另存；未复现。
> - 判定依据：original_prose_not_runtime_verified

> 原文：https://github.com/ctf-wiki/ctf-wiki/blob/e225ddfcd420a7f54a5940f47336ebdf8c29b875/docs/zh-tw/docs/misc/disk-memory/introduction.md

## 常用工具

-   EasyRecovery
-   MedAnalyze
-   FTK
-   [Elcomsoft Forensic Disk Decryptor](https://ctf-wiki.github.io/ctf-tools/misc/#_6)
-   Volatility

## 磁盤

常見的磁盤分區格式有以下幾種

-   Windows: FAT12 -> FAT16 -> FAT32 -> NTFS
-   Linux: EXT2 -> EXT3 -> EXT4
-   FAT 主磁盤結構

-   刪除文件：目錄表中文件名第一字節 `e5`。

## VMDK

VMDK 文件本質上是物理硬盤的虛擬版，也會存在跟物理硬盤的分區和扇區中類似的填充區域，我們可以利用這些填充區域來把我們需要隱藏的數據隱藏到裏面去，這樣可以避免隱藏的文件增加了 VMDK 文件的大小（如直接附加到文件後端），也可以避免由於 VMDK 文件大小的改變所帶來的可能導致的虛擬機錯誤。而且 VMDK 文件一般比較大，適合用於隱藏大文件。

## 內存

-   解析 Windows / Linux / Mac OS X 內存結構
-   分析進程，內存數據
-   根據題目提示尋找線索和思路，提取分析指定進程的特定內存數據

## 題目

-   Jarvis OJ - MISC - 取證 2

## 參考

-   [數據隱藏技術](http://wooyun.jozxing.cc/static/drops/tips-12614.html)
