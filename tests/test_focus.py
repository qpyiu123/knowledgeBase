from pathlib import Path
from types import SimpleNamespace

from kb.applicability import evaluate_conditions
from kb.focus import condition_query, focus_hits, recent_facts, workspace_basis


def test_hypotheses_and_pending_checks_are_not_technical_evidence(tmp_path):
    ws = {'goal': '同一个 n', 'pending_checks': '检查同一明文与指数互素', 'hypotheses': '同一明文，指数互素',
          'entries': [{'id': 'f1', 'kind': 'fact', 'text': '同一个 n'}]}
    query = condition_query(ws, '怎么下手')
    assert '同一明文' not in query and '指数互素' not in query
    app = evaluate_conditions(tmp_path, 'crypto/rsa-common-modulus-attack.md', query)
    assert app['status'] == 'unknown'
    assert app['conditions'][0]['status'] == 'known'


def test_recent_facts_keep_records_whole_and_include_separate_parameters():
    facts = [{'id': str(i), 'kind': 'fact', 'text': text} for i, text in enumerate(
        ['n1=15', 'n2=15', 'e1=3', 'e2=7', '同一明文'])]
    assert recent_facts({'entries': facts}) == facts
    long = {'id': 'long', 'kind': 'fact', 'text': 'n=12345678901234567890'}
    assert recent_facts({'entries': [long]}, budget=10) == []


def test_old_runtime_error_does_not_return_after_a_new_success():
    ws = {'entries': [{'id': 'e', 'kind': 'attempt', 'result': 'failed', 'failure_kind': 'runtime', 'text': '缺少模块'},
                      {'id': 's', 'kind': 'attempt', 'result': 'success', 'text': '运行正常'}]}
    assert workspace_basis(ws) == []


def test_basis_searches_are_separate_and_deduplicated():
    calls = []
    class KB:
        def search(self, text, **kwargs):
            calls.append((text, kwargs))
            return [SimpleNamespace(doc_path='crypto/rsa.md')]
    ws = {'goal': '恢复 m', 'pending_checks': '比较 e', 'entries': []}
    hits, basis = focus_hits(KB(), ws)
    assert [text for text, _ in calls] == ['比较 e', '恢复 m']
    assert all(opts['retrieval'] == 'fts' and opts['expand'] is False for _, opts in calls)
    assert len(hits) == 1 and len(hits[0]['basis']) == 2
    assert basis[0]['field'] == 'pending_checks'


def test_precise_missing_identifier_does_not_use_matches_on_year():
    class KB:
        def search(self, text, **kwargs):
            return [SimpleNamespace(doc_path='misc/year.md', title='2026', best_text='2026 年记录')]
    hits, basis = focus_hits(KB(), {'pending_checks': 'QuantumCtf.nonexistent_probe_2026', 'entries': []})
    assert hits == [] and basis[0]['missing'] is True


def test_precise_symbols_prefer_document_covering_both_and_cache_queries():
    calls = []
    class KB:
        def search(self, text, **kwargs):
            calls.append(text)
            return [SimpleNamespace(doc_path='api/both.md', title='API', best_text='json.loads JSONDecodeError'),
                    SimpleNamespace(doc_path='api/one.md', title='API', best_text='json.loads')]
    hits, _ = focus_hits(KB(), {'pending_checks': 'json.loads JSONDecodeError', 'goal': 'json.loads', 'entries': []})
    assert [row['hit'].doc_path for row in hits] == ['api/both.md']
    assert calls.count('json.loads') == 1
