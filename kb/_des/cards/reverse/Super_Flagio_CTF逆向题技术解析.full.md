---
title: "Super Flagio CTF 逆向题技术解析"
category: reverse
tags: ["Super Flagio CTF", "reverse", "cocos2d-x", "luajit-bytecode", "xxtea-decrypt", "custom-vm"]
signals: ["Super Flagio CTF 2025", "cocos2d-x", "luajit-bytecode", "xxtea-decrypt", "custom-vm", "lua-encrypt", "frida-hook", "reverse", "Super", "Flagio", "CTF", "Android", "XXTEA", "LuaJIT"]
difficulty: hard
source: "https://www.ctfiot.com/283888.html"
tools: ["Frida"]
origin: des-import
origin_kind: cards
updated: 2026-10-24
---
# Super Flagio CTF 逆向题技术解析

> 赛事：Super Flagio CTF 2025 | 方向：reverse | 难度：hard | 工具：Frida

## 一句话总结

Super Flagio CTF：cocos2d-x Android 游戏逆向，XXTEA 解 LuaJIT + 自定义 opcode VM 还原。

## 攻击链

1. unzip flagio.apk 提取 assets/src/ 加密 Lua 脚本
2. strings libgame.so | grep XXTEA 发现 xctf-flagio-2dx 密钥
3. LuaJIT 2.1.0-beta3 字节码格式识别
4. frida hook luaL_loadbuffer 拦截解密后字节码
5. 自定义 opcode 顺序：PUSH_IMM(0x41)/PUSH_REG(0x42)/PUSH_IN(0x32)/POP_REG(0x25)/POP_OUT(0x31)/INC_REG(0x21)/DEC_REG(0x22)/XOR_REG(0x24)/XOR_IMM(0x23)/RET(0x90)
6. 模拟执行 12 指令 + 链式 XOR
7. 加密算法：output[0] = (input[0]^30)-1; output[i] = (output[i-1]^input[i])±1
8. 奇偶差异处理：i%2==0 或 i==31 减 1；奇数加 1
9. 32 字节密文 [94,106,91,110,86,100,82,20,...]
10. 解密脚本从后向前 XOR+±1
11. 验证 SHA256 哈希
12. flag = A766957A53EDA9290CCF8E03F1A9B7E0

## 关键 payload

```
frida -l hook.js -f com.flagio.app
```

## 经验教训

加密字节码 + 自定义 opcode 是游戏反外挂常见组合，Frida hook luaL_loadbuffer 是标准破法。

## 标签

cocos2d-x、luajit-bytecode、xxtea-decrypt、custom-vm、lua-encrypt、frida-hook

## 参考来源

- https://www.ctfiot.com/283888.html
- 原文件：Super_Flagio_CTF逆向题技术解析.full.md
