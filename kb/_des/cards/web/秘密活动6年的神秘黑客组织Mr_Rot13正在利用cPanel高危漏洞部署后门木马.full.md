---
title: "秘密活动6年的神秘黑客组织Mr_Rot13正在利用cPanel高危漏洞部署后门木马"
category: web
tags: ["威胁情报", "web", "APT分析", "Mr_Rot13", "cPanel漏洞", "后门植入"]
signals: ["威胁情报 2025", "APT分析", "Mr_Rot13", "cPanel漏洞", "后门植入", "改root密码", "SSH公钥注入", "PHP Webshell", "JS注入", "file_upload", "APT", "cPanel", "SSH", "PHP"]
difficulty: medium
source: "https://www.ctfiot.com/307724.html"
tools: ["PHP", "Python", "wget"]
origin: des-import
origin_kind: cards
updated: 2026-10-24
---
# 秘密活动6年的神秘黑客组织Mr_Rot13正在利用cPanel高危漏洞部署后门木马

> 赛事：威胁情报 2025 | 方向：web | 难度：medium | 工具：PHP、Python、wget

## 一句话总结

Mr_Rot13 APT分析：cPanel漏洞利用全链路（改密码/SSH公钥/PHP Webshell/JS注入/Filemanager远控/Telegram C2）

## 攻击链

1. wget/curl下载Update ELF→chmod 755→nohup执行→删除自身→main_changeRootPassword改root密码→main_installSSHKey注入ssh-ed25519公钥→main_installCpanelPy植入PHP Webshell→main_injectLoginPage注入JS到cpanel登录页→main_runWpsockInstaller部署Filemanager远控→main_postData回传C2→main_sendTelegram回传Telegram

## 关键 payload

```
F=/root/.u$$ ELF下载执行;root:123Qwe123C;ssh-ed25519 cpanel-updater;cpanel.py PHP Webshell;login.js JS注入;Filemanager远控;Telegram bot 1190043163:AAEy1FDoB_r8KFiOIqsEpgDQ2k78Ai6BdWk
```

## 经验教训

APT攻击链分析：ELF后门自删除+多后门植入+多C2通道（Telegram+HTTP）

## 标签

APT分析、Mr_Rot13、cPanel漏洞、后门植入、改root密码、SSH公钥注入、PHP Webshell、JS注入、Filemanager远控、Telegram C2

## 参考来源

- https://www.ctfiot.com/307724.html
- 原文件：秘密活动6年的神秘黑客组织Mr_Rot13正在利用cPanel高危漏洞部署后门木马.full.md
