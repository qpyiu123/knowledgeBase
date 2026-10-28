---
title: "Write Up Reverse Engineering — LINE CTF 2023— Fishing and Jumpit"
category: misc
tags: ["LINE CTF 2023", "misc", "anti_decompiler_ebff", "nop_patch", "thread_modification_debug", "custom_rc4_iv"]
signals: ["LINE CTF 2023 2023", "anti_decompiler_ebff", "nop_patch", "thread_modification_debug", "custom_rc4_iv", "frida_hook_brute_force", "unity_il2cpp", "il2cppdumper", "ghidra_python_script", "reverse", "LINE", "CTF", "Fishing", "IDA"]
difficulty: hard
source: "https://www.ctfiot.com/107081.html"
tools: ["Ghidra", "IDA", "Python"]
origin: des-import
origin_kind: cards
updated: 2026-10-24
---
# Write Up Reverse Engineering — LINE CTF 2023— Fishing and Jumpit

> 赛事：LINE CTF 2023 2023 | 方向：misc | 难度：hard | 工具：Ghidra、IDA、Python

## 一句话总结

LINE CTF 2023 两道 RE：Fishing (EB FF XX 反 IDA + 线程修改 + Frida hook 41 字节爆破) + Jumpit (Unity IL2CPP 还原 + GameManager 11 段 score 拼接 AES-128 ECB 密钥解密)。

## 攻击链

1. Fishing:EB FF XX 反反编译字节码 → Python 脚本扫描全文件改 0x90 NOP → 重 IDA 反编译成功 → 发现 sub_140001DDB 段选混淆 + 线程修改 (key 调试器=m4g1KaRp_ON_7H3_Hook 实际) → XOR+sub 输入加密 + 自定义 RC4 加密 + memcmp 比 encryptedFlag → Frida hook 0x3f48 fscanf + 0x2310 encrypt + 0x3ff0 memcmp → 多线程 8 池爆破 41 字节 flag / Jumpit:Unity Android libil2cpp.so + global-metadata.dat → IL2CPPDumper → Ghidra + Python ghidra_with_struct.py 恢复符号 → GameManager$$ScoreUp 拼接 11 段 score StringLiteral → "Cia!fo2MPXZQvaVA39iuiokE6cvZUkqx" 作 AES-128 ECB 密钥 → base64 解 cWGTmeDlFsYEFI9E5mH/eCnQ1SNlWJlXj+klPLbWS/c/1vI7UPrO4dp41u2tTGM2

## 关键 payload

```
ebff_nop_patch = b'\xeb\xff\xXX' → b'\x90\x90\x90' / Frida hook 0x3f48 + 0x2310 + 0x3ff0 / key = 'Cia!fo2MPXZQvaVA39iuiokE6cvZUkqx' / AES.MODE_ECB / score literal concat
```

## 经验教训

EB FF XX" 是 IDA 反编译杀手；现代 CTF RE 必备三件套：Frida 自动化 + IL2CPPDumper Unity 反编译 + Ghidra Python 脚本恢复符号表。

## 标签

anti_decompiler_ebff、nop_patch、thread_modification_debug、custom_rc4_iv、frida_hook_brute_force、unity_il2cpp、il2cppdumper、ghidra_python_script、aes_ecb_score_concat、anti_debug_int2c

## 参考来源

- https://www.ctfiot.com/107081.html
- 原文件：Write_Up_Reverse_Engingeering_—_LINE_CTF_2023—_Fishing_and_Jumpit.full.md
