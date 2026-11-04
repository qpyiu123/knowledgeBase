from pathlib import Path

import pytest
import yaml

from accept_methods import ROOT, accept, inspect_card, source_paths
from kb.parser import split_front_matter


def test_multiline_and_quoted_yaml():
    meta, _ = split_front_matter('---\nsignals:\n  - "输入 {{1/0}} 返回 500"\n  - jmp [table + op*8]\n---\n正文', strict=True)
    assert len(meta['signals']) == 2
    assert meta['signals'][1] == 'jmp [table + op*8]'


def test_bad_yaml_is_reported():
    raw = '---\nsignals: [输入 {{1/0}} 返回 500]\n---\n正文'
    with pytest.raises(yaml.YAMLError):
        split_front_matter(raw, strict=True)
    assert split_front_matter(raw)[0] == {}


def test_sources_preserve_spaces():
    assert source_paths('kb/a file.md, kb/b.md') == ['kb/a file.md', 'kb/b.md']
    assert source_paths(['kb/a file.md']) == ['kb/a file.md']


def test_source_escape_and_bad_difficulty(tmp_path: Path):
    card = tmp_path / 'kb/_methods/card.md'
    card.parent.mkdir(parents=True)
    card.write_text('---\ntitle: 测试\ncategory: crypto\ntags: [rsa]\nsignals: [特征]\ndifficulty: 3\nsource: kb/../../outside.md\ntools: [python]\nupdated: 2026-11-05\n---\n正文', encoding='utf-8')
    errors = inspect_card(card, tmp_path)['errors']
    assert any('difficulty' in e for e in errors)
    assert any('来源不存在' in e for e in errors)


def test_received_corpus_passes_acceptance():
    report = accept(ROOT)
    assert report['cards_total'] == 54
    assert report['ok'], [c for c in report['cards'] if c['errors']]
