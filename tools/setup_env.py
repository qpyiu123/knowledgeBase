#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""setup_env.py — 环境安装器 (Python 版, 与 setup_env.ps1 等价)

为什么要这个脚本:
  tools/setup_env.ps1 需要 pwsh 7。本机有些自动化入口只能调 python,
  所以这里给一份等价的纯 Python 实现。

用法:
    python tools/setup_env.py                  # venv + 依赖 + 模型
    python tools/setup_env.py --models         # 只跑模型下载 (调 fetch_models.py)
    python tools/setup_env.py --check          # 只校验 (依赖 + 模型)
    python tools/setup_env.py --no-models      # 只装依赖
    python tools/setup_env.py --mirror         # 模型走 hf-mirror.com
    python tools/setup_env.py --with-torch     # 额外尝试 sentence-transformers
    python tools/setup_env.py --ollama         # 额外跑 Ollama (GPU 路线)
    python tools/setup_env.py --venv D:\\x\\.venv --python C:\\Python314\\python.exe

说明:
  * Python 3.14 在 PyPI 上没有 llama-cpp-python 的 wheel, 必须用
    abetlen 的 wheel 索引 (https://abetlen.github.io/llama-cpp-python/whl/cpu)。
  * torch / sentence-transformers 在 3.14 上通常装不上; 嵌入默认走
    onnxruntime + tokenizers (零 torch), 备份方案是 llama.cpp 加载 BGE GGUF。
"""
from __future__ import annotations

import argparse
import os
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
TOOLS = ROOT / "tools"

# Windows 控制台默认 gbk, 中文会乱码/丢字符
os.environ.setdefault("PYTHONIOENCODING", "utf-8")
for _s in (sys.stdout, sys.stderr):
    try:
        _s.reconfigure(encoding="utf-8", errors="replace")
    except Exception:  # noqa: BLE001
        pass

PIP_INDEX = "https://mirrors.tuna.tsinghua.edu.cn/pypi/web/simple"
LLAMA_WHEEL_IDX = "https://abetlen.github.io/llama-cpp-python/whl/cpu"

BASE_PKGS = ["numpy", "requests", "pyyaml", "huggingface_hub"]
OPTIONAL_PKGS = ["sqlite-vec", "onnxruntime", "tokenizers"]


def say(msg: str = "") -> None:
    print(msg, flush=True)


def ok(msg: str) -> None:
    print(f"  [OK]   {msg}", flush=True)


def warn(msg: str) -> None:
    print(f"  [WARN] {msg}", flush=True)


def err(msg: str) -> None:
    print(f"  [ERR]  {msg}", flush=True)


def run(cmd: list[str], quiet: bool = False) -> int:
    env = os.environ.copy()
    env.setdefault("PYTHONIOENCODING", "utf-8")
    env.setdefault("PIP_DISABLE_PIP_VERSION_CHECK", "1")
    env.setdefault("HF_HUB_DISABLE_SYMLINKS_WARNING", "1")
    if quiet:
        return subprocess.call(cmd, env=env,
                               stdout=subprocess.DEVNULL,
                               stderr=subprocess.DEVNULL)
    return subprocess.call(cmd, env=env)


def py(venv_py: Path, *args: str, quiet: bool = False) -> int:
    return run([str(venv_py), *args], quiet=quiet)


def has_module(venv_py: Path, name: str) -> bool:
    return py(venv_py, "-c", f"import {name}", quiet=True) == 0


def pylib(venv_py: Path, code: str) -> str:
    try:
        out = subprocess.run([str(venv_py), "-c", code], capture_output=True,
                             text=True, timeout=120)
        return out.stdout.strip()
    except Exception:  # noqa: BLE001
        return ""


# ---------------------------------------------------------------- venv
def ensure_venv(venv: Path, base_python: str) -> Path:
    venv_py = venv / "Scripts" / "python.exe"
    if venv_py.exists():
        v = pylib(venv_py, "import sys;print(sys.version.split()[0])")
        ok(f"复用已有 venv (Python {v})")
        return venv_py
    if not Path(base_python).exists():
        raise SystemExit(f"找不到 Python 解释器: {base_python}")
    say("  创建 venv ...")
    if run([base_python, "-m", "venv", str(venv)]) != 0:
        raise SystemExit("venv 创建失败")
    ok(f"venv 已创建: {venv}")
    return venv_py


# ---------------------------------------------------------------- 依赖
def install_deps(venv_py: Path, with_torch: bool) -> None:
    say("")
    say("=== 依赖 ===")
    py(venv_py, "-m", "pip", "install", "-q", "--upgrade", "pip", quiet=True)

    say(f"  pip install {', '.join(BASE_PKGS + OPTIONAL_PKGS)}")
    cmd = [str(venv_py), "-m", "pip", "install", "-q", "--only-binary=:all:",
           "-i", PIP_INDEX, *BASE_PKGS, *OPTIONAL_PKGS]
    if run(cmd, quiet=True) != 0:
        warn("有包无 cp314 wheel, 回退逐个安装")
        for p in BASE_PKGS + OPTIONAL_PKGS:
            if run([str(venv_py), "-m", "pip", "install", "-q",
                    "--only-binary=:all:", "-i", PIP_INDEX, p], quiet=True) != 0:
                warn(f"  {p} 安装失败 (可能无 3.14 wheel)")

    for m in ["numpy", "requests", "huggingface_hub", "yaml"]:
        (ok if has_module(venv_py, m) else err)(f"import {m}")
    for m in ["sqlite_vec", "onnxruntime", "tokenizers"]:
        ok(f"import {m}") if has_module(venv_py, m) else warn(f"{m} 不可用 (不阻塞)")

    # ---- llama-cpp-python ----
    say("")
    say("=== llama-cpp-python ===")
    if has_module(venv_py, "llama_cpp"):
        v = pylib(venv_py, "import llama_cpp;print(llama_cpp.__version__)")
        ok(f"已安装 llama_cpp {v}")
    else:
        say("  尝试清华镜像 (PyPI) ...")
        run([str(venv_py), "-m", "pip", "install", "-q", "--only-binary=:all:",
             "-i", PIP_INDEX, "llama-cpp-python"], quiet=True)
        if not has_module(venv_py, "llama_cpp"):
            warn("PyPI 无 cp314 wheel — 改用 abetlen wheel 索引")
            run([str(venv_py), "-m", "pip", "install", "--only-binary=:all:",
                 "-i", PIP_INDEX, "--extra-index-url", LLAMA_WHEEL_IDX,
                 "llama-cpp-python"], quiet=True)
        if has_module(venv_py, "llama_cpp"):
            v = pylib(venv_py, "import llama_cpp;print(llama_cpp.__version__)")
            ok(f"llama_cpp {v} 安装成功")
        else:
            err("llama-cpp-python 安装失败")

    # ---- 可选 torch ----
    if with_torch:
        say("")
        say("=== sentence-transformers (可选, 会拉 ~2.5GB torch) ===")
        run([str(venv_py), "-m", "pip", "install", "-q", "--only-binary=:all:",
             "-i", PIP_INDEX, "sentence-transformers", "torch"], quiet=True)
        ok("sentence_transformers 可用") if has_module(venv_py, "sentence_transformers") \
            else warn("sentence-transformers 装不上 — 用 ONNX / GGUF 嵌入后端")


# ---------------------------------------------------------------- 模型
def run_models(venv_py: Path, mirror: bool, check_only: bool) -> int:
    say("")
    say("=== 模型 ===")
    fetch = TOOLS / "fetch_models.py"
    if not fetch.exists():
        err(f"找不到 {fetch}")
        return 2
    args = [str(venv_py), "-u", str(fetch)]
    if check_only:
        args.append("--check")
    if mirror:
        args.append("--mirror")
    return run(args)


# ---------------------------------------------------------------- ollama
def run_ollama() -> int:
    say("")
    say("=== Ollama (GPU 路线) ===")
    ps1 = TOOLS / "setup_ollama.ps1"
    if not ps1.exists():
        warn(f"找不到 {ps1}")
        return 2
    argv = [str(ps1)]
    if has_pwsh():
        return run(["pwsh", "-NoProfile", "-File", *argv])
    return run(["powershell", "-NoProfile", "-ExecutionPolicy", "Bypass",
                "-File", *argv])


def has_pwsh() -> bool:
    from shutil import which
    return which("pwsh") is not None


# ---------------------------------------------------------------- 自检
def self_check(venv_py: Path) -> None:
    say("")
    say("=== 自检 ===")
    print(run([str(venv_py), "-m", "pip", "list"]))
    gpu = pylib(venv_py,
                "import llama_cpp;print(llama_cpp.llama_supports_gpu_offload())")
    say(f"  llama_supports_gpu_offload() = {gpu}")
    if gpu != "True":
        say("  (False = llama-cpp-python 为纯 CPU 构建, n_gpu_layers 会被忽略;"
            " 需要 GPU 请用 --ollama)")


def main() -> int:
    ap = argparse.ArgumentParser(description="CTF KB 环境安装器")
    ap.add_argument("--venv", default=str(ROOT / ".venv"))
    ap.add_argument("--python", default=r"C:\Python314\python.exe")
    ap.add_argument("--models", action="store_true", help="只跑模型下载")
    ap.add_argument("--no-models", action="store_true", help="只装依赖")
    ap.add_argument("--check", action="store_true", help="只校验")
    ap.add_argument("--mirror", action="store_true", help="模型走 hf-mirror.com")
    ap.add_argument("--with-torch", action="store_true")
    ap.add_argument("--ollama", action="store_true")
    ap.add_argument("--no-deps", action="store_true")
    args = ap.parse_args()

    venv = Path(args.venv).resolve()
    say("CTF knowledge base — 环境安装")
    say(f"  ROOT : {ROOT}")
    say(f"  VENV : {venv}")

    venv_py = venv / "Scripts" / "python.exe"
    if args.check:
        if not venv_py.exists():
            err("venv 不存在")
            return 1
        rc = run_models(venv_py, args.mirror, check_only=True)
        self_check(venv_py)
        return rc

    if not args.models:
        venv_py = ensure_venv(venv, args.python)
        if not args.no_deps:
            install_deps(venv_py, args.with_torch)
    else:
        if not venv_py.exists():
            venv_py = ensure_venv(venv, args.python)

    rc = 0
    if not args.no_models:
        rc = run_models(venv_py, args.mirror, check_only=False)

    if args.ollama:
        run_ollama()

    self_check(venv_py)
    say("")
    say(f"完成 (models rc={rc})")
    return rc


if __name__ == "__main__":
    sys.exit(main())
