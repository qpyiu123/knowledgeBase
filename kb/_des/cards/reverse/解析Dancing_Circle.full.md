---
title: "解析Dancing Circle"
category: reverse
tags: ["Dancing Circle", "reverse", "sudoku", "dancing-links", "DLX", "exact-cover"]
signals: ["Dancing Circle 2024", "sudoku", "dancing-links", "DLX", "exact-cover", "x64dbg", "dynamic-analysis", "byte-rotation", "table-composition", "reverse", "Dancing", "Circle", "cover", "T_net"]
difficulty: hard
source: "https://www.ctfiot.com/282475.html"
tools: ["IDA"]
origin: des-import
origin_kind: cards
updated: 2026-10-24
---
# 解析Dancing Circle

> 赛事：Dancing Circle 2024 | 方向：reverse | 难度：hard | 工具：IDA

## 一句话总结

Dancing Circle把"加密题"藏回数独与DLX,大整数生成数独初盘+DLX精确覆盖求解+5步×60次×4旋转=1200次cover+6次字节查表合成净变换T_net,IDA+Python复现全流程。

## 攻击链

1. 双处数据校验→生成大数Num1,Num1×Num2得数独初盘Data1
2. 解析Data1→初始化DLX(Dancing Links)精确覆盖问题
3. 中心格不由用户输入,由9个调试检查函数返回推得必须=7
4. 用户输入80位十六进制字符在cover()中分5小步做"交换+移位
5. 每60次交换得到一次向右90°旋转,共执行4次旋转回原位
6. 5×60×4=1200次cover()调用,每格经历6次字节级查表变换
7. 合成净变换T_net[0-9]=[11,181,163,154,228,232,129,94,134,151]
8. L[T_net(D_i)]==S_i (∀i≠center)对UserData2查表后与DLX解逐位比较
9. 匹配计数cnt=79(比较中心时cnt--)为通过条件
10. 动态抓初盘与查表→合成T_net→DLX解数独→逐格穷举逆向80位hex输入→自检cnt

## 关键 payload

```
32415867057146038208672345171508423626351804840632517408215763137846025652307148
```

## 经验教训

复杂加密题常包装经典算法(数独+DLX),动态分析(x64dbg/IDA)比静态分析更有效;字节级查表合成T_net是经典混淆手段;精确覆盖建模是数独问题的本质。

## 标签

sudoku、dancing-links、DLX、exact-cover、x64dbg、dynamic-analysis、byte-rotation、table-composition、anti-disassembly

## 参考来源

- https://www.ctfiot.com/282475.html
- 原文件：解析Dancing_Circle.full.md
