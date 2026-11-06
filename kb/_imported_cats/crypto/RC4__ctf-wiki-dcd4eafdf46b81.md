---
title: "RC4"
category: crypto
tags: ["crypto", "ctf-wiki", "zh-tw", "streamcipher", "special", "rc4.md", "RSA", "origin_tag:imported_cats"]
signals: ["crypto", "ctf-wiki", "zh-tw"]
difficulty: medium
source: "https://github.com/ctf-wiki/ctf-wiki/blob/e225ddfcd420a7f54a5940f47336ebdf8c29b875/docs/zh-tw/docs/crypto/streamcipher/special/rc4.md"
tools: []
origin: imported_cats
origin_id: "ctf-wiki-dcd4eafdf46b81"
origin_domain: "crypto"
origin_family: "ctf-wiki"
origin_event: ""
origin_year: ""
origin_license: "CC-BY-NC-SA-4.0"
origin_attribution: "ctf-wiki/ctf-wiki contributors; original at https://github.com/ctf-wiki/ctf-wiki/blob/e225ddfcd420a7f54a5940f47336ebdf8c29b875/docs/zh-tw/docs/crypto/streamcipher/special/rc4.md"
origin_verification: "source_document_not_reproduced"
origin_content_sha256: "774a47eb46b1aeaa1e1545b6e8b4299ef4e671e9d5ec81817a4e5b23fff09e66"
origin_body_sha256: a7bac0f209968ef1ec6a94d04afe0d77fb731d3a325cb2d9f3df9d0d40386ea1
origin_title: "RC4"
origin_meta:
  asset_refs: []
  attribution: "ctf-wiki/ctf-wiki contributors; original at https://github.com/ctf-wiki/ctf-wiki/blob/e225ddfcd420a7f54a5940f47336ebdf8c29b875/docs/zh-tw/docs/crypto/streamcipher/special/rc4.md"
  basis: "original_prose_not_runtime_verified"
  chunk_ids: [1136]
  content_sha256: "774a47eb46b1aeaa1e1545b6e8b4299ef4e671e9d5ec81817a4e5b23fff09e66"
  domain: "crypto"
  fetched_at_utc: "2026-10-22T17:53:47.929157+00:00"
  id: "ctf-wiki-dcd4eafdf46b81"
  kind: "licensed_chinese_reference"
  language: "zh"
  license: "CC-BY-NC-SA-4.0"
  license_local_path: "61_中文赛事资料/来源与许可/ctf-wiki/LICENSE.txt"
  local_path: "61_中文赛事资料/开源正文快照/ctf-wiki/docs/zh-tw/docs/crypto/streamcipher/special/rc4.md"
  response_sha256: "1cac328db5d6218619c66ecc4919535fca62721f700c14a0d53f75a247253b4a"
  scope_note: "开源中文文档正文。原作者与版本已保留；检索正文省略代码块、缩进代码和图片，完整 Markdown 另存；未复现。"
  source_family: "ctf-wiki"
  source_revision: "e225ddfcd420a7f54a5940f47336ebdf8c29b875"
  source_url: "https://github.com/ctf-wiki/ctf-wiki/blob/e225ddfcd420a7f54a5940f47336ebdf8c29b875/docs/zh-tw/docs/crypto/streamcipher/special/rc4.md"
  tags: ["crypto", "ctf-wiki", "zh-tw", "crypto", "streamcipher", "special", "rc4.md", "RSA"]
  title: "RC4"
  verification_status: "source_document_not_reproduced"
  year: ""
updated: 2026-10-31
---
# RC4

> 本文由授权中文赛事 WP 正文导入（阶段 1，仅散文，代码段未导入）。
>
> - 来源：https://github.com/ctf-wiki/ctf-wiki/blob/e225ddfcd420a7f54a5940f47336ebdf8c29b875/docs/zh-tw/docs/crypto/streamcipher/special/rc4.md
> - 许可：CC-BY-NC-SA-4.0
> - 署名：ctf-wiki/ctf-wiki contributors; original at https://github.com/ctf-wiki/ctf-wiki/blob/e225ddfcd420a7f54a5940f47336ebdf8c29b875/docs/zh-tw/docs/crypto/streamcipher/special/rc4.md
> - 文档族：ctf-wiki
> - 赛事：（无）
> - 年份：（无）
> - 核验状态：source_document_not_reproduced
> - 正文 sha256：774a47eb46b1aeaa1e1545b6e8b4299ef4e671e9d5ec81817a4e5b23fff09e66
> - 导入 ID：ctf-wiki-dcd4eafdf46b81
> - 原 domain：crypto
> - 许可文件：61_中文赛事资料/来源与许可/ctf-wiki/LICENSE.txt
> - 本地快照：61_中文赛事资料/开源正文快照/ctf-wiki/docs/zh-tw/docs/crypto/streamcipher/special/rc4.md
> - 源修订：e225ddfcd420a7f54a5940f47336ebdf8c29b875
> - 抓取时间：2026-10-22T17:53:47.929157+00:00
> - 收录说明：开源中文文档正文。原作者与版本已保留；检索正文省略代码块、缩进代码和图片，完整 Markdown 另存；未复现。
> - 判定依据：original_prose_not_runtime_verified

> 原文：https://github.com/ctf-wiki/ctf-wiki/blob/e225ddfcd420a7f54a5940f47336ebdf8c29b875/docs/zh-tw/docs/crypto/streamcipher/special/rc4.md

## 基本介紹

RSA 由 Ron Rivest 設計，最初隸屬於 RSA 安全公司，是一個專利密碼產品。它是面向字節的流密碼，密鑰長度可變，非常簡單，但也很有效果。RC4 算法廣泛應用於 SSL/TLS 協議和 WEP/WPA 協議。

## 基本流程

RC4 主要包含三個流程

- 初始化 S 和 T 數組。
- 初始化置換 S。
- 生成密鑰流。

## 初始化 S 和 T 數組

初始化 S 和 T 的代碼如下

## 生成流密鑰

我們一般稱前兩部分爲 KSA ，最後一部分是 PRGA。

## 攻擊方法

待補充。

## 原文配图

![rc4_key.png](../../_assets/images/0cc305a1ec2108371bb5dbd88aa74ad2b48dbec20a86c542323f051f9b0370d3.png)

![rc4_s.png](../../_assets/images/5cd05ed5b34757c1a9fe3737ff404206352585a72032cff97b66f2c1f252a0fe.png)

![rc4_s_t.png](../../_assets/images/a2fe96abe6c0db9472aee0f091e0ce783bb221e9580c4cc54959ced4630e742d.png)
