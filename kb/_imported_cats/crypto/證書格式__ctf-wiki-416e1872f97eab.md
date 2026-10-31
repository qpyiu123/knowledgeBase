---
title: "證書格式"
category: crypto
tags: ["crypto", "ctf-wiki", "zh-tw", "certificate", "introduction.md", "RSA", "origin_tag:imported_cats"]
signals: ["crypto", "ctf-wiki", "zh-tw"]
difficulty: medium
source: "https://github.com/ctf-wiki/ctf-wiki/blob/e225ddfcd420a7f54a5940f47336ebdf8c29b875/docs/zh-tw/docs/crypto/certificate/introduction.md"
tools: []
origin: imported_cats
origin_id: "ctf-wiki-416e1872f97eab"
origin_domain: "crypto"
origin_family: "ctf-wiki"
origin_event: ""
origin_year: ""
origin_license: "CC-BY-NC-SA-4.0"
origin_attribution: "ctf-wiki/ctf-wiki contributors; original at https://github.com/ctf-wiki/ctf-wiki/blob/e225ddfcd420a7f54a5940f47336ebdf8c29b875/docs/zh-tw/docs/crypto/certificate/introduction.md"
origin_verification: "source_document_not_reproduced"
origin_content_sha256: "57b17d2b67a43628b034b62cddb286002577c09812729a7f09fda0b9f4507483"
origin_body_sha256: 5a0d9503e9c32718ae28d631ccf872812ac1a5663bb10d2ab1d930cf81dc561c
origin_title: "證書格式"
origin_meta:
  asset_refs: []
  attribution: "ctf-wiki/ctf-wiki contributors; original at https://github.com/ctf-wiki/ctf-wiki/blob/e225ddfcd420a7f54a5940f47336ebdf8c29b875/docs/zh-tw/docs/crypto/certificate/introduction.md"
  basis: "original_prose_not_runtime_verified"
  chunk_ids: [1095, 1096]
  content_sha256: "57b17d2b67a43628b034b62cddb286002577c09812729a7f09fda0b9f4507483"
  domain: "crypto"
  fetched_at_utc: "2026-10-22T17:53:35.754658+00:00"
  id: "ctf-wiki-416e1872f97eab"
  kind: "licensed_chinese_reference"
  language: "zh"
  license: "CC-BY-NC-SA-4.0"
  license_local_path: "61_中文赛事资料/来源与许可/ctf-wiki/LICENSE.txt"
  local_path: "61_中文赛事资料/开源正文快照/ctf-wiki/docs/zh-tw/docs/crypto/certificate/introduction.md"
  response_sha256: "56eb00bd67eac6f0b098881ef64c61f69d096ebfbaecc409f79e1924a8bd0215"
  scope_note: "开源中文文档正文。原作者与版本已保留；检索正文省略代码块、缩进代码和图片，完整 Markdown 另存；未复现。"
  source_family: "ctf-wiki"
  source_revision: "e225ddfcd420a7f54a5940f47336ebdf8c29b875"
  source_url: "https://github.com/ctf-wiki/ctf-wiki/blob/e225ddfcd420a7f54a5940f47336ebdf8c29b875/docs/zh-tw/docs/crypto/certificate/introduction.md"
  tags: ["crypto", "ctf-wiki", "zh-tw", "crypto", "certificate", "introduction.md", "RSA"]
  title: "證書格式"
  verification_status: "source_document_not_reproduced"
  year: ""
updated: 2026-10-31
---
# 證書格式

> 本文由授权中文赛事 WP 正文导入（阶段 1，仅散文，代码段未导入）。
>
> - 来源：https://github.com/ctf-wiki/ctf-wiki/blob/e225ddfcd420a7f54a5940f47336ebdf8c29b875/docs/zh-tw/docs/crypto/certificate/introduction.md
> - 许可：CC-BY-NC-SA-4.0
> - 署名：ctf-wiki/ctf-wiki contributors; original at https://github.com/ctf-wiki/ctf-wiki/blob/e225ddfcd420a7f54a5940f47336ebdf8c29b875/docs/zh-tw/docs/crypto/certificate/introduction.md
> - 文档族：ctf-wiki
> - 赛事：（无）
> - 年份：（无）
> - 核验状态：source_document_not_reproduced
> - 正文 sha256：57b17d2b67a43628b034b62cddb286002577c09812729a7f09fda0b9f4507483
> - 导入 ID：ctf-wiki-416e1872f97eab
> - 原 domain：crypto
> - 许可文件：61_中文赛事资料/来源与许可/ctf-wiki/LICENSE.txt
> - 本地快照：61_中文赛事资料/开源正文快照/ctf-wiki/docs/zh-tw/docs/crypto/certificate/introduction.md
> - 源修订：e225ddfcd420a7f54a5940f47336ebdf8c29b875
> - 抓取时间：2026-10-22T17:53:35.754658+00:00
> - 收录说明：开源中文文档正文。原作者与版本已保留；检索正文省略代码块、缩进代码和图片，完整 Markdown 另存；未复现。
> - 判定依据：original_prose_not_runtime_verified

> 原文：https://github.com/ctf-wiki/ctf-wiki/blob/e225ddfcd420a7f54a5940f47336ebdf8c29b875/docs/zh-tw/docs/crypto/certificate/introduction.md

## PEM

PEM 以 `-----BEGIN` 開頭，以 `-----END` 結尾，中間包含 ASN.1 格式的數據。ASN.1 是經過 base64 轉碼的二進制數據。[Wikipedia](https://en.wikipedia.org/wiki/Privacy-Enhanced_Mail) 上有完整 PEM 文件的例子。

用 Python 3 和 PyCryptodome 庫可以與 PEM 文件交互並提取相關數據。例如我們想提取出模數 `n`：

## DER

DER 是 ASN.1 類型的二進制編碼。後綴 `.cer` 或 `.crt` 的證書通常包含 DER 格式的數據，但 Windows 也可能會接受 PEM 格式的數據。

我們可以用 `openssl` 將 PEM 文件轉化爲 DER 文件：

現在問題被簡化成了如何讀取 PEM 文件，所以我們可以重複使用上一小節中的 Python 代碼。

## 引用

1. [Attacking RSA for fun and CTF points – part 1](https://bitsdeep.com/posts/attacking-rsa-for-fun-and-ctf-points-part-1/)
2. [What are the differences between .pem, .cer and .der?](https://stackoverflow.com/questions/22743415/what-are-the-differences-between-pem-cer-and-der)
