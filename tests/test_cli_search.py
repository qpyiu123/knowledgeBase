from types import SimpleNamespace
from unittest.mock import Mock

import pytest

import cli


@pytest.mark.parametrize('flag,backend', [('--vec-only', 'vec'), ('--fts-only', 'fts')])
@pytest.mark.parametrize('explicit,expected', [((), 7), (('-k', '3'), 3)])
def test_single_search_mode_uses_configured_top_k(monkeypatch, flag, backend, explicit, expected):
    cfg = SimpleNamespace(get=lambda *_: 7)
    kb = SimpleNamespace(fts=SimpleNamespace(search=Mock(return_value=[])),
                         vec=SimpleNamespace(search=Mock(return_value=[])))
    monkeypatch.setattr(cli, 'KB', lambda _: kb)
    args = cli.build_parser().parse_args(['search', 'RSA', flag, '--json', *explicit])
    assert cli.cmd_search(cfg, args) == 2  # 空结果的既有退出码
    assert getattr(kb, backend).search.call_args.kwargs['top_k'] == expected
