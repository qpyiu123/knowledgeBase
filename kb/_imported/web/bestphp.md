---
title: "bestphp"
category: web
tags: [r00t CTF 2024, wp prose]
signals: [bestphp]
difficulty: medium
source: "https://github.com/r00t-security-lab/rtctf2024/blob/a273041a04a5dd1eed3e5f49c9345719923a8e9f/Web/bestphp.md"
tools: []
origin: imported
origin_id: official-6fd5d1aef8f0f91211f9bf
origin_sha256: 6e8e797578e335bbb5206795dd3344ffa5205db79390705575ee05a0320a602e
origin_event: "r00t CTF 2024"
origin_kind: wp_prose
license: "not_declared"
updated: 2026-10-23
---
# r00t CTF 2024 / bestphp

> 来源：r00t CTF 2024  |  类型：wp_prose  |  https://github.com/r00t-security-lab/rtctf2024/blob/a273041a04a5dd1eed3e5f49c9345719923a8e9f/Web/bestphp.md

# bestphp

我用的 php 版本是 5.6.9

题目是⼀道简单的 php 反序列化


要求传入 2 个参数，txt 参数要求是文件，而且内容是 `welcome to r00t` 并且是强等于

那就可以用到 php 的伪协议 `php://input` 把原始数据通过 POST 传入，直接用 burp 访问 `?txt=php://input` 同时 POST 传入参数 `welcome to r00t` 如果返回'have fun'则说明进入了第一层

或者用 hackbar 但是要把 mode 改成 raw 模式：

〔原图省略〕 

内部是一个 Hint 的 class 文件，有一个变量 target，两个函数 \_\_wakeup 函数和 \_\_destruct 函数，这两个是 php 的魔术方法：

> destruct 函数：在析构函数会在到某个对象的所有引用都被删除或者当对象被显式销毁时执行。
>
> wakeup 函数：在 unserialize() 会检查是否存在一个 wakeup() 方法。如果存在，则会先调用 wakeup 方法，预先准备对象需要的资源。

所以直接反序列化：


但是这样传递，在反序列化的时候，会调用 wakeup,他会把 target 变量赋值成 wakeup！

这样在析构函数的时候就不能通过了，可以通过

- PHP5 \< 5.6.25
- PHP7 \< 7.0.10

在这些版本中的 php 有这个 cve-2016-7124 漏洞，可以修改反序列化传递的参数，例如把 1 改成 2，使得 wakeup 函数被跳过，这个时候就可以正常执行，获得 flag

〔原图省略〕

最终 payload `?txt=php://input&payload=O:4:"Hint":2:{s:6:"target";s:4:"r00t";}` 同时 POST 传递数据 `welcome to r00t`

## 原文配图

![image-20240530154545759](../../_assets/images/fdcb297df24274967b8c54361c9c67f1ef0aa4f260c56f3668cee9afc3510623.png)

![image-20240530155231778](../../_assets/images/98ec0655e887c3ed1e71abffbb6242d2e66b679ff09b84b54628c71973579253.png)
