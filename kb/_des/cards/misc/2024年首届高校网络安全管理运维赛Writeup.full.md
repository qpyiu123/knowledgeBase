---
title: "2024 首届高校网络安全管理运维赛 Writeup"
category: misc
tags: ["2024 首届高校网络安全管理运维赛", "misc", "gif 帧分离 rot13", "钓鱼邮件 base64", "冰蝎 e45e329feb5d925b 默认密钥", "zip CRC 32 明文攻击"]
signals: ["2024 首届高校网络安全管理运维赛 2024", "gif 帧分离 rot13", "钓鱼邮件 base64", "冰蝎 e45e329feb5d925b 默认密钥", "zip CRC 32 明文攻击", "sqlite 索引解析", "/cgi-bin/..%2e.. 路径穿越", "MongoDB $toString", "javax.script.ScriptEngineManager JS eval", "misc_unknown", "sqli", "ssti", "xxe", "ROT13"]
difficulty: medium
source: "https://www.ctfiot.com/179730.html"
tools: ["Java", "Z3"]
origin: des-import
origin_kind: cards
updated: 2026-10-24
---
# 2024 首届高校网络安全管理运维赛 Writeup

> 赛事：2024 首届高校网络安全管理运维赛 2024 | 方向：misc | 难度：medium | 工具：Java、Z3

## 一句话总结

高校运维赛综合：签到 ROT13+钓鱼邮件+冰蝎+sqlite+路径穿越+Pickle+MongoDB+Java EL 盲注+XXE+z3+栈溢出+洗牌期望——运维/渗透/密码/取证全覆盖。

## 攻击链

1. Misc 签到: gif 帧分离 + rot13 解密 synt{fvtava-dhvm-jryy-qbar}
2. 钓鱼邮箱 Flag1: base64 解密发件人
3. 钓鱼邮箱 Flag2: base64 解密邮件内容
4. 钓鱼邮箱 Flag3: VirusTotal 查 foobar-edu-cn.com + SPF/DKIM/DMARC dnsspy
5. easyshell: 冰蝎默认密钥 e45e329feb5d925b 解倒数第二个 + CRC32 明文攻击 A8s123/+*
6. SecretDB: sqlite 格式解析 索引/值 + passwd_decode 自定义映射
7. /cgi-bin/..%2e 路径穿越到 /bin/sh 反弹 cat /fl*
8. Pickle opcode: cconfig notadmin (S''admin'' S''yes'' u0(cconfig backdoor (S''exec...'') lo.
9. MongoDB: {"username": {"$toString": "admin"}} 1''||
10. Java EL: javax.script.ScriptEngineManager JS eval 盲注 /flag 字符
11. XXE: php://filter base64 /flag + 外部 dtd 二次回传
12. reverse: z3 解 4 段 32-bit 位运算 a1=0xe3c6235c a2=0x05d9434d a3=0x04b1edf3 a4=0x04034083
13. pwn: 栈溢出 0x38 + p64(0x40117A) backdoor / pwn03 admin+密码 0x9e 填充 + p64(0x40127E)
14. crypto: shuffle m n instance 蒙特卡洛 2000 次 → 1/0 期望区分 bit

## 关键 payload

```
POST /cgi-bin/.%2e/.%2e/.%2e/.%2e/.%2e/.%2e/.%2e/.%2e/bin/sh HTTP/1.1
```

## 经验教训

/cgi-bin/.%2e/ 路径穿越是 HTTPD 经典 CVE（CVE-2021-41773/CVE-2021-42013 同款），打 Apache httpd 时要记得试；Java EL 盲注用 `contains` 逐字符爆破比 time-based 快；洗牌密码用蒙特卡洛多次实验取期望差分判断 bit 是统计侧信道套路。

## 标签

gif 帧分离 rot13、钓鱼邮件 base64、冰蝎 e45e329feb5d925b 默认密钥、zip CRC 32 明文攻击、sqlite 索引解析、/cgi-bin/..%2e.. 路径穿越、MongoDB $toString、javax.script.ScriptEngineManager JS eval、XXE php://filter base64、z3 符号执行逆向、栈溢出 0x38 p64 backdoor、洗牌 instance m n 期望区分

## 参考来源

- https://www.ctfiot.com/179730.html
- 原文件：2024年首届高校网络安全管理运维赛Writeup.full.md
