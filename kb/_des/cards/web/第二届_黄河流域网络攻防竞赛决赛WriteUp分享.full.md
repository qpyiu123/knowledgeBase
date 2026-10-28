---
title: "第二届黄河流域网络攻防竞赛决赛WriteUp分享"
category: web
tags: ["黄河流域网络攻防竞赛决赛", "web", "AWDP赛制", "Web-SSRF", "Gopher", "SQL注入"]
signals: ["黄河流域网络攻防竞赛决赛 2024", "AWDP赛制", "Web-SSRF", "Gopher", "SQL注入", "RCE", "Flask", "SSTI", "SSTI-WAF绕", "ssrf", "AWDP", "WEB", "PWN", "SSRF"]
difficulty: medium
source: "https://www.ctfiot.com/195732.html"
tools: ["Flask"]
origin: des-import
origin_kind: cards
updated: 2026-10-24
---
# 第二届黄河流域网络攻防竞赛决赛WriteUp分享

> 赛事：黄河流域网络攻防竞赛决赛 2024 | 方向：web | 难度：medium | 工具：Flask

## 一句话总结

AWDP赛制7题(WEB×4+PWN×3),核心链为SSRF+gopher+SQL注入+302跳转三层跳板打backup exec实现RCE,Flask密码爆破+SSTI,sign签名md5算法控制role+php://filter iconv爆破,Redis RESP+Pickle+SSTI三件套

## 攻击链

1. sitemap: SSRF(getPageInfoFromUrl)+SQL注入(batchDelete)→UPDATE pages SET url=gopher+302跳转(click)→打ApiContronller.php/backup exec→unzip-command参数RCE|简单的渗透: Flask Login类爆破password+admin header admingivemeflag+eval RCE|重生之我要上清华北大: 抓包修改注册时间绕过+sign md5签名算法控制role+php://filter charset爆破+include读取|重生之我要当最强管理员: 任意文件读取+Redis RESP协议pickle序列化+SSTI description字段RCE|account: tcache_struct+environ泄露栈+ORW_rop|alarm/fmt/just_a_heap

## 关键 payload

```
gopher://127.0.0.1:80/_POST%20/api.php%3Faction%3Dbackup%20HTTP/1.1...%7B%22path%22%3A%22%20-T%20--unzip-command%3D%27sh%20-c%20cat%3C/flag%7Ctee%3Eflag%27%22%7D|admingivemeflag{os.popen("cat /flag").read()}|http://IP/admin.php?file=php://filter/convert.iconv.UTF8.CSISO2022KR|...|序列化Redis SET user:xxxxxxxxxx base64(pickle.dumps({'passw0rd':'expexp','r0le':'adm1n'}))
```

## 经验教训

1) SSRF打本机需绕gopher协议黑名单→SQL注入写入DB→click() 302跳板链; 2) Flask password短比较+结果可爆破(62^36空间过大但results[0:short]逐位可爆); 3) sign签名要包含role字段,可逆向JS或动态生成伪造admin; 4) php://filter convert.iconv串可逐层降维/升维清空字符,UTF8→CSISO2022KR是经典起手式; 5) 任意文件读取+Redis RESP+Pickle组合:SSTI通过模板author字段触发__globals__.__builtins__.__import__('os').popen; 6) 禁用execve的PWN用environ泄露栈地址+改返回地址为orw_rop

## 标签

AWDP赛制、Web-SSRF、Gopher、SQL注入、RCE、Flask、SSTI、SSTI-WAF绕、PHP反序列化、Pickle、Redis、响应包、Sign越权、php://filter、反序列化、Pwn-ORW、Pwn-UAF

## 参考来源

- https://www.ctfiot.com/195732.html
- 原文件：第二届_黄河流域网络攻防竞赛决赛WriteUp分享.full.md
