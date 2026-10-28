"""在 tests 目录下直接跑 pytest 也能导入 kb 包（不依赖 pytest.ini）。"""
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
for p in (ROOT / "tools", ROOT):
    if str(p) not in sys.path:
        sys.path.insert(0, str(p))
