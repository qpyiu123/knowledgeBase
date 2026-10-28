#!/usr/bin/env python
"""P2 附件侦察的可复现评测入口。

样例由 `BUILDERS` 现场生成，不提交二进制；pytest 与 CLI 共用同一套
manifest（`eval/attachment_cases.json`）和同一份分析代码，避免“测试能过、
实际入口却不一样”。

用法：
    python tools/eval_attachments.py
    python tools/eval_attachments.py --json
    python tools/eval_attachments.py --json-out work/attachment_eval.json
    python tools/eval_attachments.py --check     # 有失败时返回非 0

评测只读本地字节，不执行附件、不联网、不调用 LLM 或外部取证命令。
"""
from __future__ import annotations

import argparse
import base64
import io
import json
import struct
import sys
import zipfile
import zlib
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "tools"))

from agent.attachment import analyze_bytes  # noqa: E402
from agent.attachment import analyze_path  # noqa: E402

DEFAULT_CASES = ROOT / "eval" / "attachment_cases.json"


# ---------------------------------------------------------------- 样例生成
def _png_chunk(kind: bytes, payload: bytes) -> bytes:
    return (struct.pack(">I", len(payload)) + kind + payload
            + struct.pack(">I", zlib.crc32(kind + payload) & 0xFFFFFFFF))


def _one_pixel_png() -> bytes:
    ihdr = struct.pack(">IIBBBBB", 1, 1, 8, 0, 0, 0, 0)
    return (b"\x89PNG\r\n\x1a\n"
            + _png_chunk(b"IHDR", ihdr)
            + _png_chunk(b"IDAT", zlib.compress(b"\x00\x00"))
            + _png_chunk(b"IEND", b""))


def _zip_bytes(files: dict[str, str]) -> bytes:
    buf = io.BytesIO()
    with zipfile.ZipFile(buf, "w", zipfile.ZIP_DEFLATED) as z:
        for name, text in files.items():
            z.writestr(name, text)
    return buf.getvalue()


def _b64(text: str) -> bytes:
    return base64.b64encode(text.encode("utf-8"))


def build_png_appended_zip() -> tuple[bytes, str]:
    """合法 PNG + 尾部 base64 文本 + 追加 ZIP。"""
    data = (_one_pixel_png()
            + b"NOTE:" + _b64("flag{p2_c4rv3_d3c0d3}") + b"\n"
            + _zip_bytes({"flag.txt": "flag{p2_inside_zip}"}))
    return data, "carved.png"


def build_fake_png_zip() -> tuple[bytes, str]:
    """扩展名是 .png，实际是 ZIP。"""
    data = _zip_bytes({"readme.txt": "just a zip", "note.txt": "not a png"})
    return data, "fake.png"


def build_text_base64() -> tuple[bytes, str]:
    data = ("hint: " + _b64("flag{p2_text_d3cod3}").decode("ascii")
            + "\n").encode("utf-8")
    return data, "hint.txt"


def _wav_with_tail() -> bytes:
    fmt = struct.pack("<HHIIHH", 1, 1, 8000, 8000, 1, 8)
    body = (b"fmt " + struct.pack("<I", len(fmt)) + fmt
            + b"data" + struct.pack("<I", 8) + b"\x00" * 8)
    return b"RIFF" + struct.pack("<I", len(body)) + b"WAVE" + body + b"flag{w4v_t41l}"


def build_wav_tail() -> tuple[bytes, str]:
    return _wav_with_tail(), "sound.wav"


def build_script_warning() -> tuple[bytes, str]:
    data = ("print('hello')\n# " + _b64("flag{p2_n0_exec}").decode("ascii")
            + "\n").encode("utf-8")
    return data, "run.py"


BUILDERS = {
    "png_appended_zip": build_png_appended_zip,
    "fake_png_zip": build_fake_png_zip,
    "text_base64": build_text_base64,
    "wav_tail": build_wav_tail,
    "script_warning": build_script_warning,
}


# ---------------------------------------------------------------- 评测
def load_cases(path: str | Path = DEFAULT_CASES) -> list[dict]:
    raw = json.loads(Path(path).read_text(encoding="utf-8"))
    items = raw.get("cases", raw) if isinstance(raw, dict) else raw
    if not isinstance(items, list) or not items:
        raise ValueError("附件评测文件里没有 cases")
    cases: list[dict] = []
    seen: set[str] = set()
    for i, item in enumerate(items):
        if not isinstance(item, dict):
            raise ValueError(f"第 {i + 1} 条不是对象")
        cid = str(item.get("id") or "").strip()
        builder = str(item.get("builder") or "").strip()
        if not cid or cid in seen:
            raise ValueError(f"id 缺失或重复: {cid!r}")
        if builder not in BUILDERS:
            raise ValueError(f"{cid}: 未知 builder {builder!r}")
        seen.add(cid)
        cases.append(item)
    return cases


