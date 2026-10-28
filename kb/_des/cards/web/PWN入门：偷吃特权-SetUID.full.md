---
title: "PWN入门 - 偷吃特权 SetUID"
category: web
tags: ["看雪论坛 ctfiot 系列", "web", "pwn", "教程", "setuid", "linux-kernel"]
signals: ["看雪论坛 ctfiot 系列 2024", "pwn", "教程", "setuid", "linux-kernel", "cred", "inode", "S_ISUID", "命令注入", "auth_bypass", "Linux", "VFS", "SetUID", "struct"]
difficulty: medium
source: "https://www.ctfiot.com/219247.html"
tools: []
origin: des-import
origin_kind: cards
updated: 2026-10-24
---
# PWN入门 - 偷吃特权 SetUID

> 赛事：看雪论坛 ctfiot 系列 2024 | 方向：web | 难度：medium

## 一句话总结

从 Linux VFS/inode/cred 结构体内核视角看 SetUID 工作机制，配合漏洞示例演示 setuid 提权 + 命令注入实战。

## 攻击链

1. struct cred 含 uid/gid/suid/sgid/euid/egid/fsuid/fsgid 8 个 ID
2. ls -lh 看 s 位 (rwsr-xr-x) 标识 SetUID 程序
3. do_new_mount → fs_context_for_mount → alloc_fs_context → fs_context->cred
4. sb->s_flags SB_NOSUID = 1 时忽略 suid 位
5. do_execve → do_execveat_common → bprm_execve → prepare_bprm_creds
6. prepare_creds 拷贝 current->cred 作 new
7. search_binary_handler → load_elf_binary → bprm_fill_uid
8. mode & S_ISUID 触发 bprm->cred->euid = uid (i_uid_into_mnt)
9. security_bprm_creds_from_file → cap_bprm_creds_from_file 设 suid/fsuid = euid
10. begin_new_exec → commit_creds 生效
11. 示例程序 vuln_by_user_input: snprintf echo %s → system 注入
12. 注入 "233333 ; /bin/sh" 或 "233333 && /bin/sh
13. vuln_by_permission_leak: open private_data.bin (root 600) 拿 fd
14. 利用 setuid 拿到的 euid=root 写 0x3 (CCCCC)

## 关键 payload

```
./set_uid_example "233333 ; /bin/sh" → root shell
```

## 经验教训

SetUID 加载时把 euid 改成文件属主 uid；snprintf + system 拼接用户输入是经典命令注入；fd 已 open 的文件即使 setuid 失效后仍可写。

## 标签

pwn、教程、setuid、linux-kernel、cred、inode、S_ISUID、命令注入

## 参考来源

- https://www.ctfiot.com/219247.html
- 原文件：PWN入门：偷吃特权-SetUID.full.md
