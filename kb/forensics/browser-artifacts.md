---
title: 浏览器取证（Chrome/Edge History、Cookies、下载与扩展）
category: forensics
tags: [browser, chrome, cookies, sqlite, history, downloads]
signals: [给了用户的 Chrome 或 Edge 用户配置目录, 附件里有 History Web Data Cookies 这些没有扩展名的文件, 题目问用户最后访问的网站或者下载了什么, 要求还原被删除的浏览记录, Cookies 里加密的 value 以 v10 开头, 题目给了 Local State 文件和一个 encrypted_key, 找某个用户的登录邮箱或者用户名]
difficulty: medium
source: "Foxton Forensics 浏览器取证文档 / Chromium 源码 docs / Chrome 密码解密公开研究"
tools: [python, sqlite3, db-browser-for-sqlite, chrome-password-decrypt-ng, exiftool]
updated: 2026-10-22
exec_yaml: ok
---

## 一、识别信号（题面长什么样）

- 附件解压后目录形如 `Users/xxx/AppData/Local/Google/Chrome/User Data/Default/`。
- 目录下有 `History`、`Web Data`、`Login Data`、`Cookies`、`Bookmarks`、`Preferences`、`Local State`——**这些文件都没扩展名**，`file` 判为 SQLite 3。
- 题目问"用户最后上传了什么文件""flag 藏在哪个网站的评论里"。
- `Cookies` 的 `encrypted_value` 以 `v10` 开头且是二进制，说明**系统级加密**（DPAPI / keyring）。
- 给了 `Local State`，里面有 `os_crypt.encrypted_key` 字段（base64 + `DPAPI` 前缀）。
- 题目要求"找出被删除的历史记录"，说明要打 freelist/WAL。

## 二、原理

**Chromium 系浏览器的取证面：**

| 文件 | 类型 | 关键表 | 能回答什么 |
| --- | --- | --- | --- |
| `History` | SQLite | `urls`、`visits`、`downloads`、`keyword_search_terms` | 访问了什么、几点访问、搜了什么词 |
| `Web Data` | SQLite | `autofill`、`keywords` | 填过的表单与搜索建议 |
| `Login Data` | SQLite | `logins` | 保存的站内账号、`origin_url`、`username_value`、加密口令 |
| `Cookies` | SQLite | `cookies` | `host_key`、`name`、`encrypted_value`、过期时间 |
| `Bookmarks` | JSON | — | 收藏夹内容 |
| `Preferences` | JSON | — | 默认搜索、下载目录、扩展列表 |
| `Local State` | JSON | `os_crypt` | 加密口令/ Cookie 的主密钥（被 DPAPI/keyring 包裹） |

- **时间戳是 WebKit/Chromium 纪元**：自 1601-01-01 UTC 起的**微秒**数（`visits.visit_time`），而 `downloads.start_time` 同样是微秒。换算：`unix = ts/1e6 - 11644473600`。
- **加密**：`v10` 表示 AES-256-GCM，密钥来自 `Local State` 的 `encrypted_key`（base64 后去掉 `DPAPI` 5 字节前缀，Windows 上再用 DPAPI 解包）；`v20` 是 Chrome 127+ 的 App-Bound 加密，密钥在浏览器进程内，离线几乎解不开。
- **删除恢复**：SQLite 删除只是把页标记为自由页，`History` 的 freelist 里仍留有旧的 URL 文本；WAL 文件（`History-wal`）也常保留最近一次提交前的旧数据。

### Firefox：登录记录和密钥是两份文件

先在赛题配置目录配对 `logins.json` 和 `key4.db`。用数据库 `metaData` 里的 `password` 行验证主密码；成功后，解读登录字段 Base64 包装中的密钥编号，再匹配 `nssPrivate.a102`。读取字段各自声明的加密方式，不要把数据库的派生密钥直接拿来解登录字段。FireFox Forensics 的库内题解按这个顺序走了一遍。

## 三、操作步骤

1. **清点用户配置**：列出 `User Data/*/`（Default、Profile 1…）与 `Snapshots`、`Extension State`。
2. **先复制再读**：浏览器打开时数据库被锁，`cp` 整个目录到工作区，并同时复制 `-wal` / `-shm`。
3. **读 History**：`urls` + `visits` 关联，按 `visit_time` 排序输出时间线。
4. **读下载**：`downloads`（含 `tab_url`、`target_path`、`start_time`）。
5. **读 Cookies**：先 dump `host_key/name/expires_utc`，加密的 value 单独处理。
6. **解密**：拿 `Local State` 的 key，Windows 用 DPAPI（在用户上下文或已知用户密码时），Linux 用 `v10` + `peanuts` 的口令。
7. **删除数据**：用 freelist/WAL 恢复，或用 `sqlite3 .recover`。

## 四、命令 / 脚本

