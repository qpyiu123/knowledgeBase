---
title: "洞 OVO"
category: reverse
tags: [NewStar CTF 2024, wp prose]
signals: [洞 OVO]
difficulty: medium
source: "https://github.com/pj-newstar/wiki-docs/blob/1a0f2ba21a30f950276396118b315eef0328371c/docs/wp/2024/week4/reverse/dongovo.md"
tools: []
origin: imported
origin_id: official-afea1d437c66b0c0e2f63a
origin_sha256: 5a6cde9fab90a24e85fe73de1b94e63a101267c52b552678fa889b3e420b5a4f
origin_event: "NewStar CTF 2024"
origin_kind: wp_prose
license: "MIT"
updated: 2026-10-23
---
# NewStar CTF 2024 / 洞 OVO

> 来源：NewStar CTF 2024  |  类型：wp_prose  |  https://github.com/pj-newstar/wiki-docs/blob/1a0f2ba21a30f950276396118b315eef0328371c/docs/wp/2024/week4/reverse/dongovo.md

import Container from '@/components/docs/Container.vue'

# 洞 OVO

首先根据题目信息直接搜索 给定版本的 WinRAR，一搜就有。

确定漏洞为 WinRAR version 6.22 - Remote Code Execution via ZIP archive (CVE-2023-38831).

找点参考文章学一学：

- [WinRAR 代码执行漏洞（CVE-2023-38831）的原理分析](https://www.cnblogs.com/GoodFish-/p/17715977.html)
- [WinRAR（CVE-2023-38831）漏洞原理](https://mp.weixin.qq.com/s?__biz=MjM5NTc2MDYxMw==&mid=2458544969&idx=1&sn=473822d99738dc8c20cf0c7df866adea)

通过文章阅读了解主要流程：<strong>获取点击的文件 → 释放到临时目录 → 执行</strong>。

那么题目要求找的函数段大概率就是释放到临时目录这一段。

网上的文章一般来说都是给的这一段：


题目当然没有这么简单，不过离答案也很接近了，向上溯源，再结合使用 bindiff，得到 `sub_1400EF508`.

流程如下：

> `sub_1400EF508` -> `sub_140009290` -> `sub_14000A650` -> `sub_1400D6070` -> `0x1400D6478` -> `0x1400D3474` -> `0x1400CEBF4` -> `0x140077054` -> `0x140089948`


预期做法难度可能较大，不过本题还有其他解法。

**PS:** 可疑函数并不多，锁定范围爆破提交一下基本就 easy 结束了。偷鸡做法：因为修复之处增加了 3 条汇编 所以把所有新旧对比改了 3 条汇编的地方 全交一遍估计也能成。
