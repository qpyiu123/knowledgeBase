"""复用已下载的 Python 3.13 嵌入包，显式准备项目内便携环境。"""
from __future__ import annotations

import argparse
import json
import subprocess
import sys
import zipfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def prepare(archive: Path, root: Path = ROOT) -> Path:
    destination = root / 'runtime/python-portable'
    if not (destination / 'python.exe').is_file():
        if destination.exists() and any(destination.iterdir()):
            raise ValueError(f'目标目录已有文件，请先检查：{destination}')
        with zipfile.ZipFile(archive) as package:
            if 'python313.dll' not in package.namelist():
                raise ValueError('请选择 Windows x64 的 Python 3.13 嵌入包')
            for item in package.infolist():
                target = (destination / item.filename).resolve()
                if not target.is_relative_to(destination.resolve()):
                    raise ValueError(f'压缩包路径越界：{item.filename}')
            package.extractall(destination)
    pth = destination / 'python313._pth'
    if not pth.is_file():
        raise ValueError('目标不是 Python 3.13 便携环境，请保留原目录后重新准备')
    # 所有路径均相对解释器，不读取机器上的 PYTHONPATH 或全局 site-packages。
    pth.write_text('python313.zip\n.\nLib/site-packages\n../../tools\nimport site\n', encoding='utf-8')
    return destination


def install_dependencies(destination: Path, wheel_dir: Path | None, offline: bool):
    command = [sys.executable, '-X', 'utf8', '-m', 'pip', 'install', '--only-binary=:all:', '--no-compile',
               '--python-version', '3.13', '--implementation', 'cp', '--abi', 'cp313',
               '--platform', 'win_amd64', '--target', str(destination / 'Lib/site-packages'),
               '--cache-dir', str(ROOT / '.cache/pip'), '-r', str(ROOT / 'requirements-runtime.txt')]
    if wheel_dir:
        command.extend(['--find-links', str(wheel_dir)])
    if offline:
        command.append('--no-index')
    subprocess.run(command, check=True)


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--archive', type=Path, required=True, help='已下载的 Python 3.13 Windows x64 嵌入 ZIP')
    parser.add_argument('--wheel-dir', type=Path, help='已有兼容 wheel 的目录')
    parser.add_argument('--install-deps', action='store_true', help='明确安装运行依赖到便携目录，不安装到系统')
    parser.add_argument('--offline', action='store_true', help='只用本地 wheel，不联网')
    args = parser.parse_args()
    destination = prepare(args.archive)
    if args.install_deps:
        install_dependencies(destination, args.wheel_dir, args.offline)
    python = destination / 'python.exe'
    probe = subprocess.run([str(python), '-I', str(ROOT / 'tools/python_runtime.py'), '--probe'],
                           capture_output=True, text=True, encoding='utf-8', check=False)
    if not probe.stdout:
        raise SystemExit(f'便携 Python 检查失败：{probe.stderr}')
    report = json.loads(probe.stdout)
    out = ROOT / 'runtime/python-runtime-info.json'
    out.write_text(json.dumps(report, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')
    print(probe.stdout)
    return 0 if report['ok'] else 1


if __name__ == '__main__':
    if hasattr(sys.stdout, 'reconfigure'):
        sys.stdout.reconfigure(encoding='utf-8')
    raise SystemExit(main())
