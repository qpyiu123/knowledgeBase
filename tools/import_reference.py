"""从已下载的旧资料接收三篇完整 Python 文档，不改原件、不覆盖不同内容。"""
from __future__ import annotations

import argparse
import hashlib
import json
import re
from pathlib import Path

import yaml

ROOT = Path(__file__).resolve().parents[1]
MODULES = ('base64', 'json', 're')


def import_references(source: Path, root: Path = ROOT) -> list[dict]:
    license_file = root / 'licenses/python-3.9-license.html'
    if not license_file.is_file():
        raise ValueError('请先保存 Python 3.9 官方许可页到 licenses/python-3.9-license.html')
    manifest = json.loads((source / 'manifest.json').read_text(encoding='utf-8'))['documents']
    destination = root / 'kb/_reference/python39'
    destination.mkdir(parents=True, exist_ok=True)
    items = []
    for module in MODULES:
        filename = f'python39-{module}.zh.md'
        entry = next(item for item in manifest if item['source_path'].endswith(filename))
        original_file = source / filename
        original = original_file.read_text(encoding='utf-8')
        lines, fenced = [], False
        for line in original.splitlines():
            if line.startswith('```'):
                fenced = not fenced
            if not fenced and re.fullmatch(r'(?:class )?' + module + r'\.[A-Za-z_]\w*\(.*\)', line):
                line = '## ' + line
            lines.append(line)
        meta = {'title': entry['title'], 'category': 'misc', 'kind': 'api',
                'tags': ['Python', '官方文档', module],
                'signals': [module + suffix for suffix in (' 函数用法', ' 参数与返回值', ' 版本差异', ' 报错排查')],
                'difficulty': 'easy', 'source': entry['source_url'], 'tools': ['python'],
                'updated': '2026-11-05', 'version': entry['version'],
                'license': 'PSF-2.0; 文档代码另可采用 0BSD', 'original_date': entry['fetched_at'],
                'copyright': 'Copyright © 2001-2026 Python Software Foundation'}
        text = '---\n' + yaml.safe_dump(meta, allow_unicode=True, sort_keys=False) + '---\n\n' + '\n'.join(lines) + '\n'
        output = destination / f'{module}.md'
        if output.exists() and output.read_text(encoding='utf-8') != text:
            raise ValueError(f'目标已有不同内容，请先比较：{output}')
        if not output.exists():
            output.write_text(text, encoding='utf-8')
        items.append({'path': output.relative_to(root).as_posix(), 'title': entry['title'],
                      'source': entry['source_url'], 'version': entry['version'], 'original_file': filename,
                      'original_sha256': hashlib.sha256(original_file.read_bytes()).hexdigest(),
                      'original_text_sha256': hashlib.sha256((original.rstrip() + '\n').encode()).hexdigest(),
                      'changes': ['增加资料字段', '函数签名单列为小节，保留正文与代码'],
                      'license_file': 'licenses/python-3.9-license.html'})
    report = {'date': '2026-11-05', 'license_source': 'https://docs.python.org/3.9/license.html', 'items': items}
    out = root / 'docs/data/r1-reference-import.json'
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(json.dumps(report, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')
    return items


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--source-dir', type=Path, required=True)
    args = parser.parse_args()
    print(f'已接收 {len(import_references(args.source_dir))} 篇完整文档')
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
