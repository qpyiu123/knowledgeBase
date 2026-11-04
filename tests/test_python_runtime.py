import json
import os
import shutil
import subprocess
from pathlib import Path
from types import SimpleNamespace

import pytest

from python_runtime import ROOT, resolve_python
from prepare_portable_python import prepare


@pytest.fixture()
def environments(tmp_path: Path):
    for name in ('chosen python.exe', 'env.exe', 'configured.exe', 'runtime/python-portable/python.exe', '.venv/Scripts/python.exe'):
        file = tmp_path / name
        file.parent.mkdir(parents=True, exist_ok=True)
        file.write_text('fixture, not executed')
    (tmp_path / 'config.toml').write_text('[runtime]\npython = "configured.exe"\n', encoding='utf-8')
    return tmp_path


@pytest.mark.parametrize('explicit,env,filename,source', [
    ('chosen python.exe', {'KB_PYTHON': 'env.exe'}, 'chosen python.exe', 'parameter'),
    ('', {'KB_PYTHON': 'env.exe'}, 'env.exe', 'KB_PYTHON'),
    ('', {}, 'configured.exe', 'config.toml'),
])
def test_explicit_environment_priority(environments, explicit, env, filename, source):
    file, selected = resolve_python(explicit, root=environments, environ=env)
    assert file == environments / filename
    assert selected == source


def test_auto_prefers_portable_and_skips_broken_venv(environments, monkeypatch):
    (environments / 'config.toml').write_text('[runtime]\npython="auto"\n')
    monkeypatch.setattr('python_runtime.subprocess.run', lambda *a, **k: SimpleNamespace(returncode=0, stdout='True'))
    path, source = resolve_python(root=environments, environ={})
    assert path == environments / 'runtime/python-portable/python.exe'
    assert source == 'auto'


def test_auto_falls_back_after_interpreter_failure(environments, monkeypatch):
    (environments / 'config.toml').write_text('[runtime]\npython="auto"\n')
    def run(command, **kwargs):
        ok = '.venv' in command[0]
        return SimpleNamespace(returncode=0 if ok else 1, stdout='True' if ok else '')
    monkeypatch.setattr('python_runtime.subprocess.run', run)
    assert resolve_python(root=environments, environ={})[0] == environments / '.venv/Scripts/python.exe'


def test_invalid_explicit_path_never_silently_falls_back(environments):
    with pytest.raises(ValueError, match='不存在'):
        resolve_python('missing.exe', root=environments, environ={})


@pytest.mark.parametrize('shell', ['powershell', 'pwsh'])
@pytest.mark.parametrize('explicit,env,filename,source', [
    ('chosen python.exe', {'KB_PYTHON': 'env.exe'}, 'chosen python.exe', 'parameter'),
    ('', {'KB_PYTHON': 'env.exe'}, 'env.exe', 'KB_PYTHON'),
    ('', {}, 'configured.exe', 'config.toml'),
])
def test_powershell_uses_same_selection(environments, shell, explicit, env, filename, source):
    executable = shutil.which(shell)
    if not executable:
        pytest.skip(f'{shell} 未安装')
    quote = lambda text: "'" + str(text).replace("'", "''") + "'"
    command = f". {quote(ROOT / 'tools/python-runtime.ps1')}; Resolve-KbPython -Root {quote(environments)} -PythonExe {quote(explicit)} | ConvertTo-Json -Compress"
    child_env = {k: v for k, v in os.environ.items() if k.upper() != 'KB_PYTHON'}
    child_env.update(env)
    result = subprocess.run([executable, '-NoProfile', '-ExecutionPolicy', 'Bypass', '-Command', command],
                            capture_output=True, text=True, encoding='utf-8', env=child_env, timeout=20)
    assert result.returncode == 0, result.stderr
    selection = json.loads(result.stdout)
    assert Path(selection['Path']) == environments / filename
    assert selection['Source'] == source


def test_prepare_rejects_wrong_archive_without_writing(tmp_path: Path):
    import zipfile
    archive = tmp_path / 'wrong.zip'
    with zipfile.ZipFile(archive, 'w') as z:
        z.writestr('python312.dll', 'wrong')
    with pytest.raises(ValueError, match='Python 3.13'):
        prepare(archive, tmp_path)
    assert not (tmp_path / 'runtime').exists()
