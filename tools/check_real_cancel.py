"""独立启动 4B，检查首段前取消与下一次正常请求，只关闭本次子进程。"""
from __future__ import annotations

import json
import os
import socket
import subprocess
import sys
import threading
import time
import uuid
from pathlib import Path
from unittest.mock import patch

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'tools'))

from kb.config import Config
from kb.llama_server import LlamaServerBackend
from llama_runtime import start


def main():
    out = ROOT / 'work/r33' / ('native-' + uuid.uuid4().hex[:8])
    out.mkdir(parents=True)
    with socket.socket() as sock:
        sock.bind(('127.0.0.1', 0))
        port = sock.getsockname()[1]
    cfg = Config.load()
    cfg.data['llm'].update(n_ctx=4096, max_tokens=512, timeout=30)
    cfg.data['llama_server']['device'] = 'Vulkan0'
    owned, pieces, errors = [], [], []
    real_popen = subprocess.Popen
    def spawn(*args, **kwargs):
        process = real_popen(*args, **kwargs)
        owned.append(process)
        return process
    with patch.dict(os.environ, {'KB_CHAT_MODEL': 'qwen35-4b', 'KB_MODEL_PORT': str(port)}), \
            patch('llama_runtime.subprocess.Popen', side_effect=spawn):
        backend = LlamaServerBackend(cfg)
        thread = None
        try:
            status = start(cfg, out, cpu=False)
            assert status['ok'] and owned and not status.get('reused')
            prompt = '请逐项分析这些固定示例资料，再列出三百项检查。\n' + '这是待查资料，包含十进制参数和字节编码。\n' * 80
            def generate():
                try:
                    pieces.extend(backend.stream([{'role': 'user', 'content': prompt}]))
                except Exception as error:
                    errors.append(str(error))
            thread = threading.Thread(target=generate)
            thread.start()
            deadline = time.monotonic() + 10
            while backend._socket is None and thread.is_alive() and time.monotonic() < deadline:
                time.sleep(.005)
            assert backend._socket is not None
            time.sleep(.1)
            before_first = not pieces
            t0 = time.perf_counter()
            backend.cancel()
            thread.join(timeout=3)
            cancelled_ms = round((time.perf_counter() - t0) * 1000, 1)
            assert not thread.is_alive() and not errors, errors
            t0 = time.perf_counter()
            next_answer = LlamaServerBackend(cfg).chat([{'role': 'user', 'content': '只回答：OK'}], max_tokens=8)
            next_ms = round((time.perf_counter() - t0) * 1000, 1)
            assert next_answer.text.strip()
            result = {'ok': True, 'model': 'qwen35-4b', 'device': 'RTX 4070 / Vulkan0', 'context': 4096,
                      'cancelled_before_first_piece': before_first, 'cancel_ms': cancelled_ms,
                      'pieces_before_cancel': len(pieces), 'next_request_ms': next_ms, 'next_text': next_answer.text}
            (ROOT / 'work/r33/real-cancel.json').write_text(json.dumps(result, ensure_ascii=False, indent=2), encoding='utf-8')
            print(json.dumps(result, ensure_ascii=False))
        finally:
            backend.cancel()
            if thread is not None:
                thread.join(timeout=3)
            for process in owned:
                if process.poll() is None:
                    process.terminate()
                    process.wait(timeout=15)
    return 0


if __name__ == '__main__':
    sys.stdout.reconfigure(encoding='utf-8')
    raise SystemExit(main())
