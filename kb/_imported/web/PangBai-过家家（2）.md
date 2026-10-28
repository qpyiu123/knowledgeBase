---
title: "PangBai 过家家（2）"
category: web
tags: [NewStar CTF 2024, wp prose]
signals: [PangBai 过家家（2）, Git, PHP]
difficulty: medium
source: "https://github.com/pj-newstar/wiki-docs/blob/1a0f2ba21a30f950276396118b315eef0328371c/docs/wp/2024/week2/web/pangbai2.md"
tools: []
origin: imported
origin_id: official-97691741347daf0d88fc2a
origin_sha256: 73fd962006cd35eb53b2a6f86c59c6c4ca17f05ad05a85eff40d053a463509ab
origin_event: "NewStar CTF 2024"
origin_kind: wp_prose
license: "MIT"
updated: 2026-10-23
---
# NewStar CTF 2024 / PangBai 过家家（2）

> 来源：NewStar CTF 2024  |  类型：wp_prose  |  https://github.com/pj-newstar/wiki-docs/blob/1a0f2ba21a30f950276396118b315eef0328371c/docs/wp/2024/week2/web/pangbai2.md

# PangBai 过家家（2）

题目所给出的提示是文件泄露（其实用 dirsearch 等扫描工具也可以扫描到 .git 目录）。

〔原图省略〕

使用 [GitHacker](https://github.com/WangYihang/GitHacker) 工具从 .git 文件夹中泄露文件到本地。

〔原图省略〕

:::info 关于 GitHacker

GitHacker 工具可快速使用 pip 安装：


:::

随后进入 output 文件夹，可以看到恢复的网站源码：

〔原图省略〕

可以使用 git 命令查看当前项目的信息，比如使用 `git log` 查看提交历史

〔原图省略〕

使用 `git reset HEAD~1` 可以回到上一个 Commit，或者直接使用 VSCode 打开泄露出来的 Git 存储库，能够更可视化地查看提交历史。

但是很遗憾，提交历史中并没有有价值的东西。查看 Stash：


〔原图省略〕

可以看到 Stash 中含有后门（实际上在 GitHacker 泄漏时就有 stash 的输出信息）

::: warning 注意

如果使用 GitHack 或其它的一些 Git 泄露获取工具，可能并不支持恢复 Stash.

:::

::: tip Stash 的作用

有时会遇到这样的情况，我们正在 dev 分支开发新功能，做到一半时有人过来反馈一个 bug，让马上解决，但是又不方便和现在已经更改的内容混杂在一起，这时就可以使用 `git stash` 命令先把当前进度保存起来。随后便可以即时处理当前要处理的内容。使用 `git stash pop` 则可以将之前存储的内容重新恢复到工作区。

又或者，我们已经在一个分支进行了修改，但发现自己修改错了分支，可以通过 Stash 进行存储，然后到其它分支中释放。

一些常见的 Stash 命令如：

- `git stash`

  保存当前工作进度，会把暂存区和工作区的改动保存起来。执行完这个命令后，在运行 `git status` 命令，就会发现当前是一个干净的工作区，没有任何改动。使用 `git stash save '一些信息'` 可以添加一些注释。

- `git stash pop [-index] [stash_id]`

  从 Stash 中释放内容，默认为恢复最新的内容到工作区。

:::

使用 `git stash pop` 恢复后门文件到工作区。

〔原图省略〕

发现了后门文件 `BacKd0or.v2d23AOPpDfEW5Ca.php`，访问显示：

〔原图省略〕

由于 `git stash pop` 已经将文件释放了出来，我们可以直接查看后门的源码：


后面的考点是 PHP 中关于非法参数名传参问题。我们重点关注下面这个表达式：


对于这个表达式，可以使用换行符绕过。`preg_match` 默认为单行模式（此时 `.` 会匹配换行符），但在 PHP 中的该模式下，`$` 除了匹配整个字符串的结尾，还能够匹配字符串最后一个换行符。

::: tip 拓展

如果加 `D` 修饰符，就不匹配换行符：


:::

但如果直接传参 `NewStar_CTF.2024=Welcome%0A` 会发现并没有用。这是由 `NewStar_CTF.2024` 中的特殊字符 `.` 引起的，PHP 默认会将其解析为 `NewStar_CTF_2024`. 在 PHP 7 中，可以使用 `[` 字符的非正确替换漏洞。当传入的参数名中出现 `[` 且之后没有 `]` 时，PHP 会将 `[` 替换为 `_`，但此之后就不会继续替换后面的特殊字符了因此，GET 传参 `NewStar[CTF.2024=Welcome%0a` 即可，随后传入 `call_user_func` 的参数即可。

〔原图省略〕
