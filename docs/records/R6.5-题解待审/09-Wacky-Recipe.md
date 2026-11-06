# Wacky Recipe：把菜谱动作写成两未知数的方程

DownUnderCTF 2024 · 杂项 · [官方题解](https://github.com/DownUnderCTF/Challenges_2024_Public/blob/main/misc/wackyrecipe/solve/WRITEUP.md)。原题只有一份菜谱文本，已在本机找到唯一符合题面格式的结果。

看到 `Ingredients`（食材）和 `Method`（做法），以及反复操作搅拌碗，先想到 Chef。这是一种把程序写成菜谱的语言。搅拌碗在这里是一个栈，也就是最后放进去的数先被取出来。

- `Put`（放入）新加一项。
- `Add`（加入）、`Remove`（去掉）、`Combine`（混合）分别对最上面的一项做加、减、乘。
- 这份菜谱最后把碗里的内容转成字符输出。

未知食材数量是 `pain` 和 `effort`。用纸算也可以：第一组先把水从 1 加到 4，乘 `pain`，再减去面包屑的量 4，最后加 `effort`，得到 `4*pain + effort - 4`。每组都可以这样化成一条一次式。

按输出顺序把赛事答案前缀代入，解两个未知数。再把所有 20 项算一遍，确认都是可打印字符、首尾格式正确。本机复做时按两种可能的读取顺序检查，只有栈顶先出的方向得到一个候选。

参考：[Chef 作者的语言说明](https://www.dangermouse.net/esoteric/chef.html)。
