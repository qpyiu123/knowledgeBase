---
title: "CISCN 2024 Qual Writeup / crypto"
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
# CISCN 2024 Qual Writeup / crypto

> 本文由授权中文赛事 WP 正文导入（阶段 1，仅散文，代码段未导入）。
>
> - 来源：https://blog.swizzer.cc/blog/ciscn-2024-qual-writeup/
> - 许可：CC-BY-4.0
> - 署名：CISCN 2024 Qual Writeup 的原作者（见原文署名）
> - 文档族：chinese_blog
> - 赛事：CISCN 2024 初赛
> - 年份：2024
> - 核验状态：author_report_not_reproduced
> - 正文 sha256：513c31fd2d741e4b64a54b6240fc5dddaa08f86563c48bcaa3729ab83441453b
> - 导入 ID：cn-blog-ciscn-swizzer-1
> - 原 domain：crypto
> - 许可依据：["https://creativecommons.org/licenses/by/4.0/"]
> - 本地快照：61_中文赛事资料/博客授权正文/ciscn-swizzer.md
> - 收录说明：已核对页面CC许可，离线收录说明正文；代码和图片在此正文中省略，未复现。保留原作者未解决或不确定的表述，抽取可能损失公式排版。
> - 判定依据：original_prose_not_runtime_verified

> 原文：https://blog.swizzer.cc/blog/ciscn-2024-qual-writeup/

## 正文

crypto

CISCN 2024 Qual Writeup

解了点Crypto和Misc题目，记录下自己的题解

题目的附件在探姬佬的repo ↗里可以找到，就不再额外说明题目了。

## 【来源分段】CISCN 2024 Qual Writeup _ misc

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

## 【来源分段】CISCN 2024 Qual Writeup _ crypto

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

## 【来源分段】CISCN 2024 Qual Writeup _ reverse

## 正文

Reverse#

asm_re#

三脚猫水平的我也只能做做Re签到了（

三脚猫水平的我也只能做做Re签到了（

汇编很长，不想看的话直接丢给GPT，GPT大概率会告诉你这玩意儿的主体逻辑的位置。稍微审计一下发现就是个仿射+异或，直接逆回去就行。

python

注意提取目标的数组的时候调一下分组大小和端序就行。
