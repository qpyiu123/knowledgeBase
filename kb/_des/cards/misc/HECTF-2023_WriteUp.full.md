---
title: "HECTF-2023 WriteUp"
category: misc
tags: ["HECTF 2023", "misc", "osint", "ntlm", "baidu-pan", "拼图"]
signals: ["HECTF 2023 2023", "osint", "ntlm", "baidu-pan", "拼图", "dou-di-zhu", "bilibili", "gif", "视频", "misc_unknown", "HECTF", "MISC", "OSINT", "NTLM"]
difficulty: medium
source: "https://www.ctfiot.com/147010.html"
tools: []
origin: des-import
origin_kind: cards
updated: 2026-10-24
---
# HECTF-2023 WriteUp

> 赛事：HECTF 2023 2023 | 方向：misc | 难度：medium

## 一句话总结

HECTF 2023 多关MISC：OSINT+牌型密码+拼图+NTLM

## 攻击链

1. 第1关: Welcome HECTF{Welcome_To_HECTF_2023}
2. Osint: 河北省邯郸市永年区永年太极广场
3. 牌型密码: 黑桃s 红桃h 梅花c 红尖d
4. small joker=kaf, big joker=wi1
5. B站视频: https://www.bilibili.com/video/BV1Lj41187kx/
6. 农民牌得flag: HECTF{Dou_di_Zhu_uhZ_id_uoD_hEccctf_TY6d145A57R7WVz}
7. 百度网盘: 二维码拼图24张
8. flag: HECTF{java_ca_fei_bao_bei}
9. NTLM流量: ntlmssp过滤+NTProofStr提取

## 关键 payload

```
HECTF{Dou_di_Zhu_uhZ_id_uoD_hEccctf_TY6d145A57R7WVz}
```

## 经验教训

综合MISC题常结合OSINT+牌型+拼图+NTLM

## 标签

osint、ntlm、baidu-pan、拼图、dou-di-zhu、bilibili、gif、视频

## 参考来源

- https://www.ctfiot.com/147010.html
- 原文件：HECTF-2023_WriteUp.full.md
