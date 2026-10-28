---
title: "ZFS 文件恢复"
category: misc
tags: [Hackergame 2024, wp prose]
signals: [ZFS 文件恢复]
difficulty: medium
source: "https://github.com/USTC-Hackergame/hackergame2024-writeups/blob/deb6fa3f906e2d0e905f5de5b12757d89f54f812/official/ZFS%20%E6%96%87%E4%BB%B6%E6%81%A2%E5%A4%8D/README.md"
tools: []
origin: imported
origin_id: official-fb4760b2f4033248591baf
origin_sha256: 53a1b2d06c5f3bac4bece1f85eab60899ea559149e6ee831f1ed4b11f2549279
origin_event: "Hackergame 2024"
origin_kind: wp_prose
license: "NOASSERTION"
updated: 2026-10-23
---
# Hackergame 2024 / ZFS 文件恢复

> 来源：Hackergame 2024  |  类型：wp_prose  |  https://github.com/USTC-Hackergame/hackergame2024-writeups/blob/deb6fa3f906e2d0e905f5de5b12757d89f54f812/official/ZFS%20%E6%96%87%E4%BB%B6%E6%81%A2%E5%A4%8D/README.md

# ZFS 文件恢复

题解作者：[iBug](https://github.com/iBug)

出题人、验题人、文案设计等：见 [Hackergame 2024 幕后工作人员](../../credits.pdf)。

## 题目描述

- 题目分类：general

- 题目分值：Text File（200）+ Shell Script（250）

你拿到了一份 ZFS 的磁盘镜像，里面据说有某沉迷 ZFS 的出题人**刚刚删除**的 flag。

「ZFS，我懂的。」这样说着，你尝试挂载了这个镜像（**请注意，以下命令仅供参考，且系统需要安装 ZFS 内核模块**）：


但是里面却没有你想要的 flag，这是怎么回事呢？

备注：

- 对于第一小题，你需要还原神秘消失的 `flag1.txt`。
- 对于第二小题，你需要还原神秘消失的 `flag2.sh`，并根据该 shell 脚本的内容恢复出更多信息，然后运行该脚本获得本小题的 flag。

[打开/下载题目](files/zfs.zip)

## 题解

题目灵感来源于 @taoky (sugoi!) 在调查 USTC 镜像站磁盘空间占用问题时提交的 bug：<https://github.com/openzfs/zfs/issues/15998>。当时我把这个有问题的 `pool1/log` dataset 打了个快照，send 到本地导入尝试排查，但是无论如何都无法复现，而且 ZFS 输出的大小也令人十分困惑：


与传统文件系统依靠 OS 做“已删除文件”的 accounting 不同，ZFS 会把“已删除但仍有 open fd”的文件移进一个叫做 delete queue 的“目录”中，这样即使系统发生崩溃，ZFS 本身仍然处于一致的状态，不像其他文件系统在开机后需要立刻 fsck，所以其实这中间差的容量都隐藏在 delete queue 里了。

解题显而易见地需要挂载镜像，这里推荐使用 Ubuntu 或者 Proxmox VE（什么您在用这么高端的系统？），它们自带了 `zfs.ko` 无需手动 DKMS 编译安装，能节省不少时间。

挂在之后首先发现的是一个空的 data 目录，可能有人已经预料到本题考察的就是硬核 ZFS 知识了（也可能有人直接猜到是谁出的题了）。根据题目名称 `disk_snapshot`，观察一下快照情况：


果然还是有个快照的，再根据文案提示，两个被删掉的文件肯定就在这个快照的 delete queue 里了。

### Text File

本来我是想给一个 `zfs send` stream 文件作为题目附件的，但是那样就相当于直接告诉你 ZFS 有 `send`/`receive` 这个功能了，并且 `zfs send` 在不带参数的情况下默认是明文发送，那么你只需要把这个附件 receive 进一个地方，再重新 send 出来，就可以对新的 send stream 直接跑 `grep` 了，<s>违背了本题的初衷</s>。考虑到这一点，决定还是给 disk image 吧。这也是为什么恢复文件内容放在第一题，错误地估计了两题的难度。

如果你真的制造了一个 send stream 文件并且尝试打开它观察的话，你很快就会发现一大串小写字母，并且后面的内容大概是这样：


再大胆假设一下，前面的一串小写字母结尾是 `fl`，后面一串可读的文字开头是 `ag{`，那么它肯定就是 flag 了！

---

以下是“正确”解法，全程高能 `zdb` 警告，并且还要 ddddd……因此这里强烈建议你在旁边打开一份 [`zdb(8)`](https://openzfs.github.io/openzfs-docs/man/master/8/zdb.8.html) 以供随时查阅，下面将不再介绍 `zdb` 的参数。

首先你需要找到 ZFS delete queue，它可以从 ZFS master node（固定为 1 号 object）里发现：


对 delete queue 跑一下 `zdb`：


可以看到两个文件的 dnode number（即 inode number）分别是 2 和 3。

首先观察 2 号文件：


从这里可以得知它的大小是 4135 字节，权限是 `100644`（无执行权限的普通文件），那么它很可能是第一题的文本文件。


于是你拿到了本文件的前 4096 字节，但是里面并没有 flag，尝试解析下一个 block，发现它是 EMBEDDED，因此你需要从那个 L1 的 block 里尝试解析：


好了，你已经获得了本文件完整的 4135 字节了，可以提交 flag 了。

---

为什么第一小题这么麻烦呢？因为前面提到，直接 `zfs send` 可以（几乎）逃课 zdb，因此在生成这份 disk.img 的时候，我特地做了额外的措施避免让 `disk.img` 文件可以直接 grep 或者 binwalk：

- `zfs set recordsize=4k compression=gzip`
- 在前面填充 4094 个字节的小写字母，使得第一个 block 包含 flag 开头的 `fl` 两个字母，并且高度可压缩
- flag 剩余的字节数不超过 112，可以被 ZFS 放进一个 embedded block pointer 里

### Shell Script

如果你已经做出第一题了，那么恢复 shell 脚本文件肯定难不倒你了：


恢复出的脚本内容如下：


根据代码提示，需要拼出 `flag_key` 字符串，你只需要看一下 [`stat(1)`](https://linux.die.net/man/1/stat) 就知道还需要找出 `flag1.txt` 和本文件（`$0`）的 atime 和 mtime，相信这也难不倒<s>已经被迫把 `zdb` 用熟练的</s>你：


还原得到 `flag_key` 手工替换进脚本中：


运行脚本确认 `sha256sum` 结果正确即可得到 `flag{snapshot_6db0f20dd59a448d314cb9cabe8daea9}`。

## 花絮


果不其然有同学私聊我说：

> 妈的 hkgame这zfs题是不是群zfs专家出的

> \[表情\]

> 现在熟练使用zdb和了解zfs on-disk了 md

🤣
