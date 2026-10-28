---
title: "2022 春秋杯冬季赛 WriteUp By EDISEC"
category: web
tags: ["2022 春秋杯冬季赛", "web", ".NET", "ComparerData", "ASP.NET-Razor", "File.WriteAllText"]
signals: ["2022 春秋杯冬季赛 2022", ".NET", "ComparerData", "ASP.NET-Razor", "File.WriteAllText", "Process.Start", "/proc/self/mem", "DCT", "FCT", "rce", "web_unknown", "ret2libc", "reverse", "NET"]
difficulty: medium
source: "https://www.ctfiot.com/88092.html"
tools: ["Go", "IDA", "Python"]
origin: des-import
origin_kind: cards
updated: 2026-10-24
---
# 2022 春秋杯冬季赛 WriteUp By EDISEC

> 赛事：2022 春秋杯冬季赛 2022 | 方向：web | 难度：medium | 工具：Go、IDA、Python

## 一句话总结

春秋杯 2022 冬季赛 6 大题：.NET + ASP.NET Razor + Python game + DCT + 位旋转 + Go

## 攻击链

1. Web ezdoenot: .NET ComparerData<T> 反射 + SerTools.Serialize gadget → File.WriteAllText 写文件
2. Web ezphp: ?num=1||1 注入
3. Misc 楠之勇者: getmoney 10 次 → buy 1 个记事录 → writeevil ../proc/self/mem +0x600000 shellcode
4. Re baby_transform: 42 个 8 字节 (float) → DCT 逆变换 (an,bn 计算) → flag{e320d3aa-...}
5. Re easy_python: flag[i] = (flag[i] >> 5) | ((flag[i] << 3) & 255) 位旋转 → flag{ddbae889-...}
6. Re godeep: IDA 反射 + 函数解析 Go 二进制

## 关键 payload

```
DCT 逆变换 an = sum(val[x][1] * cos(-2πxn/N)) / N
```

## 经验教训

.NET Gadget 链 + ASP.NET Razor 反射是高级 web；/proc/self/mem 写 shellcode 是经典 Linux pwn；DCT 逆变换是 reverse 入门

## 标签

.NET、ComparerData、ASP.NET-Razor、File.WriteAllText、Process.Start、/proc/self/mem、DCT、FCT、bit-rotate、Go-reflect、春秋杯

## 参考来源

- https://www.ctfiot.com/88092.html
- 原文件：20222022年春秋杯冬季赛-WriteUp_By_EDISEC.full.md
