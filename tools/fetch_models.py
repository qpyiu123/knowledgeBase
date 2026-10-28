#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""fetch_models.py — 幂等模型下载脚本 (CTF knowledge base)

用法:
    python tools/fetch_models.py                 # 下载全部（已存在则跳过）
    python tools/fetch_models.py --only embed    # 只下嵌入模型
    python tools/fetch_models.py --only 7b       # 只下 7B GGUF
    python tools/fetch_models.py --only 3b
    python tools/fetch_models.py --only embed-gguf
    python tools/fetch_models.py --mirror        # 强制走 hf-mirror.com
    python tools/fetch_models.py --check         # 只校验已下载文件, 不下载
    python tools/fetch_models.py --force         # 跳过幂等检查强制重下

环境变量:
    HF_ENDPOINT=https://hf-mirror.com    (或用 --mirror)
    HF_TOKEN=...                          (私有仓库才需要)

幂等策略:
  - 目标文件已存在且大小 >= 期望大小的 95%  -> 跳过
  - 否则删除残缺文件后重新下载
  - 下载完成后写入 models/_manifest.json 记录 sha256/大小/来源
"""
from __future__ import annotations

import argparse
import json
import os
import sys
import time
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
MODELS = ROOT / "models"
GGUF = MODELS / "gguf"
MANIFEST = MODELS / "_manifest.json"

MiB = 1024 * 1024

# ---------------------------------------------------------------------------
# 模型清单
# repo_id / 目标路径 / 期望字节数（用于完整性判断）/ 类别
# 期望字节数取自 HF resolve HEAD 的 content-length（2026-10 实测）
# ---------------------------------------------------------------------------
CATALOG = [
    # ---- 嵌入模型 (sentence-transformers 格式, 约 95MB) ----
    {
        "kind": "embed",
        "repo": "BAAI/bge-small-zh-v1.5",
        "dest": MODELS / "bge-small-zh-v1.5",
        "snapshot": True,
        "expect_bytes": None,  # 目录型, 见 validate_dir
        "min_bytes": 80 * MiB,
    },
    # ---- 嵌入模型 ONNX 版 (零 torch; Xenova 导出) ----
    {
        "kind": "embed",
        "repo": "Xenova/bge-small-zh-v1.5",
        "dest": MODELS / "bge-small-zh-v1.5-onnx",
        "snapshot": True,
        "allow_patterns": [
            "onnx/model.onnx", "onnx/model_quantized.onnx", "config.json",
            "tokenizer.json", "tokenizer_config.json", "special_tokens_map.json",
            "vocab.txt",
        ],
        "flatten": True,   # onnx/ 子目录下的文件压平到根目录
        "expect_bytes": None,
        "min_bytes": 100 * MiB,
    },
    # ---- 主生成模型 7B Q4_K_M (~4.36 GiB) ----
    {
        "kind": "7b",
        "repo": "Qwen/Qwen2.5-Coder-7B-Instruct-GGUF",
        "filename": "qwen2.5-coder-7b-instruct-q4_k_m.gguf",
        "dest": GGUF / "qwen2.5-coder-7b-instruct-q4_k_m.gguf",
        "expect_bytes": 4683073536,
        "min_bytes": 4096 * MiB,  # 强校验: >4GiB
        # 候选备用仓库（主仓库文件缺失时按序回退）
        "fallbacks": [
            ("bartowski/Qwen2.5-Coder-7B-Instruct-GGUF",
             "Qwen2.5-Coder-7B-Instruct-Q4_K_M.gguf"),
            ("mradermacher/Qwen2.5-Coder-7B-Instruct-GGUF",
             "Qwen2.5-Coder-7B-Instruct.Q4_K_M.gguf"),
        ],
    },
    # ---- 轻量兜底 3B Q4_K_M (~1.8 GiB, 可整模型进 4GB 显存) ----
    {
        "kind": "3b",
        "repo": "bartowski/Qwen2.5-Coder-3B-Instruct-GGUF",
        "filename": "Qwen2.5-Coder-3B-Instruct-Q4_K_M.gguf",
        "dest": GGUF / "qwen2.5-coder-3b-instruct-q4_k_m.gguf",
        "expect_bytes": 1929903360,
        "min_bytes": 1500 * MiB,
        "fallbacks": [
            ("Qwen/Qwen2.5-Coder-3B-Instruct-GGUF",
             "qwen2.5-coder-3b-instruct-q4_k_m.gguf"),
        ],
    },
    # ---- 嵌入备胎 GGUF (走 llama.cpp, 零 torch 依赖) ----
    {
        "kind": "embed-gguf",
        "repo": "CompendiumLabs/bge-small-zh-v1.5-gguf",
        "filename": "bge-small-zh-v1.5-q8_0.gguf",
        "dest": GGUF / "bge-small-zh-v1.5-q8_0.gguf",
        "expect_bytes": 26472640,
        "min_bytes": 20 * MiB,
    },
    {
        "kind": "embed-gguf",
        "repo": "nomic-ai/nomic-embed-text-v1.5-GGUF",
        "filename": "nomic-embed-text-v1.5.Q4_K_M.gguf",
        "dest": GGUF / "nomic-embed-text-v1.5-q4_k_m.gguf",
        "expect_bytes": 84106624,
        "min_bytes": 60 * MiB,
    },
]

ALL_KINDS = ["embed", "3b", "7b", "embed-gguf"]
# 下载顺序: 小文件优先
ORDER = {"embed": 0, "embed-gguf": 1, "3b": 2, "7b": 3}


def log(msg: str) -> None:
    print(f"[{time.strftime('%H:%M:%S')}] {msg}", flush=True)


def setup_endpoint(mirror: bool) -> str:
    if mirror:
        os.environ["HF_ENDPOINT"] = "https://hf-mirror.com"
        # Hub 2.x 只认 HF_ENDPOINT; 老版本认 HF_HUB_ENDPOINT
        os.environ.setdefault("HF_HUB_ENDPOINT", "https://hf-mirror.com")
    ep = os.environ.get("HF_ENDPOINT", "https://huggingface.co")
    ep = ep.rstrip("/")
    os.environ["HF_ENDPOINT"] = ep
    # 关掉 symlink 行为（Windows 上旧版会警告），使用新参数名
    os.environ.setdefault("HF_HUB_DISABLE_SYMLINKS_WARNING", "1")
    return ep


def human(n: int) -> str:
    return f"{n / MiB:.1f} MiB"


def _hub():
    try:
        import huggingface_hub as h
    except ImportError:
        log("!! 缺少 huggingface_hub, 请先: pip install huggingface_hub")
        raise SystemExit(2)
    return h


def validate_file(path: Path, expect: int | None, minimum: int) -> bool:
    if not path.exists():
        return False
    size = path.stat().st_size
    if size < minimum:
        return False
    if expect and size < expect * 0.95:
        return False
    return True


def validate_dir(path: Path, minimum: int) -> bool:
    """检查 sentence-transformers 目录是否至少含 config.json + 权重"""
    if not path.is_dir():
        return False
    if not (path / "config.json").exists():
        return False
    weights = (list(path.glob("*.safetensors")) + list(path.glob("*.bin"))
               + list(path.glob("*.onnx")) + list(path.glob("onnx/*.onnx")))
    if not weights:
        return False
    total = sum(p.stat().st_size for p in path.rglob("*") if p.is_file())
    return total >= minimum


def sha256_of(path: Path, limit_mib: int | None = None) -> str:
    import hashlib
    h = hashlib.sha256()
    read = 0
    with path.open("rb") as f:
        while chunk := f.read(8 * MiB):
            h.update(chunk)
            read += len(chunk)
            if limit_mib and read > limit_mib * MiB:
                return "skipped(large)"
    return h.hexdigest()


def download_snapshot(h, item) -> bool:
    dest: Path = item["dest"]
    dest.mkdir(parents=True, exist_ok=True)
    log(f"==> snapshot_download {item['repo']} -> {dest}")
    # 新 hub 版本 snapshot_download 已默认不建 symlink；
    # local_dir_use_symlinks 在 2.x 已移除, 用 try/except 兼容
    kwargs = dict(
        repo_id=item["repo"],
        local_dir=str(dest),
        resume_download=True,
        max_workers=4,
    )
    if item.get("allow_patterns"):
        kwargs["allow_patterns"] = item["allow_patterns"]
    try:
        path = h.snapshot_download(**kwargs, local_dir_use_symlinks=False)
    except TypeError:
        path = h.snapshot_download(**kwargs)
    except Exception as e:  # noqa: BLE001
        log(f"!! snapshot_download 失败: {type(e).__name__}: {e}")
        return False
    log(f"    ok -> {path}")
    if item.get("flatten"):
        flatten_onnx(dest)
    return validate_dir(dest, item["min_bytes"])


def flatten_onnx(dest: Path) -> None:
    """把 onnx/model.onnx 之类子目录文件压平到 dest 根, 方便直接加载.
    命中 hf-mirror Xet 导致的 File reconstruction 错误时, 回退到直连 HTTP 下载。"""
    for sub in ("onnx",):
        d = dest / sub
        if not d.is_dir():
            continue
        for f in d.iterdir():
            if f.is_file():
                target = dest / f.name
                try:
                    os.replace(f, target)
                except OSError:
                    pass
        try:
            d.rmdir()
        except OSError:
            pass

    # 校验关键文件; 0 字节说明下载被截断(镜像 Xet 401 时会这样)
    ok = True
    for name in ("model.onnx", "model_quantized.onnx"):
        p = dest / name
        if not p.exists() or p.stat().st_size < 1024:
            ok = False
    if ok:
        return
    log("    onnx 文件缺失/损坏, 回退直连 huggingface.co 下载")
    import requests
    files = {
        "model.onnx": "onnx/model.onnx",
        "model_quantized.onnx": "onnx/model_quantized.onnx",
    }
    for local, remote in files.items():
        url = f"https://huggingface.co/Xenova/bge-small-zh-v1.5/resolve/main/{remote}"
        try:
            r = requests.get(url, stream=True, timeout=600)
            r.raise_for_status()
            with (dest / local).open("wb") as fh:
                for chunk in r.iter_content(1 << 20):
                    fh.write(chunk)
            log(f"    {local} {human((dest / local).stat().st_size)}")
        except Exception as e:  # noqa: BLE001
            log(f"    !! {local} 直连失败: {type(e).__name__}: {e}")


def download_file(h, repo: str, filename: str, dest: Path) -> bool:
    dest.parent.mkdir(parents=True, exist_ok=True)
    partial = dest.with_suffix(dest.suffix + ".part")
    if partial.exists():
        partial.unlink()
    log(f"==> hf_hub_download {repo}/{filename}")
    t0 = time.time()
    try:
        got = h.hf_hub_download(
            repo_id=repo,
            filename=filename,
            local_dir=str(dest.parent),
            # 下到同名文件后改名，避免 local_dir 下出现仓库镜像子目录
        )
    except Exception as e:  # noqa: BLE001
        log(f"!! 下载失败 {repo}/{filename}: {type(e).__name__}: {e}")
        return False
    got = Path(got)
    if got.resolve() != dest.resolve():
        # hf_hub_download 会放到 local_dir/<filename>，通常正好是 dest
        try:
            if got.exists():
                os.replace(got, dest)
        except OSError as e:
            log(f"!! 无法移动到目标名 {dest.name}: {e}")
            return False
    dt = time.time() - t0
    if dest.exists():
        sz = dest.stat().st_size
        log(f"    ok {human(sz)} / {dt:.1f}s = {sz / MiB / max(dt, 1e-6):.1f} MiB/s")
        return True
    return False


def process(item, mirror_cb, force: bool) -> dict:
    kind = item["kind"]
    dest: Path = item["dest"]
    result = {"kind": kind, "repo": item["repo"], "path": str(dest),
              "ok": False, "skipped": False, "bytes": 0}

    # ---- 幂等检查 ----
    if not force:
        if item.get("snapshot"):
            if validate_dir(dest, item["min_bytes"]):
                total = sum(p.stat().st_size for p in dest.rglob("*") if p.is_file())
                log(f"[skip] {kind}: {dest} 已存在 ({human(total)})")
                result.update(ok=True, skipped=True, bytes=total)
                return result
        elif validate_file(dest, item.get("expect_bytes"), item["min_bytes"]):
            sz = dest.stat().st_size
            log(f"[skip] {kind}: {dest.name} 已存在且完整 ({human(sz)})")
            result.update(ok=True, skipped=True, bytes=sz)
            return result
        elif dest.exists():
            log(f"[warn] {kind}: {dest.name} 存在但大小不足, 将重新下载")
            try:
                dest.unlink()
            except OSError:
                pass

    h = _hub()
    # ---- 下载（含镜像回退 + 备用仓库回退）----
    tries = [(item["repo"], item.get("filename"))]
    tries += item.get("fallbacks", [])
    ok = False
    for ep_name, ep_url in mirror_cb:
        os.environ["HF_ENDPOINT"] = ep_url
        os.environ["HF_HUB_ENDPOINT"] = ep_url
        log(f"    endpoint = {ep_url}")
        for repo, fname in tries:
            if item.get("snapshot"):
                ok = download_snapshot(h, item)
            else:
                ok = download_file(h, repo, fname, dest)
            if ok:
                result["repo"] = repo
                break
        if ok:
            break
    os.environ["HF_ENDPOINT"] = "https://huggingface.co"

    if ok:
        sz = dest.stat().st_size if dest.is_file() else sum(
            p.stat().st_size for p in dest.rglob("*") if p.is_file())
        result.update(ok=True, bytes=sz)
        # 完整性复核
        if item.get("snapshot"):
            result["ok"] = validate_dir(dest, item["min_bytes"])
        else:
            result["ok"] = validate_file(dest, item.get("expect_bytes"), item["min_bytes"])
        log(f"    {'VERIFIED' if result['ok'] else 'SIZE MISMATCH'} {human(sz)}")
    return result


def main() -> int:
    ap = argparse.ArgumentParser(description="CTF KB 模型下载器（幂等）")
    ap.add_argument("--only", choices=ALL_KINDS, action="append",
                    help="只处理指定类别, 可重复")
    ap.add_argument("--mirror", action="store_true", help="强制使用 hf-mirror.com")
    ap.add_argument("--check", action="store_true", help="只校验, 不下载")
    ap.add_argument("--force", action="store_true", help="忽略幂等检查")
    ap.add_argument("--sha256", action="store_true", help="下载后计算 sha256(大文件只取前 64MiB)")
    args = ap.parse_args()

    MODELS.mkdir(parents=True, exist_ok=True)
    GGUF.mkdir(parents=True, exist_ok=True)

    ep = setup_endpoint(args.mirror)
    log(f"models root : {MODELS}")
    log(f"endpoint    : {ep}")

    if args.mirror:
        mirror_cb = [("hf-mirror", "https://hf-mirror.com")]
    else:
        mirror_cb = [("huggingface", "https://huggingface.co"),
                     ("hf-mirror", "https://hf-mirror.com")]

    kinds = set(args.only) if args.only else set(ALL_KINDS)
    items = [i for i in CATALOG if i["kind"] in kinds]
    items.sort(key=lambda i: ORDER[i["kind"]])

    # ---- 只校验模式 ----
    if args.check:
        ok_all = True
        for item in items:
            d = item["dest"]
            if item.get("snapshot"):
                good = validate_dir(d, item["min_bytes"])
            else:
                good = validate_file(d, item.get("expect_bytes"), item["min_bytes"])
            sz = (sum(p.stat().st_size for p in d.rglob("*") if p.is_file())
                  if d.is_dir() else (d.stat().st_size if d.exists() else 0))
            log(f"{'OK  ' if good else 'MISS'} {item['kind']:10s} {d.name:48s} {human(sz)}")
            ok_all &= good
        return 0 if ok_all else 1

    results = []
    for item in items:
        try:
            results.append(process(item, mirror_cb, args.force))
        except SystemExit:
            raise
        except Exception as e:  # noqa: BLE001
            log(f"!! {item['kind']} 异常: {type(e).__name__}: {e}")
            results.append({"kind": item["kind"], "repo": item["repo"],
                            "path": str(item["dest"]), "ok": False, "error": str(e)})

    # ---- manifest ----
    manifest = {"generated_at": time.strftime("%Y-%m-%dT%H:%M:%S"),
                "models_root": str(MODELS), "endpoint": ep, "entries": []}
    if MANIFEST.exists():
        try:
            manifest["entries"] = json.loads(
                MANIFEST.read_text(encoding="utf-8")).get("entries", [])
        except Exception:  # noqa: BLE001
            pass
    by_path = {e["path"]: e for e in manifest["entries"]}
    for r in results:
        p = Path(r["path"])
        if r.get("ok") and p.is_file():
            entry = {"kind": r["kind"], "repo": r["repo"], "path": str(p),
                     "bytes": p.stat().st_size}
            if args.sha256:
                entry["sha256"] = sha256_of(p, limit_mib=64)
            by_path[str(p)] = entry
    manifest["entries"] = sorted(by_path.values(), key=lambda e: e["path"])
    MANIFEST.write_text(json.dumps(manifest, ensure_ascii=False, indent=2),
                        encoding="utf-8")
    log(f"manifest -> {MANIFEST}")

    log("=" * 62)
    bad = [r for r in results if not r.get("ok")]
    for r in results:
        flag = "OK " if r.get("ok") else "FAIL"
        extra = " (skipped)" if r.get("skipped") else ""
        log(f"  {flag} {r['kind']:10s} {human(r.get('bytes', 0)):>10s} {Path(r['path']).name}{extra}")
    log(f"结果: {len(results) - len(bad)}/{len(results)} 成功")
    return 0 if not bad else 1


if __name__ == "__main__":
    sys.exit(main())
