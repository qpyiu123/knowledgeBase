"""从已有旧工作台复制运行库和完整 Qwen3.5 权重，不下载或覆盖现有文件。"""
from __future__ import annotations

import argparse
import json
import shutil
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'tools'))

from kb.llama_server import MODELS


def copy_existing(source: Path, destination: Path):
    if destination.exists():
        if destination.stat().st_size != source.stat().st_size:
            raise ValueError(f'目标已有不同大小的文件，保留原文件：{destination}')
        return 'existing'
    destination.parent.mkdir(parents=True, exist_ok=True)
    shutil.copy2(source, destination)
    return 'copied'


def prepare(source: Path, destination: Path = ROOT):
    artifacts = json.loads((source / 'resources/desktop-artifacts.lock.json').read_text(encoding='utf-8'))
    selected = [row for row in artifacts['artifacts'] if row['id'] in MODELS or row['id'] == 'vulkan']
    for model, name in MODELS.items():
        path = source / 'models' / name
        row = next(row for row in selected if row['id'] == model)
        with path.open('rb') as file:
            if file.read(4) != b'GGUF' or path.stat().st_size != row['bytes']:
                raise ValueError(f'模型不是清单中的完整 GGUF：{path}')
    results = []
    for model, name in MODELS.items():
        target = destination / 'models/gguf' / name
        results.append({'model': model, 'path': target.relative_to(destination).as_posix(),
                        'action': copy_existing(source / 'models' / name, target)})
    runtime = source / 'runtime/b11669-vulkan'
    for path in sorted(runtime.rglob('*')):
        if path.is_file():
            copy_existing(path, destination / 'runtime/llama-b11669-vulkan' / path.relative_to(runtime))
    manifest = {'runtime_release': 'b11669', 'default_model': 'qwen35-9b', 'artifacts': selected}
    for row in manifest['artifacts']:
        if row['id'] in MODELS:
            row['path'] = 'models/gguf/' + MODELS[row['id']]
        else:
            row['path'] = 'runtime/llama-b11669-vulkan/llama-server.exe'
            row['archive_bytes'] = row.pop('bytes')
            row['archive_sha256'] = row.pop('sha256')
    target_manifest = destination / 'docs/data/llama-resources.json'
    target_manifest.parent.mkdir(parents=True, exist_ok=True)
    target_manifest.write_text(json.dumps(manifest, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')
    return {'ok': True, 'models': results, 'runtime_files': sum(p.is_file() for p in runtime.rglob('*'))}


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--source', type=Path, required=True)
    args = parser.parse_args()
    print(json.dumps(prepare(args.source), ensure_ascii=False))
