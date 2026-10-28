---
title: "game3"
category: reverse
tags: [UCATFLAGS 2024, wp prose]
signals: [game3]
difficulty: medium
source: "https://github.com/UCAS-CTF/UCATFLAGS-WP/blob/b1e667240041738bf1361b555b162b5713be315c/wp/re/game3-wp.md"
tools: []
origin: imported
origin_id: official-21dd1214cc86dcff4f8d22
origin_sha256: d7b35adc781cb8fb8954b49160eb7d0d5ed8dedcb2775df10344734697bef96e
origin_event: "UCATFLAGS 2024"
origin_kind: wp_prose
license: "not_declared"
updated: 2026-10-23
---
# UCATFLAGS 2024 / game3

> 来源：UCATFLAGS 2024  |  类型：wp_prose  |  https://github.com/UCAS-CTF/UCATFLAGS-WP/blob/b1e667240041738bf1361b555b162b5713be315c/wp/re/game3-wp.md

# game3

### 逆向

undefined8 FUN_00101578(char *param_1)

{
  char cVar1;
  int iVar2;
  size_t sVar3;
  undefined8 uVar4;
  int iVar5;
  int iVar6;
  int local_20;
  
  sVar3 = strlen(param_1);
  local_20 = 0;
  while( true ) {
  }
  cVar1 = *param_1;
  *param_1 = -9;
  iVar5 = (*param_1 + 2) % 3;
  iVar2 = (iVar5 * 3) / (int)*param_1;
  iVar6 = (*param_1 + iVar5 + iVar2 + 4) % 3;
  if (*param_1 * iVar5 * iVar2 * iVar6 + *param_1 + iVar5 + iVar2 + iVar6 == 0) {
  }
  *param_1 = cVar1;
  return 0;
}


### 分析

这个程序的主要功能是读取用户输入的字符串，并根据特定条件判断输入是否正确。以下是详细的分析步骤：

1. **主函数 `FUN_00101727`**：

   - 设置标准输出和标准输入的缓冲区为无缓冲。
   - 打印一段提示信息。
   - 使用 `fgets` 函数读取最多30个字符的输入到 `local_38` 数组中。
   - 计算输入字符串的长度，如果长度为29（0x1d），则调用 `FUN_00101578` 函数进行进一步验证。
   - 如果 `FUN_00101578` 返回非零值，表示验证成功，打印 "Success!" 并执行 `system("/bin/cat ../flag")` 命令显示 flag；否则打印 "Fit But Wrong!"。
   - 如果输入长度不为29，打印 "Not Fit!"。
2. **函数 `FUN_00101578`**：

   - 计算输入字符串的长度，并初始化 `local_20` 为0。
   - 进入一个循环，检查输入字符串是否是回文（即正读和反读相同）。
   - 如果是回文，调用 `FUN_00101209` 函数进行进一步验证。
   - 如果不是回文，最终返回0。（中间的复杂计算对结果无影响）
3. **函数 `FUN_00101209`**：

   - 通过分析可知，中间一系列复杂的计算并不会影响最终的结果，因此可以忽略这部分计算。
   - 比较输入字符串是否以 "ucatflags" 是否开头，返回比较结果。

### 解题思路

则可知其接受一个以 "ucatflags" 开头的回文字符串，即可得到 flag。
