---
title: "MoeCTF 2025 / **0 二进制漏洞审计入门指北**"
category: pwn
tags: ["MoeCTF 2025", "**0 二进制漏洞审计入门指北**", "pwn", "官方资料", "official_writeups/Pwn/MoeCTF 2025 Pwn Writeup.md", "origin_tag:imported_cats"]
signals: ["MoeCTF 2025", "**0 二进制漏洞审计入门指北**", "pwn"]
difficulty: medium
source: "https://github.com/XDSEC/MoeCTF_2025/blob/da9e708029f4666da270064c5776ddd29c61dd6f/official_writeups/Pwn/MoeCTF%202025%20Pwn%20Writeup.md"
tools: []
origin: imported_cats
origin_id: "official-1d9cdaf519ceb3714f493a"
origin_domain: "pwn"
origin_family: "official_event_archive"
origin_event: "MoeCTF 2025"
origin_year: 2025
origin_license: "not_declared"
origin_attribution: ""
origin_verification: "official_source_not_reproduced"
origin_content_sha256: "b881d771f663b7f6df1ad53af1c185e1903b0ee21fabe98e9d3a9ef3aaddbf39"
origin_body_sha256: b5f563cc06b3f33951233caef420a4ec33076846ed950b95ceca9d283ba086fd
origin_title: "MoeCTF 2025 / **0 二进制漏洞审计入门指北**"
origin_meta:
  asset_refs: []
  basis: "original_prose_not_runtime_verified"
  challenge_key: "moectf2025:official_writeups/Pwn"
  chunk_ids: [8313]
  content_sha256: "b881d771f663b7f6df1ad53af1c185e1903b0ee21fabe98e9d3a9ef3aaddbf39"
  domain: "pwn"
  domain_basis: "repository_path"
  event: "MoeCTF 2025"
  external_links_not_followed: 1
  id: "official-1d9cdaf519ceb3714f493a"
  kind: "official_wp_prose"
  language: "zh"
  license: "not_declared"
  local_path: "62_官方赛事题库/objects/15f09c9eace74fd425f8532c329e228eff46b964d944a993a209c6dcc2aa059e.blob"
  official_evidence: "https://github.com/XDSEC/MoeCTF_2025"
  original_path: "official_writeups/Pwn/MoeCTF 2025 Pwn Writeup.md"
  revision: "da9e708029f4666da270064c5776ddd29c61dd6f"
  scope_note: "官方发布来源的说明正文；代码单独索引，未运行或分析。按文件收录，不把多份文件算作多道题。图片及附件下载状态见清单；仅按路径/原题分类标方向，binary 等跨方向资料留待分类。"
  source_family: "official_event_archive"
  source_url: "https://github.com/XDSEC/MoeCTF_2025/blob/da9e708029f4666da270064c5776ddd29c61dd6f/official_writeups/Pwn/MoeCTF%202025%20Pwn%20Writeup.md"
  tags: ["MoeCTF 2025", "**0 二进制漏洞审计入门指北**", "pwn", "官方资料", "official_writeups/Pwn/MoeCTF 2025 Pwn Writeup.md"]
  title: "MoeCTF 2025 / **0 二进制漏洞审计入门指北**"
  verification_status: "official_source_not_reproduced"
  year: 2025
updated: 2026-10-31
---
# MoeCTF 2025 / **0 二进制漏洞审计入门指北**

> 本文由授权中文赛事 WP 正文导入（阶段 1，仅散文，代码段未导入）。
>
> - 来源：https://github.com/XDSEC/MoeCTF_2025/blob/da9e708029f4666da270064c5776ddd29c61dd6f/official_writeups/Pwn/MoeCTF%202025%20Pwn%20Writeup.md
> - 许可：not_declared
> - 署名：（未提供）
> - 文档族：official_event_archive
> - 赛事：MoeCTF 2025
> - 年份：2025
> - 核验状态：official_source_not_reproduced
> - 正文 sha256：b881d771f663b7f6df1ad53af1c185e1903b0ee21fabe98e9d3a9ef3aaddbf39
> - 导入 ID：official-1d9cdaf519ceb3714f493a
> - 原 domain：pwn
> - 本地快照：62_官方赛事题库/objects/15f09c9eace74fd425f8532c329e228eff46b964d944a993a209c6dcc2aa059e.blob
> - 源修订：da9e708029f4666da270064c5776ddd29c61dd6f
> - 收录说明：官方发布来源的说明正文；代码单独索引，未运行或分析。按文件收录，不把多份文件算作多道题。图片及附件下载状态见清单；仅按路径/原题分类标方向，binary 等跨方向资料留待分类。
> - 判定依据：original_prose_not_runtime_verified

