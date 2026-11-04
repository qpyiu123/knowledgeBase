"""检查独立解释器、带空格目录、实际离线服务与方法脚本；不复制应用或模型。"""
from __future__ import annotations

import json
import os
import shutil
import subprocess
import sys
import socket
import uuid
from urllib.request import urlopen
from pathlib import Path

from python_runtime import ROOT, resolve_python


def run(python: Path, arguments: list[str], env: dict, timeout=120):
    process = subprocess.run([str(python), '-I', *arguments], cwd=ROOT, env=env,
                             capture_output=True, timeout=timeout)
    output = process.stdout.decode('utf-8')
    errors = process.stderr.decode('utf-8')
    if process.returncode:
        raise RuntimeError(f'检查失败：{arguments[0]}\n{output}\n{errors}')
    return output


def main() -> int:
    python, selected_by = resolve_python()
    work = ROOT / 'work/r13'
    work.mkdir(parents=True, exist_ok=True)
    environment = {k: v for k, v in os.environ.items() if not k.upper().startswith('PYTHON') and k.upper() != 'KB_PYTHON'}
    environment['PATH'] = str(Path(os.environ['SystemRoot']) / 'System32')
    probe_script = str(ROOT / 'tools/python_runtime.py')
    report = json.loads(run(python, [probe_script, '--probe'], environment))
    if Path(report['prefix']).resolve() != python.parent.resolve() or report['prefix'] != report['base_prefix']:
        raise ValueError('当前选中的不是独立 Python，检查 config.toml 和 KB_PYTHON')
    if any(not Path(path).resolve().is_relative_to(ROOT) for path in report['paths']):
        raise ValueError('便携环境仍在引用项目外目录')
    destination = work / '移动目录 带空格/runtime/python-portable'
    if not destination.exists():
        destination.parent.mkdir(parents=True, exist_ok=True)
        shutil.copytree(python.parent, destination, ignore=shutil.ignore_patterns('__pycache__'))
    moved = destination / 'python.exe'
    moved_report = json.loads(run(moved, [probe_script, '--probe'], environment))
    if not moved_report['ok'] or Path(moved_report['base_prefix']).resolve() != destination.resolve():
        raise ValueError('移动后的运行环境检查失败')
    smoke = json.loads(run(moved, [str(ROOT / 'tools/check_offline_baseline.py')], environment).strip())
    if not smoke['ok'] or smoke['generation_calls'] != 0:
        raise ValueError('独立环境的实际离线查询检查失败')
    run(moved, [str(ROOT / 'tools/accept_methods.py'), '--selftest', '--output',
                str(work / 'portable-methods.json')], environment, timeout=180)
    methods = json.loads((work / 'portable-methods.json').read_text(encoding='utf-8'))
    payload = json.loads(run(moved, [str(ROOT / 'tools/cli.py'), 'search', '用户名欢迎语 7*7 回显 49', '--json'], environment))
    hits = payload['hits']
    if not any(hit['path'] == '_methods/ssti_generic.md' for hit in hits):
        raise ValueError('便携环境的语义检索没有找到预期方法卡')
    # 使用独立日志和空闲端口验证真正的 PowerShell 启动入口。
    with socket.socket() as sock:
        sock.bind(('127.0.0.1', 0))
        port = sock.getsockname()[1]
    logs = work / ('start-logs-' + uuid.uuid4().hex[:8])
    shell = Path(os.environ['SystemRoot']) / 'System32/WindowsPowerShell/v1.0/powershell.exe'
    # Windows 后台进程可能继承管道句柄，启动器输出写文件，避免等待管道 EOF。
    with (work / 'start-output.txt').open('wb') as output:
        launched = subprocess.run([str(shell), '-NoProfile', '-ExecutionPolicy', 'Bypass', '-File',
                                   str(ROOT / 'start.ps1'), '-NoModel', '-NoBrowser', '-Port', str(port),
                                   '-PythonExe', str(moved), '-LogDirectory', str(logs)],
                                  cwd=ROOT, env=environment, stdout=output,
                                  stderr=subprocess.STDOUT, timeout=70)
    owned_pid = int((logs / 'web.pid').read_text().strip())
    with urlopen(f'http://127.0.0.1:{port}/api/health', timeout=15) as response:
        health = json.loads(response.read())
    if health['runtime']['pid'] != owned_pid or Path(health['runtime']['executable']) != moved:
        raise ValueError('监听进程与本次启动的便携环境不一致，请检查测试日志')
    try:
        if (launched.returncode or not health['index_ok'] or health.get('generation_enabled') is not False
                or (logs / 'ollama.pid').exists()):
            raise ValueError('PowerShell 启动检查失败，参见 work/r13/start-output.txt')
        with urlopen(f'http://127.0.0.1:{port}/', timeout=10) as response:
            assert response.status == 200 and b'<html' in response.read().lower()
    finally:
        # PID 由本次独立日志记录，并已与该服务的 health 返回值核对。
        subprocess.run([str(shell), '-NoProfile', '-Command', f'Stop-Process -Id {owned_pid}'],
                       check=True, capture_output=True)
    result = {'ok': True, 'selected_by': selected_by, 'runtime': report,
              'relocated_runtime': moved_report['executable'], 'external_python_removed_from_path': True,
              'http': smoke, 'semantic_hits': len(hits), 'methods': methods['accepted'],
              'script_selftests': sum(item['ok'] for item in methods['scripts']),
              'powershell51_start': True, 'model_service_started': False}
    (work / 'portable-acceptance.json').write_text(json.dumps(result, ensure_ascii=False, indent=2), encoding='utf-8')
    print(json.dumps({key: value for key, value in result.items() if key != 'runtime'}, ensure_ascii=False))
    return 0


if __name__ == '__main__':
    for stream in (sys.stdout, sys.stderr):
        if hasattr(stream, 'reconfigure'):
            stream.reconfigure(encoding='utf-8')
    raise SystemExit(main())
