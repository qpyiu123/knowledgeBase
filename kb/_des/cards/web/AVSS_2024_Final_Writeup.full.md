---
title: "AVSS 2024 Final Writeup"
category: web
tags: ["AVSS", "web", "JS bridge", "_jsbridge.add/edit/show/delete", "openfile/writefile/readfile/closefile", "heap 0x90 重叠"]
signals: ["AVSS 2024", "JS bridge", "_jsbridge.add/edit/show/delete", "openfile/writefile/readfile/closefile", "heap 0x90 重叠", "show 0x8 找指针", "stringToHex", "u32/p32端序", "xhr log exfil", "web_unknown", "AVSS", "Final", "jsbridge", "add"]
difficulty: hard
source: "https://www.ctfiot.com/213863.html"
tools: []
origin: des-import
origin_kind: cards
updated: 2026-10-24
---
# AVSS 2024 Final Writeup

> 赛事：AVSS 2024 | 方向：web | 难度：hard

## 一句话总结

AVSS 2024 Final — _jsbridge add/edit/show/delete + heap 0x90 重叠 (del 偶数+add 奇数) + show 0x8 找指针 + stringToHex/u32/p32 端序 + xhr 异步 exfil。

## 攻击链

1. _jsbridge.add(i, key, size) 申请 0x4 / 0x90 / 0x1000 大小堆
2. add 0..48 size=0x90 + edit 写 char(48+i) 填充
3. del 偶数下标 (0,2,4..46) → 释放 0x90 堆
4. 再 add 奇数下标 (1,3,5..47) → 重叠分配
5. show(j, 0x8) 拿指针, map 找相同指针的下标 → 堆重叠检测
6. 找相同指针可改写其他对象的 header
7. stringToHex + u32 + p32 端序转换
8. xhr log 异步 exfil 数据
9. 触发 _jsbridge 栈溢出 RCE

## 关键 payload

```
add(0,0x4) 10次 + add(48,0x1000) 10次 / del 偶数 0..46 / add 奇数 1..47 重叠 / show(j,0x8) 找指针 / stringToHex+u32+p32 端序
```

## 经验教训

堆重叠经典模式:交错 add+del 偶数,add 奇数回收;show 部分字节是找指针的标准做法;JS bridge 类型混乱是移动 hybrid 漏洞常见入口。

## 标签

JS bridge、_jsbridge.add/edit/show/delete、openfile/writefile/readfile/closefile、heap 0x90 重叠、show 0x8 找指针、stringToHex、u32/p32端序、xhr log exfil、_jsbridge栈溢出

## 参考来源

- https://www.ctfiot.com/213863.html
- 原文件：AVSS_2024_Final_Writeup.full.md
