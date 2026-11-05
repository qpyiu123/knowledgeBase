"""检查实际 PowerShell 入口选择 4B、网页解释与仅关闭本次测试服务。"""
from __future__ import annotations

import json
import os
import socket
import subprocess
import sys
import uuid
from pathlib import Path
from urllib.request import Request, urlopen

ROOT = Path(__file__).resolve().parents[1]


def free_port():
    with socket.socket() as sock:
        sock.bind(('127.0.0.1', 0))
        return sock.getsockname()[1]


def main():
    out = ROOT / 'work/r32' / ('start-' + uuid.uuid4().hex[:8])
    out.mkdir(parents=True)
    port, model_port = free_port(), free_port()
    shell = Path(os.environ['SystemRoot']) / 'System32/WindowsPowerShell/v1.0/powershell.exe'
    environment = dict(os.environ, KB_MODEL_PORT=str(model_port), AGENT_MAX_TOKENS='16')
    owned = []
    try:
        with (out / 'launcher.txt').open('wb') as log:
            result = subprocess.run([str(shell), '-NoProfile', '-ExecutionPolicy', 'Bypass', '-File',
                str(ROOT / 'start.ps1'), '-NoBrowser', '-ChatModel', 'qwen35-4b', '-Port', str(port),
                '-LogDirectory', str(out)], cwd=ROOT, env=environment, stdout=log, stderr=subprocess.STDOUT,
                creationflags=getattr(subprocess, 'CREATE_NO_WINDOW', 0), timeout=150)
        for name in ('llama', 'web'):
            pid = int((out / (name + '.pid')).read_text().strip())
            command = subprocess.check_output([str(shell), '-NoProfile', '-Command',
                f'(Get-CimInstance Win32_Process -Filter "ProcessId = {pid}").CommandLine'], encoding='utf-8')
            assert str(ROOT).casefold() in command.casefold(), command
            if name == 'llama':
                assert '--alias qwen35-4b' in command
            owned.append(pid)
        with urlopen(f'http://127.0.0.1:{port}/api/health', timeout=15) as response:
            health = json.loads(response.read())
        assert result.returncode == 0 and health['model_ok'] and health['index_ok']
        assert health['model'] == 'qwen35-4b' and health['backend'] == 'llama_server'
        assert health['runtime']['pid'] == owned[1]
        request = Request(f'http://127.0.0.1:{port}/api/ask',
            data=json.dumps({'q': 'RSA 共模的第一步检查什么？简短回答。',
                             'paths': ['crypto/rsa-common-modulus-attack.md']}).encode(),
            headers={'Content-Type': 'application/json'})
        with urlopen(request, timeout=180) as response:
            stream = response.read().decode('utf-8')
        events = [json.loads(line[5:]) for line in stream.splitlines() if line.startswith('data:')]
        assert any(e['t'] == 'tok' for e in events), events
        assert events[-1]['t'] == 'done', events
        assert all(e['t'] != 'err' for e in events), events
        report = {'ok': True, 'powershell': '5.1', 'model': health['model'], 'backend': health['backend'],
                  'runtime': health['runtime'], 'query_and_index': True, 'sse': [e['t'] for e in events],
                  'text': ''.join(e.get('v', '') for e in events if e['t'] == 'tok')}
        (ROOT / 'work/r32/startup-result.json').write_text(json.dumps(report, ensure_ascii=False, indent=2), encoding='utf-8')
        print(json.dumps(report, ensure_ascii=False))
    finally:
        for name in ('web', 'llama'):
            record = out / (name + '.pid')
            if not record.exists():
                continue
            pid = int(record.read_text().strip())
            if pid not in owned:
                command = subprocess.check_output([str(shell), '-NoProfile', '-Command',
                    f'(Get-CimInstance Win32_Process -Filter "ProcessId = {pid}").CommandLine'], encoding='utf-8')
                if str(ROOT).casefold() in command.casefold():
                    owned.append(pid)
        for pid in reversed(owned):
            subprocess.run([str(shell), '-NoProfile', '-Command', f'Stop-Process -Id {pid} -ErrorAction SilentlyContinue'],
                           capture_output=True)
    return 0


if __name__ == '__main__':
    sys.stdout.reconfigure(encoding='utf-8')
    raise SystemExit(main())
