---
title: "京麒CTF 2024初赛Writeup"
category: misc
tags: ["京麒CTF 2024", "misc", "走迷宫", "shellcode约束", "WASM", "HSP3"]
signals: ["京麒CTF 2024 2024", "走迷宫", "shellcode约束", "WASM", "HSP3", "Tauri", "secp256k1", "ECDSA", "LLL格基", "shellcode", "AES", "ECDSA-LLL", "Java", "UTF-8"]
difficulty: hard
source: "https://www.ctfiot.com/184181.html"
tools: ["Java"]
origin: des-import
origin_kind: cards
updated: 2026-10-24
---
# 京麒CTF 2024初赛Writeup

> 赛事：京麒CTF 2024 2024 | 方向：misc | 难度：hard | 工具：Java

## 一句话总结

京麒 2024 初赛全栈：迷宫 shellcode + WASM 爆破 + HSP3 AES + Tauri ECDSA-LLL + Java UTF-8 Overlong Rome 反序列化。

## 攻击链

1. MazeCodeV1: DFS 走迷宫得路径 + 末位&3 序列当 shellcode
2. 序列: 111122110011221122110011112211222211222222110011112211221100110000001100001100001122222222332222332211223333223322221122333322111122110011112222332211222233003322221111
3. 0=xchg esi,eax/1=push rcx/2=xchg edx,eax/3=push rbx
4. easy-wasm: window[''😘😘❤️😘😘''] 加密函数 + 每位加密 16 长 + 逐位爆破
5. Hot Soup: HSP3 + HSPdeco 反编译 + srand(2333333) + AES-128 SHA256 派生
6. possible-door: Tauri 解包 index.html + index-C9fLaX_M.js + rust pdb 看 main
7. js 调 rust get_rand_num 生成 secp256k1 私钥 + AES key/iv 共享 call_once
8. secp256k1 41 比特 nonce + 7 个签名 → LLL 7×7 矩阵还原私钥
9. 私钥 = 39313219724394204510065149548180909443668279642741674773372964155008434357587
10. ezjvav: admin/admin → /source jsrc base64 作 jwt key 伪 root
11. ByteCompare 黑名单 HashMap/TemplatesImpl/fastjson → UTF-8 Overlong 绕
12. Rome 链 EqualsBean + TemplatesImpl + HashMap 反序列化

## 关键 payload

```
京麒CTF{*} + ecdsa_nonce_LLL_recover + 0x404dd0 /bin/sh 栈迁移
```

## 经验教训

ECDSA 弱 nonce (41 比特时间戳) 用 LLL 7×7 矩阵 (BB=1716708884867*2) 一发还原私钥；Java ByteCompare 黑名单字节比对可用 UTF-8 Overlong Encoding (2 字节表示 1 字节) 绕过。

## 标签

走迷宫、shellcode约束、WASM、HSP3、Tauri、secp256k1、ECDSA、LLL格基、UTF-8 Overlong、反序列化、Rome

## 参考来源

- https://www.ctfiot.com/184181.html
- 原文件：京麒CTF_2024_初赛_Writeup.full.md
