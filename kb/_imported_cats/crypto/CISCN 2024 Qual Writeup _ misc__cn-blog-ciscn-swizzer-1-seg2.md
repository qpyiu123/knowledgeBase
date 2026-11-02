---
title: "CISCN 2024 Qual Writeup / misc"
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

Misc#

通风机#

TriID识别出是Sybase iAnywhere的database，不过似乎并不对。Google了一下基本都指向Siemens的S7-200 Program，随便找了个下载站 ↗下载安装。这里建议装在虚拟机，毕竟我对于这类下载站都不很信任，并且这个上古软件本身就很脏…

安装之后也并不能直接打开这个mwp文件，找一份mwp文件对比一下+各方搜索，确认是文件头缺少了3字节。添加上之后正常打开，在Symbol Table里有

base64 decode即可。

Update: 复现发现直接binwalk -e分离文件后strings就能拿到那串base64。这个套路我本来还挺熟悉的，结果赛场上还是太路径依赖了…

盗版软件#

很神奇的题目，解压得到一个dmp和一个exe。最初直接010 editor人肉盯帧dmp文件找到了个，交flag碰壁数十次之后觉得应该不是这个域名…后来和队友头脑风暴了半个小时，想起来头天晚上复盘前些年的CISCN时用到的gimp，抱着试试看的心态将dmp作为raw data打开图像，手工fuzz了位移和宽高(unintended solution可能？抽象做法)后整出来了：

IP地址还得从exe入手，扔沙箱里看到exe运行后生成了loader.exe和一个png。对malware有经验的应该马上就能反应过来png里大概有shellcode，而loader就是加载Shellcode连接C2执行后续恶意行为的。png丢到Stegsolve里盯出来了LSB隐写：

典型的，zip头。让GPT搓个脚本提取出zip：

python

提取之后删除多余的一坨文件尾，解压得到.b。.b看起来很像base85，猜测解码之后就是Shellcode——你说的对，但是题目给的loader.exe压根就不是exe而是一坨0xff(或许我的附件有问题？)，我一度以为还需要手搓Shellcode loader😅

解码后的文件丢VT上一堆报毒(貌似是MetaSploit家族的？)，但是YARA规则没识别出IP。丢微步 ↗发现已经有结果了，应该是做出来的前人传的吧：

MD5之后，提交，get。

可惜此时已经黑灯了，导致后来队友出的另外两道题只能挑一道提交，不过好在另两道最后都是50分，倒也没有亏什么分数😇

flag{096e8b0f9daf10869f013c1b7efda3fd}

神秘文件#

和队友合力解的，硬控3h是真的坐牢🤪

和队友合力解的，硬控3h是真的坐牢🤪

细节不想写了，大概说一下卡住的几个点吧。

宏里面的RC4没有密钥，且密码学工具箱不能正常解密(也可能我操作不当，欢迎交流)。(找了一下午密钥你告诉我密钥为空？)

属性里的是没用的

属性里的是没用的

第四张PPT里检查阅读顺序可以拿到Part7

幻灯片母版里有Part8。其实这里直接解压PPT会发现一个看似没有用到的文本框，作为线索可以找到这个点。
