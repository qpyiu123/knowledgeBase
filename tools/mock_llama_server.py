"""开发检查用模型替身：模拟首段前等待和首段后等待，不加载模型。"""
from __future__ import annotations

import json
import select
import threading
import time
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer


class MockLlama:
    def __init__(self):
        owner = self
        self.started = threading.Event()
        self.disconnected = threading.Event()
        self.posts = []
        class Handler(BaseHTTPRequestHandler):
            def log_message(self, *args):
                pass
            def json(self, payload):
                data = json.dumps(payload).encode()
                self.send_response(200)
                self.send_header('Content-Length', str(len(data)))
                self.end_headers()
                self.wfile.write(data)
            def do_GET(self):
                self.json({'data': [{'id': 'qwen35-9b'}]} if self.path == '/v1/models' else {'status': 'ok'})
            def do_POST(self):
                data = json.loads(self.rfile.read(int(self.headers['Content-Length'])))
                owner.posts.append(data)
                content = data['messages'][-1]['content']
                slow = '【取消验收：' in content
                after_first = '【取消验收：首段后】' in content
                if not slow or after_first:
                    self.send_response(200)
                    self.send_header('Content-Type', 'text/event-stream')
                    self.send_header('Connection', 'close')
                    self.end_headers()
                    self.wfile.write(('data: ' + json.dumps({'choices': [{'delta': {'content': '第一段'}}]}) + '\n\n').encode())
                    self.wfile.flush()
                owner.started.set()
                if slow:
                    deadline = time.monotonic() + 15
                    while time.monotonic() < deadline:
                        ready, _, _ = select.select([self.connection], [], [], .02)
                        if ready:
                            try:
                                if not self.connection.recv(1):
                                    owner.disconnected.set()
                                    return
                            except OSError:
                                owner.disconnected.set()
                                return
                    return
                self.wfile.write(b'data: [DONE]\n\n')
                self.wfile.flush()
        self.server = ThreadingHTTPServer(('127.0.0.1', 0), Handler)
        self.server.daemon_threads = True
        self.port = self.server.server_port
        self.thread = threading.Thread(target=self.server.serve_forever, daemon=True)
    def __enter__(self):
        self.thread.start()
        return self
    def __exit__(self, *args):
        self.server.shutdown()
        self.server.server_close()
        self.thread.join()
