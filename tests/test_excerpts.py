from kb.excerpts import select_excerpt


def test_late_section_with_code_is_selected_instead_of_intro():
    body = '# 文档\n' + '这是概览。' * 800 + '\n## base64.b64decode\n用法\n```python\nbase64.b64decode(s, validate=True)\n```\n'
    result = select_excerpt(body, 'base64.b64decode validate')
    assert result.startswith('## base64.b64decode')
    assert 'validate=True' in result
    assert '这是概览' not in result


def test_index_section_hint_and_hash_lines_in_code():
    body = '## 一、信号\n有关键词RSA。\n## 二、代码\n```python\n# 代码注释\nprint("RSA")\n```\n'
    result = select_excerpt(body, 'RSA', section='二、代码')
    assert '# 代码注释' in result and 'print("RSA")' in result


def test_empty_frontmatter_and_long_single_section():
    assert select_excerpt('---\ntitle: 空\n---\n') == ''
    text = '## 排错\n' + '背景\n' * 2000 + '特有错误\n修正方法\n'
    result = select_excerpt(text, '特有错误', limit=120)
    assert '特有错误' in result and '修正方法' in result
    assert '小节片段' in result
    assert len(result) <= 120


def test_cli_context_cannot_read_outside_library(tmp_path):
    from types import SimpleNamespace
    from kb.rag import KB
    root = tmp_path / 'kb'
    root.mkdir()
    (tmp_path / 'private.md').write_text('DO-NOT-READ', encoding='utf-8')
    fake = SimpleNamespace(cfg=SimpleNamespace(kb_dir=root))
    hit = SimpleNamespace(doc_path='../private.md', title='外部文件', best_text='')
    assert KB.build_context(fake, [hit]) == ''
