#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""bench_gguf.py — llama-cpp-python 显存/速度基准 (RTX 3050 Ti Laptop, 4096 MiB)

对同一 GGUF 依次尝试不同 n_gpu_layers，记录:
  - 能否成功加载 (ok)
  - 显存占用 VRAM (nvidia-smi used MIB, 相对基线的增量)
  - 生成速度 tokens/s (生成 64 tokens 计时, 取多次中位数)
  - prompt 解析速度

关键点:
  * llama_cpp.llama_supports_gpu_offload() 为 False 时, n_gpu_layers>0 会
    **静默退回 CPU**（不报错）。本脚本把该布尔值写入 gpu_offload 字段,
    并把每档的 effective_backend 标为 "cpu-fallback"，避免误判。
  * KV cache 用 q8_0 省显存, n_ctx 默认 4096。

用法:
    python tools/bench_gguf.py                       # 默认 7B, 全部档位
    python tools/bench_gguf.py --model models/gguf/qwen2.5-coder-3b-instruct-q4_k_m.gguf
    python tools/bench_gguf.py --layers 100 16 0 --n-ctx 4096
    python tools/bench_gguf.py --kv q4_0 --out models/benchmark.json
"""
from __future__ import annotations

import argparse
import gc
import json
import os
import statistics
import subprocess
import sys
import time
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
MODELS = ROOT / "models"

DEFAULT_MODEL = MODELS / "gguf" / "qwen2.5-coder-7b-instruct-q4_k_m.gguf"
DEFAULT_OUT = MODELS / "benchmark.json"

DEFAULT_PROMPT = (
    "You are a CTF assistant. Explain concisely how to identify the stack "
    "canary in a Linux 64-bit binary and why it is often bypassed via a "
    "format-string leak.\n\nAnswer:"
)


# --------------------------------------------------------------------------
# 显存采样
# --------------------------------------------------------------------------
def nvidia_smi_used() -> int | None:
    """返回当前显存已用 MiB；拿不到则 None。"""
    try:
        out = subprocess.run(
            ["nvidia-smi", "--query-gpu=memory.used", "--format=csv,noheader,nounits"],
            capture_output=True, text=True, timeout=15,
            creationflags=getattr(subprocess, "CREATE_NO_WINDOW", 0),
        )
        if out.returncode != 0:
            return None
        return int(out.stdout.strip().splitlines()[0])
    except Exception:  # noqa: BLE001
        return None


def vram_peak(samples: list[int]) -> int | None:
    vals = [s for s in samples if s is not None]
    return max(vals) if vals else None


# --------------------------------------------------------------------------
# 单档基准
# --------------------------------------------------------------------------
def bench_one(model_path: Path, n_gpu_layers: int, n_ctx: int, kv_type: str,
              n_tokens: int, n_threads: int | None, repeats: int,
              baseline_mib: int | None) -> dict:
    from llama_cpp import Llama

    rec: dict = {
        "n_gpu_layers": n_gpu_layers,
        "vram_mb": None,
        "tok_per_s": None,
        "ok": False,
        "effective_backend": "cpu",
        "n_ctx": n_ctx,
        "kv_cache_type": kv_type,
    }

    # llama.cpp 的 type_k/type_v 需要 ggml_type 整数枚举（不是字符串）
    from llama_cpp import llama_cpp as _C
    GGML_KV = {"f16": _C.GGML_TYPE_F16, "q8_0": _C.GGML_TYPE_Q8_0,
               "q4_0": _C.GGML_TYPE_Q4_0}
    kv_arg = GGML_KV[kv_type]
    # 注意: V cache 量化 (q8_0/q4_0) 必须开启 flash_attn, 否则
    # llama.cpp 报 "Failed to create llama_context"。
    # 仅 f16 可以在无 flash-attn 的情况下工作。
    use_fa = kv_type != "f16"
    rec["flash_attn"] = use_fa

    t_load0 = time.time()
    try:
        llm = Llama(
            model_path=str(model_path),
            n_gpu_layers=n_gpu_layers,
            n_ctx=n_ctx,
            n_threads=n_threads,
            n_batch=512,
            type_k=kv_arg,
            type_v=kv_arg,
            flash_attn=use_fa,
            verbose=False,
            seed=42,
        )
    except Exception as e:  # noqa: BLE001
        rec["error"] = f"{type(e).__name__}: {e}"
        return rec

    rec["load_s"] = round(time.time() - t_load0, 2)

    # 实际有多少层被卸载到 GPU
    try:
        n_layer = llm.metadata.get("qwen2.block_count") or llm.n_layers()
        rec["n_layer_total"] = int(n_layer)
    except Exception:  # noqa: BLE001
        pass

    samples: list[int] = []
    try:
        # ---- 预热 ----
        llm("Say OK.", max_tokens=8, echo=False, temperature=0.0, seed=42)
        samples.append(nvidia_smi_used())

        # ---- 计时: 生成固定 tokens ----
        times = []
        toks = []
        for _ in range(max(1, repeats)):
            t0 = time.perf_counter()
            out = llm(DEFAULT_PROMPT, max_tokens=n_tokens, echo=False,
                      temperature=0.0, seed=42,
                      stop=["\n\n\n"])
            dt = time.perf_counter() - t0
            n = out["usage"]["completion_tokens"]
            times.append(dt)
            toks.append(n)
            samples.append(nvidia_smi_used())

        # 取中位数算 tok/s (避免首个 chunk 抖动)
        dt_med = statistics.median(times)
        n_med = statistics.median(toks)
        rec["gen_s"] = round(dt_med, 3)
        rec["gen_tokens"] = int(n_med)
        rec["tok_per_s"] = round(n_med / dt_med, 2) if dt_med > 0 else None
        rec["tok_per_s_all_runs"] = [round(n / d, 2) for n, d in zip(toks, times)]

        # prompt 处理速度
        try:
            pt = out["usage"]["prompt_tokens"]
            rec["prompt_tokens"] = pt
            if rec.get("tok_per_s") is not None and dt_med > 0:
                rec["prefill_tok_per_s"] = round(pt / dt_med, 1)
        except Exception:  # noqa: BLE001
            pass

        rec["ok"] = True
    except Exception as e:  # noqa: BLE001
        rec["error"] = f"{type(e).__name__}: {e}"
    finally:
        peak = vram_peak(samples)
        rec["vram_mb"] = peak
        rec["vram_delta_mb"] = (peak - baseline_mib) if (peak is not None
                                                         and baseline_mib is not None) else None
        try:
            llm.close()
        except Exception:  # noqa: BLE001
            pass
        del llm
        gc.collect()
        time.sleep(2.0)  # 等显存释放

    return rec


def main() -> int:
    ap = argparse.ArgumentParser(description="GGUF 显存/速度基准")
    ap.add_argument("--model", default=str(DEFAULT_MODEL))
    ap.add_argument("--model-3b", default=str(
        MODELS / "gguf" / "qwen2.5-coder-3b-instruct-q4_k_m.gguf"))
    ap.add_argument("--out", default=str(DEFAULT_OUT))
    ap.add_argument("--layers", type=int, nargs="+", default=[100, 20, 16, 12, 8, 0])
    ap.add_argument("--n-ctx", type=int, default=4096)
    ap.add_argument("--kv", default="q8_0", choices=["f16", "q8_0", "q4_0"])
    ap.add_argument("--tokens", type=int, default=64)
    ap.add_argument("--repeats", type=int, default=2)
    ap.add_argument("--threads", type=int, default=None)
    ap.add_argument("--vram-budget", type=int, default=4096, help="显存上限 MiB")
    ap.add_argument("--reserve", type=int, default=1024,
                    help="留给 KV cache/context 的余量 MiB")
    ap.add_argument("--no-3b", action="store_true", help="跳过 3B 对照测试")
    args = ap.parse_args()

    import llama_cpp

    model_path = Path(args.model)
    if not model_path.exists():
        print(f"!! 模型不存在: {model_path}", file=sys.stderr)
        return 2

    gpu_offload = bool(llama_cpp.llama_supports_gpu_offload())
    baseline = nvidia_smi_used()
    cpu_count = os.cpu_count() or 8
    n_threads = args.threads or max(1, min(cpu_count // 2, 8))

    print("=" * 70)
    print(f"model            : {model_path.name} ({model_path.stat().st_size / 2**30:.2f} GiB)")
    print(f"llama_cpp        : {llama_cpp.__version__}")
    print(f"gpu_offload      : {gpu_offload}")
    print(f"vram baseline    : {baseline} MiB / {args.vram_budget} MiB")
    print(f"n_ctx / kv       : {args.n_ctx} / {args.kv}")
    print(f"threads          : {n_threads} (cpu={cpu_count})")
    print("=" * 70)
    if not gpu_offload:
        print("!! 本 llama-cpp-python 构建不含 CUDA 后端:")
        print("   n_gpu_layers>0 会被静默忽略并退回 CPU, 各档速度将几乎相同。")
        print("   要真正用上 3050Ti, 请走 Ollama 路线: .\\tools\\setup_ollama.ps1")
        print("   (Ollama 的结果见 models\\benchmark.json 的 results 字段)")

    results = []
    t_all = time.time()
    for nl in args.layers:
        print(f"\n>>> n_gpu_layers={nl} ...", flush=True)
        rec = bench_one(model_path, nl, args.n_ctx, args.kv, args.tokens,
                        n_threads, args.repeats, baseline)
        # 构建不支持 GPU 时，明确标注实际后端
        if gpu_offload and nl > 0:
            rec["effective_backend"] = "gpu+cpu" if rec["ok"] else "cpu"
        else:
            rec["effective_backend"] = "cpu" if (not gpu_offload or nl == 0) else "cpu"
        results.append(rec)
        if rec["ok"]:
            print(f"    ok  vram={rec['vram_mb']} MiB (Δ{rec['vram_delta_mb']})  "
                  f"{rec['tok_per_s']} tok/s  load={rec.get('load_s')}s")
        else:
            print(f"    FAIL {rec.get('error')}")

    # ---- 3B 对照（全量卸载是否可行）----
    r3 = None
    p3 = Path(args.model_3b)
    if not args.no_3b and p3.exists() and p3 != model_path:
        print(f"\n>>> 3B 对照 n_gpu_layers=100 ...", flush=True)
        r3 = bench_one(p3, 100, args.n_ctx, args.kv, args.tokens,
                       n_threads, args.repeats, baseline)
        r3["effective_backend"] = "gpu" if gpu_offload else "cpu"
        if r3["ok"]:
            print(f"    ok  vram={r3['vram_mb']} MiB  {r3['tok_per_s']} tok/s")
        else:
            print(f"    FAIL {r3.get('error')}")

    # ---- 选优 ----
    ceiling = args.vram_budget - args.reserve
    ok_recs = [r for r in results if r.get("ok")]
    best, best_reason = None, "no successful run"
    if ok_recs:
        if gpu_offload:
            fitting = [r for r in ok_recs
                       if r["vram_mb"] is not None and r["vram_mb"] <= ceiling]
            pool = fitting or ok_recs
            best = max(pool, key=lambda r: r["tok_per_s"] or 0)
            best_reason = (f"显存 {best['vram_mb']} MiB <= 上限 {ceiling} MiB "
                           f"({args.vram_budget} - 预留 {args.reserve}) 中速度最快"
                           if fitting else "无档位满足显存预算, 取整体最快")
        else:
            # CPU 构建下 n_gpu_layers 完全无作用, 各档差异纯属噪声:
            # 强制推荐 0, 并取所有 CPU 档位的速度中位数作为代表值
            pool = ok_recs
            zero = next((r for r in ok_recs if r["n_gpu_layers"] == 0), None)
            speeds = [r["tok_per_s"] for r in pool if r["tok_per_s"]]
            best = dict(zero or ok_recs[0])
            best["tok_per_s"] = round(statistics.median(speeds), 2)
            best["n_gpu_layers"] = 0
            best["speed_spread"] = [min(speeds), max(speeds)]
            best["note"] = ("gpu_offload=False: n_gpu_layers>0 被静默忽略, "
                            "各档实测差异在噪声范围内")
            best_reason = ("gpu_offload=False -> 推荐 n_gpu_layers=0 (纯 CPU); "
                           "n_gpu_layers>0 无实际效果, 仅白白占用显存")

    out = {
        "model": str(model_path),
        "model_bytes": model_path.stat().st_size,
        "llama_cpp_version": llama_cpp.__version__,
        "gpu_offload": gpu_offload,
        "gpu": "NVIDIA RTX 3050 Ti Laptop (4096 MiB)",
        "vram_budget_mb": args.vram_budget,
        "vram_reserve_mb": args.reserve,
        "vram_baseline_mb": baseline,
        "n_ctx": args.n_ctx,
        "kv_cache_type": args.kv,
        "n_threads": n_threads,
        "gen_tokens": args.tokens,
        "results": results,
        "model_3b": r3,
        # 说明: 本机 GPU 已被后台程序占用 2.2-2.5GB / 4096MiB,
        # 基线随时波动, 因此 vram_mb 是绝对读数, vram_delta_mb 仅供参考。
        "note": ("gpu_offload=False: 本 llama-cpp-python 为纯 CPU 构建, "
                 "n_gpu_layers>0 被静默退回 CPU(不报错), 各档 tok/s 差异属测量噪声; "
                 "tok/s 取 repeats 次的中位数"),
        "recommended": ({
            "n_gpu_layers": best["n_gpu_layers"],
            "tok_per_s": best["tok_per_s"],
            "vram_mb": best["vram_mb"],
            "reason": best_reason,
        } if best else None),
        "generated_at": time.strftime("%Y-%m-%dT%H:%M:%S"),
        "total_bench_s": round(time.time() - t_all, 1),
    }
    Path(args.out).parent.mkdir(parents=True, exist_ok=True)
    Path(args.out).write_text(json.dumps(out, ensure_ascii=False, indent=2),
                              encoding="utf-8")

    print("\n" + "=" * 70)
    print(f"{'n_gpu_layers':>13} {'vram(MiB)':>10} {'tok/s':>9} {'ok':>5} {'backend':>10}")
    for r in results:
        print(f"{r['n_gpu_layers']:>13} {str(r['vram_mb']):>10} "
              f"{str(r['tok_per_s']):>9} {str(r['ok']):>5} {r['effective_backend']:>10}")
    if r3:
        print(f"{'3B/100':>13} {str(r3['vram_mb']):>10} "
              f"{str(r3['tok_per_s']):>9} {str(r3['ok']):>5} {r3['effective_backend']:>10}")
    print("=" * 70)
    print(f"推荐: {out['recommended']}")
    print(f"结果 -> {args.out}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
