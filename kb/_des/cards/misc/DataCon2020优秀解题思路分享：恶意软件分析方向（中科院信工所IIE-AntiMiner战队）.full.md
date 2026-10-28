---
title: "DataCon2020优秀解题思路分享：恶意软件分析方向（中科院信工所IIE-AntiMiner战队）"
category: misc
tags: ["DataCon 2020", "misc", "malware", "lief", "section-entropy", "regex"]
signals: ["DataCon 2020 2020", "malware", "lief", "section-entropy", "regex", "bitcoin-wallet", "function-pattern", "cfg", "misc_unknown", "DataCon2020", "LIEF", "CFG", "section", "size"]
difficulty: medium
source: "https://www.ctfiot.com/75697.html"
tools: ["C"]
origin: des-import
origin_kind: cards
updated: 2026-10-24
---
# DataCon2020优秀解题思路分享：恶意软件分析方向（中科院信工所IIE-AntiMiner战队）

> 赛事：DataCon 2020 2020 | 方向：misc | 难度：medium | 工具：C

## 一句话总结

DataCon2020恶意软件分析：LIEF+正则+CFG图可视化

## 攻击链

1. 用LIEF库解析PE section属性
2. 统计R/W/X section size和熵均值
3. rsrc section个数
4. 正则提取: 路径[C-Zc-z]:/、reg/、url、IP、btc/ltc/xmr钱包
5. MZ/PE/coin/cpu/gpu/pool等模式
6. m32_pattern: \x55\x8b\xec[^\xc3]*\xc3 函数识别
7. capstone反汇编得操作码序列
8. graphviz生成CFG可视化

## 关键 payload

```
m32_pat = re.compile(b''\x55\x8b\xec[^\xc3]*\xc3'')  # 函数头
```

## 经验教训

PE section熵+操作码序列+CFG是恶意软件家族分类特征

## 标签

malware、lief、section-entropy、regex、bitcoin-wallet、function-pattern、cfg

## 参考来源

- https://www.ctfiot.com/75697.html
- 原文件：DataCon2020优秀解题思路分享：恶意软件分析方向（中科院信工所IIE-AntiMiner战队）.full.md
