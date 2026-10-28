---
title: "2023 年春秋杯春季赛 - WriteUp By EDISEC"
category: web
tags: ["春秋杯春季赛 2023", "web", "phpstudy漏洞", "numpy_pickle", "qqcms_SSTI", "ezrust"]
signals: ["春秋杯春季赛 2023 2023", "phpstudy漏洞", "numpy_pickle", "qqcms_SSTI", "ezrust", "php_again_opcache", "sudo提权", "Pell方程", "EC_ElGamal", "web_unknown", "EDISEC", "phpstudy", "pickle", "SSTI"]
difficulty: hard
source: "https://www.ctfiot.com/116586.html"
tools: ["Z3"]
origin: des-import
origin_kind: cards
updated: 2026-10-24
---
# 2023 年春秋杯春季赛 - WriteUp By EDISEC

> 赛事：春秋杯春季赛 2023 2023 | 方向：web | 难度：hard | 工具：Z3

## 一句话总结

春秋杯 EDISEC 11 题：phpstudy+pickle+SSTI+Pell+EC_ElGamal+数独 md5+TEA 36 轮+pyinstxtractor。

## 攻击链

1. Web phpstudy: 修改 admin 密码 + 勾选系统权限 + 查看文件下载 flag
2. Web easypy: numpy.loads(pickle) opcode 手搓 + base64 编码过滤 R
3. Web qqcms: SSTI 模板注入 {{loop sql=...}} 改密码 + 文件包含读 flag
4. Web ezrust: 当前目录即 work，./flag 路径穿越
5. Web php_again: opcache file_cache + bind_id + 修改 bin 文件时间戳上传
6. Misc sudo: nano -- /flag 提权读 flag
7. Misc piphack: socket AF_UNIX + pickle 反序列化 + SCM_RIGHTS
8. Misc wordle: 猜单词
9. Misc 58与64: 14268 个 base58 编码 + base64 套娃
10. Crypto checkin: Pell 方程 N=1117 + 二项式展开
11. Crypto cr2: EC-ElGamal + SHA256 k2 + MD5 key + AES-ECB
12. RE sum: 数独 + 9 个 1-9 之和=405 + md5(405)
13. RE Poisoned_tea: VMP 字符串改 UPX + upx 4.0.2 脱壳 + TEA 36 轮
14. RE Pytrans: pyinstxtractor 解包 + uncopyle6 反编译 + z3 约束求解

## 关键 payload

```
pell N=1117, key[]={0x05,0x02,9,7,0}, 数独和 405, md5(405)=bbcbff5c...
```

## 经验教训

数独答案 9 个 1-9 之和恒为 405，md5 即可；VMP 字符串改 UPX 是经典脱壳绕过；pyinstxtractor+uncopyle6 解 PyInstaller。

## 标签

phpstudy漏洞、numpy_pickle、qqcms_SSTI、ezrust、php_again_opcache、sudo提权、Pell方程、EC_ElGamal、数独md5、VMP_UPX、z3求解、EDISEC

## 参考来源

- https://www.ctfiot.com/116586.html
- 原文件：2023年春秋杯春季赛-WriteUp_By_EDISEC.full.md
