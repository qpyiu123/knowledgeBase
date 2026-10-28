---
title: "Ohn_flutter!!!"
category: reverse
tags: [NewStar CTF 2024, wp prose]
signals: [Ohn_flutter!!!]
difficulty: medium
source: "https://github.com/pj-newstar/wiki-docs/blob/1a0f2ba21a30f950276396118b315eef0328371c/docs/wp/2024/week5/reverse/ohn_flutter.md"
tools: []
origin: imported
origin_id: official-4b707b2772ceaf09203562
origin_sha256: ccf4019899bad2a6ea54f7b340da3fecd0f43dd4629f4c9c67ab9999a88fa816
origin_event: "NewStar CTF 2024"
origin_kind: wp_prose
license: "MIT"
updated: 2026-10-23
---
# NewStar CTF 2024 / Ohn_flutter!!!

> 来源：NewStar CTF 2024  |  类型：wp_prose  |  https://github.com/pj-newstar/wiki-docs/blob/1a0f2ba21a30f950276396118b315eef0328371c/docs/wp/2024/week5/reverse/ohn_flutter.md

import Container from '@/components/docs/Container.vue'

# Ohn_flutter!!!

blutter 反编译得到 `asm` 文件夹和 `ida_script` 文件夹，`ida_script` 在 IDA 里先加载 `ida_dart_struct.h` 头文件再运行 `addNames.py` 脚本可得到大部分符号

ASM 里查看 EditView.dart 可发现 `check` 函数单代码全为汇编


汇编难以阅读逻辑，在 IDA 里函数列表搜索 `check`，发现了: `ohn_flutter_EditView_MyEditTextState::check_2d50c0@<X0>`

明显是刚刚的 `check` 函数，交叉引用溯源找到主逻辑得到 `ohn_flutter_EditView_MyEditTextState::_anon_closure_2d4f08`


查看 `ohn_flutter_doi_::jumppp_2fe3c8()`，里面的函数调用了 `ohn_flutter_drink_drink::encrypt_2fe460` 是一个单独加密

在 `ohn_flutter_drink_drink::_encryptUint32List_2fe5ec` 可以看到如下特征


一眼就发现是 XXTEA

查看 `ohn_flutter_doi_::jumppp_2fe3c8` 下面的逻辑

- `KeyStub_2fe3bc` `IVStub_2fe1b8` ``AESStub_2fe1ac`

明显是 AES 加密特征

最后是 `base64` 和 `check`


`check` 函数里的判断函数没办法直接查看需要动调，同时其他加密的密钥和 IV 也无法直接得到。

在 `ohn_flutter_EditView_MyEditTextState::_anon_closure_2d4f08` 函数开头下断点，然后用 IDA 单步调试在判断处拿到密文，Key 和 IV 都可以轻易拿到，XXTEA 的 Key 在那个加密的特征处（进行 `&3` 运算的附近）也可以拿到


上面代码中提到的 AES 解密，可参见 [CyberChef Recipe](<https://gchq.github.io/CyberChef/#recipe=From_Base64('A-Za-z0-9%2B/%3D',true,false)AES_Decrypt(%7B'option':'UTF8','string':'12345678901234561234567890123456'%7D,%7B'option':'UTF8','string':'1234567890123456'%7D,'CBC','Raw','Raw',%7B'option':'Hex','string':''%7D,%7B'option':'Hex','string':''%7D)&input=L29JSE95RGc2czZ5cVZkMjZBbllKNnUyWWpQY01oYXdUZTkzK0FKUEFVaXdHWk00S1d2WGpzaWIxdGNuWkhTbmdsYWFWcGJjT2FUdE5vTUNyNW9kMkE9PQ>).

**Ans:** `flag{U_@r4_F1u774r_r4_m@ster}`
