---
title: "香港網安奪旗賽HKCERT CTF 2024 Write up（上）"
category: web
tags: ["HKCERT CTF 2024", "web", "Flask", "yaml-deserialize", "js-yaml", "js/function"]
signals: ["HKCERT CTF 2024 2024", "Flask", "yaml-deserialize", "js-yaml", "js/function", "rce", "pyodide", "sandbox-escape", "pdfkit-rce", "crypto_hash", "HKCERT", "PDF", "JSPyaml", "Web"]
difficulty: medium
source: "https://www.ctfiot.com/216353.html"
tools: ["Flask", "PHP"]
origin: des-import
origin_kind: cards
updated: 2026-10-24
---
# 香港網安奪旗賽HKCERT CTF 2024 Write up（上）

> 赛事：HKCERT CTF 2024 2024 | 方向：web | 难度：medium | 工具：Flask、PHP

## 一句话总结

HKCERT 2024上篇覆盖Flask+PDF生成器+自定义C服务端+JSPyaml+奇美拉五道Web+两道Misc+Forensics的混合WP，亮点在pyodide+js-yaml-js-types的客户端沙箱逃逸。

## 攻击链

1. 审计GroupAPI + compute_hash构造sha256爆破admin密码7df71e
2. flask /process使用wkhtmltopdf拼接命令+session_id可控触发命令注入
3. PDF生成器通过meta tag注入pdfkit---enable-local-file-access开启本地文件读取
4. 自定义C socket服务端read_file以read+真实路径拼接+ends_with白名单+目录穿越/../../读flag
5. Custom-server-2利用SSL TCP多请求Content-Length错位+多次GET路径穿越
6. /debug路由用js-yaml schema扩展支持js/function+pyodide客户端exec触发RCE
7. pyodide.code.run_js注入cookie debug=on绕过isLoopback+JSPyaml用YAML重定向到exec
8. PHP CitrusWorkspace create软链+symlink遍历+任意文件写入Webshell

## 关键 payload

```
GET /../../../../../../../flag.txt.js
```

## 经验教训

现代Web常把yaml.load+扩展schema(js/function)+pyodide+pyodide.code.run_js当作"安全沙箱"组合,但任一环节被攻破即RCE;PDF生成器类的LFI应同时检查meta tag和命令行参数。

## 标签

Flask、yaml-deserialize、js-yaml、js/function、rce、pyodide、sandbox-escape、pdfkit-rce、lfi、path-traversal、custom-server、ssl

## 参考来源

- https://www.ctfiot.com/216353.html
- 原文件：香港網安奪旗賽HKCERT_CTF_2024_Write_up（上）.full.md
