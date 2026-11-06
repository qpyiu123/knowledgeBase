---
title: "UPX"
category: reverse
tags: [NewStar CTF 2024, wp prose]
signals: [UPX, Python]
difficulty: medium
source: "https://github.com/pj-newstar/wiki-docs/blob/1a0f2ba21a30f950276396118b315eef0328371c/docs/wp/2024/week2/reverse/upx.md"
tools: []
origin: imported
origin_id: official-ba13e643706329bb955947
origin_sha256: 8fe8af183551557702d0292f39332ef963edee659eb0aa67ffc4e56b7c41b628
origin_event: "NewStar CTF 2024"
origin_kind: wp_prose
license: "MIT"
updated: 2026-10-23
---
# NewStar CTF 2024 / UPX

> 来源：NewStar CTF 2024  |  类型：wp_prose  |  https://github.com/pj-newstar/wiki-docs/blob/1a0f2ba21a30f950276396118b315eef0328371c/docs/wp/2024/week2/reverse/upx.md

# UPX

## 脱壳

使用 IDA 查看文件，发现主函数很复杂。

〔原图省略〕

这时根据文件的名称和提示，和 UPX 相关联。直接搜索 UPX，可以得知它是可执行程序文件压缩器，是一种压缩壳。在程序启动时先执行 UPX 的代码，把压缩后的原文件解压后，再把控制流转到原文件。然后这里可以使用 DIE 进行查看，特征也显示为 UPX.

〔原图省略〕

因此可以采用工具尝试能不能直接脱壳，或者使用手动脱壳的办法进行脱壳。

因为这里没有进行更改，所以可以直接使用工具 <https://github.com/upx/upx/releases/> 进行脱壳，然后发现文件的体积变大了。

〔原图省略〕

再次使用 IDA 打开脱壳后的程序，发现主函数逻辑很清晰，反汇编的结果也很明确了。

〔原图省略〕
〔原图省略〕

## 分析

查看这里的 `main` 函数，发现提示很明确。这里首先通过 `__isoc99_scanf` 输入内容，利用 `%22s` 和后续 for 循环中的比较，也提示输入的 flag 长度是 22 字节。然后后面输入 `s` 和 `key` 经过了 `RC4` 的函数，然后把输入 `s` 和 `data` 进行比较。

直接搜索 RC4，查阅相关文章，可以得知它是一种流加密算法，它通过字节流的方式依次加密明文中的每一个字节，解密的时候也是依次对密文中的每一个字节进行解密。这里直接点击 RC4 函数，查看其内部是怎么实现的。

在下面可以看到 RC4 函数的实现，它实现调用 `init_sbox` 函数对于 `a2`，也就是上面从 `main` 函数传入的 `key` 进行一系列处理，然后获取 `a1`，也就是从 `main` 函数传入的输入 `s`，然后在 for 循环中，循环遍历 `a1` 的每一位，然后使用一个异或进行处理。

〔原图省略〕

因此我们可以理清楚这个程序的逻辑，我们首先进行了输入，然后程序将我们的输入和内置的密钥及进行 RC4 加密，然后将加密的结果和内置的数据进行比较，如果一样的话，说明我们的输入是正确的。

因此分别点击 `main` 函数中的 `key` 和 `data` 变量，找到了内置的密钥和比对密文，之后就可以写脚本获取 flag 了。

点击 `key` 一直进行寻找发现了密钥 `NewStar`.

〔原图省略〕

点击 `data` 发现这里没有值。

〔原图省略〕

然后对 `data` 按 `x` 进行交叉引用，发现存在另外的函数也用到了 `data` 这个数据。

〔原图省略〕

直接点击这个使用 `data` 数据的函数 `before_main` 中，可以发现这里对 `data` 进行了赋值操作。

〔原图省略〕

这里再次交叉引用 `before_main` 函数，可以发现它在 `.init_array` 段被调用。这个段里存放着的是在 `main` 函数执行前执行的代码，可以搜索相关资料进一步掌握。这里只需要知道它是在 `main` 函数之前被调用的，那么它就是最后进行比对的密文，我们直接拿出来就行。

〔原图省略〕

## 方法一

既然已经获取了密文和密钥，那么我们完全可以套用 RC4 的算法来解密。因为 RC4 是流密码，它的本质就是异或，而 `a ^ b = c`，`c ^ b = a`，由此可以直接把内置的密文作为输入，然后使用算法进行解密。


## 方法二

上面是写代码进行解密，还可以直接在动调中把输入替换为密文，也可以进行解密。

首先在输入后和比对时按 <kbd>F2</kbd> 下断点。

〔原图省略〕

然后进行动调，首先随便输入数据，然后程序在断点处停下（这里颜色改变了，说明断在这里了），输入 `s` 也显示我们输入的数据。

〔原图省略〕

〔原图省略〕

然后先点击 data，找到 data 数据。然后使用 `sheift + e` 直接取出 data 的相关数据。

