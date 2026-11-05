"""用完整 Qwen3.5 权重做短 CPU/Vulkan 查询，关闭本次创建的进程。"""
from __future__ import annotations

import json
import argparse
import os
import socket
import subprocess
import sys
import time
from pathlib import Path
from unittest.mock import patch

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'tools'))

from kb.config import Config
from kb.llama_server import LlamaServerBackend
from llama_runtime import start

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--vulkan', action='store_true')
    parser.add_argument('--device', default='auto')
    args = parser.parse_args()
    out = ROOT / 'work/r32'
    out.mkdir(parents=True, exist_ok=True)
    real_popen = subprocess.Popen
    results = []
    for model in ('qwen35-9b', 'qwen35-4b'):
        with socket.socket() as sock:
            sock.bind(('127.0.0.1', 0))
            port = sock.getsockname()[1]
        cfg = Config.load()
        cfg.data['llm'].update(n_ctx=2048, max_tokens=16, timeout=180)
        cfg.data['llama_server']['device'] = args.device
        owned = []
        def spawn(*args, **kwargs):
            proc = real_popen(*args, **kwargs)
            owned.append(proc)
            return proc
        with patch.dict(os.environ, {'KB_CHAT_MODEL': model, 'KB_MODEL_PORT': str(port)}), \
                patch('llama_runtime.subprocess.Popen', side_effect=spawn):
            try:
                t0 = time.perf_counter()
                status = start(cfg, out / (model + ('-vulkan' if args.vulkan else '')), cpu=not args.vulkan, timeout=180)
                assert status['ok'] and not status.get('reused') and owned
                loaded_ms = round((time.perf_counter() - t0) * 1000, 1)
                backend = LlamaServerBackend(cfg)
                answer = backend.chat([{'role': 'user', 'content': '只回答两个汉字：可用'}])
                assert answer.text.strip()
                parts = list(backend.stream([{'role': 'user', 'content': '只回答：OK'}]))
                assert ''.join(parts).strip()
                results.append({'model': model, 'cpu': not args.vulkan, 'device': args.device, 'context': 2048, 'load_ms': loaded_ms,
                                'text': answer.text, 'completion_tokens': answer.completion_tokens,
                                'tokens_per_sec': answer.tokens_per_sec, 'stream_text': ''.join(parts)})
            finally:
                # 只使用本脚本直接取得的 Popen 对象，关闭本次创建的子进程。
                for process in owned:
                    if process.poll() is None:
                        process.terminate()
                        process.wait(timeout=15)
    report = {'ok': True, 'python': sys.version.split()[0], 'models': results,
              'own_processes_stopped': True, 'vulkan_inference_tested': args.vulkan}
    (out / ('real-models-vulkan.json' if args.vulkan else 'real-models.json')).write_text(json.dumps(report, ensure_ascii=False, indent=2), encoding='utf-8')
    print(json.dumps(report, ensure_ascii=False))
    return 0


if __name__ == '__main__':
    sys.stdout.reconfigure(encoding='utf-8')
    raise SystemExit(main())
