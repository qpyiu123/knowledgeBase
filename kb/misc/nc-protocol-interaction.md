---
title: 非 HTTP 协议交互 misc（nc 脚本、Telnet/SSH/SMTP 手工对话）
category: misc
tags: [nc, telnet, ssh, smtp, pwntools, protocol]
signals: [题目给了 nc 地址和端口而不是 http 链接, 连上去是一个菜单式的文字界面要求选 1-5, 协议返回 220 开头或者 SSH-2.0- 开头的横幅, 服务端要求输入密码但没有任何提示词, 交互里带中文字符串需要处理编码, 每一轮有时间限制或者连接会在 30 秒后断开, 题目说这是不是 web 题别用浏览器]
difficulty: medium
source: "RFC 854 Telnet / RFC 5321 SMTP / RFC 4253 SSH 传输层 / pwntools 文档"
tools: [nc, socat, pwntools, ssh, telnet, openssl]
updated: 2026-10-22
exec_yaml: ok
---

## 一、识别信号（题面长什么样）

- 题面给的是 `nc TARGET 31337` / `TARGET:9999`，纯 TCP，没有 `http://`。
- 连上去第一行就是 `220 mail.example.com ESMTP`、`SSH-2.0-OpenSSH_9.6p1`、`Trying 10.0.0.1...` 这种**协议横幅**。
- 是一个数字菜单：`[1] 查询 [2] 登录 [3] 反馈`，需要按序号交互。
- 服务端直接给 `password: ` 却没有用户名提示，或者需要用 ANSI 转义控制光标。
- 交互里有中文，`pwntools` 直接 `decode()` 会报 `UnicodeDecodeError`。
- 每次连接只能存活几十秒，拖久了被 RST。
- 题目明确说"不要用浏览器打开"。

## 二、原理

- **这些题本质是"自定义应用层协议"**：服务端把状态机放在 TCP 流里，你需要精确对应每一步的 `send`/`recv`。
- **三种典型**：
  1. 纯文本菜单式（自己写的协议）：状态依赖前一步输入，脚本要 `recvuntil` 到稳定的提示符。
  2. 标准协议（SMTP/IMAP/POP3/FTP/Telnet/SSH）：按 RFC 发命令行，多用 `telnet`/`openssl s_client` 手工验证。
  3. 二进制协议（长度前缀 + 类型）：`struct` 打包，注意字节序。
- **超时与断连**：服务端常有 `alarm()` 或线程超时，脚本必须"少往返、快决策"，本地把决策算好再发。
- **编码**：中文菜单一般是 UTF-8；老题可能是 GBK，`pwntools` 需 `context.encoding='gbk'`。

## 三、操作步骤

1. **手工摸协议**：`nc -v TARGET PORT` 或 `socat - TCP:TARGET:PORT`，把前几轮交互原样贴下来。
2. **确认分隔符**：提示符末尾有没有空格/冒号、换行是 `\n` 还是 `\r\n`——`recvuntil` 必须精确。
3. **写脚本**：`remote()` + `recvuntil` + `sendline`，每一步都 `log.info` 打印。
4. **状态无关化**：让脚本自己解析服务端返回的参数并本地计算，不要硬编码答案。
5. **加速**：`context.log_level='error'`、关闭 `pause`，批量跑时用 `threading` 并发。
6. **结果落盘**：`recvall()` 或逐步 `recvline` 写文件，便于复盘。

## 四、命令 / 脚本

```bash
# 手工连
nc -v TARGET 31337
socat - TCP:TARGET:31337,crlf
# 带超时
timeout 10 nc TARGET 31337 < /dev/null | xxd | head
# SMTP 手工对话
printf 'EHLO test\r\nMAIL FROM:<a@b>\r\nRCPT TO:<c@d>\r\nDATA\r\nhello\r\n.\r\nQUIT\r\n' \
  | nc TARGET 25
# IMAP / POP3（TLS）
openssl s_client -connect TARGET:993 -quiet
# Telnet（老设备/老题）
telnet TARGET 23
# SSH 题有没有弱口令
ssh -o PreferredAuthentications=password -o PubkeyAuthentication=no user@TARGET
```

```python
#!/usr/bin/env python3
# 通用菜单式协议脚本骨架
from pwn import remote, context, log
context.log_level = 'info'
context.encoding = 'utf-8'

def solve(host='TARGET', port=31337):
    io = remote(host, port)
    io.recvuntil(b'> ')                      # 与手工观察到的提示符一致
    io.sendline(b'1')
    data = io.recvuntil(b'> ')
    log.info(data.decode(errors='replace'))
    # 解析服务端给的数据，本地算答案
    token = data.split(b':')[-1].strip()
    io.sendline(b'2')
    io.sendline(token)
    print(io.recvall(timeout=5).decode(errors='replace'))

if __name__ == '__main__':
    solve()
```

