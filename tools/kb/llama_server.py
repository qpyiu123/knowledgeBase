"""Qwen3.5 的本机 llama-server 接口；网页和命令行共用。"""
from __future__ import annotations

import json
import os
import time

from .llm import BaseBackend, GenResult, LLMError

MODELS = {
    'qwen35-9b': 'Qwen3.5-9B-Q4_K_M.gguf',
    'qwen35-4b': 'Qwen3.5-4B-Q4_K_M.gguf',
}


def model_id(cfg):
    selected = os.environ.get('KB_CHAT_MODEL') or cfg.get('llama_server', 'model', 'qwen35-9b')
    if selected not in MODELS:
        raise LLMError('请选择 qwen35-9b 或 qwen35-4b；Qwen3 已停用')
    return selected


def base_url(cfg):
    port = int(os.environ.get('KB_MODEL_PORT') or cfg.get('llama_server', 'port', 8766))
    return f'http://127.0.0.1:{port}'


class LlamaServerBackend(BaseBackend):
    name = 'llama_server'

    def __init__(self, cfg):
        self.cfg = cfg
        self.model = model_id(cfg)
        self.host = base_url(cfg)

    def health(self):
        import requests
        try:
            response = requests.get(self.host + '/health', timeout=2)
            response.raise_for_status()
            models = requests.get(self.host + '/v1/models', timeout=2)
            models.raise_for_status()
            available = [m['id'] for m in models.json().get('data', [])]
            if self.model not in available:
                return False, f'当前服务使用 {available}，需要 {self.model}；请按所选模型重新启动'
            return True, self.model
        except (requests.RequestException, ValueError, KeyError) as error:
            return False, f'模型服务未就绪：{error}；请运行 start.ps1 启动解释服务'

    def _payload(self, messages, max_tokens, temperature, stream):
        return {'model': self.model, 'messages': messages, 'stream': stream,
                'max_tokens': int(max_tokens or self.cfg.get('llm', 'max_tokens', 1200)),
                'temperature': float(temperature if temperature is not None else self.cfg.get('llm', 'temperature', 0.2)),
                'chat_template_kwargs': {'enable_thinking': False}}

    def _post(self, payload):
        import requests
        ok, detail = self.health()
        if not ok:
            raise LLMError(detail)
        try:
            response = requests.post(self.host + '/v1/chat/completions', json=payload,
                                     stream=payload['stream'], timeout=int(self.cfg.get('llm', 'timeout', 300)))
            if response.status_code != 200:
                message = response.text[:500]
                response.close()
                raise LLMError(f'模型服务返回 HTTP {response.status_code}：{message}')
            return response
        except requests.RequestException as error:
            raise LLMError(f'模型服务连接失败：{error}；请检查模型是否已启动') from error

    def chat(self, messages, max_tokens=None, temperature=None):
        start = time.perf_counter()
        response = self._post(self._payload(messages, max_tokens, temperature, False))
        try:
            result = response.json()
            text = result['choices'][0]['message'].get('content') or ''
            if not text.strip():
                raise LLMError('模型没有返回内容')
            usage = result.get('usage') or {}
            seconds = time.perf_counter() - start
            tokens = int(usage.get('completion_tokens') or 0)
            return GenResult(text, self.model, self.name,
                             prompt_tokens=int(usage.get('prompt_tokens') or 0),
                             completion_tokens=tokens, seconds=round(seconds, 3),
                             tokens_per_sec=round(tokens / max(seconds, 1e-6), 2))
        finally:
            response.close()

    def stream(self, messages, max_tokens=None, temperature=None):
        response = self._post(self._payload(messages, max_tokens, temperature, True))
        try:
            for line in response.iter_lines():
                if not line or not line.startswith(b'data:'):
                    continue
                data = line[5:].strip()
                if data == b'[DONE]':
                    return
                try:
                    item = json.loads(data)
                except (ValueError, UnicodeError) as error:
                    raise LLMError('模型返回的流数据格式错误，请查看模型日志') from error
                if item.get('error'):
                    raise LLMError(str(item['error']))
                for choice in item.get('choices', []):
                    piece = (choice.get('delta') or {}).get('content')
                    if piece:
                        yield piece
            raise LLMError('模型连接提前结束，请重试本次解释')
        finally:
            response.close()
