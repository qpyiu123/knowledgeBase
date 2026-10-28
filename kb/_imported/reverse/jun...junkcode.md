---
title: "jun...junkcode?"
category: reverse
tags: [NewStar CTF 2024, wp prose]
signals: [jun...junkcode?]
difficulty: medium
source: "https://github.com/pj-newstar/wiki-docs/blob/1a0f2ba21a30f950276396118b315eef0328371c/docs/wp/2024/week5/reverse/junkcode.md"
tools: []
origin: imported
origin_id: official-36b4f160a80a65085268b3
origin_sha256: 2ef900581d31c94d421258c1e5b6ca68292bacff457670c7e828cf04acf331d0
origin_event: "NewStar CTF 2024"
origin_kind: wp_prose
license: "MIT"
updated: 2026-10-23
---
# NewStar CTF 2024 / jun...junkcode?

> 来源：NewStar CTF 2024  |  类型：wp_prose  |  https://github.com/pj-newstar/wiki-docs/blob/1a0f2ba21a30f950276396118b315eef0328371c/docs/wp/2024/week5/reverse/junkcode.md

# jun...junkcode?

打开题目，在这里发现了明显的花指令（`jz` - `jnz`）：

〔原图省略〕

「去花」后：

〔原图省略〕

恍然大悟！（然后发现这整段加密逻辑都是假的 QAQ）

关注 `sub_4017A9` 这个函数<span data-desc>（这些 API 均能在微软官方文档找到用法）</span>：

〔原图省略〕

这里就能发现一些问题：比如在之前的代码中，还没有映射过任何文件，这里怎么就取消映射了？

查看一下反复出现的 `qword_408A20` 的交叉引用：

〔原图省略〕

可以看到它在 `sub_401550` 这个函数中反复出现，检查一下这个函数：

〔原图省略〕

根据之前的分析，已经能推测出 `sub_401550` 肯定早在 `sub_4017A9` 之前就已经执行了，并且不难看出，`sub_401550` 中文件映射对象打开失败的逻辑对应父进程，打开成功的对应子进程

父进程向 `qword_408A20` 写入了如下内容：

| 地址/偏移       | 含义                                   |
| --------------- | -------------------------------------- |
| `408A20[0]`     | 父进程的进程 ID                        |
| `408A20[0] + 1` | 父进程 `sub_4017A9` 函数返回地址的地址 |
| `408A20[0] + 2` | `4201097`                              |

子进程根据这个文件映射修改父进程 `sub_4017A9` 的返回地址为 `4201097`（对应 `401A89h`）

::: info 关于反调试
这里要子进程调试父进程，如果在这之前父进程被其他进程调试了，子进程就无法附加调试，那自然无法执行正确的逻辑。
:::

可知，父进程在执行完 `sub_4017A9` 获取输入后，就跳转至 `401A89` 处继续执行

〔原图省略〕

从这里重新让 IDA 识别为代码，并反编译：

〔原图省略〕

看到了真正的加密逻辑，这段加密执行完后，跳转到了 `main` 函数里的判断部分

据此写出解密代码：


到这里，还剩下最后一个问题：`sub_401550` 是怎么被执行的？

查看一下 `sub_401550` 的交叉引用：

〔原图省略〕

再往前跟踪几个函数<span data-desc>（篇幅有限，不列出来了）</span>，能发现上面的函数最终在程序初始化阶段被 `sub_401BC0` 调用，然后才执行的 `main` 函数<span data-desc>（所以要是你比较闲，从程序入口节点步进也是能调出来的）</span>

〔原图省略〕
