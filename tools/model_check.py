"""模型准备与验收检查（不依赖具体下载过程，只做核对）。

- 检查嵌入模型与 GGUF 是否就位、大小是否合理
- 检查 Ollama 是否在线、模型 ID 能否解析
- 打印推荐配置（基于本机实测）

用法：
    python tools/model_check.py
    python tools/model_check.py --json
"""
from __future__ import annotations

import argparse
import json
import shutil
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "tools"))

from kb.config import Config  # noqa: E402

# 本机（RTX 3050 Ti Laptop 4GB / i5-12500H / 31.6GB RAM）实测数据
MEASURED = {
    "gpu": "NVIDIA GeForce RTX 3050 Ti Laptop GPU, 4096 MiB",
    "embed_backend": "numpy-bert (纯 NumPy BERT 前向，读 safetensors)",
    "embed_speed": "~80-100 ms / 条（300 字 chunk，12 线程 BLAS）",
    "llm_bench": [
        {"config": "Ollama 默认自动分配", "tok_s": 16.2, "vram_peak_mb": 3662},
        {"config": "Ollama num_gpu=16（推荐）", "tok_s": 18.2, "vram_peak_mb": None},
        {"config": "Ollama num_gpu=14", "tok_s": 13.9, "vram_peak_mb": 3752},
        {"config": "Ollama num_gpu=20（超显存，勿用）", "tok_s": 3.9, "vram_peak_mb": 3937},
        {"config": "Ollama num_gpu=0 纯 CPU", "tok_s": 9.7, "vram_peak_mb": 1562},
        {"config": "llama-cpp-python 直载 3B（pip wheel 无 CUDA）", "tok_s": 9.6, "vram_peak_mb": 0},
    ],
}


def human(n: float) -> str:
    return f"{n/1024**3:.2f} GB" if n > 1024**2 * 50 else f"{n/1024**2:.1f} MB"


def main(argv=None) -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--config", default=None)
    ap.add_argument("--json", action="store_true")
    args = ap.parse_args(argv)

    cfg = Config.load(args.config)
    report: dict = {"checks": [], "measured": MEASURED}

    def add(name: str, ok: bool, detail: str, level: str = "error"):
        report["checks"].append({"name": name, "ok": ok, "detail": detail,
                                 "level": "ok" if ok else level})

    # 1. 嵌入模型
    emb_dir = cfg.resolve(str(cfg.get("embed", "model_dir")))
    st = emb_dir / "model.safetensors"
    vocab = emb_dir / "vocab.txt"
    add("嵌入模型目录", emb_dir.exists(), str(emb_dir))
    add("嵌入权重 model.safetensors", st.exists(), human(st.stat().st_size) if st.exists() else "缺失")
    add("嵌入词表 vocab.txt", vocab.exists(), str(vocab))
    if st.exists():
        try:
            from kb.embedder import Embedder
            e = Embedder(emb_dir, str(cfg.get("embed", "query_prefix", "")))
            v = e.encode(["RSA 共模攻击"])
            add("嵌入推理自检", v.shape[1] > 0, f"dim={v.shape[1]} backend={e.backend}")
        except Exception as ex:  # noqa: BLE001
            add("嵌入推理自检", False, f"{type(ex).__name__}: {ex}")

    # 2. GGUF
    gguf = cfg.resolve(str(cfg.get("llm", "gguf_path")))
    add("主 GGUF", gguf.exists(),
        human(gguf.stat().st_size) if gguf.exists() else f"缺失: {gguf}", level="warn")
    for extra in (cfg.models_dir / "gguf").glob("*.gguf"):
        if extra != gguf:
            add(f"备用 GGUF: {extra.name}", True, human(extra.stat().st_size))

    # 3. Ollama
    host = str(cfg.get("ollama", "host", "http://127.0.0.1:11434"))
    try:
        import requests
        r = requests.get(f"{host}/api/tags", timeout=5)
        names = [m["name"] for m in r.json().get("models", [])]
        add("Ollama 服务", True, f"{host} 在线，模型 {names}")
        from kb.llm import OllamaBackend
        be = OllamaBackend(cfg)
        resolved = be.resolve_model()
        add("Ollama 模型解析", True, f"配置 {cfg.get('ollama','model')!r} -> 实际 ID {resolved!r}")
    except Exception as ex:  # noqa: BLE001
        add("Ollama 服务", False, f"{type(ex).__name__}: {ex}（运行 tools\\setup_ollama.ps1）",
            level="warn")

    # 4. GPU
    smi = shutil.which("nvidia-smi")
    if smi:
        try:
            r = subprocess.run([smi, "--query-gpu=name,memory.total,memory.used",
                                "--format=csv,noheader"], capture_output=True, text=True, timeout=10)
            add("GPU", True, r.stdout.strip())
        except Exception as ex:  # noqa: BLE001
            add("GPU", False, str(ex), level="warn")

    # 5. 索引
    fts_db = cfg.index_dir / "fts.db"
    add("FTS 索引", fts_db.exists(),
        human(fts_db.stat().st_size) if fts_db.exists() else "未建立（运行 kb index）")
    vec_db = cfg.index_dir / "vectors.db"
    add("向量索引", vec_db.exists(),
        human(vec_db.stat().st_size) if vec_db.exists() else "未建立", level="warn")

    if args.json:
        print(json.dumps(report, ensure_ascii=False, indent=2))
        return 0 if all(c["ok"] or c["level"] == "warn" for c in report["checks"]) else 1

    print("=== 模型与环境核对 ===\n")
    for c in report["checks"]:
        mark = "OK  " if c["ok"] else ("WARN" if c["level"] == "warn" else "FAIL")
        print(f"[{mark}] {c['name']:<26} {c['detail']}")

    print("\n=== 本机实测基准 ===")
    print(f"GPU: {MEASURED['gpu']}")
    print(f"嵌入: {MEASURED['embed_backend']}  {MEASURED['embed_speed']}")
    print("推理:")
    for b in MEASURED["llm_bench"]:
        vram = f"  显存峰值 {b['vram_peak_mb']} MB" if b["vram_peak_mb"] else ""
        print(f"  {b['config']:<40} {b['tok_s']:>5.1f} tok/s{vram}")
    print("\n结论：默认走 Ollama + num_gpu=16，能用上 3050Ti，约 18 tok/s。")
    bad = [c for c in report["checks"] if not c["ok"] and c["level"] != "warn"]
    return 0 if not bad else 1


if __name__ == "__main__":
    raise SystemExit(main())