```bash
# 环境准备
cp -r "User Data" workdir/
sqlite3 workdir/Default/History "SELECT name FROM sqlite_master WHERE type='table';"
# 时间线（微秒 -> 可读，自 1601 起）
sqlite3 workdir/Default/History \
  "SELECT datetime(visit_time/1000000 - 11644473600,'unixepoch'), title, url
   FROM urls JOIN visits ON urls.id = visits.url ORDER BY visit_time DESC LIMIT 50;"
# 下载记录
sqlite3 workdir/Default/History \
  "SELECT datetime(start_time/1000000 - 11644473600,'unixepoch'), target_path, tab_url FROM downloads;"
# 搜索关键词
sqlite3 workdir/Default/History "SELECT term, url_id FROM keyword_search_terms;"
# Cookie 概要
sqlite3 workdir/Default/Cookies \
  "SELECT host_key, name, datetime(expires_utc/1000000-11644473600,'unixepoch'), length(encrypted_value) FROM cookies;"
# 删除/损坏恢复
sqlite3 workdir/Default/History ".recover" | sqlite3 recovered.db
```

```python
#!/usr/bin/env python3
# Chromium 时间戳换算 + History 时间线导出
import sqlite3, datetime

EPOCH_DELTA = 11644473600  # 1601-01-01 到 1970-01-01 的秒数

def chrome_ts(v):
    if not v:
        return None
    return datetime.datetime(1970, 1, 1) + datetime.timedelta(seconds=v / 1e6 - EPOCH_DELTA)

def timeline(db='History'):
    con = sqlite3.connect('file:%s?mode=ro' % db, uri=True)
    q = """SELECT v.visit_time, u.url, u.title, v.transition
           FROM visits v JOIN urls u ON u.id = v.url
           ORDER BY v.visit_time"""
    for ts, url, title, trans in con.execute(q):
        print('%s | %-50s | %s' % (chrome_ts(ts), (title or '')[:50], url))

if __name__ == '__main__':
    timeline()
```

```bash
#!/usr/bin/env bash
# Chrome 口令/ Cookie 解密（Linux，v10 + peanuts）
python3 - <<'EOF'
import sqlite3, json, base64
from Crypto.Cipher import AES

with open('Local State') as f:
    ls = json.load(f)
key = base64.b64decode(ls['os_crypt']['encrypted_key'])[5:]      # 去 'DPAPI'
key = key.ljust(32, b'\x00')[:32]                                # v10 的 Linux 变体

con = sqlite3.connect('Cookies')
for host, name, value in con.execute('SELECT host_key, name, encrypted_value FROM cookies'):
    if value and value[:3] == b'v10':
        nonce, ct = value[3:15], value[15:-16]
        pt = AES.new(key, AES.MODE_GCM, nonce=nonce).decrypt(ct)
        print(host, name, pt[32:])                               # 前 32 字节是 host hash
    elif value:
        print(host, name, value)
EOF
```

```bash
# Windows：用 DPAPI 解 encrypted_key（在目标用户上下文下执行）
python3 -c "
import base64, win32crypt
enc = base64.b64decode(open('Local State').read().split('\"encrypted_key\":\"')[1].split('\"')[0])[5:]
print(win32crypt.CryptUnprotectData(enc, None, None, None, 0)[1].hex())
"
```

## 五、常见坑 / 变体

- **时间单位**：`visits.visit_time` 是**微秒**，`cookies.creation_utc` 也是微秒；但某些旧版 `downloads` 字段写过秒，先验证范围（2020 年应该落在 1.3e16 附近）。
- **多 Profile**：`Default` 只是默认，`Profile 1/2` 可能是真正使用的那个；`Local State` 里有 `profile.info_cache` 列出所有。
- **`Cookies` 有多个副本**：`Network/Cookies`（新版）与根目录 `Cookies`，一个有效一个可能被删。
- **v20 加密**：Chrome 127+ 的 App-Bound 加密离线无法直接解，必须回到目标机器上下文或用注入读取——CTF 里很少出，遇到优先找别的证据。
- **`History-journal` / `-wal`**：浏览器异常退出时残留，可能包含最近的条目，务必一起复制。
- **扩展取证**：`Extension State/` 与 `Extensions/` 能看出装了哪些扩展，恶意扩展常改 `Preferences` 的 `homepage`。
- **变体**：Firefox（`places.sqlite`、`cookies.sqlite`）、Safari（`History.db`、`Cookies.binarycookies`）、Edge 同 Chromium 结构。

## 六、参考来源

- [Foxton Forensics：Chrome History 数据库位置与表结构](https://www.foxtonforensics.com/browser-history-examiner/chrome-history-location)
- [Browser forensics：History 数据库字段详解](https://medium.com/@laurent.mandine/browser-forensics-89429fe0749f)
- [SQLite 官方文档（freelist 与 .recover 恢复）](https://github.com/sqlite/sqlite)
- [Chromium 源码目录：User Data 文件布局与 os_crypt](https://chromium.googlesource.com/chromium/src/+/main/docs/user_data_dir.md)
- [Chrome 口令与 Cookie 解密的公开实现](https://github.com/ohyicong/decrypt-chrome-passwords)