> 原文：https://github.com/XDSEC/MoeCTF_2025/blob/da9e708029f4666da270064c5776ddd29c61dd6f/official_writeups/Pwn/MoeCTF%202025%20Pwn%20Writeup.md

## **0 二进制漏洞审计入门指北**

这个题主要是希望大家能在没有了解pwn的情况下，能先去知道怎么和程序交互以及我们在pwn的过程中一个基本的流程是怎么样的，通过逆向题目所给的可执行文件，就能发现这里都需要发送一些什么，然后scanf以及read在读取的时候都有什么区别，基本没有什么难度。

## ez_u64

pwntools的u64可以将小端序bytes转为整形

## find_it

初始fd：0，1，2分配给了stdin,stdout,stderr。新的stdout从3开始分配。open flag后，由于关闭了1，flag会被分配到1。依次输入3,./flag,1即可。

## EZtext

很简单的ret2text的一个题，防护开的也不多，比较板子，只需要去控制返回地址执行backdoor即可。

## ezshellcode

同样是一道shellcode的板子，但是此处我添加了一个权限的选择，你需要起码先了解shellcode是一个什么概念，然后去选取此处应该更改为什么权限，之后再通过pwntools库去生成一个对应架构的shellcode发过去，此处新手应该注意，pwntools的shellcraft生成shellcode的时候，是需要你指定context里的架构的，否则会出现问题，shellcode的本质其实就是指令，而不同架构的指令显然不同，所以希望大家注意这一点，另外，shellcode其实也有很多花样，感兴趣的同学可以去pwn college有一个shellcode的模块，比较有意思，里面会对你的shellcode进行各种的限制，包括但不限于开启沙箱限制系统调用，限制长度，限制某些指令的使用，做完这个模块可以对shellcode有一个更好的理解。

## 认识libc

一个libc的纯板子，之前的ezlibc还是对于新手有点不友好，所以从这个入门，总体来说，就是当可执行文件本身的指令不足以让你getshell的时候，此时libc就变成了一个百宝箱，里面不仅有system函数，还有很多其他的东西，只要你能泄露出libc的地址并且劫持控制流，就打开了新世界的大门！

## boom(revenge)

time(0)种子在一秒内不变，因此可以以伪随机数方式攻击。远程可能需要微调时间。本题也存在覆盖栈上内容跳过检查的非预期。

## fmt

栈上放了一个字符串和一个字符串指针，分别%p和%s泄露(可以开个python用p64或者别的转一下)，不用写exp

payload:%10\$p.%7\$s

## inject

本题漏洞与内存损坏无关，但在现实中不算少见。漏洞点是 `ping_host` 中对用户输入 IP 地址的检查有疏漏，没有过滤换行符。用户输入换行符即可分隔命令，从而注入任意 shell 命令。

Exp:

## randomlock

可以通过gdb调试或者直接看出来seed是1（考拉兹猜想）。攻击伪随机数。

## str_check

手动输入\0可截断strlen绕过检查。strncpy被截断后会补0，因此选择memcpy

## syslock

负索引修改进入后门，ret2syscall

## xdulaker

pull函数给了程序基址可得到后门函数真实地址，laker函数存在栈上未初始化字符串，可在photo函数中输入。

## easylibc

这个题，在最开始的时候，我给你打印了read在got中的地址，这个题的初衷是希望大家对于动态链接和延迟绑定能有一个更好的理解，最开始got中read的表项填写的是read函数plt中的一条指令的地址，当第一次调用read之后，完成了地址解析，此时got中的地址就变成了read函数在libc中的真实地址，此时就可以完成libc地址的泄露，很多同学在做的时候，出现的一个坑是，他们知道要重新执行一次这个printf，但是他们返回错地方了，在printf调用之前，有好几条指令都是在完成参数的装载，而他们返回到了装载指令之后，导致参数出现问题，出现了地址泄露不稳定等一系列的问题，希望大家注意这一点。

## ezpivot

