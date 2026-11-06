---
title: "控制流平坦化"
category: reverse
tags: ["reverse", "ctf-wiki", "zh-tw", "obfuscate", "control-flow-flatten.md", "origin_tag:imported_cats"]
signals: ["reverse", "ctf-wiki", "zh-tw"]
difficulty: medium
source: "https://github.com/ctf-wiki/ctf-wiki/blob/e225ddfcd420a7f54a5940f47336ebdf8c29b875/docs/zh-tw/docs/reverse/obfuscate/control-flow-flatten.md"
tools: []
origin: imported_cats
origin_id: "ctf-wiki-6b34dde0b51545"
origin_domain: "reverse"
origin_family: "ctf-wiki"
origin_event: ""
origin_year: ""
origin_license: "CC-BY-NC-SA-4.0"
origin_attribution: "ctf-wiki/ctf-wiki contributors; original at https://github.com/ctf-wiki/ctf-wiki/blob/e225ddfcd420a7f54a5940f47336ebdf8c29b875/docs/zh-tw/docs/reverse/obfuscate/control-flow-flatten.md"
origin_verification: "source_document_not_reproduced"
origin_content_sha256: "1f162177f4355b3b66ee7ff982d7a49fa2c3e66f24b9c443b8a8d679a3ddae44"
origin_body_sha256: 08abb4abade332b605a00a89d0db68718b2557bb651559b66602ba3ae99b11f9
origin_title: "控制流平坦化"
origin_meta:
  asset_refs: []
  attribution: "ctf-wiki/ctf-wiki contributors; original at https://github.com/ctf-wiki/ctf-wiki/blob/e225ddfcd420a7f54a5940f47336ebdf8c29b875/docs/zh-tw/docs/reverse/obfuscate/control-flow-flatten.md"
  basis: "original_prose_not_runtime_verified"
  chunk_ids: [1472, 1473, 1474]
  content_sha256: "1f162177f4355b3b66ee7ff982d7a49fa2c3e66f24b9c443b8a8d679a3ddae44"
  domain: "reverse"
  fetched_at_utc: "2026-10-22T17:53:54.034332+00:00"
  id: "ctf-wiki-6b34dde0b51545"
  kind: "licensed_chinese_reference"
  language: "zh"
  license: "CC-BY-NC-SA-4.0"
  license_local_path: "61_中文赛事资料/来源与许可/ctf-wiki/LICENSE.txt"
  local_path: "61_中文赛事资料/开源正文快照/ctf-wiki/docs/zh-tw/docs/reverse/obfuscate/control-flow-flatten.md"
  response_sha256: "6c795c6beb507cb40285e8393ace9029612934550f8f47a48ea10b9a1f12752e"
  scope_note: "开源中文文档正文。原作者与版本已保留；检索正文省略代码块、缩进代码和图片，完整 Markdown 另存；未复现。"
  source_family: "ctf-wiki"
  source_revision: "e225ddfcd420a7f54a5940f47336ebdf8c29b875"
  source_url: "https://github.com/ctf-wiki/ctf-wiki/blob/e225ddfcd420a7f54a5940f47336ebdf8c29b875/docs/zh-tw/docs/reverse/obfuscate/control-flow-flatten.md"
  tags: ["reverse", "ctf-wiki", "zh-tw", "reverse", "obfuscate", "control-flow-flatten.md"]
  title: "控制流平坦化"
  verification_status: "source_document_not_reproduced"
  year: ""
updated: 2026-10-31
---
# 控制流平坦化

> 本文由授权中文赛事 WP 正文导入（阶段 1，仅散文，代码段未导入）。
>
> - 来源：https://github.com/ctf-wiki/ctf-wiki/blob/e225ddfcd420a7f54a5940f47336ebdf8c29b875/docs/zh-tw/docs/reverse/obfuscate/control-flow-flatten.md
> - 许可：CC-BY-NC-SA-4.0
> - 署名：ctf-wiki/ctf-wiki contributors; original at https://github.com/ctf-wiki/ctf-wiki/blob/e225ddfcd420a7f54a5940f47336ebdf8c29b875/docs/zh-tw/docs/reverse/obfuscate/control-flow-flatten.md
> - 文档族：ctf-wiki
> - 赛事：（无）
> - 年份：（无）
> - 核验状态：source_document_not_reproduced
> - 正文 sha256：1f162177f4355b3b66ee7ff982d7a49fa2c3e66f24b9c443b8a8d679a3ddae44
> - 导入 ID：ctf-wiki-6b34dde0b51545
> - 原 domain：reverse
> - 许可文件：61_中文赛事资料/来源与许可/ctf-wiki/LICENSE.txt
> - 本地快照：61_中文赛事资料/开源正文快照/ctf-wiki/docs/zh-tw/docs/reverse/obfuscate/control-flow-flatten.md
> - 源修订：e225ddfcd420a7f54a5940f47336ebdf8c29b875
> - 抓取时间：2026-10-22T17:53:54.034332+00:00
> - 收录说明：开源中文文档正文。原作者与版本已保留；检索正文省略代码块、缩进代码和图片，完整 Markdown 另存；未复现。
> - 判定依据：original_prose_not_runtime_verified

> 原文：https://github.com/ctf-wiki/ctf-wiki/blob/e225ddfcd420a7f54a5940f47336ebdf8c29b875/docs/zh-tw/docs/reverse/obfuscate/control-flow-flatten.md

## 簡介

控制流平坦化（control flow flattening）是作用於控制流圖的代碼混淆技術，其基本思想是重新組織函數的控制流圖中的基本塊關係，通過插入一個“主分發器”來控制基本塊的執行流程，例如下圖是正常的執行流程：

經過控制流平坦化處理之後便變成了這個樣子，由一個“主分發器”負責控制程序執行流：

通過控制流平坦化，基本塊間的前後關係將被混淆，從而加大了程序逆向分析的難度。更多關於控制流平坦化的實現細節可以參考[這篇論文](http://ac.inf.elte.hu/Vol_030_2009/003.pdf).

## 利用符號執行去除控制流平坦化

> 待施工。

## Reference

[騰訊安全應急響應中心 - 利用符號執行去除控制流平坦化](https://security.tencent.com/index.php/blog/msg/112)

[OBFUSCATING C++ PROGRAMS VIA CONTROL FLOW FLATTENING](http://ac.inf.elte.hu/Vol_030_2009/003.pdf)

## 原文配图

![after-flattenning.png](../../_assets/images/4082f470a2303ac9f0ff989fd1cb7f18d3182abcaa93f88b361bef9f4c4b6a1e.png)

![before-flattening.png](../../_assets/images/ba30d07b0459c99599dcb507353793fb43c12b54c85220cdb2cd7548c7cb2534.png)
