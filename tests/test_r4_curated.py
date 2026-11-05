"""只运行本批逐行审阅过的固定示例，不执行库内其他文章。"""
from __future__ import annotations

import json
from pathlib import Path
import re
import runpy

import pytest

ROOT = Path(__file__).resolve().parents[1]
PAGES = ['kb/_reference/rsa-path-check.md', 'kb/_reference/python-decoding-errors.md']


@pytest.mark.parametrize('page', PAGES)
def test_reviewed_examples(page, monkeypatch):
    monkeypatch.chdir(ROOT)
    text = (ROOT / page).read_text(encoding='utf-8')
    blocks = re.findall(r'^```python\n(.*?)^```', text, re.M | re.S)
    assert blocks
    for index, block in enumerate(blocks):
        exec(compile(block, f'{page}:block{index + 1}', 'exec'), {})


@pytest.mark.parametrize('n,e,c,k', [(15, 3, 15, 0), (15, 3, -1, 0), (15, 3, 1, -1)])
def test_small_e_rejects_input_outside_stated_domain(n, e, c, k):
    attack = runpy.run_path(str(ROOT / 'kb/_methods/scripts/rsa_small_e.py'))['small_e_attack']
    with pytest.raises(ValueError, match='0<=c<n'):
        attack(n, e, c, max_k=k)


def test_small_e_candidates_stay_in_plaintext_domain():
    attack = runpy.run_path(str(ROOT / 'kb/_methods/scripts/rsa_small_e.py'))['small_e_attack']
    assert attack(5, 3, 0, max_k=25) == [(0, b'\x00')]


def test_curation_entries_reference_existing_files_and_fixed_questions():
    report = json.loads((ROOT / 'docs/data/r4-curation.json').read_text(encoding='utf-8'))
    assert len(report['items']) == 6
    for item in report['items']:
        assert item['decision'] == 'accepted' and item['reviewed']
        assert (ROOT / item['path']).is_file()
        assert item['license'] and item['sections'] and item['changes']
        for source in item['local_sources']:
            assert (ROOT / source).is_file()
    cases = json.loads((ROOT / 'eval/r4_curated.json').read_text(encoding='utf-8'))['queries']
    assert len(cases) == 8
    for case in cases:
        assert all((ROOT / 'kb' / path).is_file() for path in case['expected'])
