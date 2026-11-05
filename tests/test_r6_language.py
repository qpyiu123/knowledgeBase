import sqlite3
from pathlib import Path

import pytest

from kb.fts import FtsIndex
from kb.parser import iter_docs
from kb import language_reference

ROOT = Path(__file__).resolve().parents[1]


@pytest.fixture(scope="module")
def library(tmp_path_factory):
    root = ROOT / "kb"
    wanted = {"web/php-filter-chain.md", "reverse/wasm-reverse.md", "pwn/checksec-and-basics.md",
              "_reference/python39/base64.md", "_reference/python39/json.md", "_reference/python39/re.md", "web/xss-and-csp.md"}
    index = FtsIndex(tmp_path_factory.mktemp("language") / "fts.db")
    index.rebuild([doc for doc in iter_docs(root) if doc.path in wanted])
    return index


@pytest.mark.parametrize(("query","symbol"), [
    ("Python base64.b64decode", "base64.b64decode"), ("Python json.loads", "json.loads"),
    ("Python re.findall", "re.findall"), ("PHP str_replace", "str_replace"),
    ("PHP str_ireplace", "str_ireplace"), ("PHP base64_decode", "base64_decode"),
    ("PHP file_get_contents", "file_get_contents"), ("Node.js Buffer.from", "Buffer.from"),
    ("Node.js Buffer.readUInt32LE", "Buffer.readUInt32LE"),
    ("Node.js Buffer.readUInt32BE", "Buffer.readUInt32BE"),
    ("C memcpy", "memcpy"), ("C memmove", "memmove"),
    ("JavaScript encodeURIComponent", "encodeURIComponent"),
    ("JavaScript: decodeURIComponent", "decodeURIComponent"),
])
def test_function_search_finds_chinese_section(library, query, symbol):
    hit = library.search_language(query, 5)[0]
    assert hit["api"]["symbol"] == symbol
    assert hit["api"]["source"].startswith("https://")
    assert hit["api"]["anchor"] and hit["section"]
    assert any("\u4e00" <= c <= "\u9fff" for c in hit["snippet"])


def test_missing_and_language_browse(library):
    assert library.search_language("PHP definitely_missing", 5, True) == []
    assert library.search_language("C Buffer.from", 5, True) == []
    assert library.search_language("PHP", 5, True)
    assert library.search_language("PHP 文件读取", 5, True)[0]["api"]["symbol"] == "file_get_contents"
    assert library.search_language("Python题目是一个压缩包", 5) == []
    with sqlite3.connect(":memory:") as conn:
        assert language_reference.lookup(conn, "PHP str_replace", 5, True) == []
