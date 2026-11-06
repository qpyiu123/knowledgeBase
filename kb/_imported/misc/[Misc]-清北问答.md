---
title: "[Misc] 清北问答"
category: misc
tags: [GeekGame 2024, wp prose]
signals: ["[Misc] 清北问答", "Git"]
difficulty: medium
source: "https://github.com/PKU-GeekGame/geekgame-4th/blob/a21d7f7387512ec7ef77720e998d60efa16f2353/official_writeup/misc-trivia/README.md"
tools: []
origin: imported
origin_id: official-9fc0e5d74c3b20af66aa19
origin_sha256: 666a5d81e2bdfe15c9ed6c16623ad604745cdb2235dc0f0fe2446c723878f48b
origin_event: "GeekGame 2024"
origin_kind: wp_prose
license: "not_declared"
updated: 2026-10-23
---
# GeekGame 2024 / [Misc] 清北问答

> 来源：GeekGame 2024  |  类型：wp_prose  |  https://github.com/PKU-GeekGame/geekgame-4th/blob/a21d7f7387512ec7ef77720e998d60efa16f2353/official_writeup/misc-trivia/README.md

# [Misc] 清北问答

- 命题人：xmcp、debugger
- Flag 1：150 分
- Flag 2：200 分

## 题目描述

.tp-rotate {
}
.tp-rotate>span {
}
@keyframes tp-rotate {
}


**【网页链接：访问题目网页】**

## 预期解法

### Q1

> 在清华大学百年校庆之际，北京大学向清华大学赠送了一块石刻。石刻**最上面**一行文字是什么？
>
> 答案格式：`^[\u4E00-\u9FFF\w]{10,15}$`
>
> 答案：`贺清华大学建校100周年`

