"""库内文档的来源、配套代码和只读代码内容。"""
from __future__ import annotations

import ast
import re
import sqlite3
import sys
from pathlib import Path

from .parser import split_front_matter

CODE_LANGUAGES = {".py": "python", ".js": "javascript", ".ts": "typescript",
                  ".c": "c", ".cpp": "cpp", ".h": "c", ".rs": "rust", ".sol": "solidity"}
CODE_LINK = re.compile(r"kb[/\\]((?:_methods[/\\]scripts|_code)[/\\][\w/\\.-]+)")


def code_path(root: Path, name: str) -> Path:
    if not isinstance(name, str):
        raise ValueError("需要库内代码路径")
    root = root.resolve()
    p = (root / name).resolve()
    if (not p.is_relative_to(root) or p.suffix not in CODE_LANGUAGES
            or not any(p.is_relative_to(root / scope) for scope in ("_methods/scripts", "_code"))):
        raise ValueError("只能查看库内 _methods/scripts 或 _code 下的代码")
    if not p.is_file():
        raise FileNotFoundError("代码文件不存在")
    if p.stat().st_size > 1024 * 1024:
        raise ValueError("代码文件超过 1 MiB，请在本地编辑器中查看")
    return p


def read_code(root: Path, name: str) -> dict:
    path = code_path(root, name)
    body = path.read_text(encoding="utf-8-sig")
    dependencies = []
    arguments = []
    summary = ""
    if path.suffix == ".py":
        try:
            tree = ast.parse(body)
            summary = (ast.get_docstring(tree) or "").split("\n\n")[0]
            imports = set()
            for node in ast.walk(tree):
                if isinstance(node, ast.Import):
                    imports.update(alias.name.split('.')[0] for alias in node.names)
                elif isinstance(node, ast.ImportFrom) and node.module and not node.level:
                    imports.add(node.module.split('.')[0])
                elif (isinstance(node, ast.Call) and isinstance(node.func, ast.Attribute)
                      and node.func.attr == 'add_argument'):
                    arguments.extend(a.value for a in node.args if isinstance(a, ast.Constant)
                                     and isinstance(a.value, str) and a.value.startswith('--'))
            dependencies = sorted(imports - sys.stdlib_module_names - {'__future__'})
        except SyntaxError:
            pass
    return {"path": path.relative_to(root.resolve()).as_posix(), "body": body,
            "language": CODE_LANGUAGES[path.suffix], "dependencies": dependencies,
            "arguments": arguments, "summary": summary}


def document_info(root: Path, name: str, body: str) -> dict:
    meta, _ = split_front_matter(body)
    sources = []
    raw = meta.get("source", [])
    values = re.split(r"[,，;；]", raw) if isinstance(raw, str) else raw
    if isinstance(values, list):
        for value in values:
            text = str(value).strip().replace('\\', '/')
            if text.startswith(('https://', 'http://')):
                sources.append({"path": text, "external": True})
            elif text.startswith('kb/'):
                p = (root / text[3:]).resolve()
                if p.is_relative_to(root.resolve()) and p.suffix == '.md' and p.is_file():
                    sources.append({"path": p.relative_to(root.resolve()).as_posix(), "external": False})
    scripts = []
    seen = set()
    for match in dict.fromkeys(CODE_LINK.findall(body)):
        try:
            p = code_path(root, match.replace('\\', '/'))
        except (ValueError, OSError):
            continue
        path = p.relative_to(root.resolve()).as_posix()
        if path not in seen:
            scripts.append({"path": path, "title": p.name})
            seen.add(path)
    kind = str(meta.get('kind', ''))
    if name.startswith('_methods/'):
        kind = 'method'
    elif name.startswith(('_imported/', '_imported_cats/', '_des/cards/')):
        kind = 'writeup'
    if kind not in ('method', 'writeup', 'api', 'tutorial'):
        kind = 'tutorial'
    return {"scripts": scripts, "sources": sources, "kind": kind,
            "kind_label": {'method': '方法卡', 'writeup': '题解', 'api': 'API 参考', 'tutorial': '教程'}[kind]}


class LibraryCatalog:
    """从已有 FTS 清单读取方法卡的明确来源关系；索引更新后刷新内存缓存。"""

    def __init__(self, root: Path, index: Path):
        self.root, self.index = root, index
        self._stamp = None
        self._related = {}

    def _refresh(self):
        if not self.index.is_file():
            return
        stat = self.index.stat()
        stamp = (stat.st_mtime_ns, stat.st_size)
        if self._stamp == stamp:
            return
        related = {}
        with sqlite3.connect(self.index) as connection:
            rows = connection.execute("SELECT path, title FROM docs WHERE path GLOB '_methods/*'").fetchall()
        for path, title in rows:
            file = (self.root / path).resolve()
            if not file.is_relative_to(self.root.resolve()) or not file.is_file():
                continue
            info = document_info(self.root, path, file.read_text(encoding='utf-8-sig'))
            for source in info['sources']:
                if source['external']:
                    continue
                entry = related.setdefault(source['path'], {'methods': [], 'scripts': []})
                entry['methods'].append({'path': path, 'title': title})
                entry['scripts'].extend(info['scripts'])
        self._related, self._stamp = related, stamp

    def info(self, path: str, body: str) -> dict:
        result = document_info(self.root, path, body)
        self._refresh()
        related = self._related.get(path, {})
        result['methods'] = related.get('methods', [])
        have = {item['path'] for item in result['scripts']}
        for item in related.get('scripts', []):
            if item['path'] not in have:
                result['scripts'].append(item)
                have.add(item['path'])
        return result
