---
title: "从data段中加载PE Executable——2022蓝帽杯Reverse Loader Writeup"
category: reverse
tags: ["蓝帽杯 2022 Reverse", "reverse", "PE加载器", "无文件PE", "IAT修复", "Base Relocation"]
signals: ["蓝帽杯 2022 Reverse 2022", "PE加载器", "无文件PE", "IAT修复", "Base Relocation", "CRC32", "GetProcAddress", "PEB", "LDR", "reverse", "Loader", "data", "IAT", "Base"]
difficulty: hard
source: "https://www.ctfiot.com/48420.html"
tools: ["Sage"]
origin: des-import
origin_kind: cards
updated: 2026-10-24
---
# 从data段中加载PE Executable——2022蓝帽杯Reverse Loader Writeup

> 赛事：蓝帽杯 2022 Reverse 2022 | 方向：reverse | 难度：hard | 工具：Sage

## 一句话总结

手写 PE Loader 从 .data 段加载无文件 PE，IAT 用 CRC32 查表 + Base Relocation；nim 关键逻辑是 Pell 方程 x²-11y²=1 求解。

## 攻击链

1. VirtualProtect 把 .data 段设为 RWX 加载内嵌 PE dump
2. 修改栈顶 rip 跳转到 code+0x34000 主逻辑
3. gs:[0x60] 拿 PEB 指针 → PEB:[0x18] 拿 LDR 指针
4. LDR:[0x20] 拿 InMemoryOrderModuleList 遍历已加载模块
5. 解析 kernel32.dll 的 IMAGE_NT_HEADERS + IMAGE_DATA_DIRECTORY 拿 Export table
6. 用 0xEDB88320 多项式 CRC32 校验函数名查 GetProcAddress
7. lodsd 取下一个 checksum 循环查 LoadLibraryA
8. 处理 Import Table IMAGE_IMPORT_DESCRIPTOR FirstThunk 填绝对地址
9. 处理 Base Relocation Table 遍历每个要改写地址加上 code 基址
10. 跳转 OEP 后是 nim 编译逻辑：input 解析 big num
11. 约束 num1*num1-11*num2*num2 == 9 + big1 < num1 < big2
12. sage 算 Pell 方程 x²-11y²=1 连分数收敛子
13. 复合 (x1,y1)×(x2,y2) 找 num1 = 3x, num2 = 3y

## 关键 payload

```
flag{%018d%018d}'' % (num1, num2)
```

## 经验教训

无文件 PE 加载 = VirtualProtect RWX + 手写 IAT (CRC 查函数名) + Base Relocation; Pell 方程 x²-Dy²=1 用连分数 convergents + 复合群无限解。

## 标签

PE加载器、无文件PE、IAT修复、Base Relocation、CRC32、GetProcAddress、PEB、LDR、InMemoryOrderModuleList、Pell方程、big num、nim

## 参考来源

- https://www.ctfiot.com/48420.html
- 原文件：从_data_段中加载_PE_Executable_——_2022-蓝帽杯-Reverse-Loader_Writeup.full.md
