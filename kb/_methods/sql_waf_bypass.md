---
title: 方法卡 · SQL 注入 WAF 绕过（等价改写 / 探测矩阵 / tamper 组合）
category: web
tags: [waf 绕过, sqli, 等价改写, 注释混写, 探测矩阵, tamper]
signals: [正常 payload 返回 403 或 406 或被拦截页, union 换成 union/**/ 就能过, 空格被过滤但 /**/ 可用, select 与和 or 出现在黑名单里, information_schema 被拦而回显还在, 题目提示有过滤或给了 modsecurity 规则]
difficulty: medium
source: kb/web/sql-injection-basics.md, kb/web/sql-injection-waf-bypass.md
tools: [curl, burpsuite, sqlmap, python]
updated: 2026-11-03
---

# 方法卡 · SQL 注入 WAF 绕过（等价改写 / 探测矩阵 / tamper 组合）

## 适用场景

- 原始 payload 被拦：403 / 406 / "Your request has been blocked"，但同样的注入在别的写法下回显正常；
- `union select` 被拦，换成 `union/**/select`、`UNION(SELECT)`、`union%0aselect` 就通 → 关键词黑名单；
- 空格被过滤（`%20` 被拦）：`/**/`、`%09`、`%0a`、`+` 可用；
- 逗号 / `select` / `and` / `or` / 等号 / 引号 里某些被过滤；
- `information_schema`、`sleep`、`substr` 被拦，需要语义等价替换；
- 变体：WAF 只查 GET，改 POST body / Cookie / `X-Forwarded-For` 即通。

## 前置条件

- 先确认**存在注入**（`and 1=1` / `and 1=2` 回显差异，或 `sleep` 有延迟），否则绕 WAF 没有意义；
- 知道数据库类型（MySQL / SQLServer / Oracle 的函数与系统表不同，等价替换不通用）；
- 绕过后仍需能观察效果：回显位、布尔差异、或延时基线（先测一次无 sleep 的正常耗时）；
- 本卡脚本**离线**：只生成等价改写与探测 payload 列表，不发包、不跑 sqlmap。

## 步骤

1. **定位被拦元素**：用 `--probe` 出的梯度 payload 逐条打，哪条开始 403 就说明该条引入的元素被拦（先 `1 and 1=1`，再 `/**/`、`%09`、`like`、`union`）。
2. **按元素选改写**：`--morph 'union select 1'` 给全部等价形式；空格被拦优先 `/**/`，`/**/` 也被拦换 `%0a`、`%09`。
3. **函数/系统表替换**：`substr→mid/substring/left`、`ascii→ord`、`sleep→benchmark`、`information_schema→mysql.innodb_table_stats`。
4. **换通道**：GET 被拦改 POST body / Cookie / `X-Forwarded-For`；云 WAF 场景用 HPP（`?id=1&id=1' union ...`）。
5. **编码层**：双重 URL 编码、`0x` 十六进制字符串、`CHAR(117,110,105,111,110)` 拆关键词。
6. **批量**：sqlmap `--tamper=space2comment,between,charencode,randomcase`，`--delay=0.5` 避免触发频率封禁。

```powershell
# 单个 payload 的全部等价改写（注释混写 / 换空白 / 换大小写 / 换函数）
.\.venv\Scripts\python.exe kb/_methods/scripts/sql_waf_bypass.py --morph "union select 1,2,3-- -"
# 生成"定位被拦元素"的梯度探测列表
.\.venv\Scripts\python.exe kb/_methods/scripts/sql_waf_bypass.py --probe
# 检测 payload 里有哪些元素通常被黑名单拦
.\.venv\Scripts\python.exe kb/_methods/scripts/sql_waf_bypass.py --check "1' union select load_file('/flag')-- -"
```

## 脚本

脚本路径：`kb/_methods/scripts/sql_waf_bypass.py`（纯标准库，离线）

- `morph(payload)`：生成注释混写、空白替换、大小写、函数替换四类等价形式（去重后按"对 WAF 最不显眼"排序）；
- `probe_matrix(db="mysql")`：按「基础 → 空格替换 → 注释 → 函数 → 系统表」递进的探测 payload 列表，用于二分定位被拦词；
- `check_tokens(payload)`：标出命中的高危词（select/union/sleep/information_schema/load_file/引号/注释）与可替换建议；
- `tamper_chain(tokens)`：把命中的元素转成 sqlmap `--tamper=` 推荐组合；
- `--selftest`：固定断言 6 组，退出码 0 才算过。

## 失效场景

- **正则只拦 `select\s+`**：`select/**/*` 能过；但若规则写了 `select.*` 再配 `t:lowercase`，大小写与注释混写全部无效。
- **ModSecurity 默认不区分大小写**：`UnIoN` 这类绕过白费功夫，先看响应头是否有 `Server: ModSecurity`。
- **数字型注入无需空格**：等价改写收益为 0，直接换通道（POST/Cookie）更快。
- **`/**/` 本身在规则里**：注释混写全部失效，只能 `%0a`/`%09` 或换函数。
- **布尔/时间盲注被限速**：WAF 对高频请求直接封 IP，绕语法没用，必须加 `--delay` 或降并发。
- **`load_file`/`into outfile` 被 `secure_file_priv` 禁**：这是数据库配置而不是 WAF，改写不能解决。

## 相关文档

- `kb/web/sql-injection-waf-bypass.md`（替换速查表、tamper 列表、HPP 与分块传输）
- `kb/web/sql-injection-basics.md`（联合/报错/布尔/时间四类注入的判断与取数语句）
