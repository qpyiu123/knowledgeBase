"""启动项目内的 Qwen3.5 Vulkan 服务，不下载文件、不停止其他服务。"""
from __future__ import annotations

import argparse
import json
import os
import socket
import subprocess
import sys
import time
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'tools'))

from kb.config import Config
from kb.llama_server import MODELS, LlamaServerBackend, model_id, base_url


def command(cfg, cpu=False):
    model = model_id(cfg)
    runtime = cfg.resolve(str(cfg.get('llama_server', 'runtime', 'runtime/llama-b11669-vulkan')))
    weights = cfg.resolve('models/gguf/' + MODELS[model])
    args = [str(runtime / 'llama-server.exe'), '-m', str(weights), '--alias', model,
            '--host', '127.0.0.1', '--port', base_url(cfg).rsplit(':', 1)[1],
            '-c', str(cfg.get('llm', 'n_ctx', 8192)), '-t', str(cfg.get('llm', 'n_threads', 6)),
            '-np', '1', '-ngl', '0' if cpu else str(cfg.get('llm', 'n_gpu_layers', 99)), '--jinja',
            '--cors-origins', 'localhost', '--no-webui', '--no-agent']
    device = cfg.get('llama_server', 'device', 'auto')
    if not cpu and device != 'auto':
        args += ['--device', str(device)]
    return args


def start(cfg, log_dir: Path, cpu=False, timeout=120):
    backend = LlamaServerBackend(cfg)
    port = int(base_url(cfg).rsplit(':', 1)[1])
    with socket.socket() as check:
        if check.connect_ex(('127.0.0.1', port)) == 0:
            ok, detail = backend.health()
            if not ok:
                raise RuntimeError(f'端口 {port} 已被占用：{detail}')
            return {'ok': True, 'reused': True, 'model': backend.model}
    args = command(cfg, cpu)
    if not Path(args[2]).is_file():
        raise FileNotFoundError(f'缺少所选模型 {backend.model}：{args[2]}；请选择已保留的模型，或用 -NoModel 仅查询')
    if not Path(args[0]).is_file():
        raise FileNotFoundError(f'缺少 Vulkan 运行文件：{args[0]}；请复制完整运行目录，或用 -NoModel 仅查询')
    log_dir.mkdir(parents=True, exist_ok=True)
    environment = {k: v for k, v in os.environ.items() if not k.startswith('LLAMA_ARG_')}
    with (log_dir / 'llama.log').open('ab') as log:
        process = subprocess.Popen(args, cwd=Path(args[0]).parent, stdin=subprocess.DEVNULL,
                                   stdout=log, stderr=subprocess.STDOUT, env=environment,
                                   creationflags=getattr(subprocess, 'CREATE_NO_WINDOW', 0))
    (log_dir / 'llama.pid').write_text(str(process.pid), encoding='ascii')
    deadline = time.monotonic() + timeout
    try:
        while time.monotonic() < deadline:
            if process.poll() is not None:
                raise RuntimeError(f'模型服务退出，代码 {process.returncode}；查看 {log_dir / "llama.log"}')
            ok, detail = backend.health()
            if ok:
                return {'ok': True, 'model': backend.model, 'pid': process.pid,
                        'backend': 'cpu' if cpu else 'vulkan', 'url': backend.host}
            time.sleep(0.5)
        raise RuntimeError(f'模型加载超时：{detail}；查看 {log_dir / "llama.log"}')
    except BaseException:
        if process.poll() is None:
            process.terminate()
            process.wait(timeout=10)
        raise


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('action', choices=['start', 'status', 'command'])
    parser.add_argument('--model', choices=list(MODELS))
    parser.add_argument('--cpu', action='store_true')
    parser.add_argument('--log-dir', type=Path, default=ROOT / 'logs')
    args = parser.parse_args()
    if args.model:
        os.environ['KB_CHAT_MODEL'] = args.model
    cfg = Config.load()
    if args.action == 'command':
        result = {'command': command(cfg, args.cpu), 'model': model_id(cfg),
                  'backend': cfg.get('llm', 'backend', 'llama_server')}
    elif args.action == 'start':
        result = start(cfg, args.log_dir, args.cpu)
    else:
        ok, detail = LlamaServerBackend(cfg).health()
        result = {'ok': ok, 'detail': detail, 'model': model_id(cfg)}
    print(json.dumps(result, ensure_ascii=False))
    return 0


if __name__ == '__main__':
    sys.stdout.reconfigure(encoding='utf-8')
    raise SystemExit(main())
