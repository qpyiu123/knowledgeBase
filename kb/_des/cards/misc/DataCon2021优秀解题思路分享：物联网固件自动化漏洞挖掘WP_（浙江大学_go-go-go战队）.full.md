---
title: "DataCon2021优秀解题思路分享：物联网固件自动化漏洞挖掘WP （浙江大学 go-go-go战队）"
category: misc
tags: ["DataCon 2021", "misc", "iot", "firmware", "angr", "def-use"]
signals: ["DataCon 2021 2021", "iot", "firmware", "angr", "def-use", "symbols", "pypy", "多架构", "污点分析", "misc_unknown", "DataCon2021", "PyPy", "popen", "system"]
difficulty: hard
source: "https://www.ctfiot.com/74660.html"
tools: []
origin: des-import
origin_kind: cards
updated: 2026-10-24
---
# DataCon2021优秀解题思路分享：物联网固件自动化漏洞挖掘WP （浙江大学 go-go-go战队）

> 赛事：DataCon 2021 2021 | 方向：misc | 难度：hard

## 一句话总结

DataCon2021物联网固件angr+def-use自动漏洞挖掘多架构

## 攻击链

1. 用angr跨平台静态分析+PyPy即时编译
2. 危险函数表: popen/system/doSystemCmd/sprintf/snprintf/AES_cbc_encrypt等
3. 获取CFG+PLT段处理延迟绑定
4. ReachingDefinitionsAnalysis def-use链追踪
5. 参数只读地址段→确定不可利用
6. 命令注入: system前0x20字节sprintf+format不含%s
7. 密码学误用: IV/KEY需来自安全随机数
8. 调用路径DFS深度10：source func到sink func

## 关键 payload

```
RDA.tracking=arg; if arg@ro: NOT_EXPLOITABLE
```

## 经验教训

angr RDA+CFG可跨mips/arm/x86分析，PyPy加速

## 标签

iot、firmware、angr、def-use、symbols、pypy、多架构、污点分析

## 参考来源

- https://www.ctfiot.com/74660.html
- 原文件：DataCon2021优秀解题思路分享：物联网固件自动化漏洞挖掘WP_（浙江大学_go-go-go战队）.full.md
