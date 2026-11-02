---
title: "CISCN 2024 Qual Writeup / crypto"
split_from: "_imported_cats/crypto/CISCN 2024 Qual Writeup _ crypto__cn-blog-ciscn-swizzer-1.md"
category: crypto
tags: ["crypto", "中文题解", "origin_tag:imported_cats"]
signals: ["crypto", "中文题解", "origin_tag:imported_cats"]
difficulty: medium
source: "https://blog.swizzer.cc/blog/ciscn-2024-qual-writeup/"
tools: []
origin: imported_cats
origin_id: "cn-blog-ciscn-swizzer-1"
origin_domain: "crypto"
origin_family: "chinese_blog"
origin_event: "CISCN 2024 初赛"
origin_year: 2024
origin_license: "CC-BY-4.0"
origin_attribution: "CISCN 2024 Qual Writeup 的原作者（见原文署名）"
origin_verification: "author_report_not_reproduced"
origin_content_sha256: "513c31fd2d741e4b64a54b6240fc5dddaa08f86563c48bcaa3729ab83441453b"
origin_body_sha256: 03ad2906fe83bd27772317525559e62c7d42d5f1a85dabd159e7a0a0bbc708ad
origin_title: "CISCN 2024 Qual Writeup / crypto"
origin_meta:
  asset_refs: []
  basis: "original_prose_not_runtime_verified"
  chunk_ids: [5881, 5882, 5883]
  content_sha256: "513c31fd2d741e4b64a54b6240fc5dddaa08f86563c48bcaa3729ab83441453b"
  domain: "crypto"
  event: "CISCN 2024 初赛"
  id: "cn-blog-ciscn-swizzer-1"
  kind: "licensed_blog_wp_prose"
  language: "zh"
  license: "CC-BY-4.0"
  license_evidence_urls: ["https://creativecommons.org/licenses/by/4.0/"]
  local_path: "61_中文赛事资料/博客授权正文/ciscn-swizzer.md"
  scope_note: "已核对页面CC许可，离线收录说明正文；代码和图片在此正文中省略，未复现。保留原作者未解决或不确定的表述，抽取可能损失公式排版。"
  source_author: "CISCN 2024 Qual Writeup 的原作者（见原文署名）"
  source_family: "chinese_blog"
  source_url: "https://blog.swizzer.cc/blog/ciscn-2024-qual-writeup/"
  tags: ["crypto", "中文题解"]
  title: "CISCN 2024 Qual Writeup / crypto"
  verification_status: "author_report_not_reproduced"
  year: 2024
updated: 2026-10-31
---

## 正文

Crypto#

古典密码#

感谢cyberchef，在我走投无路的时候信手筛选了下Cipher，把第一个Atbash Cipher拖进去直接就魔法棒了🪄

OvO#

挺不错的数学题，听人说跟XY的某个Copper是同一篇Paper？不过我是没看出来，欢迎各位指教。

一个有用的观察是e//n=rre//n = rre//n=rr，这样就消去了一个变量。我们拿到的e经过了截位，并且高位信息明显跟p，q有关，所以需要想办法抠出点p或者q的高位信息。

在纸上推算一会儿可以发现，65537+kk∗p+rr∗((p+1)∗(q+1))+165537 + kk * p + rr * ((p+1) * (q+1)) + 165537+kk∗p+rr∗((p+1)∗(q+1))+1这个式子乘上p是可以再消去一个变量的，接下来就可以尝试多项式求根了。

如果e没有截位，那么我们拿到f=(65537∗x+kk∗x2+(kk+2)∗n∗x+(kk+2)∗x2+(kk+2)∗n+(kk+3)∗x)−e∗xf = (65537*x + kk*x^2 + (kk+2)*n*x + (kk+2)*x^2 + (kk+2)*n + (kk+3)*x) - e*xf=(65537∗x+kk∗x2+(kk+2)∗n∗x+(kk+2)∗x2+(kk+2)∗n+(kk+3)∗x)−e∗x之后直接f.roots()就可以得到p。但是e经过了截位，所以得到的x其实比p要大/小一点，不过这已经可以让我们拿到p的高位了——拿到高位就够了。后面就是简单的p高位泄露。

python

python

嗯，exp里的Copper函数其实不是CopperSmith，之所以叫这个是因为是从CopperSmith的板子改过来的，我懒得改名字了（轻喷qwq

*hash#

python 2.7内置的hash是魔改了一点的fnv hash，问问GPT就可以得到实现细节。爆破的时候使用中间相遇的手法，可以大幅降低时间复杂度。

因为赛场上没去翻源码又理解错了GPT的回复，以为输出前异或的是bit length，所以最后与flag失之交臂😭😭其实Python 2.7的hash最后是与byte length做异或后输出。

python

翻了一下CTF wiki，发现直接拿格子去打也是可以的，实验了一下速度确实快上不少。只能说学海无涯了。
