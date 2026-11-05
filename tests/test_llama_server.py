import json

import pytest

from kb.config import Config
from kb.llama_server import LlamaServerBackend, model_id
from kb.llm import LLMError, get_backend
from llama_runtime import command


class Response:
    status_code = 200
    def __init__(self, data=None, lines=()):
        self.data, self.lines, self.closed = data, lines, False
    def json(self):
        return self.data
    def raise_for_status(self):
        pass
    def iter_lines(self):
        yield from self.lines
    def close(self):
        self.closed = True


@pytest.fixture()
def cfg(monkeypatch):
    monkeypatch.delenv('KB_CHAT_MODEL', raising=False)
    monkeypatch.delenv('KB_MODEL_PORT', raising=False)
    cfg = Config()
    cfg.data['llm']['backend'] = 'llama_server'
    cfg.data['llama_server'] = {'model': 'qwen35-9b', 'port': 8766}
    return cfg


@pytest.fixture()
def backend(cfg, monkeypatch):
    monkeypatch.setattr('requests.get', lambda url, **_: Response({'data': [{'id': 'qwen35-9b'}]}))
    return LlamaServerBackend(cfg)


def test_factory_and_explicit_4b_override(cfg, monkeypatch):
    assert get_backend(cfg).model == 'qwen35-9b'
    monkeypatch.setenv('KB_CHAT_MODEL', 'qwen35-4b')
    assert model_id(cfg) == 'qwen35-4b'
    monkeypatch.setenv('KB_CHAT_MODEL', 'qwen3-4b')
    with pytest.raises(LLMError, match='Qwen3 已停用'):
        model_id(cfg)


def test_commands_use_existing_vulkan_single_slot_and_correct_weight(cfg):
    cfg.data['llm']['n_gpu_layers'] = 99
    args = command(cfg)
    assert args[args.index('--alias') + 1] == 'qwen35-9b'
    assert args[args.index('-np') + 1] == '1'
    assert args[args.index('-ngl') + 1] == '99'
    assert 'Qwen3.5-9B-Q4_K_M.gguf' in args[2]
    assert command(cfg, cpu=True)[command(cfg, cpu=True).index('-ngl') + 1] == '0'


def test_chat_and_thinking_default_off(backend, monkeypatch):
    response = Response({'choices': [{'message': {'content': '核对 gcd'}}],
                         'usage': {'prompt_tokens': 10, 'completion_tokens': 4}})
    seen = {}
    def post(url, **kwargs):
        seen.update(kwargs['json'])
        return response
    monkeypatch.setattr('requests.post', post)
    result = backend.chat([{'role': 'user', 'content': 'RSA'}])
    assert result.text == '核对 gcd' and result.model == 'qwen35-9b'
    assert result.completion_tokens == 4
    assert seen['chat_template_kwargs'] == {'enable_thinking': False}
    assert response.closed


def test_stream_and_generator_close_release_upstream(backend, monkeypatch):
    response = Response(lines=[b'data: ' + json.dumps({'choices': [{'delta': {'content': 'hello'}}]}).encode(),
                               b'data: [DONE]'])
    monkeypatch.setattr('requests.post', lambda *a, **k: response)
    assert list(backend.stream([])) == ['hello']
    assert response.closed
    response.closed = False
    stream = backend.stream([])
    assert next(stream) == 'hello'
    stream.close()
    assert response.closed


@pytest.mark.parametrize('lines', [[b'data: invalid'], [b'data: {"error":"busy"}'], []])
def test_stream_errors_are_visible_and_close_response(backend, monkeypatch, lines):
    response = Response(lines=lines)
    monkeypatch.setattr('requests.post', lambda *a, **k: response)
    with pytest.raises((LLMError, ValueError)):
        list(backend.stream([]))
    assert response.closed


def test_wrong_active_model_never_generates(backend, monkeypatch):
    monkeypatch.setattr('requests.get', lambda *a, **k: Response({'data': [{'id': 'qwen35-4b'}]}))
    calls = []
    monkeypatch.setattr('requests.post', lambda *a, **k: calls.append(a))
    with pytest.raises(LLMError, match='重新启动'):
        backend.chat([])
    assert not calls