〔原图省略〕

然后可以先找到输入 `s` 的起始地址（`0x56201B813040` 需要你自己动调时的地址），然后使用 `shift + F2` 调出 `IDAPython`脚本窗口，然后使用 python 脚本进行修改，最后点击 Run 进行执行。然后可以发现左侧的输入 `s` 数据改变了。

〔原图省略〕


或者可以手动 **右键 » Patching » Change byte** 进行修改。

〔原图省略〕

〔原图省略〕

修改完之后，使用快捷键 <kbd>F9</kbd> 让程序直接运行，然后它会断在我们之前下的第二个断点处。

〔原图省略〕

这时再看我们的输入 `s`，会发现它经过 RC4 的再次加密（其实是解密，因为 RC4 是流密码，加密解密的流程一摸一样），呈现出来了 flag.

〔原图省略〕

这里按 `a` 就可以转化为字符串的形式，这个就是最后的 flag 了。

〔原图省略〕

## 方法三

上面可以知道 RC4 流密码的最后一步就是异或了，那么我们可以在动调的过程中，把这个异或的值拿出来，然后直接把密文和这个异或的数据进行异或即可。

这里先找到 RC4 的加密函数处，在这个最后一步的异或处按 Tab 转化为汇编窗格形式。

〔原图省略〕

然后在这个汇编的异或处下断点。下面展示了两种汇编代码的视图方式，可以按空格进行相互转换。

〔原图省略〕

〔原图省略〕

这里不知道两个参数 `al` 和 `[rbp+var_9]` 分别代表什么，因此我们可以先直接动调，断在这里的时候再去看看数值。这里动调需要注意，因为 RC4 根据输入的字符个数进行逐个加密的，所以我们需要输入和密文长度相等的字符长度，也就是 22 个字符才可以获得完整的异或值。

这里发现 `al` 存储的就是我们的输入数据（我这里输入 22 个字符 `a`，它的十六进制就是 `0x61`），然后由此可以知道 `[rbp+var_9]` 存储的就是需要异或的值。因为它经过了22次循环，所以每次异或的值都可能不一样，但是都只在一个函数中，`rbp` 的值应该不变，所以可以直接使用条件断点的方式，把 `[rbp+var_9]` 中的值取出来，或者也可以在下面的 `mov [rdx], al` 中下条件断点，把异或后的 `al` 值提取出来

〔原图省略〕

对于在 `[rbp+var_9]` 下条件断点，首先寻找这个数据的地址。点击进去可以发现数据存储在栈上，当前的数据为 `0xA2`.

![[rbp+var_9] 的内容](/assets/images/wp/2024/week2/upx_26.png)

然后回来，在断点处 **右键 » Edit breakpoint**，然后点击三个点就可调出 IDAPython 的窗口，然后我这里使用 Python 脚本，所以在下面选择语言为 Python.

〔原图省略〕

〔原图省略〕

然后在 Script 中写入 IDAPython 脚本，点击左右两边的 OK 即可。

〔原图省略〕


〔原图省略〕

然后最为关键的就是在下面 Output 栏中打印的数据了，可以看到打印出了每次异或的值，但是因为断点的时候第一数据已经运行到了，所以没有第一个数据，但是我们之前查看 `[rbp+var_9]` 的时候观察到了，所以自己把这个 `0xA2` 给加上即可。

〔原图省略〕

然后直接把之前获得的密文和这个数据进行异或即可。


这里我们还可以在下一条语句 `mov [rdx], al` 中下条件断点

〔原图省略〕


然后得到了假数据经过异或后的数据，然后我们可以利用异或的特性获得 flag.

〔原图省略〕


## 方法四

这里观察主函数，发现存在 `exit` 函数，它的功能就是关闭所有文件，终止正在执行的进程，中间的status 参数就是退出码，可以通过 `echo $?` 来进行获取。

〔原图省略〕

然后观察 `status` 就是循环的下标，因此可以知道它是单字节判断的，若是某个字节判断错了就直接退出，同时返回第几个字节判断错了。由此根据退出码，我们可以直接进行爆破处理。

这里就是进行爆破的代码，`tqdm` 只是为了直观显示，可以删去相关代码。


然后爆破一分钟左右就跑出结果了。

〔原图省略〕

## 原文配图

![很复杂的主函数](../../_assets/images/6d712d87d15bab78fd07497dec9b35bbb72b19d95611345174bd3e1cbd862744.png)

![DIE 的查看结果](../../_assets/images/d58c79ac496b3863147ccdcb100dd4e3d9488dbe2e4fc859bb34328706d1f656.png)

![UPX 命令行程序脱壳的结果](../../_assets/images/fecd78cc9a4d3dc7d9dbe9e0f413da6e3327fc12b0c6e41be226793031abbffa.png)

![脱壳后的 IDA View](../../_assets/images/880ff2b2e0020297d7d294b9aa5ac552fff278c70bbfaf8d4c667d0484b7ee6b.png)

