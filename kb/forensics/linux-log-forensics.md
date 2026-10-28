---
title: Linux 日志取证（syslog / SSH / undo 文件）
category: forensics
tags: [linux, auth.log, syslog, ssh, undo文件, bash_history]
signals: [附件是 var log 目录, 题目问谁 ssh 登录了, 需要还原 vim 编辑内容, 需要看 cron 任务, 日志被清空, 需要看 systemd 单元]
difficulty: easy
source: "Ubuntu/Debian auth.log 格式 / Vim undo 文件文档 / systemd journalctl 手册"
tools: [grep, journalctl, last, faillog, strings, vim, logcat, ausearch]
updated: 2026-10-22
---

## 一、识别信号（题面长什么样）

- 附件是 `auth.log`、`secure`、`syslog`、`messages`、`access.log` 等纯文本日志。
- 题目问「谁在什么时间登录成功」「攻击者从哪个 IP 爆破」。
- 附件里有 `.viminfo`、`.filename.swp`、`.filename.un~` 之类的隐藏文件。
- 题目说「服务器被入侵，找入侵痕迹」。
- 需要从 `.bash_history` 或 `/var/log/` 里找出执行的命令。

## 二、原理

Linux 日志是**纯文本 + 固定格式**，`syslog` 格式为：

```
<时间戳> <主机名> <程序>[<PID>]: <消息>
2026-03-01T10:00:00.123456+08:00 web01 sshd[1234]: Accepted password for root from 10.0.0.5 port 52222 ssh2
```

关键日志文件（Debian/Ubuntu）：

| 文件 | 内容 |
| --- | --- |
| `/var/log/auth.log` | SSH 登录、sudo、su（RHEL 系是 `/var/log/secure`） |
| `/var/log/syslog` / `messages` | 所有 syslog 事件 |
| `/var/log/cron` | 定时任务执行 |
| `/var/log/wtmp`、`/var/log/btmp` | 登录/失败记录（二进制，用 `last`/`lastb`） |
| `/var/log/lastlog` | 每个用户最后登录 |
| `/var/log/apt/history.log` | 安装记录 |

**Vim 的三件套**：
- `.file.swp`：交换文件，保存**未保存的缓冲区**（崩溃后 `vim -r file` 可恢复）。
- `.file.un~`：**undo 文件**，保存编辑历史（`vim -u NONE -c 'undofile 1' file` 后 `u` 可逐步回退）。
- `.viminfo`：光标位置、搜索历史、寄存器。

## 三、操作步骤

1. **确定日志时间范围**：`head/tail` 看首尾，注意时区后缀。
2. **grep 关键事件**：`Accepted password`、`Failed password`、`sudo:`、`session opened`。
3. **按 IP 聚合**：统计爆破源 IP 与其尝试次数。
4. **恢复编辑器痕迹**：找 `.swp`/`.un~`/`.viminfo`，用 vim 恢复。
5. **查执行命令**：`.bash_history`、`/proc` 残留、`cron` 日志。
6. **看持久化**：`/etc/crontab`、`systemd` 单元、`/etc/rc.local`、SSH `authorized_keys`。

## 四、命令/脚本

### SSH 登录分析

```bash
grep 'Accepted password' /var/log/auth.log | tail -20
grep -oE 'from [0-9.]+' auth.log | awk '{print $2}' | sort | uniq -c | sort -rn | head
grep 'Failed password' auth.log | grep -oE 'from [0-9.]+' | sort | uniq -c | sort -rn | head -5
# 成功登录的时间线（含用户名与源 IP）
grep 'Accepted' auth.log | awk '{print $1,$2,$3,$9,$11}'
# 爆破节奏：同一 IP 每分钟失败次数
grep 'Failed password' auth.log | awk '{print substr($3,1,5)}' | uniq -c | sort -rn | head
# 提权
grep -E 'sudo:|su: session' auth.log | tail -20
# 新建用户/改密码
grep -E 'useradd|usermod|passwd' auth.log
```

### 二进制日志（wtmp/btmp）

```bash
last -f wtmp -a | head -20          # 登录历史（含来源 IP）
lastb -f btmp | head -20            # 失败记录
lastlog -b 0                         # 每用户最后登录
who -a /var/log/wtmp
utmpdump /var/log/wtmp | head       # 原始字段
```

### systemd/journald