```python
#!/usr/bin/env python3
# 带长度前缀的二进制协议示例
import struct
from pwn import remote

def pkt(kind: int, payload: bytes) -> bytes:
    return struct.pack('<HI', kind, len(payload)) + payload

def talk():
    io = remote('TARGET', 4000)
    hello = io.recvn(6)
    assert hello[:2] == b'\xca\xfe', hello
    io.send(pkt(1, b'auth\x00guest'))
    resp = io.recvn(6)
    kind, ln = struct.unpack('<HI', resp)
    body = io.recvn(ln)
    print('kind=%d body=%r' % (kind, body))
    io.close()

if __name__ == '__main__':
    talk()
```

## 五、常见坑 / 变体

- **`recvuntil` 卡死**：提示符里有不可见字符（`\r`、`\x00`、ANSI 转义），用 `xxd` 看原始字节。
- **服务器用 `\r\n`**：`socat ...,crlf` 能自动转换；脚本里用 `sendline` 只发 `\n` 时可能对不上，需 `send(b'...\r\n')`。
- **交互题被限速**：服务端可能每轮 `sleep(0.5)`，脚本别加额外 sleep。
- **行缓冲**：有些服务端是 `readline`，你发的内容必须带换行才会被处理。
- **标准协议陷阱**：SMTP 用 CRLF，行首 `.` 要转成 `..`（dot-stuffing）；Telnet 有 IAC 协商字节 `FF FB 01`。
- **SSH 题**：常见是给用户名 + 提示"flag 在某个目录"，靠 `ssh -v` 看 banner 版本推漏洞；或者用 `ssh user@TARGET` 后 `cat`。
- **超时后重连策略**：记录已完成进度，重连从断点继续（服务端多半不支持，只能一次跑完）。
- **变体**：gopher（内网打 Redis）、Redis 原生协议 `RESP`、MQTT 的 CONNECT/SUBSCRIBE、WebSocket。

## 七、按协议速查表

| 协议 | 端口 | 冒烟命令 | 常见 CTF 考法 |
| --- | --- | --- | --- |
| 自定义菜单 | 任意 | `nc TARGET PORT` | 按序号交互，本地算答案 |
| SMTP | 25 / 587 | `EHLO x` → `MAIL FROM` | 伪造发件人、开放中继 |
| IMAP | 143 / 993 | `a1 LOGIN u p` → `a2 LIST "" *` | 读取指定邮箱附件 |
| POP3 | 110 / 995 | `USER u` / `PASS p` / `RETR 1` | 明文凭据、删除邮件残留 |
| FTP | 21 | `USER anonymous` | 匿名访问、被动模式 |
| Redis | 6379 | `PING` / `INFO` / `KEYS *` | 直接读写 key、写文件 |
| Memcached | 11211 | `stats` / `get key` | 无鉴权缓存投毒 |
| SSH | 22 | `ssh -vv user@TARGET` | banner 版本、口令爆破 |
| Telnet | 23 | `telnet TARGET` | 明文口令、IAC 协商 |
| MySQL | 3306 | `mysql -h TARGET -u root` | 弱口令、`LOAD_FILE` |

## 八、异常排查顺序

1. 连不上：`nc -vz TARGET PORT` 先确认端口通；`nmap -p PORT --reason TARGET` 看是 SYN 无响应还是 RST。
2. 能连但立刻断开：服务端可能在等特定首包（如伪装成 HTTP 的 `GET / HTTP/1.1`）。
3. 响应被截断：检查是否存在**长度前缀**或**以 `\x00` 结尾**的帧格式。
4. `recvuntil` 超时：把 `context.log_level='debug'` 打开，看实际收到的原始字节。
5. 脚本跑通了但答案错：服务端可能对同一 IP 有次数限制，导致你的第二遍跑已在错误状态。

## 六、参考来源

- [pwntools 官方文档（remote / recvuntil / context）](https://docs.pwntools.com/en/stable/)
- [RFC 5321：SMTP 协议规范](https://www.rfc-editor.org/rfc/rfc5321)
- [RFC 854：Telnet 协议（IAC 协商）](https://www.rfc-editor.org/rfc/rfc854)
- [RFC 4253：SSH 传输层协议（banner 与密钥交换）](https://www.rfc-editor.org/rfc/rfc4253)
- [socat 手册（crlf 转换与地址族）](https://man7.org/linux/man-pages/man1/socat.1.html)
