"""离线模拟原生流连接，保留请求和关闭记录。"""
import json


def mock_stream(monkeypatch, lines, status=200):
    class Response:
        closed = False
        def __init__(self):
            self.status = status
        def __iter__(self):
            yield from lines
        def read(self):
            return b'model error'
        def close(self):
            self.closed = True
    response = Response()
    sent = []
    class Socket:
        def dup(self):
            return self
        def shutdown(self, how):
            pass
        def close(self):
            pass
    class Connection:
        def __init__(self, host, port, **kwargs):
            self.host, self.port, self.sock = host, port, Socket()
        def connect(self):
            pass
        def request(self, method, path, body, headers):
            sent.append((f'http://{self.host}:{self.port}{path}', json.loads(body)))
        def getresponse(self):
            return response
        def close(self):
            pass
    monkeypatch.setattr('kb.llama_server.HTTPConnection', Connection)
    return response, sent
