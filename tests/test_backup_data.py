import sqlite3
from pathlib import Path
from zipfile import ZipFile

import pytest

from backup_data import backup, restore


def test_roundtrip_includes_methods_and_attachments(tmp_path: Path):
    root = tmp_path / 'app'
    root.mkdir()
    originals = {'kb/_methods/test.md': b'card', 'kb/_methods/scripts/test.py': b'code',
                 'work/attachments/a/upload.bin': bytes(range(256)),
                 'work/workspaces/a.json': b'{"id":"a"}', 'work/feedback/f.jsonl': b'{}',
                 'config.toml': b'[kb]'}
    for name, data in originals.items():
        p = root / name
        p.parent.mkdir(parents=True, exist_ok=True)
        p.write_bytes(data)
    (root / 'index').mkdir()
    db = sqlite3.connect(root / 'index/fts.db')
    db.execute('pragma journal_mode=wal')
    db.execute('create table docs(title)')
    db.execute("insert into docs values ('committed WAL')")
    db.commit()
    try:
        archive = backup(root)
        destination = tmp_path / 'restored'
        assert restore(archive, destination) == len(originals) + 1
        for name, data in originals.items():
            assert (destination / name).read_bytes() == data
            assert (root / name).read_bytes() == data
        with sqlite3.connect(destination / 'index/fts.db') as restored:
            assert restored.execute('select title from docs').fetchone()[0] == 'committed WAL'
    finally:
        db.close()


@pytest.mark.parametrize('name', ['../escape', 'kb/../../escape', 'C:/escape', 'kb\\..\\escape', 'models/private'])
def test_restore_rejects_paths_before_writing(tmp_path: Path, name: str):
    archive = tmp_path / 'bad.zip'
    with ZipFile(archive, 'w') as z:
        z.writestr('kb/valid.md', 'ok')
        z.writestr(name, 'bad')
    target = tmp_path / 'target'
    with pytest.raises(ValueError):
        restore(archive, target)
    assert not target.exists()


def test_restore_never_overwrites_existing_files(tmp_path: Path):
    archive = tmp_path / 'backup.zip'
    with ZipFile(archive, 'w') as z:
        z.writestr('kb/card.md', 'new')
    target = tmp_path / 'target'
    target.mkdir()
    original = target / 'mine'
    original.write_text('keep')
    with pytest.raises(ValueError, match='必须为空'):
        restore(archive, target)
    assert original.read_text() == 'keep'
