from pathlib import Path
from types import SimpleNamespace

import pytest

from kb.fts import FtsIndex
from kb.library import LibraryCatalog, document_info, read_code
from kb.parser import Doc
from kb.rag import KB


def test_fts_search_does_not_touch_vector_backend(tmp_path: Path):
    fts = FtsIndex(tmp_path / 'fts.db')
    fts.rebuild([Doc(path='_methods/example.md', title='示例', category='misc', body='bytecode handler pc')])
    class NoVectors:
        def search(self, *args, **kwargs):
            raise AssertionError('纯关键词不应加载编码器或搜索向量')
    kb = KB.__new__(KB)
    kb.cfg = SimpleNamespace(get=lambda *args: args[-1])
    kb.fts, kb.vec = fts, NoVectors()
    result = kb.search('bytecode', retrieval='fts', expand=False, doc_type='method')
    assert result[0].doc_path == '_methods/example.md'
    assert result[0].sources == ['fts']


def test_document_sources_and_code_are_existing_library_files(tmp_path: Path):
    code = tmp_path / '_methods/scripts/example.py'
    code.parent.mkdir(parents=True)
    code.write_text('print("should not run")')
    source = tmp_path / 'misc/original.md'
    source.parent.mkdir()
    source.write_text('original')
    info = document_info(tmp_path, '_methods/example.md',
                         '---\nsource: kb/misc/original.md, kb/../../private.md\n---\n'
                         '`kb/_methods/scripts/example.py` 和 `kb\\_methods\\scripts\\example.py`')
    assert info['kind_label'] == '方法卡'
    assert info['sources'] == [{'path': 'misc/original.md', 'external': False}]
    assert info['scripts'][0]['path'] == '_methods/scripts/example.py'
    assert len(info['scripts']) == 1


def test_code_is_read_and_statically_described_without_execution(tmp_path: Path):
    code = tmp_path / '_methods/scripts/example.py'
    code.parent.mkdir(parents=True)
    code.write_text('"""离线计算示例。"""\nimport argparse\nimport sympy\n'
                    'raise RuntimeError("not executed")\n'
                    'parser = argparse.ArgumentParser()\nparser.add_argument("--number")\n', encoding='utf-8')
    result = read_code(tmp_path, '_methods/scripts/example.py')
    assert result['dependencies'] == ['sympy']
    assert result['arguments'] == ['--number']
    assert result['summary'] == '离线计算示例。'
    assert 'not executed' in result['body']


@pytest.mark.parametrize('name', ['../secret.py', 'other.py', '_methods/scripts/test.txt', '/etc/passwd'])
def test_code_scope_is_limited(tmp_path: Path, name: str):
    with pytest.raises(ValueError):
        read_code(tmp_path, name)


def test_source_document_offers_method_code_from_existing_index(tmp_path: Path):
    source = tmp_path / 'misc/original.md'
    source.parent.mkdir()
    source.write_text('原文')
    method = tmp_path / '_methods/example.md'
    method.parent.mkdir()
    body = '---\nsource: kb/misc/original.md\n---\n`kb/_methods/scripts/example.py`'
    method.write_text(body, encoding='utf-8')
    code = tmp_path / '_methods/scripts/example.py'
    code.parent.mkdir()
    code.write_text('print("read only")')
    index = FtsIndex(tmp_path / 'fts.db')
    index.rebuild([Doc(path='_methods/example.md', title='相关方法', category='misc', body=body)])
    catalog = LibraryCatalog(tmp_path, tmp_path / 'fts.db')
    result = catalog.info('misc/original.md', '原文')
    assert result['methods'] == [{'path': '_methods/example.md', 'title': '相关方法'}]
    assert result['scripts'][0]['path'] == '_methods/scripts/example.py'
    stamp = catalog._stamp
    assert catalog.info('misc/original.md', '原文')['scripts'] == result['scripts']
    assert catalog._stamp == stamp
