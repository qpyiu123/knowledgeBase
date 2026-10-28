---
title: "[Binary] 从零开始学Python"
category: pwn
tags: [GeekGame 2024, wp prose]
signals: [[Binary] 从零开始学Python, Python]
difficulty: medium
source: "https://github.com/PKU-GeekGame/geekgame-4th/blob/a21d7f7387512ec7ef77720e998d60efa16f2353/official_writeup/binary-pymaster/README.md"
tools: []
origin: imported
origin_id: official-5241a0f23aeeae876b6f0d
origin_sha256: 1d80346e42ab803ef5ba89e0dfdd1f3ea05f44cb284cfdc3f8abe3a317a2de04
origin_event: "GeekGame 2024"
origin_kind: wp_prose
license: "not_declared"
updated: 2026-10-23
---
# GeekGame 2024 / [Binary] 从零开始学Python

> 来源：GeekGame 2024  |  类型：wp_prose  |  https://github.com/PKU-GeekGame/geekgame-4th/blob/a21d7f7387512ec7ef77720e998d60efa16f2353/official_writeup/binary-pymaster/README.md

# [Binary] 从零开始学Python

- 命题人：Yasar
- 源码中遗留的隐藏信息：200 分
- 影响随机数的神秘力量：150 分
- 科学家获得的实验结果：200 分

## 题目描述

2024 年他获得了诺贝尔物理学奖，以表彰在使用人工神经网络实现机器学习方面奠基性发现和发明。
他表示自己完全没有想到这样的事情会发生。</p>
程序在几百年后的电脑上已经无法运行，但是电脑上遗留的一些实验日志记录了一些蛛丝马迹。</p>
但是有<strong>神秘力量</strong>稳定了混乱的随机数，让程序失去了随机性，实验获得了一个稳定且非常好的结果。</p>

**[【附件：下载题目附件（binary-pymaster.zip）】](attachment/binary-pymaster.zip)**

## 预期解法

本题主要希望大家对 Python 的**可执行文件打包**以及**字节码**进行了解和学习。

题目的可执行文件使用 *PyInstaller* 进行打包，*PyInstaller* 会将 Python 应用程序及其所有依赖项打包成一个可执行文件。用户无需安装 Python 解释器和任何模块即可运行打包好的应用程序。所以程序运行中调用的库也会被打包进其中。

本题使用的逆向工具主要有：

- [pyinstxtractor-ng](https://github.com/pyinstxtractor/pyinstxtractor-ng) 可以帮助我们对 PyInstaller 打包的应用程序进行解包得到 pyc 文件，这是 Python 源文件经过编译之后生成的字节码文件，也可以被 Python 直接运行。
- [pycdc](https://github.com/zrax/pycdc) 可以帮助我们对 pyc 文件进行反编译，在很多情况下 pycdc 都可以非常好地还原源代码。但是在特定情况下，它还原的代码可能会存在一些错误，但在本题并没有出现。

使用 pyinstxtractor-ng 解包后，用 pycdc 对解包得到的 `pymaster.pyc` 进行反编译得到如下结果：


首先关注到在程序入口处有个随机数，而 Python 中的随机数默认是以时间戳为 seed 的，理论上并没有办法稳定输出一样的结果，但是执行下发的文件会发现每次都可以进入 flag 校验的步骤。说明 random 的 seed 可能被固定了。

之前提到 PyInstaller 会将所有的库文件也打包进可执行文件，它们被储存在 pyz 文件当中。pyinstxtractor-ng 会自动解包 pyz 文件，在其中可以找到 `random.pyc`，使用 pycdc 反编译后会在构建函数中发现预设的 seed：


~~出题人并没有想到这一步会给很多选手带来困难 orz~~

继续分析程序逻辑，marshal 是 Python 的对象序列化方法，被序列化的是一个 code object 对象，通过 `compile(code, "", "exec")` 生成。可以使用 Python 中 `dis` 库对其反汇编并进行分析：


至此获得了源码，虽然源码经过了混淆，通过手动反混淆会发现实现了一个伸展树 Splay，将 flag 以随机权值插入树后进行了 0x100 次随机伸展，最后将树的中序遍历异或上随机值后进行判断。由于随机的 seed 是固定的，所以整个过程就可以稳定运行。

由于随机伸展部分只涉及位置的改变，而异或部分只涉及值的改变，将两个部分分别逆向进行即可获得最终的 flag。

## Exp
