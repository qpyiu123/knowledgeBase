---
title: "jocker：公开题解导读"
category: "reverse"
kind: "writeup"
tags: ["反编译", "栈不平衡", "自修改代码"]
signals: ["假答案", "分段校验"]
source: "https://www.ylcao.top/2021/12/01/%E7%BD%91%E9%BC%8E%E6%9D%AF-2020-%E9%9D%92%E9%BE%99%E7%BB%84jocker/"
origin_id: "r66-jocker"
relates_to: ["reverse/vm-protection.md"]
verification: "公开题解导读"
---

# jocker：公开题解导读

网鼎杯 2020 青龙组 · 逆向。这里只整理公开题解，不另做逆向或提交。

## 先看这一步

公开题解记录了栈不平衡提示、假答案和改写后的分段检查。先看作者如何核对每条线索，再回原文对照。

**适用时**：仅作为网鼎杯 2020 青龙组同一题的导读。 **留意**：函数导入和反编译报错只是线索。

- [YLCao 的原文](https://www.ylcao.top/2021/12/01/%E7%BD%91%E9%BC%8E%E6%9D%AF-2020-%E9%9D%92%E9%BE%99%E7%BB%84jocker/)按作者自己的分析顺序记录了栈提示、假答案和后续检查。
- [PYozo_free 的原文](https://www.cnblogs.com/pppyyyzzz/p/13463136.html)可以交叉参考自修改部分的截图。

建议先看前文如何区分“工具没读懂这段代码”和“已经找到了答案”。几个函数分段做检查，第一个看起来像答案的字符串只是干扰。公开题解把后半部分放在程序改写自身代码之后讲解；遇到这一步，可回到原文对照作者记录的证据。
