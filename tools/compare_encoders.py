"""在同一正文与固定查询上比较 BGE 和旧 Qwen 编码器；不更新现用索引。"""
from __future__ import annotations

import argparse
from collections import defaultdict
from contextlib import contextmanager
import json
import os
from pathlib import Path
import platform
import socket
import statistics
import subprocess
import time

import numpy as np
import requests

from kb.config import Config
from kb.manifest import load, scan
from kb.parser import iter_docs
from kb.rag import KB
from kb.vectors import VectorIndex

ROOT = Path(__file__).resolve().parents[1]
QWEN_PREFIX = "Instruct: Given a CTF study question, retrieve relevant Chinese reference passages.\nQuery: "
SUITES = ("search_queries.json", "search_queries_expanded.json", "r1_quick_lookup.json")


def latency(values):
    ordered = sorted(values)
    return {"median_ms": round(statistics.median(ordered), 2),
            "p95_ms": round(ordered[min(len(ordered) - 1, int(0.95 * len(ordered)))], 2)}


def query_cases():
    result = []
    for name in SUITES:
        raw = json.loads((ROOT / "eval" / name).read_text(encoding="utf-8"))
        for row in raw["queries"] if isinstance(raw, dict) else raw:
            result.append((name, row.get("query") or row["q"], row["expected"], row.get("category")))
    raw = json.loads((ROOT / "eval/r52_real_cases.json").read_text(encoding="utf-8"))
    for case in raw["cases"]:
        for query in case["queries"]:
            result.append(("真题待复核", query["q"], [], query.get("category")))
    return result


class QwenEncoder:
    available = True

    def __init__(self, url, progress=None):
        self.url = url
        self.progress = progress
        self.session = requests.Session()
        self.session.trust_env = False

    def encode(self, texts, batch_size=12, is_query=False, show_progress=False):
        out = []
        texts = [QWEN_PREFIX + text for text in texts] if is_query else texts
        for i in range(0, len(texts), batch_size):
            response = self.session.post(self.url + "/v1/embeddings", json={
                "model": "r6-qwen", "input": texts[i:i+batch_size], "encoding_format": "float",
            }, timeout=120)
            if not response.ok:
                raise RuntimeError(f"Qwen 编码失败（HTTP {response.status_code}）：{response.text[:500]}")
            rows = sorted(response.json()["data"], key=lambda x: x["index"])
            values = np.array([row["embedding"] for row in rows], dtype=np.float32)
            norm = np.linalg.norm(values, axis=1, keepdims=True)
            if values.shape != (len(texts[i:i+batch_size]), 1024) or not np.isfinite(values).all() or not norm.all():
                raise RuntimeError("Qwen 返回的向量数量、维度或值不正确")
            out.append(values / norm)
            if self.progress and len(texts) > batch_size and i // batch_size % 100 == 0:
                self.progress(min(len(texts), i + batch_size), len(texts))
        return np.concatenate(out)


@contextmanager
def local_qwen(weights, executable, log_path, threads, device):
    with socket.socket() as sock:
        sock.bind(("127.0.0.1", 0))
        port = sock.getsockname()[1]
    url = f"http://127.0.0.1:{port}"
    flags = [str(executable), "-m", str(weights), "--host", "127.0.0.1",
             "--port", str(port), "--alias", "r6-qwen", "-c", "4096",
             "-t", str(threads), "-tb", str(threads), "-np", "1",
             "--embedding", "--pooling", "last", "-ub", "4096", "-b", "4096",
             "-ngl", "99" if device == "vulkan" else "0"]
    started = time.perf_counter()
    with log_path.open("wb") as log:
        process = subprocess.Popen(flags, cwd=executable.parent, stdout=log, stderr=log,
                                   stdin=subprocess.DEVNULL,
                                   creationflags=getattr(subprocess, "CREATE_NO_WINDOW", 0))
        try:
            while time.perf_counter() - started < 90:
                if process.poll() is not None:
                    raise RuntimeError(f"编码服务退出；查看 {log_path}")
                try:
                    if requests.get(url + "/health", timeout=1).ok:
                        break
                except requests.RequestException:
                    pass
                time.sleep(.15)
            else:
                raise RuntimeError(f"编码服务没有就绪；查看 {log_path}")
            yield QwenEncoder(url, lambda a, b: print(f"Qwen {a}/{b}", flush=True)), round(time.perf_counter()-started,3), process.pid
        finally:
            if process.poll() is None:
                process.terminate()
                process.wait(timeout=10)


def assess(kb, cases, retrieval):
    rows, samples = [], []
    for suite, query, expected, category in cases:
        start = time.perf_counter()
        hits = kb.search(query, top_k=5, category=category, retrieval=retrieval, expand=False)
        samples.append((time.perf_counter()-start)*1000)
        paths = [hit.doc_path for hit in hits]
        rank = next((i+1 for i, path in enumerate(paths) if path in expected), 0)
        rows.append({"suite": suite, "query": query, "expected": expected, "rank": rank, "paths": paths})
    groups = defaultdict(list)
    for row in rows:
        if row["expected"]:
            groups[row["suite"]].append(row["rank"])
    return {"summary": {suite: {"n":len(ranks), "top1": ranks.count(1), "top5":sum(bool(r) for r in ranks),
                                "mrr":round(sum(1/r if r else 0 for r in ranks)/len(ranks),4)}
                        for suite,ranks in groups.items()},
            "query_latency":latency(samples), "rows":rows}


