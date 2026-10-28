---
title: "阿里CTF2026-license"
category: reverse
tags: ["阿里CTF", "reverse", "协议逆向", "AES-GCM", "zstd压缩", "base64"]
signals: ["阿里CTF 2026", "协议逆向", "AES-GCM", "zstd压缩", "base64", "protobuf", "Rijndael-160魔改AES", "SBOX+mixcolumn+加解密互换", "RSA4096签名", "reverse", "CTF2026-license", "nonce", "zstd", "AES-160"]
difficulty: hard
source: "https://www.ctfiot.com/299954.html"
tools: ["C"]
origin: des-import
origin_kind: cards
updated: 2026-10-24
---
# 阿里CTF2026-license

> 赛事：阿里CTF 2026 | 方向：reverse | 难度：hard | 工具：C

## 一句话总结

阿里CTF2026-license协议逆向:4字节长度+12字节nonce数据流→AES-GCM解密→zstd解压缩→base64→protobuf→魔改AES-160(20字节块7轮,SBOX/mixcolumn/加解密互换,CBC+PKCS#7)解JSON含license_code+sign(RSA4096签名)→读FLAG环境变量

## 攻击链

1. 1. 数据包=4字节长度+12字节nonce+(长度-12)字节数据流|2. 数据流AES-GCM解密|3. zstd解压缩|4. base64解码|5. protobuf解析4字段(enc_data+password+salt+sha256_hash)|6. 魔改AES-160(20字节块,7轮)解密:密钥=PBKDF2-HMAC-SHA256(password,salt,ITER)→48字节,前28字节key+后20字节iv|CBC+PKCS#7填充,加解密互换,SBOX魔改,mix_column魔改|7. 解密JSON含license_code+sign(RSA4096签名)|8. 读取FLAG环境变量|9. 失败:e就是65537,卡在RSA签名分析

## 关键 payload

```
AES_SBOX=bytes.fromhex("637C699066329A0E6441CBA99FFAD5AA6524F777371D83EB981A2A7DBD2502EEE5E7455029C4ECA7CCF05C4D1396A2099EFF5AA1C76FE9150C1BC5975614A5B620D62111700D7F4E4652354BA4C9011E310F2F17FCDB7430DE481C950653D36718FD2D1F7A8D8775B426E071A3825807D4BADAA8B5D99CCFF960D81200798904C2B83C614276DF6CEA495462E8B3F50BF1287ED2CD23F28E80F836E3D722DDF34A2E5510C0B15943AC683FBB6DAFCAC638B973AEDCBC9DC3D14CFEA63B92E42B5BFB2CF6C1B25D8FEF78915F9472ED4088B7443427E16A0586C8938A7B8451E63D990A33BF39038C086B3E8519CEB08BABA0E247BE4F5E9B57AD6E81163AD0F4")|Rijndael-160:Nb=5 Nk=7 Nr=11|MIX_MAT=[[4,1,6,2],[2,4,1,6],[6,2,4,1],[1,6,2,4]]|rijndael160_encrypt_block(block20, key28)|gf_mul(xtime 0x8D)|PBKDF2-HMAC-SHA256 password,salt,ITER dklen=48 key28+mask20|GCM J0=nonce12+0x00000001|H = AES_K(0^128)|S = AES_K(J0)|tag = S XOR GHASH(H, AAD, C)
```

## 经验教训

1) 数据包格式:4字节长度+12字节nonce+(长度-12)字节数据流; 2) AES-GCM:J0=nonce12||0x00000001, H=AES_K(0^128), S=AES_K(J0), tag=S⊕GHASH(H,A,C); 3) zstd+zlib混合压缩; 4) protobuf:varint编码+field-length-delimited; 5) Rijndael-160魔改:Nb=5块长20字节,Nk=7密钥28字节,Nr=11轮; 6) 魔改SBOX+魔改mixcolumn+加解密互换+CBC+PKCS#7; 7) PBKDF2-HMAC-SHA256 dklen=48; 8) RSA4096签名e=65537;

## 标签

协议逆向、AES-GCM、zstd压缩、base64、protobuf、Rijndael-160魔改AES、SBOX+mixcolumn+加解密互换、RSA4096签名、PBKDF2-HMAC-SHA256、PKCS#7、JSON license_code+sign

## 参考来源

- https://www.ctfiot.com/299954.html
- 原文件：阿里CTF2026-license.full.md
