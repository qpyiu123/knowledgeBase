---
title: "TJCTF 2024 Writeups"
category: web
tags: ["TJCTF", "web", "ssrf-localhost", "jwt-jku", "file-upload", "jinja-ssti"]
signals: ["TJCTF 2024", "ssrf-localhost", "jwt-jku", "file-upload", "jinja-ssti", "race-condition", "websocket-spoof", "web_unknown", "TJCTF", "Web", "Reverse", "Forensics", "JWT", "jku"]
difficulty: medium
source: "https://www.ctfiot.com/182723.html"
tools: ["Flask"]
origin: des-import
origin_kind: cards
updated: 2026-10-24
---
# TJCTF 2024 Writeups

> 赛事：TJCTF 2024 | 方向：web | 难度：medium | 工具：Flask

## 一句话总结

TJCTF 2024 多类 (Web/Reverse/Forensics)：JWT jku 路径穿越 + Flask SSTI + WebSocket 抢答。

## 攻击链

1. 1.monitor: 路由 /secret-frogger-78570618/ 拿到提示
2. app.route("/monitor") 检查 request.remote_addr in ('localhost', '127.0.0.1')
3. 2. 路由 /flag: req.ip !== ''::ffff:127.0.0.1'' && req.ip !== ''::1'' && req.ip !== ''127.0.0.1'' 校验
4. /fetch 路由：URL 校验 https?:// 但 host.includes('localhost') 拒
5. 但用 0.0.0.0 / 127.0.0.1 IP 形式 bypass
6. 3. jinja SSTI：add_template_key 设 key=value 改 template_keys 字典
7. /template POST 模板字符串 → re 匹配 {{key}} → 替换
8. flag 字符串禁止 (403)，但 ssti 可以从 class chain 拿
9. 4. JWT jku：verify_token 读 header.jku 路径 static/{jku}
10. 路径穿越 static/../uploads/<uuid>/<file>
11. 上传 jwk 格式公钥 + 生成 EC 私钥签名 token
12. 5. playlist: render_template_string username 拼到 playlist.html
13. 文件名 uuid 写盘 → /view_playlist/<uuid>.html 触发 SSTI
14. 6. Kaboom websocket: 抢答类游戏 send_time >= time 检查绕过
15. i==0 时 edit_score(0) 重置; 然后用 user2/user1 交替得 1000 分

## 关键 payload

```
jwt.encode + jku=''../uploads/<uuid>/<file>''  # 路径穿越 jku
```

## 经验教训

JWT jku 字段直接拼到文件系统路径时，../ 序列允许加载攻击者控制的公钥 → 签名伪造。

## 标签

ssrf-localhost、jwt-jku、file-upload、jinja-ssti、race-condition、websocket-spoof

## 参考来源

- https://www.ctfiot.com/182723.html
- 原文件：TJCTF_2024_Writeups.full.md
