---
title: "UCATFLAGS 2024 / Sikesibian 的 Misc 题目简化题解合集"
category: misc
tags: ["UCATFLAGS 2024", "Sikesibian 的 Misc 题目简化题解合集", "misc", "官方资料", "wp/misc/misc-wp-sike.md", "origin_tag:imported_cats"]
signals: ["UCATFLAGS 2024", "Sikesibian 的 Misc 题目简化题解合集", "misc"]
difficulty: medium
source: "https://github.com/UCAS-CTF/UCATFLAGS-WP/blob/b1e667240041738bf1361b555b162b5713be315c/wp/misc/misc-wp-sike.md"
tools: []
origin: imported_cats
origin_id: "official-d64a31ba5b1bb7706f0bd1"
origin_domain: "misc"
origin_family: "official_event_archive"
origin_event: "UCATFLAGS 2024"
origin_year: 2024
origin_license: "not_declared"
origin_attribution: ""
origin_verification: "official_source_not_reproduced"
origin_content_sha256: "450159c6d05f534a420f902f4b6c2d32ab0b84e76cf78b2ba628d3ccccf80d3f"
origin_body_sha256: f691f7c1e0af536a6da41e79afab50d4361258c4cb050ad46ccad97e5fbd8746
origin_title: "UCATFLAGS 2024 / Sikesibian 的 Misc 题目简化题解合集"
origin_meta:
  asset_refs: []
  basis: "original_prose_not_runtime_verified"
  challenge_key: "ucatflags2024:wp/misc/misc-wp-sike"
  chunk_ids: [7950, 7951, 7952]
  content_sha256: "450159c6d05f534a420f902f4b6c2d32ab0b84e76cf78b2ba628d3ccccf80d3f"
  domain: "misc"
  domain_basis: "repository_path"
  event: "UCATFLAGS 2024"
  external_links_not_followed: 0
  id: "official-d64a31ba5b1bb7706f0bd1"
  kind: "official_wp_prose"
  language: "zh"
  license: "not_declared"
  local_path: "62_官方赛事题库/objects/25d5bf8b6804073e6f5e4368ba7054bebe37d3f3b66b7b8bf1ce8bfeb65e60be.blob"
  official_evidence: "https://github.com/UCAS-CTF/UCATFLAGS-WP"
  original_path: "wp/misc/misc-wp-sike.md"
  revision: "b1e667240041738bf1361b555b162b5713be315c"
  scope_note: "官方发布来源的说明正文；代码单独索引，未运行或分析。按文件收录，不把多份文件算作多道题。图片及附件下载状态见清单；仅按路径/原题分类标方向，binary 等跨方向资料留待分类。"
  source_family: "official_event_archive"
  source_url: "https://github.com/UCAS-CTF/UCATFLAGS-WP/blob/b1e667240041738bf1361b555b162b5713be315c/wp/misc/misc-wp-sike.md"
  tags: ["UCATFLAGS 2024", "Sikesibian 的 Misc 题目简化题解合集", "misc", "官方资料", "wp/misc/misc-wp-sike.md"]
  title: "UCATFLAGS 2024 / Sikesibian 的 Misc 题目简化题解合集"
  verification_status: "official_source_not_reproduced"
  year: 2024
updated: 2026-10-31
---
# UCATFLAGS 2024 / Sikesibian 的 Misc 题目简化题解合集

> 本文由授权中文赛事 WP 正文导入（阶段 1，仅散文，代码段未导入）。
>
> - 来源：https://github.com/UCAS-CTF/UCATFLAGS-WP/blob/b1e667240041738bf1361b555b162b5713be315c/wp/misc/misc-wp-sike.md
> - 许可：not_declared
> - 署名：（未提供）
> - 文档族：official_event_archive
> - 赛事：UCATFLAGS 2024
> - 年份：2024
> - 核验状态：official_source_not_reproduced
> - 正文 sha256：450159c6d05f534a420f902f4b6c2d32ab0b84e76cf78b2ba628d3ccccf80d3f
> - 导入 ID：official-d64a31ba5b1bb7706f0bd1
> - 原 domain：misc
> - 本地快照：62_官方赛事题库/objects/25d5bf8b6804073e6f5e4368ba7054bebe37d3f3b66b7b8bf1ce8bfeb65e60be.blob
> - 源修订：b1e667240041738bf1361b555b162b5713be315c
> - 收录说明：官方发布来源的说明正文；代码单独索引，未运行或分析。按文件收录，不把多份文件算作多道题。图片及附件下载状态见清单；仅按路径/原题分类标方向，binary 等跨方向资料留待分类。
> - 判定依据：original_prose_not_runtime_verified

> 原文：https://github.com/UCAS-CTF/UCATFLAGS-WP/blob/b1e667240041738bf1361b555b162b5713be315c/wp/misc/misc-wp-sike.md

## 1. BigConcert

> “一只耳”的音乐会 （大小写不敏感，单词之间加下划线）

使用 **Audacity** 查看音频文件，发现右声道隐藏了规律性消息，可以肉眼看，也可以使用脚本进行提取。猜测是摩斯电码，用摩斯电码转写即可。写脚本也行，但是肉眼快会更快一些。And注意断句，这是一个句子，而不是一大坨字符。那么怎么断句呢？这就是歌曲第一句的英文翻译啦！

歌曲：《香水有毒》

## 2. backdoor

> DNN is **Do Not be Nervous**.

这个题看懂代码就好了，其实就是基于原先的FLAG的所有字符构建了一个置换映射，而这个模型就是这个置换映射。对于置换映射来说，我们只要还原出来这个置换表即可。这件事情很简单，题目给到的变换后的字符种类和变换前的是一致的，所以我们类似地把这些字符直接送入模型中，然后观测输出即可获得置换表，之后将置换表逆过来即可。

{% raw %}
{% endraw %}

## 3. easypicture

> 图片格式千千万。。。（本题flag中无空格，且不区分大小写）

用16进制阅读器（比如`winhex` 等工具）打开看到这是一个PDF，只是前面的PDF标识字符被改成了PDD，把这个字节改过来，然后把后缀名改成.pdf，打开即可。打开后发现是白色的，但是里面实际上是有文字的，不过也是白色的，复制出来即可。