def _check(report: dict, expect: dict) -> list[str]:
    fails: list[str] = []
    typ = report.get("type") or {}
    kind = str(typ.get("kind") or "")
    if "kind_contains" in expect and str(expect["kind_contains"]) not in kind:
        fails.append(f"类型不含 {expect['kind_contains']!r}（实际 {kind!r}）")
    if "is_text" in expect and bool(typ.get("is_text")) != bool(expect["is_text"]):
        fails.append(f"is_text 期望 {expect['is_text']}，实际 {typ.get('is_text')}")
    if "mismatch" in expect and bool(typ.get("extension_mismatch")) != bool(expect["mismatch"]):
        fails.append(f"扩展名不符期望 {expect['mismatch']}，"
                     f"实际 {typ.get('extension_mismatch')}")

    carve_types = [c.get("type") for c in report.get("carve") or []]
    for t in expect.get("carve_types") or []:
        if t not in carve_types:
            fails.append(f"雕刻结果缺少 {t}（实际 {carve_types}）")

    decoded = " ".join(str(d.get("decoded") or "")
                       for d in report.get("decoded") or [])
    if "decoded_contains" in expect and str(expect["decoded_contains"]) not in decoded:
        fails.append(f"解码结果不含 {expect['decoded_contains']!r}")

    anomalies = " ".join(str(a) for a in report.get("anomalies") or [])
    if "anomaly_contains" in expect and str(expect["anomaly_contains"]) not in anomalies:
        fails.append(f"异常提示不含 {expect['anomaly_contains']!r}")

    warnings = " ".join(str(w) for w in report.get("warnings") or [])
    if "warning_contains" in expect and str(expect["warning_contains"]) not in warnings:
        fails.append(f"警告不含 {expect['warning_contains']!r}")

    structures = report.get("structures") or {}
    if "structure" in expect and expect["structure"] not in structures:
        fails.append(f"结构结果缺少 {expect['structure']}")
    zips = str((structures.get("zip") or {}).get("entries") or "")
    if "zip_entry_contains" in expect and str(expect["zip_entry_contains"]) not in zips:
        fails.append(f"ZIP 条目不含 {expect['zip_entry_contains']!r}")

    if report.get("executed") is not False:
        fails.append("executed 必须为 false")
    return fails


def evaluate_cases(cases: list[dict], builders: dict | None = None) -> dict:
    builders = builders or BUILDERS
    results = []
    for case in cases:
        data, built_name = builders[case["builder"]]()
        name = str(case.get("name") or built_name)
        report = analyze_bytes(data, name)
        fails = _check(report, case.get("expect") or {})
        results.append({
            "id": case["id"],
            "builder": case["builder"],
            "name": name,
            "ok": not fails,
            "failures": fails,
            "type": (report.get("type") or {}).get("kind"),
            "executed": report.get("executed"),
        })
    passed = sum(1 for r in results if r["ok"])
    total = len(results)
    return {
        "total": total,
        "passed": passed,
        "failed": total - passed,
        "pass_rate": round(passed / total, 4) if total else 0.0,
        "results": results,
    }


def _local_report(path: str | Path, name: str) -> dict:
    """可选验证本地文件（不写入隔离目录）。"""
    return analyze_path(Path(path), name=name)


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description="附件侦察可复现评测")
    ap.add_argument("--cases", default=str(DEFAULT_CASES))
    ap.add_argument("--json", action="store_true", help="输出 JSON")
    ap.add_argument("--json-out", default=None, help="同时写入 JSON 文件")
    ap.add_argument("--check", action="store_true", help="有失败时返回非 0")
    ap.add_argument("--file", default=None, help="改为分析一个本地文件")
    args = ap.parse_args(argv)

    if args.file:
        p = Path(args.file)
        report = _local_report(p, p.name)
        text = json.dumps(report, ensure_ascii=False, indent=2)
        print(text)
        if args.json_out:
            Path(args.json_out).write_text(text, encoding="utf-8")
        return 0

    result = evaluate_cases(load_cases(args.cases))
    if args.json:
        print(json.dumps(result, ensure_ascii=False, indent=2))
    else:
        print(f"附件侦察评测：{result['passed']}/{result['total']} 通过 "
              f"(pass_rate={result['pass_rate']:.4f})")
        for r in result["results"]:
            mark = "PASS" if r["ok"] else "FAIL"
            print(f"  [{mark}] {r['id']}: {r['type']}")
            for f in r["failures"]:
                print(f"        - {f}")
    if args.json_out:
        Path(args.json_out).parent.mkdir(parents=True, exist_ok=True)
        Path(args.json_out).write_text(
            json.dumps(result, ensure_ascii=False, indent=2), encoding="utf-8")
    return 0 if (result["failed"] == 0 or not args.check) else 1


if __name__ == "__main__":
    raise SystemExit(main())
