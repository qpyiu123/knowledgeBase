"""正式题解、出处、配图和阅读器代码入口的检查。"""

import json
import posixpath
from pathlib import Path

from kb.images import IMAGE_DIR
from kb.library import document_info, read_code
from kb.parser import Doc, chunk_doc, split_front_matter

ROOT = Path(__file__).resolve().parents[1]
KB = ROOT / "kb"


def test_approved_writeups_have_readable_summaries_and_evidence():
    rows = json.loads(
        (ROOT / "docs/data/r66-curation.json").read_text(encoding="utf-8")
    )
    assert len(rows) == len({row["id"] for row in rows}) == 19
    for row in rows:
        raw = (KB / row["path"]).read_text(encoding="utf-8")
        meta, body = split_front_matter(raw, strict=True)
        assert meta["origin_id"] == row["id"]
        assert meta["kind"] == "writeup"
        assert "## 先看这一步" in body and row["summary"]["text"] in body
        for group in (row["conditions"], row["limits"]):
            assert all(item["text"] in body for item in group)
        assert all(quote in body for quote in row["quotes"].values())
        assert all(url in body for url in row["sources"])
        for section in [
            row["summary"],
            *row["conditions"],
            *row["limits"],
            *row["steps"],
        ]:
            assert (
                section["evidence"] and set(section["evidence"]) <= row["quotes"].keys()
            )
        previous = set()
        for step in row["steps"]:
            assert set(step["depends_on"]) <= previous
            previous.add(step["id"])
        for marker in row["code_contains"]:
            assert body.count(marker) == 1
        info = document_info(KB, row["path"], raw)
        assert [script["path"] for script in info["scripts"]] == row["code"]
        for code in row["code"]:
            assert read_code(KB, code)["summary"]
        for image in row["images"]:
            assert (KB / image).is_file() and image in body


def test_archived_images_keep_caption_but_not_file_name_in_search_chunks():
    ref = "../../_assets/images/" + "a" * 64 + ".png"
    body = (
        f"## 先看格式\n先核对位数。\n![界面左侧是事件类型]({ref})\n\n"
        f"## 原文配图\n![重复图]({ref})\n"
    )
    chunks = chunk_doc(Doc(path="demo.md", title="测试", category="misc", body=body))
    assert len(chunks) == 1
    assert "界面左侧是事件类型" in chunks[0]["text"]
    assert "_assets" not in chunks[0]["text"]


def test_image_source_records_point_to_files_and_article_references():
    rows = json.loads((KB / "_assets/_sources.json").read_text(encoding="utf-8"))
    assert {row["method"] for row in rows} >= {"本地原件", "原链接取回"}
    articles = {}
    for row in rows:
        article = row["article"]
        asset = f"{IMAGE_DIR}/{row['image']}"
        assert (KB / asset).stat().st_size == row["bytes"]
        if article not in articles:
            articles[article] = (KB / article).read_text(encoding="utf-8")
        assert posixpath.relpath(asset, posixpath.dirname(article)) in articles[article]
