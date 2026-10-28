---
title: "Writeup｜1024 羊群之谜 (M01N 战队)"
category: misc
tags: ["1024 羊群之谜 (M01N 队出题)", "misc", "dns_txt_spf", "map_id_param_tamper", "ptrace_set_pc", "suid_setuid_register_redirect"]
signals: ["1024 羊群之谜 (M01N 队出题) 2022", "dns_txt_spf", "map_id_param_tamper", "ptrace_set_pc", "suid_setuid_register_redirect", "write_syscall_hook", "hint_zer0pts2022_readflag", "spf_dkim_dmarc", "classic_pwn", "forensic_traffic", "DNS", "TXT", "map_id", "ptrace"]
difficulty: medium
source: "https://www.ctfiot.com/66460.html"
tools: ["BurpSuite"]
origin: des-import
origin_kind: cards
updated: 2026-10-24
---
# Writeup｜1024 羊群之谜 (M01N 战队)

> 赛事：1024 羊群之谜 (M01N 队出题) 2022 | 方向：misc | 难度：medium | 工具：BurpSuite

## 一句话总结

1024 羊群之谜 3 关：DNS TXT 邮件协议 + 改 map_id 简化 + ptrace 在 write() 系统调用时劫持 PC 跳 puts 输出未覆盖的 flag M01N{w1sh_y0u_happiness_forever}。

## 攻击链

1. 1) berichyang.group DNS TXT 查 SPF "spf1 a mx ?all nice try, but this is not your flag, try another~" → 邮件协议线索 / 2) Burp 改 map_id=80001 简化第二关 / 3) 全局变量 const char *flag="M01N{...}" → main 函数覆盖为 "I hope you are very happy..." → ptrace 注入在 write() 系统调用时改 PC 跳 0x40058E → puts(flag) → flag: M01N{w1sh_y0u_happiness_forever}

## 关键 payload

```
berichyang.group TXT spf1 a mx ?all / map_id=80001 简化 / ptrace 注入 → write 时改 PC=0x40058E → puts(0x400638) / flag M01N{w1sh_y0u_happiness_forever}
```

## 经验教训

经典 ptrace pwn：在 write() 等高频系统调用时改寄存器劫持 PC 跳 puts，是 suid 程序 + 内存不可读写时唯一可行方案。

## 标签

dns_txt_spf、map_id_param_tamper、ptrace_set_pc、suid_setuid_register_redirect、write_syscall_hook、hint_zer0pts2022_readflag、spf_dkim_dmarc、classic_pwn

## 参考来源

- https://www.ctfiot.com/66460.html
- 原文件：Writeup｜1024羊群之谜.full.md