这个题是一个栈迁移的入门题，希望新手在入门栈迁移的时候，不要用自己大脑模拟，多调试多跟踪，exp一步一步的写，然后去观察rbp以及rsp的变化，此时才能对于迁移的过程更加了然于胸，这里的坑是，首先，当system调用的时候，需要预留好栈空间，如果栈空间不足，当迁移到bss段之后，一些指令会访问或者甚至修改到只读的代码段，引起段错误，我注意到很多锤的同学，他们抬高栈的手段是硬生生输入诸如0x600个a，其实无需这么麻烦，并且太大量的输入会导致打远程的时候，出现io问题，直接玄学报错，你要注意到，read在读取的时候，是用rbp寻址的，因此当你控制了rbp之后，就可以直接任意地址写了，此时直接写到高地址即可，另一个坑的话，就是，当你迁移之后，执行system之前，一定要注意rbp的有效性，很多同学将rsp迁移过来之后，就对rbp不管不顾了，此时rbp相关的指令在访存的时候，会因为rbp是一个无

效的值而引起段错误。

## ezprotection

其实这个题并不是很难，主要就是对canary和pie的一个考察，首先是canary的一个特点，第一是，单进程情况下，当程序执行之后，canary就已经确定了，如果你注意一下的话，会发现它是从fs0x28取了一个值作为随机值，有兴趣的同学可以去问问ai这个是什么，其实这里针对此点还可以出成另一个爆破板子，去爆破canary，但希望多考一点东西，就改成了爆破pie，另一个特点就是，canary为了截断一些用来泄露的函数，诸如puts，它的最低一个字节是0x00，因此，如果你能通过栈溢出覆盖掉这个0x00，就可以用输出函数将其泄露出来，之后，要考察的就是pie了，pie在进行随机化的时候，粒度并没有那么细，一页的大小往往是0x1000字节，因此，一个页面内的低12位是不会发生变化的，所以你可以通过多次运行，赌它正好是某个地址，比如这里赌它正好是0x127d，还要注意的一点是，我这里给了一些迷惑性

的判断，让你去输入一个随机数passwd进行验证，但是题里压根没有给你一个能泄露这个随机值的地方，但是，你都已经可以跳转到任意地址，干嘛还要验证呢？所以请同学们不要看到backdoor函数，就刻板印象的从最开头开始执行，你都可以瞬移了，难不成还要掏出钥匙手动开锁吗？（bushi。

## fmt_S

my_read函数填满后存在一字节\0溢出，可多次触发格式化字符串。利用栈上长链作为跳板可以修改到talk返回地址。my_read函数调用后rdi为bss上的atk，可输入/bin/sh传参。

## fmt_T

先泄露libc，由于是递归返回所以依次写'sh'，printf_got表地址，以及修改got的payload

## hardpivot

一个进阶版的栈迁移，其实本质就是，当栈迁移之后，溢出长度不够，不能一次性ROP秒掉的时候，就多迁移一次，每一次都要注意下一次迁移的栈布局，并没有太过于复杂的地方，只是需要细心，耐下心来，一点点的去写exp，一点点的调，不要妄想一次性通过脑洞，直接大脑生成一个三段迁移的exp。

## shellbox

循环中的i可越界写，构造栈溢出

静态链接，用程序中的mprotect改出可执行段

沙箱禁用了execve,open，用openat代替写orw的shellcode

## No way to leak

这个题，我确实没有想到什么好的出法，因为ret2dl这个打法它本身的用途，就是在没有任何手段可以泄露地址的时候，通过ret2dl去getshell，不然的话你是无法获取到libc的地址，因为哪有几个系统不开aslr呢。我这里讲一下我认为的ret2dl的一些局限性：

- 你需要足够的gadget，但是在版本比较新的libc，以及一些题目里，其实不会有那么多类似于pop rdi和pop rsi这种gadget给你用，这里题目最开始想要用的是2.35的libc库，但是因为2.35里fix_up函数发生了一些变动，导致如果大家直接用网上的板子，会打不通，需要去调，调起来对于新手并不友好。2.31里，之所以大家能直接搜到pop rdi，是因为当前版本，csu并没有移动到libc里，而是在主程序里，感兴趣的同学可以去了解一下ret2csu这个打法，以及csu是什么，简单来说就是很多gadget，可以让你很好的进行参数的控制。如果是2.35并且我不给gadget的话，那么你是无法用到csu中的gadget的，因为它们被调整到了libc的内存段中，而libc由于aslr的存在，你并不知道它的基址，题目也无法泄露，所以用不了。如果说你都能泄露libc基址了，我说实话，

