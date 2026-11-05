"""管理本网页进程启动的单个推理实例。读取状态不会加载权重。"""
from __future__ import annotations

import os
from pathlib import Path
import socket
import threading


class ModelControl:
    def __init__(self, log_dir):
        self.log_dir = Path(log_dir)
        self._lock = threading.Lock()
        self._process = None
        self._config = None
        self._ready = False
        self._error = ""

    def status(self):
        from kb.llama_server import model_id

        with self._lock:
            active = self._process is not None and self._process.poll() is None
            return {"state": ("ready" if self._ready else "loading") if active else "stopped",
                    "model": model_id(self._config) if active else None,
                    "pid": self._process.pid if active else None, "error": self._error}

    def prepare(self, config, allow_start=True, cancelled=None):
        from kb.llama_server import LlamaServerBackend
        from llama_runtime import spawn, wait_ready

        with self._lock:
            if cancelled is not None and cancelled.is_set():
                raise RuntimeError("已取消")
            if self._process is not None and self._process.poll() is None:
                if self._ready:
                    return self._config
                raise RuntimeError("正在启动，请稍后再试")
            backend = LlamaServerBackend(config)
            port = int(backend.host.rsplit(":", 1)[1])
            with socket.socket() as check:
                check.settimeout(0.3)
                occupied = check.connect_ex(("127.0.0.1", port)) == 0
            if occupied:
                ok, detail = backend.health()
                if ok:
                    return config
                raise RuntimeError(f"推理端口 {port} 已被占用：{detail}")
            if not allow_start:
                raise RuntimeError("请先在设置中启动")
            cpu = os.environ.get("KB_CPU_ONLY") == "1" or config.get("llama_server", "compute") == "cpu"
            try:
                process = spawn(config, self.log_dir, cpu)
            except Exception as error:
                self._error = str(error)
                raise
            self._process, self._config, self._ready, self._error = process, config, False, ""
        try:
            wait_ready(process, backend, self.log_dir, cpu, cancelled=cancelled)
            with self._lock:
                if self._process is not process or process.poll() is not None:
                    raise RuntimeError("启动已取消")
                self._ready = True
            return config
        except Exception as error:
            with self._lock:
                if self._process is process:
                    self._error = str(error)
                    self._clear(process)
            raise

    def _clear(self, process):
        self._process = self._config = None
        self._ready = False
        pid = self.log_dir / "llama.pid"
        if pid.is_file() and pid.read_text(encoding="ascii").strip() == str(process.pid):
            pid.unlink()

    def stop(self):
        with self._lock:
            process = self._process
            if process is not None:
                if process.poll() is None:
                    process.terminate()
                    process.wait(timeout=10)
                self._clear(process)
            self._error = ""
