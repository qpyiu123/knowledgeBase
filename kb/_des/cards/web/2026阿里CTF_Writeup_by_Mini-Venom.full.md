---
title: "2026 阿里 CTF Writeup by Mini-Venom"
category: web
tags: ["阿里CTF", "web", "heartbeat代理", "Content-Type覆盖", "format string", "{0.config}"]
signals: ["阿里CTF 2026", "heartbeat代理", "Content-Type覆盖", "format string", "{0.config}", "SSTI", ".webp伪装.class", "CAFEBABE", "DexClassLoader动态加载", "web_unknown", "CTF", "Web", "heartbeat", "format"]
difficulty: hard
source: "https://www.ctfiot.com/295706.html"
tools: []
origin: des-import
origin_kind: cards
updated: 2026-10-24
---
# 2026 阿里 CTF Writeup by Mini-Venom

> 赛事：阿里CTF 2026 | 方向：web | 难度：hard

## 一句话总结

阿里CTF 2026 — Web heartbeat 代理 + format string + SSTI + Android .webp 伪装 .class DexClassLoader + 3 batch 流量 (RSA-2048+LZRR+89ali) + BackupExec RPC NDR 16字节XOR。

## 攻击链

1. Web: heartbeat 代理 action 部分, client Content-Type + token multipart/form-data 注入
2. 用 {0.view_functions[index].__globals__[API_KEY]} format string 泄 API_KEY
3. admin 读模板 SSTI: {config.__class__.__init__.__globals__[''os''].popen(''cat /flag*'').read()}
4. 伪装: res/mipmap 数字命 .webp 头是 CAFEBABE 实际是 .class
5. DexClassLoader 动态加载 .webp 中的代码
6. C0003L 扫描器遍历目录找 .java 源文件
7. Runner.encrypt: 8字节 Key + IV + Base64 指令 → 置换移位变换（对称算法）
8. Il1.LZRR 自定义 LZ77 压缩 (头 4C 5A 52 52, version/mode/origLen/crc32, mode=15 走 RLE)
9. 协议: 8 字节 Session Key 用 RSA-2048 公钥加密 + XOR 233 文件名 + LZRR 压缩 payload + 89 61 6C 69 头
10. 流量包 data0/data1/data2 = 3 batch
11. 奇数 batch algo3 keyless（rank=0）, 偶数 batch algo2 依赖 key 需已知明文恢复 keystream
12. BackupExec RPC OpenRemoteFile NDR 16字节 XOR 解密读 flag

## 关键 payload

```
heartbeat 代理 + format string + SSTI / .webp=.class DexClassLoader / LZRR 4C5A5252 / 89ali 头 + RSA-2048 SessionKey + XOR 233 / BackupExec RPC OpenRemoteFile + 16字节 XOR
```

## 经验教训

伪装 .webp/.png/.jpg 是反检测常规手段（CAFEBABE 头 magic number 直接暴露 .class）；加密协议魔数 + RSA 会话密钥 + LZRR 自定义压缩是常见样本偷数据模式；BackupExec RPC 是历史漏洞重灾区。

## 标签

heartbeat代理、Content-Type覆盖、format string、{0.config}、SSTI、.webp伪装.class、CAFEBABE、DexClassLoader动态加载、C0003L扫描器、Runner.encrypt虚拟机、LZRR压缩、4C5A5252头、CRC32 0xEDB88320、RSA-2048 SessionKey、89ali魔数、XOR 233文件名、BackupExec RPC NDR、OpenRemoteFile、16字节XOR

## 参考来源

- https://www.ctfiot.com/295706.html
- 原文件：2026阿里CTF_Writeup_by_Mini-Venom.full.md
