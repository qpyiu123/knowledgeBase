---
title: "流密碼"
category: crypto
tags: ["crypto", "ctf-wiki", "zh-tw", "streamcipher", "intro.md", "origin_tag:imported_cats"]
signals: ["crypto", "ctf-wiki", "zh-tw"]
difficulty: medium
source: "https://github.com/ctf-wiki/ctf-wiki/blob/e225ddfcd420a7f54a5940f47336ebdf8c29b875/docs/zh-tw/docs/crypto/streamcipher/intro.md"
tools: []
origin: imported_cats
origin_id: "ctf-wiki-2b65d2f059551b"
origin_domain: "crypto"
origin_family: "ctf-wiki"
origin_event: ""
origin_year: ""
origin_license: "CC-BY-NC-SA-4.0"
origin_attribution: "ctf-wiki/ctf-wiki contributors; original at https://github.com/ctf-wiki/ctf-wiki/blob/e225ddfcd420a7f54a5940f47336ebdf8c29b875/docs/zh-tw/docs/crypto/streamcipher/intro.md"
origin_verification: "source_document_not_reproduced"
origin_content_sha256: "a673fec0497272233e7faf2a91afafb39c555719684be2efb44c16e0b5091ab9"
origin_body_sha256: 218d95488ec4bc3e74215be6e005a37c6a76037299eaeec5617b353bc2d856f6
origin_title: "流密碼"
origin_meta:
  asset_refs: []
  attribution: "ctf-wiki/ctf-wiki contributors; original at https://github.com/ctf-wiki/ctf-wiki/blob/e225ddfcd420a7f54a5940f47336ebdf8c29b875/docs/zh-tw/docs/crypto/streamcipher/intro.md"
  basis: "original_prose_not_runtime_verified"
  chunk_ids: [1101, 1102, 1103]
  content_sha256: "a673fec0497272233e7faf2a91afafb39c555719684be2efb44c16e0b5091ab9"
  domain: "crypto"
  fetched_at_utc: "2026-10-22T17:53:38.893943+00:00"
  id: "ctf-wiki-2b65d2f059551b"
  kind: "licensed_chinese_reference"
  language: "zh"
  license: "CC-BY-NC-SA-4.0"
  license_local_path: "61_中文赛事资料/来源与许可/ctf-wiki/LICENSE.txt"
  local_path: "61_中文赛事资料/开源正文快照/ctf-wiki/docs/zh-tw/docs/crypto/streamcipher/intro.md"
  response_sha256: "7efdf4507d4afa88ed31958d4e8503d30e4a9d55cd32c0d91eb65b4f475fbc23"
  scope_note: "开源中文文档正文。原作者与版本已保留；检索正文省略代码块、缩进代码和图片，完整 Markdown 另存；未复现。"
  source_family: "ctf-wiki"
  source_revision: "e225ddfcd420a7f54a5940f47336ebdf8c29b875"
  source_url: "https://github.com/ctf-wiki/ctf-wiki/blob/e225ddfcd420a7f54a5940f47336ebdf8c29b875/docs/zh-tw/docs/crypto/streamcipher/intro.md"
  tags: ["crypto", "ctf-wiki", "zh-tw", "crypto", "streamcipher", "intro.md"]
  title: "流密碼"
  verification_status: "source_document_not_reproduced"
  year: ""
updated: 2026-10-31
---
# 流密碼

> 本文由授权中文赛事 WP 正文导入（阶段 1，仅散文，代码段未导入）。
>
> - 来源：https://github.com/ctf-wiki/ctf-wiki/blob/e225ddfcd420a7f54a5940f47336ebdf8c29b875/docs/zh-tw/docs/crypto/streamcipher/intro.md
> - 许可：CC-BY-NC-SA-4.0
> - 署名：ctf-wiki/ctf-wiki contributors; original at https://github.com/ctf-wiki/ctf-wiki/blob/e225ddfcd420a7f54a5940f47336ebdf8c29b875/docs/zh-tw/docs/crypto/streamcipher/intro.md
> - 文档族：ctf-wiki
> - 赛事：（无）
> - 年份：（无）
> - 核验状态：source_document_not_reproduced
> - 正文 sha256：a673fec0497272233e7faf2a91afafb39c555719684be2efb44c16e0b5091ab9
> - 导入 ID：ctf-wiki-2b65d2f059551b
> - 原 domain：crypto
> - 许可文件：61_中文赛事资料/来源与许可/ctf-wiki/LICENSE.txt
> - 本地快照：61_中文赛事资料/开源正文快照/ctf-wiki/docs/zh-tw/docs/crypto/streamcipher/intro.md
> - 源修订：e225ddfcd420a7f54a5940f47336ebdf8c29b875
> - 抓取时间：2026-10-22T17:53:38.893943+00:00
> - 收录说明：开源中文文档正文。原作者与版本已保留；检索正文省略代码块、缩进代码和图片，完整 Markdown 另存；未复现。
> - 判定依据：original_prose_not_runtime_verified

> 原文：https://github.com/ctf-wiki/ctf-wiki/blob/e225ddfcd420a7f54a5940f47336ebdf8c29b875/docs/zh-tw/docs/crypto/streamcipher/intro.md

## 流密碼

流密碼一般逐字節或者逐比特處理信息。一般來說

- 流密碼的密鑰長度會與明文的長度相同。
- 流密碼的密鑰派生自一個較短的密鑰，派生算法通常爲一個僞隨機數生成算法。

需要注意的是，流加密目前來說都是對稱加密。

需要注意的是，流加密目前來說都是對稱加密。

僞隨機數生成算法生成的序列的隨機性越強，明文中的統計特徵被覆蓋的更好。

流密碼加解密非常簡單，在已知明文的情況下，可以非常容易地獲取密鑰流。

流密碼的關鍵在於設計好的僞隨機數生成器。一般來說，僞隨機數生成器的基本構造模塊爲反饋移位寄存器。當然，也有一些特殊設計的流密碼，比如 RC4。
