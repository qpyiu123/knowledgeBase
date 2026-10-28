---
title: "强网拟态@2025 writeup - AI/Pwn/Web/Misc/Crypto全方向"
category: misc
tags: ["强网拟态@2025", "misc", "smolagents", "prompt_injection", "ROP", "ret2libc"]
signals: ["强网拟态@2025 2025", "smolagents", "prompt_injection", "ROP", "ret2libc", "libc_environ", "AArch64_pwn", "mprotect", "ORW_shellcode", "ssrf", "heap", "AArch64", "Spring", "Gateway"]
difficulty: hard
source: "https://www.ctfiot.com/276905.html"
tools: ["Flask", "Jinja2", "ROP", "Spring"]
origin: des-import
origin_kind: cards
updated: 2026-10-24
---
# 强网拟态@2025 writeup - AI/Pwn/Web/Misc/Crypto全方向

> 赛事：强网拟态@2025 2025 | 方向：misc | 难度：hard | 工具：Flask、Jinja2、ROP、Spring

## 一句话总结

强网拟态2025全方向10+题:smolagents提示词注入+ROP+heap+AArch64+Spring Gateway Actuator SpEL+Flask SSRF链+Jinja2 lipsum+RCE+LCG LLL恢复。

## 攻击链

1. AI small_injection:smolagents系统提示词欺骗+Python子类Popen反弹shell → Pwn babystack:栈溢出+覆盖n180097847为0x1337ABC → Pwn pin_note:tcache堆编辑+environ泄露+heap交叉指针 → Pwn printf+ORW:ROP+openat+read+puts → Pwn aarch64:qemu模拟aarch64+tcache poison+environ栈迁移 → Web Spring:Actuator routes SpEL执行restrictive-property-accessor=false+resourceHandlerMapping locationValues=file:// + file:///flag → Web fetch+SSRF:Flask Refresh头+meta跳转+X-Next头7步跳到127.0.0.1:5000/_internal/secret → SSTI:Jinja2 {{set lipsum[sget('g')].os.popen(sget('p'))}} → Crypto LCG:LLL恢复s33+反推s1+生成admin_pass+AES MD5(ts) ECB+Ciallo～(∠・ω<)编码

## 关键 payload

```
smolagents注入 + Actuator SpEL + Jinja2 lipsum os.popen + LCG LLL + 7步SSRF Refresh
```

## 经验教训

smolagents system prompt可被用户消息覆盖;Spring Cloud Gateway Actuator routes配置filter SpEL可执行任意SpEL + property accessor解禁;Flask Refresh header+meta refresh+X-Next串联7步跳转绕过同源+SSRF;Jinja2 lipsum全局函数os.popen SSTI;LCG高字节通过LLL格密码恢复;AArch64 libc-2.27 environ栈迁移;openat+read+puts orw链。

## 标签

smolagents、prompt_injection、ROP、ret2libc、libc_environ、AArch64_pwn、mprotect、ORW_shellcode、Spring_Gateway_Actuator、SpEL注入、file://、Refresh_header_SSRF、Jinja2_SSTI、lipsum、LCG_LLL、AES_MD5

## 参考来源

- https://www.ctfiot.com/276905.html
- 原文件：强网拟态@2025_writeup.full.md