```bash
journalctl --file system.journal -o short-iso | head -20
journalctl --file system.journal -u ssh -S '2026-03-01 00:00:00' | head
journalctl --file system.journal PRIORITY=3           # 只看错误
journalctl --file system.journal _COMM=sudo
journalctl --file system.journal --since '1 hour ago' -g flag   # 关键字
```

### Vim 交换/undo 文件恢复

```bash
ls -la ~/.vim/swap ~/.vim/undo 2>/dev/null
# 方式 1：打开文件时自动提示 "Swap file found"，选 R 进恢复，再 :w 另存
vim -r /path/to/flag.txt
# 方式 2：直接读 swap 里的字符串（swap 是内存镜像，明文在）
strings -n 6 .flag.txt.swp | head -40
# 方式 3：undo 文件（二进制树结构），用 vim 打开原文件后不断按 u 回退
vim -u NONE -c 'set undofile' -c 'set undodir=.' flag.txt
#   进入后 :earlier 10s / :earlier 5f 逐级回退，直到出现原始内容
```

```python
#!/usr/bin/env python3
# viminfo_parse.py —— 从 .viminfo 里提取搜索历史与寄存器
import re
data = open('.viminfo', 'rb').read().decode('latin1')
for tag, name in [('~', '搜索模式'), ('"', '寄存器命名'), ('/','搜索历史')]:
    pass
# .viminfo 是文本格式，但编码混杂；直接按 # 段落切
sections = re.split(r'\n#([^\n]*)\n', data)
for i in range(1, len(sections) - 1, 2):
    title, body = sections[i], sections[i+1]
    if any(k in title.lower() for k in ('search', 'register', 'command-line')):
        print('===', title)
        print('\n'.join(l for l in body.splitlines()[:40] if l.strip()))
```

### bash_history 与执行痕迹

```bash
cat ~/.bash_history; cat /root/.bash_history
# 带时间戳（若 HISTTIMEFORMAT 已设置）
grep -B1 -a 'flag' ~/.bash_history
# 其他 shell
ls -la ~/.zsh_history ~/.local/share/fish/fish_history 2>/dev/null
# 进程回收站/临时文件
ls -la /tmp /var/tmp; find / -name '*.swp' 2>/dev/null | head
# 反连/下载痕迹
grep -riE 'wget|curl|nc -e|bash -i|/dev/tcp' ~/.bash_history /var/log/
```

### 常见入侵痕迹清单

```bash
cat /etc/crontab; ls -la /etc/cron.*; crontab -l
systemctl list-units --type=service --state=running | head -30
cat /etc/passwd | grep -E 'sh$'
cat ~/.ssh/authorized_keys; ls -la /root/.ssh
ls -la /etc/rc.local /etc/init.d/
grep -i 'Failed' /var/log/auth.log | wc -l
cat /etc/os-release; uname -a
```

## 五、常见坑 / 变体

- **时区**：`auth.log` 常见 UTC 或本地时间（`+08:00`），与题面时间要换算。
- **日志轮转**：`auth.log.1`、`.gz` 压缩包也要看：`zgrep 'Accepted' auth.log.*.gz`。
- **日志被清**：用户 `.bash_history` 清空后，还有 `/proc/<pid>/environ`（内存中）；`journalctl` 里有 `_COMM=rm` 记录。
- **wtmp 被篡改**：`utmpdump` 前后对照，或看文件 mtime。
- **swap 是二进制**：`strings` 读不全，vim `-r` 恢复最靠稳。
- **undo 文件格式**：`un~` 是内部树结构，不能直接文本读，必须 vim 加载。
- **容器/云主机**：日志可能在 `/var/log/syslog` 里但 `auth.log` 缺失（systemd-journald 接管），优先 `journalctl`。

## 六、参考来源

- [rsyslog 文档（syslog 消息格式与模板）](https://www.rsyslog.com/doc/index.html)
- [Vim 帮助 - swapfile（恢复机制）](https://vimhelp.org/recover.txt.html)
- [Vim 帮助 - undo 持久化](https://vimhelp.org/undo.txt.html)
- [systemd journalctl 手册](https://www.freedesktop.org/software/systemd/man/journalctl.html)
- [Linux `last`/`wtmp` 手册](https://man7.org/linux/man-pages/man1/last.1.html)
- [CTF Wiki - 取证隐写前置技术](https://ctf-wiki.org/misc/prefix/)
