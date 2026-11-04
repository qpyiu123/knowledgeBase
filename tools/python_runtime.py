"""选择和检查项目 Python；不修改配置、不安装依赖。"""
from __future__ import annotations

import argparse
import importlib
import json
import os
import shutil
import sqlite3
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
CORE_MODULES = ('numpy', 'yaml', 'requests')
OPTIONAL_MODULES = ('onnxruntime', 'tokenizers', 'sqlite_vec', 'sympy', 'Crypto')


def configured_python(root: Path = ROOT) -> str:
    import tomllib
    path = root / 'config.toml'
    if not path.is_file():
        return 'auto'
    return str(tomllib.loads(path.read_text(encoding='utf-8-sig')).get('runtime', {}).get('python') or 'auto')


def resolve_python(explicit: str = '', *, root: Path = ROOT, environ=None) -> tuple[Path, str]:
    root = root.resolve()
    env = os.environ if environ is None else environ
    configured = configured_python(root) if not explicit and not env.get('KB_PYTHON') else 'auto'
    selected = next(((value, source) for value, source in (
        (explicit, 'parameter'), (env.get('KB_PYTHON', ''), 'KB_PYTHON'),
        (configured if configured.lower() != 'auto' else '', 'config.toml')) if value), None)
    if selected:
        value, source = selected
        path = Path(value)
        if not path.is_absolute():
            local = root / path
            path = local if local.is_file() else Path(shutil.which(value) or local)
        if not path.is_file():
            raise ValueError(f'{source} 指定的 Python 不存在：{path}')
        return path.resolve(), source
    errors = []
    for name in ('runtime/python-portable/python.exe', '.venv/Scripts/python.exe'):
        path = root / name
        if not path.is_file():
            continue
        try:
            result = subprocess.run([str(path), '-I', '-c', 'import sys;print(sys.version_info >= (3,11))'],
                                    capture_output=True, text=True, timeout=10)
            if result.returncode == 0 and result.stdout.strip() == 'True':
                return path, 'auto'
            errors.append(name)
        except (OSError, subprocess.TimeoutExpired):
            errors.append(name)
    raise ValueError('找不到可运行的 Python 3.11+；请准备便携环境或用 -PythonExe / KB_PYTHON 指定解释器'
                     + (f'。无法使用：{", ".join(errors)}' if errors else ''))


def probe() -> dict:
    missing, optional, versions = [], [], {}
    for name in CORE_MODULES + OPTIONAL_MODULES:
        try:
            module = importlib.import_module(name)
            versions[name] = str(getattr(module, '__version__', 'available'))
        except (ImportError, OSError) as exc:
            (missing if name in CORE_MODULES else optional).append({'module': name, 'error': str(exc)})
    with sqlite3.connect(':memory:') as connection:
        try:
            connection.execute('create virtual table test using fts5(body)')
            fts = True
        except sqlite3.Error:
            fts = False
    return {'ok': sys.version_info >= (3, 11) and not missing and fts,
            'executable': sys.executable, 'version': sys.version.split()[0],
            'prefix': sys.prefix, 'base_prefix': sys.base_prefix, 'paths': sys.path,
            'fts5': fts, 'modules': versions, 'missing': missing, 'optional_missing': optional}


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--probe', action='store_true')
    parser.add_argument('--python', default='')
    args = parser.parse_args()
    if args.probe:
        report = probe()
    else:
        path, source = resolve_python(args.python)
        proc = subprocess.run([str(path), '-I', str(Path(__file__).resolve()), '--probe'],
                              capture_output=True, text=True, encoding='utf-8', timeout=60)
        if proc.returncode or not proc.stdout:
            raise SystemExit(f'Python 环境检查失败：{proc.stderr.strip()}')
        report = json.loads(proc.stdout)
        report['selected_by'] = source
    print(json.dumps(report, ensure_ascii=False, indent=2))
    return 0 if report['ok'] else 1


if __name__ == '__main__':
    if hasattr(sys.stdout, 'reconfigure'):
        sys.stdout.reconfigure(encoding='utf-8')
    raise SystemExit(main())