那干嘛不直接打ret2libc呢？

那干嘛不直接打ret2libc呢？

所以这个题的初衷是希望大家，能认真的跟一下延迟绑定的这个过程，了解一下相关的一些数据结构，尤其是跟一下fix_up这个函数，在今年的dasctf？当时有一个题就是，它的dynstr是可写的（现在正常来说已经变成只读了），所以可以通过修改dynstr，来影响解析过程。所以深度了解一下动态链接和延迟绑定的过程，真的还是很重要的，要在脑子里自己建立起一个动态链接的框架。

远程打不通的同学，有限考虑一下是不是在不同的send发送数据上发生了io玄学问题，试着在send之间添加sleep，来让上一次的传输能传输彻底。

以下提供两个写的很不错的ret2dl的帖子，比较详细，大家可以跟着做一下，切勿好高骛远，直接跳到后面的，从最简单的开始跟着做，对于你的帮助会更大。

https://blog.csdn.net/qq_51868336/article/details/114644569

https://www.cnblogs.com/xshhc/p/17335007.html

另外的话，建议同学们可以自己编译一个带调试信息和源码的动态链接库，并且重新跟踪一下这个过程， 这里有整理出一个编译的过程，希望能帮助到大家。

之后patch一下就可以直接用了，此时你再去调试的时候会发现可以看到当前执行的是哪一行代码，进行源码级别的调试。

## call_it

本题其实不是一个典型的 JOP 攻击，作为新生赛题，只是想让新生了解：

1. 控制流完整性（CFI）保护这个概念；
2. 代码重用攻击构造链式任意代码执行不只有 ROP 这一种形式，ROP 并非万能。

如果你想要体验更纯正的 JOP，可以尝试 [TGCTF 2025 - noret](https://ctf.xidian.edu.cn/training/19?challenge=766)。

其实 JOP 更像是对 ROP 的概念扩充而不是一个新的攻击方式，让我们先来回顾下熟悉的 amd64 ROP。（以下只是我个人极不严谨的理解，可能和学术界普遍的描述有较大偏差，仅供参考。）在 ROP 中，我们大概可以将 gadgets 分为三类：

* 传递参数或做准备的 gadgets（例如 `pop rdi`）、收集函数返回值的 gadgets（例如 `mov rdi, rax`）
* 执行有意义操作的 gadgets（例如 `system`、`orw`、`syscall`、`shellcode`）。
* 控制 ROP 本身的 gadgets（例如 `ret`、`leave` 栈迁移）

以上 gadgets 通过 `ret` 指令和 `rsp` 寄存器串联起来。

为了引出 JOP，我想到了一个好方法，一个“分解”x86 中较复杂指令的游戏：

（下文 `reg` 表示任意通用寄存器。）我们来“分解”`pop reg` 指令，它“等效”于 `mov reg, qword ptr [rsp]; add rsp, 8`。（我们忽略了对标志位的影响，如果考虑的话第二个指令应为 `lea rsp, [rsp + 8]`。）JOP 链的位置完全可以不在栈上，最终我们可以提取出：

（由于有 `+ offset`，我们不需要 `add`，下同。）这就是 JOP 中类似 ROP 的“传参准备”或“收集结果”gadgets。（例如考虑 `reg1` 是 `rdi` 的情况。）

但是可以看到这并不能构造链式执行。现在我们来“分解”`ret` 指令，它“等效”于 `pop tmp; jmp tmp`，由上文进而“展开”为 `mov tmp, qword ptr [rsp]; add rsp, 8; jmp tmp`，现在我们又提取出了：

我们只需预先在 `reg2 + offset` 位置布置好下一个 JOP gadget，这就是 JOP 中类似 ROP 的“控制”gadgets。

把上述两部分拼起来，我们最终获得了和 ROP 相同的能力。它与栈无关，与函数返回无关。这就是 JOP。希望大家能通过本文从 ROP 流畅过渡到更广义的 JOP 概念。

来看点具体的吧，本题的 JOP gadgets 就是：

当然还有：

可以看到就是上述简单情况的排列组合。

可以看到就是上述简单情况的排列组合。

另外我们还需要注意到 `program` 在遇到“Invalid choice”时依旧会增加 index，因此可以越界写篡改 MoeBot 动作函数地址。

Exp:
