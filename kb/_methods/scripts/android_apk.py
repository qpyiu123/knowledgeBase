"""APK 静态排查：zip 目录、AndroidManifest 二进制 AXML、加固特征、dex 头。纯标准库。"""
from __future__ import annotations

import argparse
import struct
import sys
import zipfile

SHELL_SO = ("libjiagu", "libshella", "libmobisec", "libbaiduprotect", "libDexHelper",
            "libexecmain", "libnesec", "libkwscmm", "libtup")
SHELL_DEX = (b"dex\n035", b"dex\n037", b"dex\n038", b"dex\n039")


def is_apk(path):
    """只按 zip 结构 + AndroidManifest.xml 判定，不看扩展名。"""
    if not zipfile.is_zipfile(path):
        raise ValueError("不是 zip 容器（APK 必须是 zip）：%s" % path)
    with zipfile.ZipFile(path) as zf:
        names = zf.namelist()
    if "AndroidManifest.xml" not in names:
        raise ValueError("zip 里没有 AndroidManifest.xml，可能不是 APK：%s" % path)
    return names


def axml_strings(data):
    """读 AXML 字符串池，返回 (字符串列表, 包名前缀?)。"""
    if data[:4] != b"\x03\x00\x08\x00" and not data.startswith(b"\x02\x00\x08\x00"):
        raise ValueError("AndroidManifest.xml 不是二进制 AXML（缺少文件头 03 00 08 00）")
    if len(data) < 16:
        raise ValueError("AXML 头部被截断")
    off = struct.unpack_from("<I", data, 8)[0]
    if off + 28 > len(data):
        raise ValueError("AXML 字符串池偏移越界")
    typ, hsize, ssize, count, _, flags, sstart = struct.unpack_from("<HHIIII I", data, off)
    if typ != 0x0001:
        raise ValueError("AXML 第一个块不是字符串池（type=0x%04x）" % typ)
    base = off + sstart
    utf8 = bool(flags & 0x100)
    out = []
    for i in range(count):
        if base + 2 > len(data):
            break
        p = struct.unpack_from("<H", data, off + 28 + i * 4)[0] + base
        if p >= len(data):
            break
        if utf8:
            n = data[p]
            p += 2 if n & 0x80 else 1
            n = data[p]
            if n & 0x80:
                n = ((n & 0x7F) << 8) | data[p + 1]
                p += 1
            out.append(data[p + 1:p + 1 + n].decode("utf-8", "replace"))
        else:
            n = struct.unpack_from("<H", data, p)[0]
            p += 2
            out.append(data[p:p + n * 2].decode("utf-16-le", "replace"))
    return out


def manifest_flags(strings):
    """在字符串表里找 debuggable / exported / 权限名，返回命中列表。"""
    want = ("debuggable", "allowBackup", "usesCleartextTraffic", "exported",
            "android.permission.INTERNET", "android.permission.READ_SMS",
            "android.permission.SEND_SMS", "android.permission.CAMERA")
    return [s for s in strings if s in want or s.startswith("android.permission.")]


def dex_info(zf):
    """统计 dex 文件与大小；大 dex 之外的异常加密提示加固可能。"""
    out = []
    for name in zf.namelist():
        if name.startswith("classes") and name.endswith(".dex"):
            head = zf.read(name)[:8]
            size = zf.getinfo(name).file_size
            ok = len(head) == 8 and head[:4] == b"dex\n"
            out.append((name, size, ok))
    return out


def shell_hints(names, dexes):
    """加固特征：libjiagu*.so、小得离谱的 classes.dex、assets 里的加密 dex。"""
    hints = []
    for name in names:
        low = name.lower()
        for tag in SHELL_SO:
            if low.endswith(".so") and tag in low:
                hints.append("发现加固库 %s（%s）" % (name, tag))
                break
    for name, size, ok in dexes:
        if not ok:
            hints.append("%s 的 dex 魔数不正常，可能被加密/加壳" % name)
        elif size < 4096:
            hints.append("%s 只有 %d 字节，主体逻辑大概率在别处" % (name, size))
    for name in names:
        low = name.lower()
        if low.startswith("assets/") and (low.endswith((".dex", ".bin", ".dat", ".jar"))):
            hints.append("assets 内有可疑载荷 %s" % name)
    return hints


def analyze(path):
    names = is_apk(path)
    with zipfile.ZipFile(path) as zf:
        dexes = dex_info(zf)
        strings = []
        raw = zf.read("AndroidManifest.xml")
    try:
        strings = axml_strings(raw)
    except ValueError as exc:
        hints_note = "AXML 解析失败：%s" % exc
    else:
        hints_note = "AXML 字符串 %d 条" % len(strings)
    return {"entries": len(names), "dex": dexes, "manifest": manifest_flags(strings),
            "hints": shell_hints(names, dexes) + [hints_note], "names": names}


def selftest():
    fails = []
    import io

    buf = io.BytesIO()
    with zipfile.ZipFile(buf, "w") as zf:
        zf.writestr("classes.dex", SHELL_DEX[0] + b"\x00" * 6000)
        zf.writestr("AndroidManifest.xml", b"\x03\x00\x08\x00" + b"\x00" * 12)
        zf.writestr("lib/arm64-v8a/libjiagu.so", b"\x7fELF")
    path = buf.getvalue()
    tmp = "_selftest.apk"
    with open(tmp, "wb") as fh:
        fh.write(path)
    try:
        info = analyze(tmp)
    finally:
        import os
        os.remove(tmp)
    if info["entries"] != 3:
        fails.append("case1: zip 条目数应为 3，实际 %d" % info["entries"])
    if not any("libjiagu" in h for h in info["hints"]):
        fails.append("case1: 未识别 libjiagu 加固库")
    if not any("AXML" in h for h in info["hints"]):
        fails.append("case1: 缺少 AXML 解析提示")
    if len(info["dex"]) != 1 or not info["dex"][0][2]:
        fails.append("case2: dex 头识别错误 %r" % (info["dex"],))
    tiny = shell_hints(["classes.dex"], [("classes.dex", 9000, True)])
    if any("魔数" in h for h in tiny):
        fails.append("case2: 正常 dex 被判成魔数异常")
    bad = ["x"], [("classes.dex", 10, False)]
    if not shell_hints(*bad):
        fails.append("case3: dex 魔数异常未被标记")
    try:
        axml_strings(b"\x00\x01\x02")
        fails.append("case3: 非 AXML 数据未拒绝")
    except ValueError:
        pass
    for fn, arg in ((is_apk, "_no_such_file.apk"),
                    (is_apk, "_selftest_dummy.txt")):
        try:
            fn(arg)
            fails.append("case4: %s 未拒绝 %r" % (fn.__name__, arg))
        except (ValueError, OSError):
            pass
    if fails:
        for line in fails:
            print("FAIL", line, file=sys.stderr)
        return 1
    print("selftest ok: 4 组断言全过（zip 结构/加固特征/AXML 拒绝/缺文件）")
    return 0


def main(argv=None):
    ap = argparse.ArgumentParser(description="APK 静态排查（离线、纯标准库）")
    ap.add_argument("--file", help="APK 路径")
    ap.add_argument("--strings", action="store_true", help="打印 AndroidManifest 字符串表")
    ap.add_argument("--selftest", action="store_true", help="运行内置自测")
    a = ap.parse_args(argv)
    if a.selftest:
        return selftest()
    if not a.file:
        ap.error("必须提供 --file（或 --selftest）")
    try:
        info = analyze(a.file)
    except (ValueError, OSError, zipfile.BadZipFile) as exc:
        print("失败：%s" % exc, file=sys.stderr)
        return 2
    print("条目 %d，dex %d 个" % (info["entries"], len(info["dex"])))
    for name, size, ok in info["dex"]:
        print("  %s  %d 字节  魔数%s" % (name, size, "正常" if ok else "异常"))
    print("清单命中：%s" % (", ".join(info["manifest"]) or "无"))
    for hint in info["hints"]:
        print("提示：%s" % hint)
    if a.strings:
        print("条目列表：")
        for name in info["names"]:
            print("  " + name)
    return 0


if __name__ == "__main__":
    sys.exit(main())
