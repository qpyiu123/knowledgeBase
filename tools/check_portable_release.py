"""用实际 PowerShell 入口检查移动后的离线包。"""
from __future__ import annotations

import argparse
import json
import os
from pathlib import Path
import socket
import subprocess
import sys
import time
from urllib.parse import quote
from urllib.request import Request, ProxyHandler, build_opener
import uuid

from check_model_startup import free_port

ROOT = Path(__file__).resolve().parents[1]


def check_browser(base, out):
    from playwright.sync_api import sync_playwright
    errors, blocked = [], []
    with sync_playwright() as p:
        browser = p.chromium.launch(channel='msedge', headless=True)
        context = browser.new_context(service_workers='block')

        def route(req):
            if req.request.url.startswith(base + '/'):
                req.continue_()
            else:
                blocked.append(req.request.url)
                req.abort()

        context.route('**/*', route)
        page = context.new_page()
        page.on('pageerror', lambda error: errors.append(str(error)))
        page.goto(base + '/', wait_until='networkidle')
        page.get_by_label('搜索内容', exact=True).fill('base64.b64decode')
        page.get_by_role('button', name='查找', exact=True).click()
        page.locator('article.hit').first.wait_for()
        page.get_by_role('button', name='阅读资料', exact=False).first.click()
        page.get_by_role('dialog').wait_for()
        page.screenshot(path=str(out / 'page.png'))
        assert not errors, errors
        browser.close()
    return {'ok': True, 'external_requests_blocked': len(blocked)}


