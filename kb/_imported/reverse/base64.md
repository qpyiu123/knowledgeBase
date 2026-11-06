---
title: "base64"
category: reverse
tags: [NewStar CTF 2024, wp prose]
signals: [base64]
difficulty: medium
source: "https://github.com/pj-newstar/wiki-docs/blob/1a0f2ba21a30f950276396118b315eef0328371c/docs/wp/2024/week1/reverse/base64.md"
tools: []
origin: imported
origin_id: official-faad918c9c39f28f5edd23
origin_sha256: 1a65996202d2da855543de931c4757f5c7aae8ac8bb4dde98a7078b387882354
origin_event: "NewStar CTF 2024"
origin_kind: wp_prose
license: "MIT"
updated: 2026-10-23
---
# NewStar CTF 2024 / base64

> 来源：NewStar CTF 2024  |  类型：wp_prose  |  https://github.com/pj-newstar/wiki-docs/blob/1a0f2ba21a30f950276396118b315eef0328371c/docs/wp/2024/week1/reverse/base64.md

# base64

在开始之前，你需要知道什么是 Base64，可参见 [密码学 base 的 WriteUp](/wp/2024/week1/crypto/base).

此题目是教大家定位主函数，Base64 的一个常见的魔改方式——换表，以及 CTF 一个编解码工具 [CyberChef](https://gchq.github.io/CyberChef/).

双击打开程序，我们看到如下界面：

〔原图省略〕

可以看到让你输入一个字符串，然后会判断对错。一般来说，`Enter the flag:` 这个字符串会离主逻辑不远，所以我们找到这个字符串的位置就可以定位到主逻辑。

在 IDA 中，按 <kbd>⇧ Shift</kbd><kbd>F12</kbd> 调出字符串界面。

〔原图省略〕

双击就可以转到对应的 IDA View.

〔原图省略〕

双击 `DATA XREF` 右边的地址加偏移，就可以到引用他的地方，按下 <kbd>F5</kbd>，即可反编译这段逻辑。

〔原图省略〕

这就是主逻辑了。看到 `=` 结尾的字符串可以想到 Base64（常识）。但是直接解会出乱码。

此处需要大家识别出 Base64 算法的魔改点。大家可以自行对比标准的 Base64 编码算法，为了不过多增加难度，我仅把码表换了。

〔原图省略〕

base64标准码表是 `ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789+/`，这里换成了 `WHydo3sThiS7ABLElO0k5trange+CZfVIGRvup81NKQbjmPzU4MDc9Y6q2XwFxJ/`.

推荐使用`CyberChef`进行解密，这个工具用了的都说牛逼，你也来试试吧！

〔原图省略〕

把左边的「From base64」拖到「Recipe」那一栏，然后把「Alphabet」换成上面说的魔改后的码表，「Input」处输入密文，「Output」处就得到 flag 了。当然，编写脚本解码也是可以的。

## 原文配图

![运行界面](../../_assets/images/ce18d1f0964860cf6f4a3bea197bf5445b1646e0f36f8ff73f1cf207c8ef5776.png)

![IDA 界面 1](../../_assets/images/b5142833e53016831b72a473569969c14ce63afae643406c88d441bc8dcaa2da.png)

![IDA 界面 2](../../_assets/images/6fb378cdd1f9feda057b120b66b6f2065876ff0fcb01b781130cbad1f8b9739d.png)

![IDA 界面 3](../../_assets/images/e2f7ea43f25c357e8768a9bdc43f7f1452bbb526029ee60b6d40dcf85a01c921.png)

![IDA 界面 4](../../_assets/images/b2ad9cb3777262e0949ac8c66a38aa2f6dc14fcc8c7442392dc7f04f8d0de135.png)

![CyberChef 界面](../../_assets/images/961f57adaec120852c21d14b83c3cd4ed301ea5976eeedfe0e66b27d7f962e64.png)
