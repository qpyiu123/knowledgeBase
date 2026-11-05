import json

import pytest

from kb.llama_server import MODELS
from prepare_llama_resources import prepare


def source(tmp_path):
    src = tmp_path / 'old'
    (src / 'models').mkdir(parents=True)
    (src / 'runtime/b11669-vulkan').mkdir(parents=True)
    (src / 'runtime/b11669-vulkan/llama-server.exe').write_bytes(b'runtime')
    artifacts = []
    for ident, name in MODELS.items():
        (src / 'models' / name).write_bytes(b'GGUF')
        artifacts.append({'id': ident, 'bytes': 4, 'path': 'models/' + name})
    artifacts.append({'id': 'vulkan', 'bytes': 10, 'sha256': 'archive', 'path': 'runtime.zip'})
    (src / 'resources').mkdir()
    (src / 'resources/desktop-artifacts.lock.json').write_text(json.dumps({'artifacts': artifacts}), encoding='utf-8')
    return src


def test_copy_is_repeatable_and_leaves_originals_and_part_files(tmp_path):
    src = source(tmp_path)
    (src / 'models/model.gguf.part').write_bytes(b'partial')
    dest = tmp_path / 'project'
    assert all(row['action'] == 'copied' for row in prepare(src, dest)['models'])
    assert all(row['action'] == 'existing' for row in prepare(src, dest)['models'])
    assert (src / 'models/model.gguf.part').read_bytes() == b'partial'
    assert not list(dest.rglob('*.part'))
    assert (src / 'runtime/b11669-vulkan/llama-server.exe').is_file()


def test_existing_different_file_is_never_overwritten(tmp_path):
    src = source(tmp_path)
    dest = tmp_path / 'project'
    (dest / 'models/gguf').mkdir(parents=True)
    existing = dest / 'models/gguf' / MODELS['qwen35-9b']
    existing.write_bytes(b'user-data')
    with pytest.raises(ValueError, match='保留原文件'):
        prepare(src, dest)
    assert existing.read_bytes() == b'user-data'


def test_incomplete_source_is_rejected_before_copying(tmp_path):
    src = source(tmp_path)
    (src / 'models' / MODELS['qwen35-4b']).write_bytes(b'partial')
    with pytest.raises(ValueError, match='完整 GGUF'):
        prepare(src, tmp_path / 'project')
    assert not (tmp_path / 'project').exists()