![脱壳后的反编译结果](../../_assets/images/d703218c627e16b0ac4197def0dab94689c06514b51feb8b34d3c558a5ae31b2.png)

![RC4 函数的实现](../../_assets/images/3c403c821b54f6b8ac78679c483e5f33ff25f97c5aecdc68253282170faeb46f.png)

![key 变量](../../_assets/images/cc2451c668d31c83a7e8cb8131cfae04858e03af85ecfa6754a66b5436f9180d.png)

![没有值的 data 变量](../../_assets/images/1d7523d83c6a95383fe6128bee0fddd08056a5cab3bd2db7c0dce029390ee3f7.png)

![data 的交叉引用](../../_assets/images/4e0aeb6b2ac08c1f94670d241078e09c4d2730c610b5f4a28bd63ee9b07a0c41.png)

![before_main 函数里的赋值操作](../../_assets/images/ef722dfd5637487f4b7aa3be9baf27fd0063dbe4dda6e7ce5ef71e72898ec9c7.png)

![.init_array 段](../../_assets/images/8b378fedfce3158b067490fe3b5e2925e3c8d02dd9212ac14e30961001501d77.png)

![下断点](../../_assets/images/01eaa01edde08bd4d75d5b6bfe324eac4e257b9ac9292d2f1e102f3b10d36d39.png)

![我们的输入](../../_assets/images/5cf24193db5b9f63fba1c2f9dd13565b8a1d0368d5e7959452784f4703a58a6b.png)

![IDA 中看到的 s 内的值](../../_assets/images/8dfa9e8cd3b109e26c8b1d34d393a81c41cf83a74d4cabe32245ffb86034710f.png)

![data 数据](../../_assets/images/244a4222295fc482075a9c4ab5205fc94d923a6728a50ab19a04c4d6d09e7230.png)

![修改 s 的数据](../../_assets/images/0d5fa988fb5ab6d754eec3c78cae625594e79f05d27c39574da2f2a716cfa1d5.png)

![手动修改 s 的数据 1](../../_assets/images/50419051c49d84eaf5f6f2cde4b5a9fcf55f36da2d98eff7e5a528665ede112b.png)

![手动修改 s 的数据 2](../../_assets/images/5656b268b400f06389860503e60fa6baf1380072bd95167bd3f8f546e03fc9a1.png)

![断在第二个断点处](../../_assets/images/3dfa89742864956a5cd118522519a05d5e1f4f4e3bb82bfd54ecf6dd0c1b2cda.png)

![解密后的 flag](../../_assets/images/1a2c57a36539e2e3664f0020ae23f2cd7fe52d7dd3faf0b8df268207eb3b343f.png)

![flag](../../_assets/images/011da3a8f6b0e14b5265458f24eb6789b2eabf4709ec23d81b1fc18844ff6fc2.png)

![RC4 的加密函数](../../_assets/images/3bd6c7207b8880af9b97bca405e9c54e914f98901d7a6aea3d29d30207c58c18.png)

![汇编的视图方式 1](../../_assets/images/7ed567ad7f9171c1c21b6545599e09af9c883237e89cb38e18c661ff6211f4fc.png)

![汇编的视图方式 2](../../_assets/images/3ddd2fb536d48578e4392a36e132c96bc1f59c113f5bd780b5164354d6c8afba.png)

![动调查看 al](../../_assets/images/2d876e7d13066e0079212b8c7fa3e7444146792dbc6d82401107b2def839b641.png)

![调出 IDAPython 窗口 1](../../_assets/images/4e9678771538b58273e717b9106bd8cc8c882ca591279f4e85a779a2484f022e.png)

![调出 IDAPython 窗口 2](../../_assets/images/ae98833e61a60c3ff9029d661d252c63f0450f2199341b72f9e2df828de79fe0.png)

![IDAPython 脚本](../../_assets/images/ad75b7fc85d03deb92a33a838576c946d02b7d4763f7f4c663b694e2a6c12d8f.png)

![retn 下断点](../../_assets/images/0220f8d9097727c145b5b2656c5387d608d7955891333b120bcdfcc31143ef77.png)

![异或的值](../../_assets/images/ee2b77b546b8b80065d181525e328f0a67796a215e904f6c810a41389aa652e4.png)

![下条件断点](../../_assets/images/f36a8543181c5d8b1bef53d397b222446fd9db285c68689d43a79a547f92de1a.png)

![假数据](../../_assets/images/61991372bfbe5d829ef745d902a55b06fcdacb236c8dd054819ea6bb4d5dad2a.png)

![exit 函数相关代码](../../_assets/images/5b2fe0afb936a7aa756f54f3f2e5e3f82cbacbad14146061eca9abf07fdafeda.png)

![爆破结果](../../_assets/images/1ad1958b885d134c30b678371b8b3e5fc6e7a8a528158c2fda0f2a6bc13c56fc.png)
