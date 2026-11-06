---
title: "Maze_Rust"
category: pwn
tags: [NewStar CTF 2024, wp prose]
signals: [Maze_Rust, Rust]
difficulty: medium
source: "https://github.com/pj-newstar/wiki-docs/blob/1a0f2ba21a30f950276396118b315eef0328371c/docs/wp/2024/week4/pwn/maze_rust.md"
tools: []
origin: imported
origin_id: official-3f3e0e66db71d5e1f333bc
origin_sha256: edf3881ba8cee0067edf67ce7ad775f80ee3e896d8348016557f9c5e80ec1cb2
origin_event: "NewStar CTF 2024"
origin_kind: wp_prose
license: "MIT"
updated: 2026-10-23
---
# NewStar CTF 2024 / Maze_Rust

> 来源：NewStar CTF 2024  |  类型：wp_prose  |  https://github.com/pj-newstar/wiki-docs/blob/1a0f2ba21a30f950276396118b315eef0328371c/docs/wp/2024/week4/pwn/maze_rust.md

import Container from '@/components/docs/Container.vue'

# Maze_Rust

〔原图省略〕


IDA 逆向看不懂，先当黑盒打（

## 解法一

进入程序，发现这是个简单的迷宫

〔原图省略〕

于是可以搓脚本，读取迷宫用算法解迷宫了

成功解出迷宫后，会让我们输入

〔原图省略〕

随便试试可以发现，这是一个 `system()`，可以执行我们输入的东西

贴一个 GPT 生成的迷宫脚本


## 解法二

观察力惊人的我们发现，菜单

〔原图省略〕

只出现了 1、3，唯独跳过了 2，于是好奇心过剩的我们，尝试输入 `2`，得到了一句提示

〔原图省略〕

当然，不知道是什么数字也没事，我们可以掏出 IDA，一逆究竟

:::tip
本题是用 Rust 编写的，这会导致在 IDA 中会显得十分杂乱
:::

Rust 编译出来的程序，其主函数在 `Maze_Rust::main` 中

〔原图省略〕

进入到主函数中，我们通过题目的功能来进行猜测。题目的菜单要求我们输入数字来进行选择，我们找到类似多个 if 判断选择的地方

〔原图省略〕

在这段代码中，我们发现程序对 `v74` 进行了多次的if比较，猜测它就是我们输入的数字，判断后执行的如 `generate_maze`，也符合程序中菜单的功能

通过逆向<span data-desc>（或是对绫地宁宁的理解）</span>我们可以知道，输入的数字是 `0721`

〔原图省略〕

在代码中，我们发现程序对 DEBUG 的一个全局变量做了修改

〔原图省略〕

通过 <kbd>X</kbd> 键查找引用

〔原图省略〕

找到了第二处引用的位置，因此在第二次附近，我们猜测就是 Backdoor 的 Stage2

〔原图省略〕

激活后门 Stage1 后，程序会给出提示

〔原图省略〕

〔原图省略〕

我们找到输入的地方，发现输入的字符串最终是 `v20`，并且和后面的东西进行了 `cmp` 比较

〔原图省略〕

:::tip
Rust 的字符串比较用上了 xmm 寄存器，提高效率
:::

跟进查看这两处存的字符

〔原图省略〕

使用 <kbd>⇧ Shift</kbd><kbd>E</kbd> 提取内容

〔原图省略〕

〔原图省略〕

合起来就是 `I'm the best pwner!!!`

于是我们输入就可以 Get Shell：

〔原图省略〕

## 原文配图

![Maze_Rust](../../_assets/images/ec925034db33937a858cc38f24c00024888b3c07749a32fa4b282c7e4f765d62.png)

![迷宫](../../_assets/images/9bc8ea0233fac9cc3fe1955cbb6594384b84ca7b80eb335db3c826367408da19.png)

![输入](../../_assets/images/6f4a255d8dc6546f603d2dccb6ebb0c54bdda5861a4b153853023a1a7347822b.png)

![菜单](../../_assets/images/9117539cb798355d79d6677878514ca2418068167bfaa4135ed950beb08156e1.png)

![提示](../../_assets/images/a7eba88c97677f1767ddd991fa2210fdd58a0a6ae1956351616eb9c951e911e8.png)

![main](../../_assets/images/129109b6d682a905d3191fff3b7aeddd78e0ff60ba51248730f976697825d10b.png)

![if 比较](../../_assets/images/f9c2cf948ed5cf6d664a85d0d9d602c80a6be77b5888ea6b294854d69bb710fa.png)

![0721](../../_assets/images/91fbe5034d4d1dc87028da823b3ba7f51a377af0b69350456783a5e975cf088a.png)

![DEBUG](../../_assets/images/76d11b600b38126e366b06725799d9624046d1a0fdf65c18ba17bc0bfd7945c0.png)

![交叉引用](../../_assets/images/e8b7f0d4a3fc63498ae5c813dbd56b41c63353bcc60bd576289aacd1f8dee820.png)

![Stage2](../../_assets/images/0e625c91af078117ec98db282cc12bf7076a374de54892e496e6b825d87e3f70.png)

![提示](../../_assets/images/c40f629368355fb27ae515e619d670ec21c78c73e733388e93fee35a00741268.png)

![IDA 反编译看代码](../../_assets/images/f8c3998ba6bae89dcbac324d9f07d355c9cc9772ef2dbf7d350f5f45c44bd116.png)

![cmp](../../_assets/images/4694732072ad9d93d34bc95f564c4921db2a80fa5635dac669d736aec4afad3f.png)

![字符](../../_assets/images/5628569df0cb78b462a8b99070fe8c38d7680f2eacad7cf8a3885b0967fa7d9a.png)

![提取 1](../../_assets/images/6a3f27d0099b551d2a66bcb3594e61091d71d92500fc29d9967061e052a9e0a9.png)

![提取 2](../../_assets/images/4a7aa24e1c69db9f369e2ce47cba86ec54ce8101193a7d0198c841ba2dcbd163.png)

![输入](../../_assets/images/43e66be44ff73575bce6cf19510c8ec3c7bbbbd49a15f804e3130adb4005e675.png)
