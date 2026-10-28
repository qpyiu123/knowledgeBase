---
title: "[Web] ICS笑传之抄抄榜"
category: web
tags: [GeekGame 2024, wp prose]
signals: [[Web] ICS笑传之抄抄榜]
difficulty: medium
source: "https://github.com/PKU-GeekGame/geekgame-4th/blob/a21d7f7387512ec7ef77720e998d60efa16f2353/official_writeup/web-manuallab/README.md"
tools: []
origin: imported
origin_id: official-b39837fbb70c8548765a22
origin_sha256: 0c2266a3c7dc3b277319b8c02d45c417f243bb5856095ca243e26d03fdc861ab
origin_event: "GeekGame 2024"
origin_kind: wp_prose
license: "not_declared"
updated: 2026-10-23
---
# GeekGame 2024 / [Web] ICS笑传之抄抄榜

> 来源：GeekGame 2024  |  类型：wp_prose  |  https://github.com/PKU-GeekGame/geekgame-4th/blob/a21d7f7387512ec7ef77720e998d60efa16f2353/official_writeup/web-manuallab/README.md

# [Web] ICS笑传之抄抄榜

- 命题人：thezzisu
- 哈基狮传奇之我是带佬：200 分
- 哈基狮传奇之我是牢师：200 分
- 哈基狮传奇之我是嗨客：200 分

## 题目描述


**【网页链接：访问Autolab网站】**

**【网页链接：访问源码】**

## 预期解法

### Flag. 1

搜索往年的SOTA并不困难，但这并不是预期解。本题三个Flag都预计可以在30秒内解决（在找到攻击链条后，当然）。

同时，在提交后，可以在AutoGrader输出中发现Lab是如何评测的：


先解压Lab source然后解压Handin之后直接使用 `driver.pl` 评测。所以我们只需要上传一个假的，输出满分的 `driver.pl` 即可。

> [!NOTE]
> 本题的原型是古早的Lab可以通过类似的方式拿到满分。不过我不建议你这么尝试。
>
> 〔原图省略〕
> 
> 〔原图省略〕

### Flag. 2

由于给出了源码的PR链接，你只需要关注修改的部分即可。

〔原图省略〕

可惜截至比赛开始Autolab的人还是没有回应，所以就直接出成题了。

只需要在UAAA上修改邮箱为 `ics@guake.la` ，重新开一个实例并登录，你就是牢师了。

> 非预期解：非常好选手，又发现0day。访问 `/users/$id/update_password_for_user?id=$id` 可以任意重置其他账户密码并提权。

> [!NOTE]
> 本题是在今年接入OIDC的时候偶然发现的逻辑问题。

### Flag. 3

成为牢师后，当然是要给牢生们上上强度啦。上传的Lab里会包含一个 `labname.rb` 文件，使用Ruby可以反弹Shell然后找找flag在哪里。当然，也可以重载一些函数来控制Lab的UI，从而不出网也可以带回Flag，例如：


感谢诸位选手对开源安全工作的贡献。
