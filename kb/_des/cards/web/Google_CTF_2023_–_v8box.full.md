---
title: "Google CTF 2023 – v8box"
category: web
tags: ["Google CTF 2023", "web", "v8", "javascript-engine", "jitless", "sandbox"]
signals: ["Google CTF 2023 2023", "v8", "javascript-engine", "jitless", "sandbox", "code-pointer", "memory-corruption-api", "maglev", "web_unknown", "Google", "CTF", "v8box", "code", "pointer"]
difficulty: hard
source: "https://www.ctfiot.com/251187.html"
tools: ["C", "Python", "x86/x64"]
origin: des-import
origin_kind: cards
updated: 2026-10-24
---
# Google CTF 2023 – v8box

> 赛事：Google CTF 2023 2023 | 方向：web | 难度：hard | 工具：C、Python、x86/x64

## 一句话总结

Google CTF 2023 v8box：V8 sandbox+code pointer sandbox+JITless

## 攻击链

1. fetch v8: git switch -d d90d4533b05301e2be813a5f90223f4c6c1bf63d
2. gclient sync
3. git apply v8.patch + 0001-Protect-chunk-headers-on-the-heap.patch
4. ./tools/dev/v8gen.py x64.release
5. v8_enable_sandbox=true + v8_code_pointer_sandboxing=true
6. v8_jitless=true (无JIT)
7. v8_enable_maglev=false + v8_enable_turbofan=false
8. v8_expose_memory_corruption_api=true
9. gn gen out.gn/x64.release
10. ninja -C out.gn/x64.release -j 12 d8
11. V8_EXPOSE_MEMORY_CORRUPTION_API 暴露漏洞

## 关键 payload

```
v8_enable_sandbox=true + v8_code_pointer_sandboxing=true
```

## 经验教训

V8 sandbox模式开启后内存破坏API需特殊配置

## 标签

v8、javascript-engine、jitless、sandbox、code-pointer、memory-corruption-api、maglev

## 参考来源

- https://www.ctfiot.com/251187.html
- 原文件：Google_CTF_2023_–_v8box.full.md
