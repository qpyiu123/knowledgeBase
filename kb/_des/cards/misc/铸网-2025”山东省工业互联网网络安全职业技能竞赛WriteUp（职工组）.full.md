---
title: "铸网-2025\"山东省工业互联网网络安全职业技能竞赛WriteUp（职工组）"
category: misc
tags: ["铸网-2025 山东省工业互联网网络安全职业技能竞赛", "misc", "XXTEA", "custom-Base64", "modified-TEA", "sum-decrement"]
signals: ["铸网-2025 山东省工业互联网网络安全职业技能竞赛 2025", "XXTEA", "custom-Base64", "modified-TEA", "sum-decrement", "pcap-reassemble", "PK-extract", "crc32-bruteforce", "png-height", "misc_unknown", "WriteUp", "CRC32", "PNG", "Base64"]
difficulty: medium
source: "https://www.ctfiot.com/270057.html"
tools: []
origin: des-import
origin_kind: cards
updated: 2026-10-24
---
# 铸网-2025"山东省工业互联网网络安全职业技能竞赛WriteUp（职工组）

> 赛事：铸网-2025 山东省工业互联网网络安全职业技能竞赛 2025 | 方向：misc | 难度：medium

## 一句话总结

铸网-2025山东省工业互联网职业技能竞赛WriteUp,涵盖流量分析PK文件提取+CRC32爆破+PNG高度修改隐写+RE魔改XXTEA+自定义Base64方向。

## 攻击链

1. MISC安全流量: Net-A嗦哈解码得class数据→反编译按序拼接得PK文件头→恢复压缩包
2. CRC32爆破得密码ICTF_so_Intrest1ng解压得PNG
3. 随波修改PNG高度直接得flag{08ca4a8d32bd08b13f260f224a834b75}
4. RE-寻找序列号: 自定义B64表"ZYXWVUTSRQPONMLKJIHGFEDCBAzxvtrpnljhfdbywusqomkigeca0123456789#$"+XXTEA魔改(sum递减)+key="abcdef9876543210
5. pack_string_le_with_len追加长度字段+b64_encode_custom_from_function索引v18/v19/i_idx/v21
6. flag=everflag{cd00b4953fe9a109148f350427ceddbd}

## 关键 payload

```
everflag{cd00b4953fe9a109148f350427ceddbd}
```

## 经验教训

工业互联网安全赛常考"流量+隐写+魔改密码学"组合拳,XXTEA魔改重点关注sum递增/递减方向+key长度+delta常量+pack模式。

## 标签

XXTEA、custom-Base64、modified-TEA、sum-decrement、pcap-reassemble、PK-extract、crc32-bruteforce、png-height、traffic-analysis

## 参考来源

- https://www.ctfiot.com/270057.html
- 原文件：铸网-2025”山东省工业互联网网络安全职业技能竞赛WriteUp（职工组）.full.md
