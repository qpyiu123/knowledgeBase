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


def test_rsa_pairing_selects_the_scoped_script_not_another_method():
    from pathlib import Path
    from kb.excerpts import paired_code
    from kb.library import LibraryCatalog
    root = Path(__file__).resolve().parents[1]
    catalog = LibraryCatalog(root / 'kb', root / 'index/fts.db')
    script = paired_code(root / 'kb', 'crypto/rsa-common-modulus-attack.md', catalog)
    assert script['path'] == '_methods/scripts/rsa_common_modulus.py'
    assert 'def ' in script['body']


def test_web_materials_include_paired_code_once_and_honor_selected_section():
    from pathlib import Path
    from types import SimpleNamespace
    from agent.server import _collect_sources, MAX_CONTEXT_CHARS
    from kb.library import LibraryCatalog
    root = Path(__file__).resolve().parents[1]
    original = 'crypto/rsa-common-modulus-attack.md'
    card = '_methods/rsa_common_modulus_attack.md'
    kb = SimpleNamespace(cfg=SimpleNamespace(kb_dir=root / 'kb'),
                         library=LibraryCatalog(root / 'kb', root / 'index/fts.db'))
    parts, error = _collect_sources(kb, [original, card], '模糊问题', {original: '二、原理'})
    assert error is None
    assert '## 二、原理' in parts[0]
    code = [p for p in parts if p.startswith(('【完整代码', '【代码片段'))]
    assert len(code) == 1 and '_methods/scripts/rsa_common_modulus.py' in code[0]
    assert '脚本参数：' in code[0] and '第三方导入：' in code[0]
    assert sum(map(len, parts)) <= MAX_CONTEXT_CHARS