首先通过各种手段找到这块石头的照片，比如 [这篇公众号](https://mp.weixin.qq.com/s?__biz=MTI0MDU3NDYwMQ==&mid=2656664430&idx=1&sn=7865ab67e46631403412369287378e7f&chksm=7a6386884d140f9ed4a4c59597b6d611b82b2b430b3e247a3e7a33418d3a49f24bf956fe3f64&scene=27) 和 [维基百科](https://commons.wikimedia.org/wiki/File:%E6%B8%85%E5%8D%8E%E5%8C%97%E5%A4%A7%E5%8F%8B%E8%B0%8A%E9%95%BF%E5%9C%A8%E7%9F%B3.jpg) 上面都有。如果你是校内选手，也可以选择线下观看。

需要注意本题答案不是 “清华北大友谊常在”，因为它上面还有一行字。问最上面这行字而不是 “清华北大友谊常在” 是为了防止校内选手对这八个字印象深刻从而对此题获得过大的相对优势 <del>逃课</del>。本题通过答案格式里的字数限制避免了选手不小心输入这个错误答案。

### Q2

> 有一个微信小程序收录了北京大学的流浪猫。小程序中的流浪猫照片被存储在了哪个域名下？
>
> 答案格式：`^[a-z.-]+$`
>
> 答案：`pku-lostangel.oss-cn-beijing.aliyuncs.com`

首先搜到这个小程序叫 “燕园猫速查手册”。

〔原图省略〕

然后，抓包，启动！

〔原图省略〕

不抓包的话也可以做。先找到小程序源码的[仓库](https://gitee.com/circlelq/yan-yuan-mao-su-cha-shou-ce)：

〔原图省略〕

然后在代码里的各种地方都能找到这个域名。

〔原图省略〕

### Q3

> 在 Windows 支持的标准德语键盘中，一些字符需要同时按住 AltGr 和另一个其他按键来输入。需要通过这种方式输入的字符共有多少个？
>
> 答案格式：`^\d+$`
>
> 答案：`12`

看看 [维基百科](https://en.wikipedia.org/wiki/German_keyboard_layout)，或者 [微软文档](https://learn.microsoft.com/en-us/globalization/windows-keyboard-layouts)，数出来共有 12 个字符。计数题最简单的一集.jpg

〔原图省略〕

### Q4

> 比赛平台的排行榜顶部的图表是基于 `@antv/g2` 这个库渲染的。实际使用的版本号是多少？
>
> 答案格式：`^[\d.]+$`
>
> 答案：`5.2.1`

先去看比赛平台的前端源码。发现 Git 仓库里喜提 `package-lock.json` 文件，在里面搜索可得。或者直接 `npm install` 一下也行。

〔原图省略〕

爱你.jpg

注意到有很多人被这行误导从而写了 `5.1.18`：

〔原图省略〕

如果你仔细看了前面几行的内容，就会注意到它的实际含义是比赛平台依赖的 `@ant-design/plots` 这个库它依赖于不低于 `5.1.18` 版本的 `@antv/g2`。因此，这并不是实际使用的版本号，只是一个最低的限制。

### Q5

> 在全新安装的 Ubuntu Desktop 22.04 系统中，把音量从 75% 调整到 25% 会使声音减小多少分贝？（保留一位小数）
>
> 答案格式：`^\d+\.\d$`
>
> 答案：`28.6`

最方便的方法是拿 U 盘刻个 22.04 的 LiveCD 玩玩或者开个虚拟机玩玩。用百度以外的搜索引擎搜索 “ubuntu command line set volume”，发现有一个叫 `pactl` 的命令：

〔原图省略〕

既然能 `set` 那也能 `get`。于是 `pactl set-sink-volume 1 xxx` 然后 `pactl get-sink-volume 1`。

我在 LiveCD 里面试出来的音量是 75% 对应 -7.50 dB，25% 对应 -36.12 dB，减一下即可得到答案。下图为拍屏，因为 LiveCD 里面懒得截图（

〔原图省略〕

当然，直接上网搜也是能做的，就是比较麻烦。比如说，我们搜 “pulseaudio volume curve”：

〔原图省略〕

点开第一个 [ArchLinux 论坛里的帖子](https://bbs.archlinux.org/viewtopic.php?id=211768)，看到一则回复：

〔原图省略〕

继续点开 [Bugzilla 链接](https://bugzilla.redhat.com/show_bug.cgi?id=502057)，可以看到下面有人说 PulseAudio 音量百分比和具体响度为立方的关系（在所有操作系统里这都不是线性的，要不然你就会发现音量70%-100%无事发生，20%-50%天差地别，Windows似乎用的是平方）：

〔原图省略〕

或者直接 [看源码](https://cgit.freedesktop.org/pulseaudio/pulseaudio/tree/src/pulse/volume.c#n278) 也是一种选择：

〔原图省略〕

于是计算一下 `0.75**3` 和 `0.25**3` 转换为分贝之后的结果，即可得到答案。

有一些人用 alsamixer 查看的音量，发现得到的答案是 28.5 dB，和正确答案差一点。我不知道具体是什么情况，但怀疑是因为精度问题：25% 音量对应的 -36.12 dB 已经很小声了，如果它显示的 dB 值是从振幅转换回来的就很可能出现一定误差。

顺便一提，此题选择了 Ubuntu 22.04 而非最新的 24.04，是因为 24.04 的音频系统用了 Pipewire 框架，`pactl` 似乎默认不装（至少 LiveCD 里没有）。考虑 Pipewire 网上资料相对较少，所以限定了 22.04。

### Q6

> [这张照片](game/static/osint-challenge.webp)用红框圈出了一个建筑。离它最近的已开通地铁站是什么？
>
> 答案格式：`^[^站]+$`
>
> 答案：`通州北关`

图中显而易见 “七星公馆” 的招牌没有被涂黑，看起来过于刻意，因此我们搜索一下：

〔原图省略〕

可以遍历得到的每个结果，发现北京市通州区这个七星公馆周围有条河，看着很逼真。于是选中七星公馆西北方向的这座桥，街景，启动！

我去，船！我去，塔！

〔原图省略〕

甚至点下面的 “时光机” 按钮，把时间调回 2016 年，还能看见同款招牌。就这个了！（因为这题的图片就是从百度街景里面截的，所以你当然能看见）

〔原图省略〕

于是返回地图，找到那个塔，再找到地铁站就OK。注意答案格式要求，没有结尾的 “站” 字。

## 花絮

这 6 个题目的解出人数分别为 614、413、419、314、234、382。这些数据是截止到比赛结束时的，在第一阶段时第五题只有 170 多个人解出，是所有题目里最少的（也符合出题时的预期）。

让我们来看看选手们每个题目都写了什么答案（计数为答案出现的次数，因此每人可以贡献多次）：

〔原图省略〕

〔原图省略〕

〔原图省略〕

〔原图省略〕

〔原图省略〕

〔原图省略〕

## 原文配图

![image-20241019202246496](../../_assets/images/b3d56ae7f55babb30cc508d8028af5facf45a636f454f35444efc1d16138b353.png)

![image-20241019202452037](../../_assets/images/93a445376c060cb575b29667ad3c7424b3a9e4f0aa92ae251eb8e020ab0844e3.png)

![image-20241019202858356](../../_assets/images/ea8d9912a0f9689dfebab1cfa8dc6c07692afa20326fe467dea322c2b059a20a.png)

![image-20241019203152681](../../_assets/images/e4f1860f252ce13c57b46fe3f2106c4affb44d8ce53fb009e28b674ecaa1a513.png)

![image-20241019204101698](../../_assets/images/6565de9faa28ed21d80d7c901221d5ae532020e576a857e33682ccf5cad25ddb.png)

![image-20241019204419778](../../_assets/images/8a5622395fcf8ca3369b5e2db682f3084356e1f149bb930cc4e7bae9ac165f96.png)

![image-20241020220352835](../../_assets/images/383961a8d276a403c86d6cf1d737754f7e5c3566fe39ac6f2660316f492c3439.png)

![image-20241019204916921](../../_assets/images/3cedb52d05c4b5a452d6fbd78e8bcb70973c207f9d05dec1cdbf7b8de04eee1c.png)

![image-20241019205107366](../../_assets/images/4a0c09a0e4818af4b217401348143b6990580a75f4dedf30e0ef2c01eae8a608.png)

![image-20241019205711875](../../_assets/images/38ba5489345ccb34f60dc5a0fc42b3ea850d3ac8a2f7ab3b93f68621abebc3eb.png)

![image-20241019205817749](../../_assets/images/76fd393a476892733a4150e86580e82bc9f97d5ccfb5c1816f5b99bec4e26984.png)

![image-20241019210001205](../../_assets/images/33863e6acf37392abb5a1770833b8c9ec37d50e7a141cc7668b472ea739404d1.png)

![image-20241019210139561](../../_assets/images/6b83dd605c76ab24cfdf3d364203c1d85336779bc794797bff5eb1b6921afe2d.png)

![image-20241019210625426](../../_assets/images/5ec6ebeb91c5c263d23a5f00d787d38e4016993cd27499f636c7252f05a40cd3.png)

![image-20241019211233312](../../_assets/images/d26264ac647d3da0355c9619854d429de2be4888a103331518ac77197cd14ca0.png)

![image-20241019211544307](../../_assets/images/f4e58da2806ce02d21496a34bac601ac75415b2f58343b4ea6075489979ba55e.png)

![image-20241020163811018](../../_assets/images/ae8b5d86411bd8b4b2c82547a19e642659b5207c3de456e2cad562a2c3149d50.png)

![image-20241020163858687](../../_assets/images/62e58856a2e4792d8fed20d9315400ed369c9aded3a5d697703da3ddcb237a16.png)

![image-20241020163936202](../../_assets/images/48d300a138a652ecbc91893c548050f0fab0bd5779d38601481c34c88825d325.png)

![image-20241020164214366](../../_assets/images/cd34b36417594c95992c4b12b6082db65d8c3012514d1edf25377eb06e873081.png)

![image-20241020164316735](../../_assets/images/05d842bef1503015a791f2abf117655736dffd698eb17943efff67ccd5204b0b.png)

![image-20241020164426076](../../_assets/images/12fb21ea57b3ae1fa3ae8a38b5d1e5b3b03d1cb7fdde87fbe210907cd88a8a64.png)