def check(physical, out, args):
    root = physical
    system = Path(os.environ['SystemRoot']) / 'System32'
    shell = system / 'WindowsPowerShell/v1.0/powershell.exe'
    inventory = json.loads((physical / 'release-manifest.json').read_text(encoding='utf-8'))
    for name, size in inventory['files'].items():
        assert (physical / name).stat().st_size == size, name
    assert not any((physical / name).exists() for name in ('.git', '.venv', 'tools/agent/webapp/node_modules'))
    env = {k: v for k, v in os.environ.items() if not k.upper().startswith(
        ('AGENT_', 'KB_', 'PYTHON', 'LLAMA_ARG_', 'OLLAMA_', 'HF_', 'TRANSFORMERS_'))}
    port, model_port, ollama_port = free_port(), free_port(), free_port()
    env.update(PATH=str(system), HTTP_PROXY='http://127.0.0.1:1', HTTPS_PROXY='http://127.0.0.1:1',
               ALL_PROXY='http://127.0.0.1:1', NO_PROXY='127.0.0.1,localhost', HF_HUB_OFFLINE='1',
               KB_MODEL_PORT=str(model_port), AGENT_MAX_TOKENS='16')
    if not args.backup:
        env.update(AGENT_WORKSPACE_DIR=str(out / 'workspaces'), AGENT_ATTACHMENT_DIR=str(out / 'attachments'),
                   AGENT_FEEDBACK_FILE=str(out / 'feedback.jsonl'))
    base = f'http://127.0.0.1:{port}'
    opener = build_opener(ProxyHandler({}))

    def run(*command, log=None):
        options = dict(cwd=out, env=env, timeout=160, creationflags=getattr(subprocess, 'CREATE_NO_WINDOW', 0))
        command = [str(x) for x in command]
        if log:
            # 启动器会留下后台服务；写日志文件，避免子进程保留父进程的输出管道。
            with (out / log).open('wb') as stream:
                result = subprocess.run(command, stdout=stream, stderr=subprocess.STDOUT, **options)
            output = (out / log).read_text(encoding='utf-8', errors='replace')
        else:
            result = subprocess.run(command, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, **options)
            output = result.stdout.decode('utf-8', errors='replace')
        if result.returncode:
            raise RuntimeError(f'命令退出 {result.returncode}：{command[0]}\n{output[-3000:]}')
        return output

    def ps(script, *arguments, log=None):
        return run(shell, '-NoProfile', '-ExecutionPolicy', 'Bypass', '-File', root / script, *arguments, log=log)

    def request(path, data=None, raw=False):
        req = Request(base + path, None if data is None else json.dumps(data).encode(),
                      {'Content-Type': 'application/json'})
        with opener.open(req, timeout=120 if raw else 20) as response:
            payload = response.read().decode('utf-8')
        return payload if raw else json.loads(payload)

    mapped = launched = False
    common = ('-NoBrowser', '-Port', port, '-OllamaPort', ollama_port, '-LogDirectory', out)
    if not args.model:
        common += ('-NoModel',)
    try:
        if args.drive:
            if Path(args.drive + '/').exists():
                raise ValueError(f'{args.drive} 已被使用')
            run(system / 'subst.exe', args.drive, physical.parent)
            mapped = True
            root = Path(args.drive + '/') / physical.name
        probe = json.loads(ps('start.ps1', '-CheckEnvironment', '-LogDirectory', out, log='python.txt'))
        runtime = physical / 'runtime/python-portable'
        assert probe['ok'] and not probe['optional_missing'], probe
        assert Path(probe['base_prefix']).resolve() == runtime
        assert all(Path(p).resolve().is_relative_to(physical) for p in probe['paths']), probe
        t0 = time.perf_counter()
        launched = True
        choice = ('-ChatModel', args.model) if args.model not in (None, 'default') else ()
        ps('start.ps1', *common, *choice, log='launcher.txt')
        startup_s = round(time.perf_counter() - t0, 2)
        health = request('/api/health')
        assert health['index_ok'] and health['index']['docs'] == inventory['index']['docs'], health
        assert Path(health['runtime']['executable']).resolve() == runtime / 'python.exe'
        assert health['model_ok'] == bool(args.model), health
        assert 'assets/index-' in request('/', raw=True)
        doc = '_reference/python39/base64.md'
        hits = request('/api/search', {'q': 'base64.b64decode', 'top_k': 5, 'retrieval': 'fts'})['hits']
        assert any(hit['path'] == doc for hit in hits), hits
        assert 'base64.b64decode' in request('/api/doc?path=' + quote(doc))['body']
        assert '--max-k' in request('/api/code?path=_methods/scripts/rsa_small_e.py')['arguments']
        semantic = json.loads(run(root / 'runtime/python-portable/python.exe', '-B', '-X', 'utf8',
                                  root / 'tools/cli.py', 'search', '两个密文共用相同的模数', '--vec-only', '--json'))
        assert semantic['hits'], semantic
        wid = request('/api/workspaces', {'title': '移动包验收'})['workspace']['id']
        request(f'/api/workspaces/{wid}/entries', {'kind': 'fact', 'text': '离线保存检查'})
        assert request(f'/api/workspaces/{wid}')['workspace']['entries'][0]['text'] == '离线保存检查'
        report = {'ok': True, 'profile': inventory['profile'], 'drive': root.drive, 'python': probe['version'],
                  'startup_s': startup_s, 'docs': health['index']['docs'], 'keyword_and_code': True,
                  'semantic': True, 'workspace_save': True, 'model': health.get('model') if args.model else None,
                  'network': '子进程外网代理不可达，未关闭系统网卡'}
        if args.model:
            expected = inventory['default_model'] if args.model == 'default' else args.model
            assert health['model'] == expected, health
            stream = request('/api/ask', {'q': '简短说明 RSA 共模第一步',
                'paths': ['crypto/rsa-common-modulus-attack.md']}, raw=True)
            events = [json.loads(line[5:]) for line in stream.splitlines() if line.startswith('data:')]
            assert any(e['t'] == 'tok' for e in events) and events[-1]['t'] == 'done' and all(e['t'] != 'err' for e in events), events
            report['explanation_tokens'] = sum(e['t'] == 'tok' for e in events)
        if args.browser:
            report['edge'] = check_browser(base, out)
        ps('start.ps1', '-Stop', *common, log='stop.txt')
        for check_port in (port, model_port):
            with socket.socket() as sock:
                assert sock.connect_ex(('127.0.0.1', check_port)) != 0, f'测试端口仍在监听：{check_port}'
        launched = False
        if args.backup:
            ps('backup.ps1', log='backup.txt')
            archive = max((physical / 'backup').glob('ctf_kb_*.zip'), key=lambda p: p.stat().st_mtime)
            restored = out / 'restore'
            ps('backup.ps1', '-Restore', archive, '-Destination', restored, log='restore.txt')
            workspace = restored / 'work/workspaces' / f'{wid}.json'
            assert '离线保存检查' in workspace.read_text(encoding='utf-8')
            assert (restored / 'index/fts.db').stat().st_size > 0
            report['backup_restore'] = True
        return report
    finally:
        try:
            if launched:
                ps('start.ps1', '-Stop', *common, log='stop-finally.txt')
        finally:
            if mapped:
                run(system / 'subst.exe', args.drive, '/D')


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('directory', type=Path)
    parser.add_argument('--model', choices=('default', 'qwen35-9b', 'qwen35-4b'))
    parser.add_argument('--drive', choices=tuple(chr(c) + ':' for c in range(68, 91)))
    parser.add_argument('--backup', action='store_true', help='只在专门测试目录备份样例记录')
    parser.add_argument('--browser', action='store_true')
    args = parser.parse_args()
    target = args.directory.resolve()
    if not target.is_relative_to(ROOT):
        parser.error('请指定项目内本次打包生成的测试目录')
    out = ROOT / 'work/r5' / ('check-' + uuid.uuid4().hex[:8])
    out.mkdir(parents=True)
    result = check(target, out, args)
    (out / 'result.json').write_text(json.dumps(result, ensure_ascii=False, indent=2), encoding='utf-8')
    print(json.dumps(result | {'log_dir': str(out)}, ensure_ascii=False))


if __name__ == '__main__':
    sys.stdout.reconfigure(encoding='utf-8')
    main()
