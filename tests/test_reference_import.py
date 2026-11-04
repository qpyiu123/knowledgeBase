import json
import hashlib
import re
from pathlib import Path

from kb.library import document_info
from kb.parser import split_front_matter

ROOT = Path(__file__).resolve().parents[1]


def test_python_reference_has_body_version_source_and_local_license():
    manifest = json.loads((ROOT / 'docs/data/r1-reference-import.json').read_text(encoding='utf-8'))
    assert len(manifest['items']) == 3
    for item in manifest['items']:
        file = ROOT / item['path']
        text = file.read_text(encoding='utf-8')
        meta, body = split_front_matter(text, strict=True)
        assert meta['kind'] == 'api'
        assert meta['version'] == 'Python 3.9'
        assert meta['source'] == item['source']
        original = re.sub(r'^## (?=(?:class )?(?:base64|json|re)\.[A-Za-z_]\w*\(.*\)$)', '', body, flags=re.M)
        assert hashlib.sha256((original.strip() + '\n').encode()).hexdigest() == item['original_text_sha256']
        assert (ROOT / item['license_file']).is_file()
        assert document_info(ROOT / 'kb', file.relative_to(ROOT / 'kb').as_posix(), text)['kind_label'] == 'API 参考'
    assert '## base64.b64decode(' in (ROOT / 'kb/_reference/python39/base64.md').read_text(encoding='utf-8')
