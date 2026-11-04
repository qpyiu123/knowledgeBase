"""R2 固定样例和来源检查，完全离线。"""
import json
from pathlib import Path

import pytest

from kb.applicability import evaluate_conditions, resolve_target
from kb.condition_guides import evaluate_guide, load_guides

ROOT = Path(__file__).resolve().parents[1]
CASES = json.loads((ROOT / 'eval/r2_conditions.json').read_text(encoding='utf-8'))


@pytest.mark.parametrize('case', CASES, ids=[c['id'] for c in CASES])
def test_fixed_conditions(case):
    app = evaluate_conditions(ROOT / 'kb', case['path'], case['query'])
    assert app['status'] == case['status'], app
    conditions = {c['id']: c['status'] for c in app['conditions']}
    for key, status in case.get('conditions', {}).items():
        assert conditions[key] == status
    assert all(c['trace'] == 'rule' for c in app['conditions'])


def test_guides_have_existing_paths_sections_and_quotes():
    for g in load_guides():
        for path in g['paths'] + [c['path'] for c in g['contrasts']]:
            assert (ROOT / 'kb' / path).is_file(), path
        body = (ROOT / 'kb' / g['source']['path']).read_text(encoding='utf-8')
        assert g['source']['section'] in body
        section = body.split('## ' + g['source']['section'], 1)[1].split('\n## ', 1)[0]
        assert g['source']['quote'] in section


def test_original_and_card_share_conditions():
    for g in load_guides():
        original, card = [evaluate_conditions(ROOT / 'kb', p, 'RSA 同一个 n') for p in g['paths']]
        assert original['conditions'] == card['conditions']
        assert original['guide'] == card['guide']


@pytest.mark.parametrize('query', ['gcd(e1,e2)=10', 'e1=9 e2=12', 'e1=0x9 e2=0xc'])
def test_non_coprime_does_not_match_one(query):
    out = evaluate_guide(load_guides()[0], query)
    assert out[2]['status'] == 'unsatisfied'


def test_repeated_numeric_values_do_not_choose_arbitrarily():
    out = evaluate_guide(load_guides()[0], 'n1=15 n1=21 n2=15，e1=3 e2=7')
    assert out[0]['status'] == 'unknown'
    assert '冲突' in out[0]['evidence']


def test_evidence_preserves_input_spaces():
    out = evaluate_guide(load_guides()[0], '同一个 n，同一明文，两个指数互素')
    assert '同一个 n' in out[0]['evidence']


def test_question_does_not_erase_separate_numeric_fact():
    out = evaluate_guide(load_guides()[2], '已知 e=3，整数根精确吗？')
    assert out[0]['status'] == 'known'
    assert out[1]['status'] == 'unknown'


def test_double_negative_needs_confirmation():
    out = evaluate_guide(load_guides()[0], '并非不同 n')
    assert out[0]['status'] == 'unknown'


def test_reading_does_not_override_technical_facts(tmp_path):
    root = tmp_path / 'kb'
    (root / 'crypto').mkdir(parents=True)
    rel = 'crypto/rsa-common-modulus-attack.md'
    (root / rel).write_text('---\nrequires: [missing.md]\n---\n正文', encoding='utf-8')
    app = evaluate_conditions(root, rel, '同一个 n，同一明文，两个指数互素')
    assert app['status'] == 'known'
    assert len(app['conditions']) == 3
    assert app['reading'][0]['missing'] is True


def test_reading_cannot_open_outside_library(tmp_path):
    root = tmp_path / 'kb'
    root.mkdir()
    outside = tmp_path / 'private.md'
    outside.write_text('private', encoding='utf-8')
    for path in ('../private.md', str(outside)):
        assert resolve_target(root, path) is None
