---
title: "crypto"
category: crypto
tags: [CISCN 2024 初赛, licensed blog wp prose]
signals: [crypto]
difficulty: medium
source: "https://blog.swizzer.cc/blog/ciscn-2024-qual-writeup/"
tools: []
origin: imported
origin_id: cn-blog-ciscn-swizzer-3
origin_sha256: 7684f1387ccd74f99adbf6e2d17f50af56df22c0d53ce61db7584decf167f329
origin_event: "CISCN 2024 初赛"
origin_kind: licensed_blog_wp_prose
license: "CC-BY-4.0"
updated: 2026-10-23
---
# CISCN 2024 Qual Writeup / crypto

> 来源：CISCN 2024 初赛  |  类型：licensed_blog_wp_prose  |  https://blog.swizzer.cc/blog/ciscn-2024-qual-writeup/

Crypto#

古典密码#

感谢cyberchef，在我走投无路的时候信手筛选了下Cipher，把第一个Atbash Cipher拖进去直接就魔法棒了🪄

OvO#

挺不错的数学题，听人说跟XY的某个Copper是同一篇Paper？不过我是没看出来，欢迎各位指教。

一个有用的观察是e//n=rre//n = rre//n=rr，这样就消去了一个变量。我们拿到的e经过了截位，并且高位信息明显跟p，q有关，所以需要想办法抠出点p或者q的高位信息。

在纸上推算一会儿可以发现，65537+kk∗p+rr∗((p+1)∗(q+1))+165537 + kk * p + rr * ((p+1) * (q+1)) + 165537+kk∗p+rr∗((p+1)∗(q+1))+1这个式子乘上p是可以再消去一个变量的，接下来就可以尝试多项式求根了。

如果e没有截位，那么我们拿到f=(65537∗x+kk∗x2+(kk+2)∗n∗x+(kk+2)∗x2+(kk+2)∗n+(kk+3)∗x)−e∗xf = (65537*x + kk*x^2 + (kk+2)*n*x + (kk+2)*x^2 + (kk+2)*n + (kk+3)*x) - e*xf=(65537∗x+kk∗x2+(kk+2)∗n∗x+(kk+2)∗x2+(kk+2)∗n+(kk+3)∗x)−e∗x之后直接f.roots()就可以得到p。但是e经过了截位，所以得到的x其实比p要大/小一点，不过这已经可以让我们拿到p的高位了——拿到高位就够了。后面就是简单的p高位泄露。

python

嗯，exp里的Copper函数其实不是CopperSmith，之所以叫这个是因为是从CopperSmith的板子改过来的，我懒得改名字了（轻喷qwq

*hash#

python 2.7内置的hash是魔改了一点的fnv hash，问问GPT就可以得到实现细节。爆破的时候使用中间相遇的手法，可以大幅降低时间复杂度。

因为赛场上没去翻源码又理解错了GPT的回复，以为输出前异或的是bit length，所以最后与flag失之交臂😭😭其实Python 2.7的hash最后是与byte length做异或后输出。

python

翻了一下CTF wiki，发现直接拿格子去打也是可以的，实验了一下速度确实快上不少。只能说学海无涯了。
