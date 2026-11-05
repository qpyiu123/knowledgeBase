import http.client
import json
import threading
import time

import pytest

from agent import server
from kb.config import Config
from mock_llama_server import MockLlama
from test_server_api import env, call, sse_events


@pytest.mark.parametrize('after_first', [False, True], ids=['before-first-byte', 'after-first-piece'])
def test_cancel_interrupts_native_connection_and_allows_next_ask(env, monkeypatch, after_first):
    with MockLlama() as native:
        cfg = Config()
        cfg.data['llama_server']['port'] = native.port
        cfg.data['llm'].update(backend='llama_server', timeout=10)
        monkeypatch.setattr(server, 'CFG', cfg)
        monkeypatch.delenv('KB_MODEL_PORT', raising=False)
        monkeypatch.delenv('KB_CHAT_MODEL', raising=False)
        marker = '首段后' if after_first else '首段前'
        first_piece = threading.Event()
        result = []
        def ask():
            connection = http.client.HTTPConnection('127.0.0.1', env['port'], timeout=10)
            try:
                body = json.dumps({'q': f'RSA【取消验收：{marker}】', 'paths': ['crypto/rsa.md'], 'request_id': 'cancel-one'})
                connection.request('POST', '/api/ask', body, {'Content-Type': 'application/json'})
                response = connection.getresponse()
                line = response.readline()
                if b'"tok"' in line:
                    first_piece.set()
                result.append((response.status, line.decode() + response.read().decode()))
            finally:
                connection.close()
        thread = threading.Thread(target=ask)
        thread.start()
        assert native.started.wait(3)
        if after_first:
            assert first_piece.wait(3)
        status, _, _ = call(env, 'POST', '/api/ask', {'q': 'busy', 'paths': ['crypto/rsa.md']})
        assert status == 429
        status, _, _ = call(env, 'POST', '/api/cancel', {'request_id': 'other-request'})
        assert status == 200 and not native.disconnected.is_set()
        started = time.perf_counter()
        status, text, _ = call(env, 'POST', '/api/cancel', {'request_id': 'cancel-one'})
        assert status == 200 and json.loads(text)['cancelled']
        assert time.perf_counter() - started < 2
        thread.join(timeout=2)
        assert not thread.is_alive() and native.disconnected.wait(2)
        events = sse_events(result[0][1])
        assert events[-1] == {'t': 'done', 'info': '已取消'}
        assert not any(e['t'] == 'err' for e in events)
        assert sum(e['t'] == 'tok' for e in events) == int(after_first)
        status, text, _ = call(env, 'POST', '/api/ask', {'q': 'RSA', 'paths': ['crypto/rsa.md'], 'request_id': 'next-one'})
        assert status == 200 and [e['t'] for e in sse_events(text)] == ['tok', 'done']


def test_early_cancel_prevents_generation(env, monkeypatch):
    monkeypatch.setattr('requests.post', lambda *a, **k: pytest.fail('已取消的请求不得开始生成'))
    status, _, _ = call(env, 'POST', '/api/cancel', {'request_id': 'early-cancel'})
    assert status == 200
    status, text, _ = call(env, 'POST', '/api/ask', {'q': 'RSA', 'paths': ['crypto/rsa.md'], 'request_id': 'early-cancel'})
    assert status == 200
    assert sse_events(text) == [{'t': 'done', 'info': '已取消'}]


@pytest.mark.parametrize('payload', [{}, {'request_id': '../bad'}, {'request_id': 123}])
def test_cancel_validates_request_id(env, payload):
    status, _, _ = call(env, 'POST', '/api/cancel', payload)
    assert status == 400
