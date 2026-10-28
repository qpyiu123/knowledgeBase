"""工具调用文本兜底解析的单元测试。"""
from __future__ import annotations

import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from agent.loop import _parse_text_tool_calls, _strip_tool_json  # noqa: E402


def test_parse_code_fence_json():
    text = (
        "我先查一下知识库。\n\n"
        '```json\n{"name": "search_kb", "arguments": {"query": "n相同 e不同", "category": "crypto"}}\n```\n'
        "然后根据结果回答。"
    )
    calls = _parse_text_tool_calls(text)
    assert len(calls) == 1
    fn = calls[0]["function"]
    assert fn["name"] == "search_kb"
    assert json.loads(fn["arguments"])["query"] == "n相同 e不同"


def test_parse_bare_json():
    text = '好的，我来读文件 {"name": "read_file", "arguments": {"path": "kb/crypto/x.md"}}'
    calls = _parse_text_tool_calls(text)
    assert len(calls) == 1
    assert calls[0]["function"]["name"] == "read_file"


def test_parse_write_file():
    text = ('```json\n{"name":"write_file","arguments":'
            '{"path":"work/exp.py","content":"print(1)"}}\n```')
    calls = _parse_text_tool_calls(text)
    assert calls[0]["function"]["name"] == "write_file"
    assert json.loads(calls[0]["function"]["arguments"])["path"] == "work/exp.py"


def test_parse_tool_key_variant():
    text = '{"tool": "search_kb", "args": {"query": "栈溢出"}}'
    calls = _parse_text_tool_calls(text)
    assert calls and calls[0]["function"]["name"] == "search_kb"


def test_parse_function_wrapper():
    text = '```json\n{"function": {"name": "search_kb", "arguments": {"query": "xx"}}}\n```'
    calls = _parse_text_tool_calls(text)
    assert calls and calls[0]["function"]["name"] == "search_kb"


def test_parse_truncated_json():
    """模型输出被 max_tokens 截断时的容错。"""
    text = '```json\n{"name": "write_file", "arguments": {"path": "work/a.py", "content": "x"}\n```'
    calls = _parse_text_tool_calls(text)
    # 截断后可能补不齐，但不应抛异常
    assert isinstance(calls, list)


def test_no_tool_mentioned_returns_empty():
    assert _parse_text_tool_calls("这是一个普通回答，没有工具调用。") == []


def test_unknown_tool_ignored():
    text = '{"name": "rm_rf", "arguments": {}}'
    assert _parse_text_tool_calls(text) == []


def test_only_first_call_taken():
    text = ('{"name":"search_kb","arguments":{"query":"a"}}\n'
            '{"name":"read_file","arguments":{"path":"b"}}')
    calls = _parse_text_tool_calls(text)
    assert len(calls) == 1


def test_strip_removes_json_block():
    text = ('前言\n```json\n{"name":"search_kb","arguments":{"query":"x"}}\n```\n后记')
    out = _strip_tool_json(text)
    assert "search_kb" not in out
    assert "前言" in out and "后记" in out


# ---- 回归：write_file 的 content 是多行大段脚本时也要能解析出来 ----
_SCRIPT = """from Crypto.Util.number import long_to_bytes
from gmpy2 import gcdext, invert

def common_modulus(n, e1, c1, e2, c2):
    g, a, b = gcdext(e1, e2)
    if a < 0:
        a, c1 = -a, invert(c1, n)
    m = (pow(c1, int(a), n) * pow(c2, int(b), n)) % n
    return long_to_bytes(int(m))
"""


def _payload():
    return json.dumps(
        {"name": "write_file",
         "arguments": {"path": "work/exp.py", "content": _SCRIPT}},
        ensure_ascii=False,
    )


def test_parse_write_file_multiline_fenced():
    """曾经的 bug：正则用 [^}]* 或按短文本判断，导致带大段脚本的调用解析不出来，
    用户表现为"agent 能查知识库但写不了文件"。"""
    calls = _parse_text_tool_calls(f"```json\n{_payload()}\n```")
    assert len(calls) == 1
    fn = calls[0]["function"]
    assert fn["name"] == "write_file"
    args = json.loads(fn["arguments"])
    assert args["path"] == "work/exp.py"
    assert "gcdext" in args["content"]
    assert "\n" in args["content"], "换行必须保留"


def test_parse_write_file_multiline_bare():
    calls = _parse_text_tool_calls(_payload())
    assert calls and calls[0]["function"]["name"] == "write_file"
    assert json.loads(calls[0]["function"]["arguments"])["path"] == "work/exp.py"


def test_parse_write_file_with_preamble():
    text = f"好的，我来写文件：\n\n{_payload()}\n\n写完请运行。"
    calls = _parse_text_tool_calls(text)
    assert calls and calls[0]["function"]["name"] == "write_file"


def test_parse_long_text_not_skipped():
    """文本很长（超过以往"短文本才解析"的阈值）也必须解析。"""
    padding = "这是一段很长的解释文字。" * 200
    text = f"{padding}\n{_payload()}\n{padding}"
    calls = _parse_text_tool_calls(text)
    assert calls and calls[0]["function"]["name"] == "write_file"


def test_salvage_truncated_write_file():
    """max_tokens 截断时，至少把 path 和被截断的 content 抢救出来。"""
    trunc = ('{"name": "write_file", "arguments": '
             '{"path": "work/exp.py", "content": "import sys\\nprint(1)')
    calls = _parse_text_tool_calls(trunc)
    assert calls, "截断场景应当能抢救出部分参数"
    args = json.loads(calls[0]["function"]["arguments"])
    assert args["path"] == "work/exp.py"
    assert "print(1)" in args["content"]


# ---- 回归：模型把工具调用写成 Python 函数调用语法 ----
# 这是 7B 模型的实际行为：读完知识库后输出
#   ```python
#   write_file("work/exp.py", ...)
#   ```
# 而不发 tool_calls。不识别就会卡在最后一步。
def test_parse_python_call_positional():
    calls = _parse_text_tool_calls(
        '```python\nwrite_file("work/exp.py", "print(1)")\n```')
    assert calls, "Python 位置参数调用应当被识别"
    fn = calls[0]["function"]
    assert fn["name"] == "write_file"
    args = json.loads(fn["arguments"])
    assert args["path"] == "work/exp.py"
    assert args["content"] == "print(1)"


def test_parse_python_call_kwargs():
    calls = _parse_text_tool_calls(
        '```python\nwrite_file(path="work/exp.py", content="print(1)")\n```')
    assert calls
    args = json.loads(calls[0]["function"]["arguments"])
    assert args["path"] == "work/exp.py"


def test_parse_python_call_with_parens_in_content():
    """content 里含括号（print(1)）时，括号匹配不能提前截断。"""
    calls = _parse_text_tool_calls('write_file("work/a.py", "print(1)\\nprint(2)")')
    assert calls
    args = json.loads(calls[0]["function"]["arguments"])
    assert "print(2)" in args["content"]


def test_parse_python_call_search():
    calls = _parse_text_tool_calls('search_kb("n相同 e不同")')
    assert calls
    assert json.loads(calls[0]["function"]["arguments"])["query"] == "n相同 e不同"


def test_parse_python_call_variable_arg_rejected():
    """参数是变量名时解析不出内容，应返回空而不是乱填。"""
    calls = _parse_text_tool_calls(
        '```python\nwrite_file("work/exp.py", common_modulus_script)\n```')
    assert calls == []
