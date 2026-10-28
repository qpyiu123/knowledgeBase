---
title: "TIME HACKER"
category: misc
tags: [NewStar CTF 2025, wp prose]
signals: [TIME HACKER]
difficulty: medium
source: "https://github.com/pj-newstar/wiki-docs/blob/1a0f2ba21a30f950276396118b315eef0328371c/docs/wp/2025/week5/misc/time-hacker.md"
tools: []
origin: imported
origin_id: official-f0b0c630b3020f1050b752
origin_sha256: ab6319afeb7e49070165145410c3a6015a8536e14171c0a7af3b523dff81f2f0
origin_event: "NewStar CTF 2025"
origin_kind: wp_prose
license: "MIT"
updated: 2026-10-23
---
# NewStar CTF 2025 / TIME HACKER

> 来源：NewStar CTF 2025  |  类型：wp_prose  |  https://github.com/pj-newstar/wiki-docs/blob/1a0f2ba21a30f950276396118b315eef0328371c/docs/wp/2025/week5/misc/time-hacker.md

# TIME HACKER

> 我所害怕的，只有时间

> [Misc] TIME HACKER.zip

这道题的知识点包含侧信道攻击、时间戳隐写和 EXIF 信息读取。

首先将压缩包文件拖入 010 Editor，发现文件尾部存在冗余的 Base64 编码数据，解码后可得到提示信息：

> I heard you can hack the time in different dimensions?

〔原图省略〕
〔原图省略〕
下面继续分析该提示的含义。

`password_checker.exe` 用于校验压缩包密码是否正确。
〔原图省略〕
直接逆向该程序获取密码并不现实，因为该 exe 加了 VMProtect 壳。

我们再把 FLAG.zip 文件拖入 010 尾部依旧存在冗余数据，解码后可获得提示

〔原图省略〕

> The password is ten digits

〔原图省略〕
此时可以考虑直接爆破密码，但 ARCHPR 预估时间达到 7 天，无法在比赛时间内完成。

因此，前面提示中「hack the time」指向的是通过侧信道时间攻击获取压缩包密码。

输入密码后，程序会延迟一段时间再输出正确或错误，这正是漏洞所在。经过测试，可以推测后端校验逻辑大致如下：


因此只需要编写脚本反复调用 `password_checker.exe`，按响应时间逐位爆破密码即可。


得到密码 `2145768093`。

> 有选手通过猜测密码与被压缩文件的时间戳有关，在其时间戳附近爆破也得到了密码；这实际上与下一阶段有关。

观察解压后的图片。
〔原图省略〕

> 一个文件包含三个时间：创建时间、访问时间、修改时间。

可以注意到修改时间异常，推测出题人通过该时间隐藏了信息。将其转换为时间戳后发现与密码值相差不大，因此很可能通过二者差值隐藏信息。打印差值：


此时已经能看出 FLAG 字符，但字符顺序不正确。图片的 EXIF 信息也是常见的信息隐藏载体，因此可以从 EXIF 中读取文件顺序。最终脚本如下：
