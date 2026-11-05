"""R3.1 题目记录、失败原因、导出和上下文的离线检查。"""
import json
from pathlib import Path

import pytest

from agent.server import compile_workspace_context
from agent.workspace import WorkspaceStore, WorkspaceError


@pytest.fixture()
def store(tmp_path):
    store = WorkspaceStore(tmp_path / 'workspaces')
    store.create('共模题', workspace_id='case')
    return store


def test_focus_save_reload_partial_update_and_clear(store):
    store.update('case', goal='恢复 m', hypotheses='两个指数可能互素', pending_checks='计算 gcd')
    ws = store.load('case')
    assert ws['goal'] == '恢复 m'
    store.update('case', goal='验证候选 m')
    assert store.load('case')['hypotheses'] == '两个指数可能互素'
    store.update('case', hypotheses='')
    assert store.load('case')['hypotheses'] == ''
    assert store.load('case')['pending_checks'] == '计算 gcd'


@pytest.mark.parametrize('value', ['x' * 4001, {'bad': 'value'}, ['bad']])
def test_invalid_focus_does_not_overwrite_existing_record(store, value):
    store.update('case', goal='保留目标')
    before = store._path('case').read_bytes()
    with pytest.raises(WorkspaceError):
        store.update('case', goal=value)
    assert store._path('case').read_bytes() == before


def test_old_workspace_fields_are_added_only_in_memory(store):
    path = store._path('case')
    ws = json.loads(path.read_text(encoding='utf-8'))
    for key in ('goal', 'hypotheses', 'pending_checks'):
        ws.pop(key)
    path.write_text(json.dumps(ws, ensure_ascii=False), encoding='utf-8')
    before = path.read_bytes()
    loaded = store.load('case')
    assert loaded['goal'] == loaded['hypotheses'] == loaded['pending_checks'] == ''
    assert path.read_bytes() == before


def test_attempt_failure_reason_save_change_and_reset(store):
    _, entry = store.add_entry('case', 'attempt', direction='运行脚本', result='failed', failure_kind='runtime')
    assert entry['failure_kind'] == 'runtime'
    store.update_entry('case', entry['id'], failure_kind='condition')
    assert store.load('case')['entries'][0]['failure_kind'] == 'condition'
    store.update_entry('case', entry['id'], result='pending')
    assert store.load('case')['entries'][0]['failure_kind'] == 'unknown'
    with pytest.raises(WorkspaceError):
        store.update_entry('case', entry['id'], failure_kind='runtime')


@pytest.mark.parametrize('reason', ['other', [], 123])
def test_invalid_failure_reason_is_rejected(store, reason):
    with pytest.raises(WorkspaceError):
        store.add_entry('case', 'attempt', text='test', result='failed', failure_kind=reason)


def test_focus_and_reason_in_both_exports(store):
    store.update('case', goal='恢复 m', hypotheses='同一明文', pending_checks='计算 gcd')
    store.add_entry('case', 'attempt', text='缺少 sympy', result='failed', failure_kind='runtime')
    for md in (store.export_markdown('case'), store.export_writeup('case')):
        assert '## 当前目标\n\n恢复 m' in md
        assert '## 待验证假设\n\n同一明文' in md
        assert '## 待查项\n\n计算 gcd' in md
        assert '失败原因：运行出错' in md


def test_context_separates_hypotheses_runtime_errors_and_excluded_conditions(store):
    store.update('case', goal='恢复 m', hypotheses='可能复用明文', pending_checks='检查 m 编码')
    store.add_entry('case', 'fact', text='n 相同')
    store.add_entry('case', 'attempt', direction='先运行脚本', conclusion='缺少 sympy', result='failed', failure_kind='runtime')
    store.add_entry('case', 'attempt', direction='广播路径', conclusion='n 相同', result='failed', failure_kind='condition')
    store.add_entry('case', 'attempt', direction='旧尝试', result='failed')
    context = compile_workspace_context(store.load('case'))
    assert '待验证假设（未确认为事实）' in context
    assert '运行出错的尝试（先排错再试）：\n- 先运行脚本 → 缺少 sympy' in context
    assert '前提已排除的方法：\n- 广播路径 → n 相同' in context
    assert '失败原因待确认：\n- 旧尝试' in context
    assert context.index('已确认的事实') < context.index('待验证假设')


def test_long_numeric_fact_is_omitted_whole_instead_of_cut_mid_value():
    value = 'n=' + '1234567890' * 200
    context = compile_workspace_context({'entries': [{'kind': 'fact', 'text': value}]})
    assert '1234567890' not in context
    assert '已省略部分完整记录' in context


def test_later_success_replaces_old_exclusion_in_model_context():
    context = compile_workspace_context({'entries': [
        {'kind': 'attempt', 'direction': '共模', 'result': 'failed', 'failure_kind': 'condition', 'conclusion': '旧参数不适用'},
        {'kind': 'attempt', 'direction': '共模', 'result': 'success', 'conclusion': '新参数验证成功'},
    ]})
    assert '旧参数不适用' not in context
    assert '前提已排除' not in context
