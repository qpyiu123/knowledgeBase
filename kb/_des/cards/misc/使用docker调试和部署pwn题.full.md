---
title: "使用docker调试和部署pwn题"
category: misc
tags: ["Docker PWN 调试部署", "misc", "Dockerfile", "ubuntu", "pwndbg", "gef"]
signals: ["Docker PWN 调试部署 2024", "Dockerfile", "ubuntu", "pwndbg", "gef", "pwntools", "pwncli", "one_gadget", "seccomp-tools", "misc_unknown", "Docker", "PWN", "xinetd", "socat"]
difficulty: easy
source: "https://www.ctfiot.com/154995.html"
tools: ["GDB", "Python", "Z3", "pwntools"]
origin: des-import
origin_kind: cards
updated: 2026-10-24
---
# 使用docker调试和部署pwn题

> 赛事：Docker PWN 调试部署 2024 | 方向：misc | 难度：easy | 工具：GDB、Python、Z3、pwntools

## 一句话总结

Docker 调试部署 PWN 题标准模板：ubuntu + pwndbg/gef + pwntools + one_gadget + seccomp-tools + xinetd/socat。

## 攻击链

1. 调试环境: docker run -it --rm -v host:container -p port --cap-add=SYS_PTRACE IMAGE
2. --cap-add=SYS_PTRACE 允许 gdb 附加进程
3. --privileged 给全部权限 (绕过 seccomp/apparmor)
4. 完整 Dockerfile: ubuntu + python3+pwntools+pwncli + gdb+pwndbg+gef+Pwngdb
5. apt install: xinetd gdb gdbserver gcc ruby gem one_gadget seccomp-tools
6. gem install one_gadget + gem install seccomp-tools
7. pip3 install pwntools pwncli ropper capstone z3-solver qiling lief
8. 创建 ctf 普通用户 NOPASSWD ALL sudo
9. oh-my-zsh + zsh-syntax-highlighting + zsh-autosuggestions
10. 出题模板: xinetd (传统) 或 socat (新式)
11. update.sh: apt install + pwntools + gef 一键安装

## 关键 payload

```
docker run -it --rm --cap-add=SYS_PTRACE IMAGE + xinetd/socat 出题
```

## 经验教训

--cap-add=SYS_PTRACE 必备让 gdb 附加；--privileged 给全部权限 (绕过 docker seccomp) 才能 seccomp-tools dump；出题用 socat 比 xinetd 更现代。

## 标签

Dockerfile、ubuntu、pwndbg、gef、pwntools、pwncli、one_gadget、seccomp-tools、xinetd、socat、SYS_PTRACE、--privileged

## 参考来源

- https://www.ctfiot.com/154995.html
- 原文件：使用docker调试和部署pwn题.full.md