def build(kb, encoder, cfg, docs, dest, batch):
    kb.vec = VectorIndex(dest, encoder)
    info = kb.vec.rebuild(docs, int(cfg.get("search", "chunk_chars", 900)),
                          int(cfg.get("search", "chunk_overlap", 120)), batch_size=batch)
    if not info["enabled"]:
        raise RuntimeError(f"编码器不可用：{info}")
    return {**info, "index_bytes":dest.stat().st_size}


def peak_mib(pid):
    if os.name != "nt":
        return None
    from ctypes import Structure, WinDLL, byref, c_size_t, c_ulong, c_void_p, sizeof

    class Counters(Structure):
        _fields_ = [("cb", c_ulong), ("faults", c_ulong)] + [
            (name, c_size_t) for name in ("peak", "working", "pool_peak", "pool", "nonpaged_peak",
                                         "nonpaged", "pagefile", "pagefile_peak")
        ]

    kernel = WinDLL("kernel32")
    kernel.OpenProcess.argtypes = [c_ulong, c_ulong, c_ulong]
    kernel.OpenProcess.restype = c_void_p
    kernel.CloseHandle.argtypes = [c_void_p]
    handle = kernel.OpenProcess(0x1010, False, pid)
    if not handle:
        return None
    try:
        info = Counters()
        info.cb = sizeof(info)
        psapi = WinDLL("psapi")
        psapi.GetProcessMemoryInfo.argtypes = [c_void_p, c_void_p, c_ulong]
        if psapi.GetProcessMemoryInfo(handle, byref(info), sizeof(info)):
            return round(info.peak / 2**20, 2)
        return None
    finally:
        kernel.CloseHandle(handle)


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--qwen", type=Path, required=True, help="旧库已下载的 Qwen3-Embedding GGUF")
    parser.add_argument("--device", choices=["cpu","vulkan"], default="cpu")
    parser.add_argument("--threads", type=int, default=4)
    parser.add_argument("--output", type=Path, required=True, help="项目 work 下的新结果目录")
    parser.add_argument("--reuse-indexes", type=Path, help="同一语料已完成的对照目录，只比较查询")
    args = parser.parse_args()
    out = args.output.resolve()
    if not out.is_relative_to((ROOT / "work").resolve()) or out == (ROOT / "work").resolve():
        parser.error("输出目录必须是本项目 work 的一个新子目录")
    weights = args.qwen.resolve(strict=True)
    out.mkdir(parents=True, exist_ok=False)
    os.environ["KB_ONNX_THREADS"] = str(args.threads)
    cfg = Config.load()
    manifest = load(cfg.index_dir / "manifest.json")
    if scan(cfg.kb_dir) != manifest:
        raise RuntimeError("当前关键词索引与语料不一致，先更新索引")
    docs = list(iter_docs(cfg.kb_dir))
    cases = query_cases()
    kb = KB(cfg)
    previous = None
    if args.reuse_indexes:
        reuse = args.reuse_indexes.resolve(strict=True)
        if not reuse.is_relative_to((ROOT / "work").resolve()):
            parser.error("对照索引应位于本项目 work 目录")
        previous = json.loads((reuse / "comparison.json").read_text(encoding="utf-8"))
        if previous.get("docs") != len(docs):
            raise RuntimeError("对照索引资料数已变化")
    report = {"platform":platform.platform(), "processor":platform.processor(), "threads":args.threads,
              "qwen_device":args.device, "docs":len(docs), "qwen_bytes":weights.stat().st_size,
              "fts":assess(kb,cases,"fts"), "reused_indexes":bool(previous)}
    started = time.perf_counter()
    kb.embedder.encode(["第一条编码"], is_query=True)
    report["bge_cold_seconds"] = round(time.perf_counter()-started,3)
    if previous:
        kb.vec = VectorIndex(reuse/"bge.db",kb.embedder)
        report["bge_index"] = previous["bge_index"]
    else:
        print("BGE 全量编码", flush=True)
        report["bge_index"] = build(kb,kb.embedder,cfg,docs,out/"bge.db",32)
    report["bge"] = assess(kb,cases,"hybrid")
    report["bge_process_peak_mib"] = peak_mib(os.getpid())
    (out/"bge-and-fts.json").write_text(json.dumps(report,ensure_ascii=False,indent=2),encoding="utf-8")
    print(report["bge_index"],flush=True)
    executable = cfg.resolve(cfg.get("llama_server", "runtime")) / "llama-server.exe"
    print("Qwen 查询复测" if previous else "Qwen 全量编码",flush=True)
    with local_qwen(weights,executable,out/"qwen.log",args.threads,args.device) as (encoder,cold,pid):
        started = time.perf_counter()
        encoder.encode(["第一条编码"],is_query=True)
        report["qwen_cold_seconds"] = round(cold + time.perf_counter()-started,3)
        if previous:
            kb.vec = VectorIndex(reuse/"qwen.db",encoder)
            report["qwen_index"] = previous["qwen_index"]
        else:
            report["qwen_index"] = build(kb,encoder,cfg,docs,out/"qwen.db",12)
        report["qwen"] = assess(kb,cases,"hybrid")
        report["qwen_process_peak_mib"] = peak_mib(pid)
    (out/"comparison.json").write_text(json.dumps(report,ensure_ascii=False,indent=2),encoding="utf-8")
    for key in ("fts","bge","qwen"):
        print(key,report[key]["summary"],report[key]["query_latency"],flush=True)
    print("结果：",out/"comparison.json",flush=True)


if __name__ == "__main__":
    main()
