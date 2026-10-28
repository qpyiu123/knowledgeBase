---
title: "ACTF Writeup by SU"
category: web
tags: ["ACTF", "web", "Shellshock BASH_FUNC_env", "cgi-bin/hello", "WebSocket prototype pollution", "JSON.stringify劫持"]
signals: ["ACTF 2022", "Shellshock BASH_FUNC_env", "cgi-bin/hello", "WebSocket prototype pollution", "JSON.stringify劫持", "hook onanimationstart", "XSS webhook exfil", "TLS-poison client-hello", "vsFTPd 3.0.3蜜罐", "web_unknown", "ACTF", "Shellshock", "BASH_FUNC_env", "WebSocket"]
difficulty: hard
source: "https://www.ctfiot.com/46685.html"
tools: []
origin: des-import
origin_kind: cards
updated: 2026-10-24
---
# ACTF Writeup by SU

> 赛事：ACTF 2022 | 方向：web | 难度：hard

## 一句话总结

ACTF by SU — Shellshock BASH_FUNC_env + WebSocket prototype pollution XSS + JSON.stringify/parse hook exfil + TLS-poison + vsFTPd 蜜罐 + MySQL LOAD DATA LOCAL。

## 攻击链

1. Shellshock: BASH_FUNC_env%%=(None, "() { cat /flag; exit; }") POST /cgi-bin/hello 触发
2. WebSocket XSS: sendmsg ''image'' type + onanimationstart=eval(atob(...)) + animation: ''1s App-logo-spin
3. JSON.stringify hook: 备份原 JSON.stringify, 调用时改为 {api:''getflag''}
4. JSON.parse hook: 备份原 JSON.parse, 调用时 send(str) → webhook exfil
5. TLS-poison: client-hello-poisoning 注入到 SNI 后的 32 字节
6. vsFTPd 3.0.3 蜜罐: 监听 2048, USER/PASS 接受, CWD secret_path 验证
7. 227 Passive Mode (127,0,0.1,43,192) 引到 mysql://127.0.0.1:11200
8. MySQL LOAD DATA LOCAL: 触发 mysql 客户端读 /flag

## 关键 payload

```
BASH_FUNC_env Shellshock / JSON.stringify + JSON.parse hook exfil / TLS-poison 32字节注入 / vsFTPd 蜜罐 + MySQL LOAD DATA LOCAL
```

## 经验教训

Shellshock 用 BASH_FUNC_env%% 函数导出名做 RCE;JSON.stringify/parse 钩子是 Web 前端 exfil 经典;TLS-poison 利用 SNI 后字节注入;vsFTPd PASV 模式可引到 MySQL 触发 LOAD DATA LOCAL 任意文件读。

## 标签

Shellshock BASH_FUNC_env、cgi-bin/hello、WebSocket prototype pollution、JSON.stringify劫持、hook onanimationstart、XSS webhook exfil、TLS-poison client-hello、vsFTPd 3.0.3蜜罐、MySQL LOAD DATA LOCAL、file:// 协议、JSON.parse hook exfil

## 参考来源

- https://www.ctfiot.com/46685.html
- 原文件：ACTF_Writeup_by_SU.full.md
