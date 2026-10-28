---
title: "Node.js is Web Scale"
category: web
tags: [Hackergame 2024, wp prose]
signals: [Node.js is Web Scale, Node]
difficulty: medium
source: "https://github.com/USTC-Hackergame/hackergame2024-writeups/blob/deb6fa3f906e2d0e905f5de5b12757d89f54f812/official/Node.js%20is%20Web%20Scale/README.md"
tools: []
origin: imported
origin_id: official-8acf86a43d003e1515245f
origin_sha256: 4fda9f97619bc5e1ba423627936a82ce2e4d279c9933efc3d0750c1cbd76228e
origin_event: "Hackergame 2024"
origin_kind: wp_prose
license: "NOASSERTION"
updated: 2026-10-23
---
# Hackergame 2024 / Node.js is Web Scale

> 来源：Hackergame 2024  |  类型：wp_prose  |  https://github.com/USTC-Hackergame/hackergame2024-writeups/blob/deb6fa3f906e2d0e905f5de5b12757d89f54f812/official/Node.js%20is%20Web%20Scale/README.md

# Node.js is Web Scale

题解作者：[taoky](https://github.com/taoky)

出题人、验题人、文案设计等：见 [Hackergame 2024 幕后工作人员](../../credits.pdf)。

## 题目描述

- 题目分类：web

- 题目分值：200

小 Q 最近在写 Node.js，需要一个键值数据库来存储数据。


注：

- 如果你在好奇标题是什么意思，可以搜索一个标题叫 "Mongo DB Is Web Scale" 的视频（虽然与本题解法无关）。

- flag 在 `/flag` 文件中。

- 点击下面的「打开/下载题目」按钮会为你创建一个独立的题目环境，有效时间一小时。如果环境遇到问题，可以 [关闭环境](https://chal03-manager.hack-challenge.lug.ustc.edu.cn/docker-manager/stop?{token}) 后再试。

[打开/下载题目](https://chal03-manager.hack-challenge.lug.ustc.edu.cn/docker-manager/start?{token})

## 题解

这是一道简单的 Node.js 原型链污染的题目。JavaScript 语言的初学者可能很难意识到的是，JavaScript 中 `{}` 不仅仅是一个字典/哈希表，它事实上是个**对象**，因此它有一些意料之外的属性。原型链污染就和 [`Object.prototype.__proto__`](https://developer.mozilla.org/en-US/docs/Web/JavaScript/Reference/Global_Objects/Object/proto) 这个属性有关。从效果上讲，通过 `__proto__` 属性，可以给对象的的属性设置默认值：


而且可能让其他语言的程序员感到反直觉的是，这样也是可以的：


如果用户可以任意控制这类赋值的话，就构成了原型链污染漏洞。本题也符合这个条件。观察 `/set`：


可以发现它会将用户的 key 输入按 `.` 分割，然后一个循环操作 `current`。如果 `key` 是 `__proto__.a` 的话，结果就是 `current["__proto__"]["a"]` 被设定上了用户给定的值。而本题中，执行命令参考的表长这样：


这是一个对象，因此会被原型链污染问题影响。接下来怎么做应该不用多介绍了。

JavaScript 中真正的「字典」是 [`Map`](https://developer.mozilla.org/en-US/docs/Web/JavaScript/Reference/Global_Objects/Map)。JS 引擎可能会实现成哈希表或者搜索树结构。

此外，`JSON.parse()` 函数可以[正确处理 `__proto__` 作为键的情况](https://developer.mozilla.org/en-US/docs/Web/JavaScript/Reference/Operators/Object_initializer#object_literal_syntax_vs._json)。但是对 `JSON.parse()` 的输出做处理时，程序员仍然需要特别注意。
