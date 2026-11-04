"""R0 实际索引的 HTTP 检查：不开生成模型，搜索、阅读并保存题目记录。"""
from __future__ import annotations

import json
import os
import threading
from http.server import ThreadingHTTPServer
from pathlib import Path
from unittest.mock import patch
from urllib.request import Request, urlopen

from agent import server

ROOT = Path(__file__).resolve().parents[1]


def main() -> int:
    # 使用独立测试工作区，不碰个人题目记录。
    os.environ["AGENT_WORKSPACE_DIR"] = str(ROOT / "work/r0/http-workspaces")
    with patch("requests.post", side_effect=AssertionError("离线查询不应调用生成服务")):
        httpd = ThreadingHTTPServer(("127.0.0.1", 0), server.Handler)
        thread = threading.Thread(target=httpd.serve_forever, daemon=True)
        thread.start()
        base = f"http://127.0.0.1:{httpd.server_port}"

        def call(path, body=None):
            req = Request(base + path, data=None if body is None else json.dumps(body).encode(),
                          headers={"Content-Type": "application/json"})
            with urlopen(req, timeout=30) as response:
                return json.loads(response.read())

        try:
            with urlopen(base, timeout=10) as response:
                assert response.status == 200 and b'<html' in response.read().lower()
            hits = call('/api/search', {"q": "用户名欢迎语 7*7 回显 49", "top_k": 10, "retrieval": "fts"})['hits']
            assert any(h['path'] == '_methods/ssti_generic.md' for h in hits), hits
            doc = call('/api/doc?path=_methods/ssti_generic.md')
            assert '前置条件' in doc['body']
            assert doc['scripts'][0]['path'] == '_methods/scripts/ssti_generic.py'
            code = call('/api/code?path=_methods/scripts/ssti_generic.py')
            assert '--selftest' in code['arguments']
            created = call('/api/workspaces', {"title": "R0 离线检查"})
            wid = created['workspace']['id']
            call(f'/api/workspaces/{wid}/entries', {"kind": "fact", "text": "7*7 回显 49"})
            saved = call(f'/api/workspaces/{wid}')
            assert saved['workspace']['entries'][0]['text'] == '7*7 回显 49'
            print(json.dumps({"ok": True, "search": len(hits), "document": doc['path'],
                              "workspace": wid, "generation_calls": 0}, ensure_ascii=False))
        finally:
            httpd.shutdown()
            httpd.server_close()
            thread.join()
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
