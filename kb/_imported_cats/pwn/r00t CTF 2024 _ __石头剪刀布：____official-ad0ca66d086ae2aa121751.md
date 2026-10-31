---
title: "r00t CTF 2024 / **石头剪刀布：**"
category: pwn
tags: ["r00t CTF 2024", "**石头剪刀布：**", "pwn", "官方资料", "Pwn/石头剪刀布wp.md", "origin_tag:imported_cats"]
signals: ["r00t CTF 2024", "**石头剪刀布：**", "pwn"]
difficulty: medium
source: "https://github.com/r00t-security-lab/rtctf2024/blob/a273041a04a5dd1eed3e5f49c9345719923a8e9f/Pwn/%E7%9F%B3%E5%A4%B4%E5%89%AA%E5%88%80%E5%B8%83wp.md"
tools: []
origin: imported_cats
origin_id: "official-ad0ca66d086ae2aa121751"
origin_domain: "pwn"
origin_family: "official_event_archive"
origin_event: "r00t CTF 2024"
origin_year: 2024
origin_license: "not_declared"
origin_attribution: ""
origin_verification: "official_source_not_reproduced"
origin_content_sha256: "ac6c6c8c5382363c4a8b8a19b83018a752e84b9a7b6cc40a11b43a7f97f6c095"
origin_body_sha256: 7e9266444220c97e46771b2e0ca27a09cb95fcc82ed15f9920e79c388e0a52f2
origin_title: "r00t CTF 2024 / **石头剪刀布：**"
origin_meta:
  asset_refs: []
  basis: "original_prose_not_runtime_verified"
  challenge_key: "rtctf2024:Pwn"
  chunk_ids: [7745, 7746, 7747]
  content_sha256: "ac6c6c8c5382363c4a8b8a19b83018a752e84b9a7b6cc40a11b43a7f97f6c095"
  domain: "pwn"
  domain_basis: "repository_path"
  event: "r00t CTF 2024"
  external_links_not_followed: 6
  id: "official-ad0ca66d086ae2aa121751"
  kind: "official_wp_prose"
  language: "zh"
  license: "not_declared"
  local_path: "62_官方赛事题库/objects/bb1b7488d057d28a8d99ce32743cb2776cb047016d99bc651c53ca459ad5aa61.blob"
  official_evidence: "https://github.com/r00t-security-lab/rtctf2024"
  original_path: "Pwn/石头剪刀布wp.md"
  revision: "a273041a04a5dd1eed3e5f49c9345719923a8e9f"
  scope_note: "官方发布来源的说明正文；代码单独索引，未运行或分析。按文件收录，不把多份文件算作多道题。图片及附件下载状态见清单；仅按路径/原题分类标方向，binary 等跨方向资料留待分类。"
  source_family: "official_event_archive"
  source_url: "https://github.com/r00t-security-lab/rtctf2024/blob/a273041a04a5dd1eed3e5f49c9345719923a8e9f/Pwn/%E7%9F%B3%E5%A4%B4%E5%89%AA%E5%88%80%E5%B8%83wp.md"
  tags: ["r00t CTF 2024", "**石头剪刀布：**", "pwn", "官方资料", "Pwn/石头剪刀布wp.md"]
  title: "r00t CTF 2024 / **石头剪刀布：**"
  verification_status: "official_source_not_reproduced"
  year: 2024
updated: 2026-10-31
---
# r00t CTF 2024 / **石头剪刀布：**

> 本文由授权中文赛事 WP 正文导入（阶段 1，仅散文，代码段未导入）。
>
> - 来源：https://github.com/r00t-security-lab/rtctf2024/blob/a273041a04a5dd1eed3e5f49c9345719923a8e9f/Pwn/%E7%9F%B3%E5%A4%B4%E5%89%AA%E5%88%80%E5%B8%83wp.md
> - 许可：not_declared
> - 署名：（未提供）
> - 文档族：official_event_archive
> - 赛事：r00t CTF 2024
> - 年份：2024
> - 核验状态：official_source_not_reproduced
> - 正文 sha256：ac6c6c8c5382363c4a8b8a19b83018a752e84b9a7b6cc40a11b43a7f97f6c095
> - 导入 ID：official-ad0ca66d086ae2aa121751
> - 原 domain：pwn
> - 本地快照：62_官方赛事题库/objects/bb1b7488d057d28a8d99ce32743cb2776cb047016d99bc651c53ca459ad5aa61.blob
> - 源修订：a273041a04a5dd1eed3e5f49c9345719923a8e9f
> - 收录说明：官方发布来源的说明正文；代码单独索引，未运行或分析。按文件收录，不把多份文件算作多道题。图片及附件下载状态见清单；仅按路径/原题分类标方向，binary 等跨方向资料留待分类。
> - 判定依据：original_prose_not_runtime_verified

> 原文：https://github.com/r00t-security-lab/rtctf2024/blob/a273041a04a5dd1eed3e5f49c9345719923a8e9f/Pwn/%E7%9F%B3%E5%A4%B4%E5%89%AA%E5%88%80%E5%B8%83wp.md

## **石头剪刀布：**

拿到可执行文件，拖到IDA里看源码：

首先是一个1000次的for循环

我们可以发现当循环1000次执行后，才会执行我们的后门函数：

所以现在关键就是如何让这1000次的循环运行完：

到这儿有两种解法：

**第一种**是基于pwntools写一个脚本，接受程序的输出，再向程序输入，主要考察对pwn工具pwntools的使用

脚本如下：（这个脚本是按照石头剪刀布的玩法进行相应的接收和输入，但其实石头剪刀的输赢是没关系的，只要循环1000次就可以了）

这里运行的时间会久一点，毕竟有1000次，可以看到我们不仅成功拿到shell，而且也赢了1000次的石头剪刀布✌

**第二种：**就是直接nc连接，直接输入1000个字符，r,s,p都可以：

尽管输了，但还是拿到shell啦
