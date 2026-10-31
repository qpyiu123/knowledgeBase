---
title: "2024WMCTF / crypto"
category: crypto
tags: ["crypto", "中文题解", "RSA", "origin_tag:imported_cats"]
signals: ["crypto", "中文题解", "RSA"]
difficulty: medium
source: "https://dexterjie.github.io/2024/09/17/%E8%B5%9B%E9%A2%98%E5%A4%8D%E7%8E%B0/2024WMCTF/"
tools: []
origin: imported_cats
origin_id: "cn-blog-dexter-f2e567a6-1"
origin_domain: "crypto"
origin_family: "chinese_blog"
origin_event: "WMCTF 2024"
origin_year: 2024
origin_license: "CC-BY-NC-SA-4.0"
origin_attribution: "2024WMCTF 的原作者（见原文署名）"
origin_verification: "author_report_not_reproduced"
origin_content_sha256: "4f72682bcac1eafd31ee1b869ccf91c583a7c86e2fbeee89f2273baa007b8a4e"
origin_body_sha256: 9f62b7021f29daa1ba2c9d3b677d3e79e5cb970477cf7ca05561fdd6253cdf2f
origin_title: "2024WMCTF / crypto"
origin_meta:
  asset_refs: []
  basis: "original_prose_not_runtime_verified"
  chunk_ids: [6006, 6007, 6008]
  content_sha256: "4f72682bcac1eafd31ee1b869ccf91c583a7c86e2fbeee89f2273baa007b8a4e"
  domain: "crypto"
  event: "WMCTF 2024"
  id: "cn-blog-dexter-f2e567a6-1"
  kind: "licensed_blog_wp_prose"
  language: "zh"
  license: "CC-BY-NC-SA-4.0"
  license_evidence_urls: ["https://creativecommons.org/licenses/by-nc-sa/4.0/"]
  local_path: "61_中文赛事资料/博客授权正文/dexter-f2e567a6.md"
  scope_note: "已核对页面CC许可，离线收录说明正文；代码和图片在此正文中省略，未复现。保留原作者未解决或不确定的表述，抽取可能损失公式排版。"
  source_author: "2024WMCTF 的原作者（见原文署名）"
  source_family: "chinese_blog"
  source_url: "https://dexterjie.github.io/2024/09/17/%E8%B5%9B%E9%A2%98%E5%A4%8D%E7%8E%B0/2024WMCTF/"
  tags: ["crypto", "中文题解", "RSA"]
  title: "2024WMCTF / crypto"
  verification_status: "author_report_not_reproduced"
  year: 2024
updated: 2026-10-31
---
# 2024WMCTF / crypto

> 本文由授权中文赛事 WP 正文导入（阶段 1，仅散文，代码段未导入）。
>
> - 来源：https://dexterjie.github.io/2024/09/17/%E8%B5%9B%E9%A2%98%E5%A4%8D%E7%8E%B0/2024WMCTF/
> - 许可：CC-BY-NC-SA-4.0
> - 署名：2024WMCTF 的原作者（见原文署名）
> - 文档族：chinese_blog
> - 赛事：WMCTF 2024
> - 年份：2024
> - 核验状态：author_report_not_reproduced
> - 正文 sha256：4f72682bcac1eafd31ee1b869ccf91c583a7c86e2fbeee89f2273baa007b8a4e
> - 导入 ID：cn-blog-dexter-f2e567a6-1
> - 原 domain：crypto
> - 许可依据：["https://creativecommons.org/licenses/by-nc-sa/4.0/"]
> - 本地快照：61_中文赛事资料/博客授权正文/dexter-f2e567a6.md
> - 收录说明：已核对页面CC许可，离线收录说明正文；代码和图片在此正文中省略，未复现。保留原作者未解决或不确定的表述，抽取可能损失公式排版。
> - 判定依据：original_prose_not_runtime_verified

> 原文：https://dexterjie.github.io/2024/09/17/%E8%B5%9B%E9%A2%98%E5%A4%8D%E7%8E%B0/2024WMCTF/

## 正文

2024WMCTF

发表于

2024-09-17

2024-09-17

更新于
      2025-10-07

分类于

Wp

Wp

阅读次数：

Waline：

本文字数：
      6.1k

本文字数：
      6.1k

阅读时长 ≈
      22 分钟

记录2024WMCTF——Crypto部分题解

K-Cessation

K-Cessation

task.py

根据密文的值，我们可以判断出轮子中部分位置的值是相反的。比如密文第一个值是2，那么说明wheel中第一位和第二位不同

密文第4个值是3，说明wheel中第5，6位和第七位不同。根据这些约束，我们可以解方程得到wheel

exp

把所有的解都弄出来尝试解密。

flag:

flag:

FACRT

task.py

找到一篇名为Revisiting PACD-based Attacks on RSA-CRT的论文

根据论文的格实现攻击

exp

flag:

flag:

RSA

task.py

$$M = \begin{pmatrix}m & -m-p-q&-m-2p&2q-m\\m+p+q&m&2q-m&m+2p\\m+2p&m-2q&m&-m-p-q\\m-2q&-m-2p&m+p+q&m\end{pmatrix}$$

$$C = M^e$$

把M化成Jordan型，存在P矩阵使得$$P^{-1}MP = M_{jordan}$$

$$C \equiv (PM_{jordan}P^{-1})^{65537} \mod n$$

$$C \equiv PM_{jordan}^{65537}P^{-1} \mod n$$

$$CP \equiv PM_{jordan}^{65537} \mod n$$

注意到$P$长这样$$P = \begin{pmatrix}1 & 1 & 1 &1\\0 & 0 & 0 & 0\\p_{2,0} & p_{2,1} & p_{2,2} & p_{2,3}\\p_{3,0} & p_{3,1} & p_{3,2} & p_{3,3}\\\end{pmatrix}$$P矩阵下面两行都是比较复杂的式子

那可以知道$CP$这个矩阵的第二行全是0

$$CP = \begin{pmatrix}c_{0,0}&c_{0,1} &c_{0,2} & c_{0,3}\\c_{1,0}&c_{1,1} &c_{1,2} & c_{1,3}\\c_{2,0}&c_{2,1} &c_{2,2} & c_{2,3}\\c_{3,0}&c_{3,1} &c_{3,2} & c_{3,3}\\end{pmatrix}\begin{pmatrix}1 & 1 & 1 &1\\0 & 0 & 0 & 0\\p_{2,0} & p_{2,1} & p_{2,2} & p_{2,3}\\p_{3,0} & p_{3,1} & p_{3,2} & p_{3,3}\\end{pmatrix}=\begin{pmatrix}t_{0,0}&t_{0,1} &t_{0,2} & t_{0,3}\\0&0&0&0\\t_{2,0}&t_{2,1} &t_{2,2} & 

t_{2,3}\\t_{3,0}&t_{3,1} &t_{3,2} & t_{3,3}\\end{pmatrix}$$

利用sagemath把第二行的值打印出来

得到的值还是有点复杂

我们利用之后得到

我们利用之后得到

实部:

提取出以下式子即可

虚部:

虚部:

这里两个式子再利用上$p\times q =n$，用gb基可以解出m,p,q

exp

这个返回的是p，具体原因我不太理解，得到p之后解矩阵RSA即可，注意$\phi(n) = (p^2-1)(q^2-1)$
