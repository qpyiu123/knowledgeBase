---
title: "2025 湾区杯网络安全竞赛 WriteUP（SM4 国密 + 沙箱逃逸 + JWT 爆破 + Quaternion BSGS + AES Sbox 逆推）"
category: crypto
tags: ["2025 湾区杯", "crypto", "湾区杯 2025", "SM4 国密 32 轮 encrypt/decrypt", "base64 VCWBIdzfjm45EmYFWcqXX0VpQeZPeI6Qqyjsv31yuPTDC80lhFlaJY2R3TintdQu", "沙箱逃逸 chr(95)*2+builtins+chr(95)*2 globals[builtins][import] os"]
signals: ["2025 湾区杯 2025", "湾区杯 2025", "SM4 国密 32 轮 encrypt/decrypt", "base64 VCWBIdzfjm45EmYFWcqXX0VpQeZPeI6Qqyjsv31yuPTDC80lhFlaJY2R3TintdQu", "沙箱逃逸 chr(95)*2+builtins+chr(95)*2 globals[builtins][import] os", "JWT HS256 2 字母爆破 @o70xO$0%#qR9#m0", "Quaternion DLP BSGS secret < 2^50", "AES-ECB + md5(secret) 派生密钥", "自定义 S-box invert_table 逆推", "crypto_rsa", "jwt", "lattice", "web_unknown", "SM4"]
difficulty: hard
source: "https://www.ctfiot.com/269807.html"
tools: ["Python"]
origin: des-import
origin_kind: cards
updated: 2026-10-24
---
# 2025 湾区杯网络安全竞赛 WriteUP（SM4 国密 + 沙箱逃逸 + JWT 爆破 + Quaternion BSGS + AES Sbox 逆推）

> 赛事：2025 湾区杯 2025 | 方向：crypto | 难度：hard | 工具：Python

## 一句话总结

2025 湾区杯：SM4 国密 32 轮解密 + Python 沙箱逃逸 globals+builtins+import + JWT 2 字母爆破 + Quaternion DLP BSGS + 自定义 S-box 逆推。

## 攻击链

1. SM4 国密 32 轮：FK[4] + CK[32] 固定 + 16 字节密钥 a8a58b78f41eeb6a
2. decrypt: cryptBlockDecrypt 倒序用 sk[31-i]
3. base64 解密 VCWB... → plaintext
4. 沙箱逃逸：chr(95)*2 + "builtins" + chr(95)*2 → globals()['__builtins__']['__import__']('os').system('cat /fl11lag')
5. JWT 2 字母爆破：jwtKey = "@o70xO$0%#qR9#" + 2 字母
6. Quaternion DLP BSGS: secret < 2^50 → AES key = md5(secret)
7. 自定义 S-box 逆推：byte_2120 → mapping = invert_table(sub_13E1) → ror(tmp, k) 逆 sub_1492

## 关键 payload

```
jwtKey = '@o70xO$0%#qR9#' + 2 字母 (charset 62)
```

## 经验教训

SM4 32 轮国密 SPN：FK[4] + CK[32] 固定 + sk[32] 子密钥；JWT HS256 弱密钥爆破 62 字符×2=3844 次；Quaternion DLP BSGS secret<2^50 优化。

## 标签

湾区杯 2025、SM4 国密 32 轮 encrypt/decrypt、base64 VCWBIdzfjm45EmYFWcqXX0VpQeZPeI6Qqyjsv31yuPTDC80lhFlaJY2R3TintdQu、沙箱逃逸 chr(95)*2+builtins+chr(95)*2 globals[builtins][import] os、JWT HS256 2 字母爆破 @o70xO$0%#qR9#m0、Quaternion DLP BSGS secret < 2^50、AES-ECB + md5(secret) 派生密钥、自定义 S-box invert_table 逆推、ROR 逆 sub_1492

## 参考来源

- https://www.ctfiot.com/269807.html
- 原文件：2025湾区杯网络安全竞赛WriteUP.full.md
