---
title: "r00t CTF 2024 / broken_flag"
category: reverse
tags: ["r00t CTF 2024", "broken_flag", "reverse", "官方资料", "Rev/broken_flag.md", "origin_tag:imported_cats"]
signals: ["r00t CTF 2024", "broken_flag", "reverse"]
difficulty: medium
source: "https://github.com/r00t-security-lab/rtctf2024/blob/a273041a04a5dd1eed3e5f49c9345719923a8e9f/Rev/broken_flag.md"
tools: []
origin: imported_cats
origin_id: "official-ffdc4de19d4c43e08663d5"
origin_domain: "reverse"
origin_family: "official_event_archive"
origin_event: "r00t CTF 2024"
origin_year: 2024
origin_license: "not_declared"
origin_attribution: ""
origin_verification: "official_source_not_reproduced"
origin_content_sha256: "0bc3654d3557849576181fabe111308610fd098b872079eae8f22cf5b3c0ab52"
origin_body_sha256: a22ccdefc5bb1dd10bb4170a64b1d8fb954dc56c9e756cc049d2253f4ed6c497
origin_title: "r00t CTF 2024 / broken_flag"
origin_meta:
  asset_refs: []
  basis: "original_prose_not_runtime_verified"
  challenge_key: "rtctf2024:Rev"
  chunk_ids: [7762, 7763, 7764]
  content_sha256: "0bc3654d3557849576181fabe111308610fd098b872079eae8f22cf5b3c0ab52"
  domain: "reverse"
  domain_basis: "repository_path"
  event: "r00t CTF 2024"
  external_links_not_followed: 0
  id: "official-ffdc4de19d4c43e08663d5"
  kind: "official_wp_prose"
  language: "zh"
  license: "not_declared"
  local_path: "62_官方赛事题库/objects/8cc1c730371de2806c4c0525945b062a1abfdbd7177fa2e99adb8184cd47093b.blob"
  official_evidence: "https://github.com/r00t-security-lab/rtctf2024"
  original_path: "Rev/broken_flag.md"
  revision: "a273041a04a5dd1eed3e5f49c9345719923a8e9f"
  scope_note: "官方发布来源的说明正文；代码单独索引，未运行或分析。按文件收录，不把多份文件算作多道题。图片及附件下载状态见清单；仅按路径/原题分类标方向，binary 等跨方向资料留待分类。"
  source_family: "official_event_archive"
  source_url: "https://github.com/r00t-security-lab/rtctf2024/blob/a273041a04a5dd1eed3e5f49c9345719923a8e9f/Rev/broken_flag.md"
  tags: ["r00t CTF 2024", "broken_flag", "reverse", "官方资料", "Rev/broken_flag.md"]
  title: "r00t CTF 2024 / broken_flag"
  verification_status: "official_source_not_reproduced"
  year: 2024
updated: 2026-10-31
---
# r00t CTF 2024 / broken_flag

> 本文由授权中文赛事 WP 正文导入（阶段 1，仅散文，代码段未导入）。
>
> - 来源：https://github.com/r00t-security-lab/rtctf2024/blob/a273041a04a5dd1eed3e5f49c9345719923a8e9f/Rev/broken_flag.md
> - 许可：not_declared
> - 署名：（未提供）
> - 文档族：official_event_archive
> - 赛事：r00t CTF 2024
> - 年份：2024
> - 核验状态：official_source_not_reproduced
> - 正文 sha256：0bc3654d3557849576181fabe111308610fd098b872079eae8f22cf5b3c0ab52
> - 导入 ID：official-ffdc4de19d4c43e08663d5
> - 原 domain：reverse
> - 本地快照：62_官方赛事题库/objects/8cc1c730371de2806c4c0525945b062a1abfdbd7177fa2e99adb8184cd47093b.blob
> - 源修订：a273041a04a5dd1eed3e5f49c9345719923a8e9f
> - 收录说明：官方发布来源的说明正文；代码单独索引，未运行或分析。按文件收录，不把多份文件算作多道题。图片及附件下载状态见清单；仅按路径/原题分类标方向，binary 等跨方向资料留待分类。
> - 判定依据：original_prose_not_runtime_verified

> 原文：https://github.com/r00t-security-lab/rtctf2024/blob/a273041a04a5dd1eed3e5f49c9345719923a8e9f/Rev/broken_flag.md

## broken_flag

在主函数中是对flag的第一部分的加密，就是一个简单的字母移位操作，由于未设定随机数种子，会采用默认的种子，可以直接跑一下获取随机数的值

继续向下看可以看到一个tips函数，会提示看一下奇怪的字符串和交叉引用，这两种方法都能找到第二部分

就能找到第二部分了，第二部分的加密是对每一位异或0x24

第三部分的线索就要看字符串了，可以看到在函数fun11_()中，在旁边搜索函数列表，可以搜到几个函数名满足条件的，依次查看就行

在fun114()中找到了不一样的东西，进入Th3_8r0kEn_flag函数，里面是一句话，意思就是这个函数名很奇怪，发现是符合flag的常用格式的，这个函数名就是第三部分了

脚本：

脚本：

flag：r00t2024{th4hK_Y0U_FOr_5ucCEs5Fu1lY_f1x!Ng_Th3_8r0kEn_flag}
