---
title: "pyz3"
category: reverse
tags: [NewStar CTF 2025, wp prose]
signals: [pyz3, Python, Z3]
difficulty: medium
source: "https://github.com/pj-newstar/wiki-docs/blob/1a0f2ba21a30f950276396118b315eef0328371c/docs/wp/2025/week3/reverse/pyz3.md"
tools: []
origin: imported
origin_id: official-fd734aea4a2c3871277878
origin_sha256: a513507d95ec6cb0abef10fd9de96263b15135a8546da1902decafabb60e9712
origin_event: "NewStar CTF 2025"
origin_kind: wp_prose
license: "MIT"
updated: 2026-10-23
---
# NewStar CTF 2025 / pyz3

> 来源：NewStar CTF 2025  |  类型：wp_prose  |  https://github.com/pj-newstar/wiki-docs/blob/1a0f2ba21a30f950276396118b315eef0328371c/docs/wp/2025/week3/reverse/pyz3.md

# pyz3

〔原图省略〕

`DIE` 查壳后发现附件是由 `PyInstaller` 打包的，先用 [PyInstaller Extractor](https://github.com/extremecoders-re/pyinstxtractor) 对 exe 进行解包。

运行 `python path\to\pyinstxtractor.py task.exe` 后，根目录下会生成一个 `task.exe_extracted` 文件夹，exe 所有的资源文件都在这个文件夹中。由于 `PyInstaller` 打包时会把其他库也打包进去，所以文件夹里面的文件比较多，我们要分析的话只要分析 `task.pyc` 就可以了（一般来说与原程序名相同）。

> [!TIP]
>
> 网上很多教程中会有补充 magic number 的步骤，但其实最新版的 PyInstaller Extractor 已经可以自动补充 magic number 了，不需要手动补充。

`pyc` 文件是 Python 编译后的字节码文件，对于 pyc 文件的反编译，这里推荐几个工具：

- 在线反编译网站：
  - [在线 Python pyc 文件编译与反编译](https://www.lddgo.net/string/pyc-compile-decompile)（3.9以下成功率较高）
  - [PyLingual](https://pylingual.io/)（不会像 pycdc 那样注明哪里没有反编译成功，有时会缺失一部分代码）
- 本地反编译工具：
  - [Decompyle++](https://github.com/zrax/pycdc)（pycdc 和 pycdas）
  - [Pylingual](https://github.com/syssec-utd/pylingual)（不支持 Windows）
  - uncompyle6（可直接 pip install，对 3.9 以上版本的支持不佳）

实际分析时常用的是 `Pylingual` 和 `Decompyle++` ，这两个可以覆盖大部分情况，其他工具可能受版本影响，稳定性相对较差。

下面是 `pycac` 对 `task.pyc` 反编译后的结果：


其实是一个输入和一个矩阵相乘，最后与结果比较，题目的预期解是用 z3 对其求解。

> [!NOTE]
>
> [Z3 solver](https://github.com/Z3Prover/z3) 是由微软开发的 **可满足性模理论求解器**（**Satisfiability Modulo Theory solver**， 即 `SMT solver`），用于检查逻辑表达式的可满足性，并可以找到一组约束中的其中一个可行解（无法找出所有的可行解）。
>
> 在 CTF 逆向题中，我们有的时候会遇到一些较为复杂的约束条件，此时可以使用 `z3` 来辅助求解。

下面是我的脚本，z3 的写法可以参考网上的文档。
