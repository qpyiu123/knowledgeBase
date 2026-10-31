---
title: "网鼎杯2024青龙组官方资格赛wp_网鼎杯wp-CSDN博客 / pwn"
category: pwn
tags: ["pwn", "中文题解", "栈", "origin_tag:imported_cats"]
signals: ["pwn", "中文题解", "栈"]
difficulty: medium
source: "https://blog.csdn.net/qq_66013948/article/details/143415199"
tools: []
origin: imported_cats
origin_id: "cn-blog-csdn-wangding-1"
origin_domain: "pwn"
origin_family: "chinese_blog"
origin_event: "网鼎杯 2024"
origin_year: 2024
origin_license: "CC-BY-SA-4.0"
origin_attribution: "网鼎杯2024青龙组官方资格赛wp_网鼎杯wp-CSDN博客 的原作者（见原文署名）"
origin_verification: "author_report_not_reproduced"
origin_content_sha256: "935f767875eff56e67b792b0051dfdbbd71e2c9d660513e623a19e3468daa63a"
origin_body_sha256: fe501d347c7b25a472f7aa008877340e85b065be9e3c72ab6bdd2adb7d84c7ce
origin_title: "网鼎杯2024青龙组官方资格赛wp_网鼎杯wp-CSDN博客 / pwn"
origin_meta:
  asset_refs: []
  basis: "original_prose_not_runtime_verified"
  chunk_ids: [6051, 6052, 6053]
  content_sha256: "935f767875eff56e67b792b0051dfdbbd71e2c9d660513e623a19e3468daa63a"
  domain: "pwn"
  event: "网鼎杯 2024"
  id: "cn-blog-csdn-wangding-1"
  kind: "licensed_blog_wp_prose"
  language: "zh"
  license: "CC-BY-SA-4.0"
  license_evidence_urls: ["http://creativecommons.org/licenses/by-sa/4.0/"]
  local_path: "61_中文赛事资料/博客授权正文/csdn-wangding.md"
  scope_note: "已核对页面CC许可，离线收录说明正文；代码和图片在此正文中省略，未复现。保留原作者未解决或不确定的表述，抽取可能损失公式排版。"
  source_author: "网鼎杯2024青龙组官方资格赛wp_网鼎杯wp-CSDN博客 的原作者（见原文署名）"
  source_family: "chinese_blog"
  source_url: "https://blog.csdn.net/qq_66013948/article/details/143415199"
  tags: ["pwn", "中文题解", "栈"]
  title: "网鼎杯2024青龙组官方资格赛wp_网鼎杯wp-CSDN博客 / pwn"
  verification_status: "author_report_not_reproduced"
  year: 2024
updated: 2026-10-31
---
# 网鼎杯2024青龙组官方资格赛wp_网鼎杯wp-CSDN博客 / pwn

> 本文由授权中文赛事 WP 正文导入（阶段 1，仅散文，代码段未导入）。
>
> - 来源：https://blog.csdn.net/qq_66013948/article/details/143415199
> - 许可：CC-BY-SA-4.0
> - 署名：网鼎杯2024青龙组官方资格赛wp_网鼎杯wp-CSDN博客 的原作者（见原文署名）
> - 文档族：chinese_blog
> - 赛事：网鼎杯 2024
> - 年份：2024
> - 核验状态：author_report_not_reproduced
> - 正文 sha256：935f767875eff56e67b792b0051dfdbbd71e2c9d660513e623a19e3468daa63a
> - 导入 ID：cn-blog-csdn-wangding-1
> - 原 domain：pwn
> - 许可依据：["http://creativecommons.org/licenses/by-sa/4.0/"]
> - 本地快照：61_中文赛事资料/博客授权正文/csdn-wangding.md
> - 收录说明：已核对页面CC许可，离线收录说明正文；代码和图片在此正文中省略，未复现。保留原作者未解决或不确定的表述，抽取可能损失公式排版。
> - 判定依据：original_prose_not_runtime_verified

> 原文：https://blog.csdn.net/qq_66013948/article/details/143415199

## 正文

pwn02:

**第一步：**checksec发现32位架构，开了NX和ASLR。

**第二步：**login函数有个登陆，账号密码都在里面

**第三步：**vuln函数存在栈溢出，但是只能溢出8个字节，确定位栈迁移。

**第四步：**编写脚本，攻击：

## 【来源分段】网鼎杯2024青龙组官方资格赛wp_网鼎杯wp-CSDN博客 _ misc

## 正文

misc03：

**第一步：**打开流量包，根据协议排序发现了两种有用的协议，一个TCP，一个HTTP，察觉可能是个网站，然后过滤HTTP：

**第二步：**过滤HTTP后发现了个疑似危险ip：39.144.218.183，有爆破目录的可能：

**第三步：**根据很多请求响应对，发现很多都是404，404的状态长度比较短，根据Length排序，从最大的和最小的开始选，找出与众不同的一批流量，发现了木马和访问木马的ip：

**第四步：**跟踪这个流，发现了危险的payload，确定这个就是攻击者：

## 【来源分段】网鼎杯2024青龙组官方资格赛wp_网鼎杯wp-CSDN博客 _ crypto

## 正文

crypto01：

​		原题，直接上https://www.cnblogs.com/mumuhhh/p/17789591.html，有个脚本，改一下，具体参数之后直接sagemath跑：

​		得到了d，然后解密：

​		得到了d，然后解密：

crypto02：

## 【来源分段】网鼎杯2024青龙组官方资格赛wp_网鼎杯wp-CSDN博客 _ reverse

## 正文

reverse02：

​		flag有四个部分，每个部分都有一个加密。

​		首先第一部分：

​		首先第一部分：

​		输入flag，然后技能高兴对比，进行比较， 首先是长度，之后就是flag的为 wdflag{XXXXXX}格式。

​		第二部分：

​		第三段，就是个异或：

​		第三段，就是个异或：

​		输入的数据需要和XorrLord进行异或操作，之后和Ajc2AYKBjg进行比较，脚本：

​		最后一个部分就是AES加密：

​		将数据提取出来之后一把梭了：
