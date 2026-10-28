---
title: "赏金猎人:IChunQiu云境-Spoofing Writeup"
category: web
tags: ["IChunQiu云境-Spoofing", "web", "GhostCat", "CNVD-2020-10487", "Tomcat-AJP", "MS17-010"]
signals: ["IChunQiu云境-Spoofing 2022", "GhostCat", "CNVD-2020-10487", "Tomcat-AJP", "MS17-010", "WebClient-Coerce", "PetitPotam", "NTLM-relay", "RBCD", "web_unknown", "IChunQiu", "Spoofing", "Tomcat", "web"]
difficulty: hard
source: "https://www.ctfiot.com/89262.html"
tools: ["John"]
origin: des-import
origin_kind: cards
updated: 2026-10-24
---
# 赏金猎人:IChunQiu云境-Spoofing Writeup

> 赛事：IChunQiu云境-Spoofing 2022 | 方向：web | 难度：hard | 工具：John

## 一句话总结

IChunQiu云境Spoofing赏金猎人WP,Tomcat GhostCat读web.xml+MS17-010内网打域+PetitPotam+WebClient NTLM中继+RBCD攻击+nopac域提权,完整内网渗透链。

## 攻击链

1. Nmap发现8009 AJP端口,Tomcat 9.0.30,使用GhostCat (CNVD-2020-10487) 读/web-inf/web.xml
2. 字典爆破servlet路径找到uploadservlet,上传temp.txt
3. ajpShooter替换./upload为/upload,读上传文件
4. 上传JSP shell,执行ssh-rsa公钥注入/root/.ssh/authorized_keys
5. chomod 600 + SSH flag01
6. 入口Ubuntu 172.22.11.76,挂代理扫445发现3台主机
7. XR-Desktop 172.22.11.45 (Windows7) MS17-010利用+提权
8. 本地凭据:Administrator/John,域凭据:yangmei
9. 不能直接拿域控(xiaorang-dc 172.22.11.6):MAQ=0无法addcomputer,无LDAPS
10. 域内有nopac但对XR-Desktop无WriteDacl无法改SamAccountName
11. 无CVE-2019-1040,改用PetitPotam + WebClient NTLM中继
12. 目标:XR-LCM3AE8B 172.22.11.26 (开启WebClient)
13. socat+SSH反向端口转发让80监听0.0.0.0
14. ntlmrelayx -t ldap://DC --escalate-user 'xr-desktop$' --delegate-access
15. PetitPotam触发XR-LCM3AE8B认证→RBCD攻击
16. 申请XR-LCM3AE8B CIFS银票+psexec拿flag03
17. mimikatz获取zhanghui 1232126b24cdf8c9bd2f788a9d7c7ed1 (MA_Admin组)
18. zhanghui + nopac create-child申请CIFS票据登录DC
19. flag04+域管administrator 0fadb57f5ec71437d1b03eea2cda70b9

## 关键 payload

```
CNVD-2020-10487 + PetitPotam + RBCD + nopac
```

## 经验教训

Tomcat AJP GhostCat (CNVD-2020-10487) 是稳定的web入口;PetitPotam+WebClient+NTLM中继是AD域渗透的稳定攻击链;RBCD + nopac是2022-2024 AD提权标配;BloodHound采集需注意CreateChild等ACL。

## 标签

GhostCat、CNVD-2020-10487、Tomcat-AJP、MS17-010、WebClient-Coerce、PetitPotam、NTLM-relay、RBCD、noPac、AD-pentest、BloodHound

## 参考来源

- https://www.ctfiot.com/89262.html
- 原文件：赏金猎人-IChunQiu云境-Spoofing_Writeup.full.md
