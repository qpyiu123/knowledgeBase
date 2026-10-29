"""题目工作区：本地 JSON 存储与 HTTP API 的离线测试。

不启动 Ollama、不加载嵌入模型；工作区只写临时目录。
"""
from __future__ import annotations

import http.client
import json
import threading
from http.server import ThreadingHTTPServer
from pathlib import Path
from types import SimpleNamespace

import pytest

from agent import server
from agent.workspace import (
    WorkspaceError,
    WorkspaceExists,
    WorkspaceNotFound,
    WorkspaceStore,
)


@pytest.fixture()
def store(tmp_path: Path) -> WorkspaceStore:
    return WorkspaceStore(tmp_path / "workspaces")


def test_create_list_load_and_delete(store: WorkspaceStore):
    ws = store.create("共模攻击", "crypto")
    assert ws["title"] == "共模攻击"
    assert ws["category"] == "crypto"
    assert ws["status"] == "open"
    assert ws["entries"] == []
    assert ws["timeline"][0]["kind"] == "create"

    wid = ws["id"]
    listed = store.list()
    assert [w["id"] for w in listed] == [wid]
    assert listed[0]["entries"] == 0
    assert listed[0]["counts"] == {"fact": 0, "attempt": 0, "reference": 0}

    loaded = store.load(wid)
    assert loaded["title"] == "共模攻击"

    store.delete(wid)
    assert store.list() == []
    with pytest.raises(WorkspaceNotFound):
        store.load(wid)


def test_user_supplied_id_and_duplicate(store: WorkspaceStore):
    ws = store.create("自定义", workspace_id="my-ws_1")
    assert ws["id"] == "my-ws_1"
    with pytest.raises(WorkspaceExists):
        store.create("重复", workspace_id="my-ws_1")
    assert (store.root / "my-ws_1.json").is_file()


@pytest.mark.parametrize("wid", ["../evil", "a/b", "x" * 65, "中文"])
def test_invalid_workspace_id(store: WorkspaceStore, wid):
    with pytest.raises(WorkspaceError):
        store.create("标题", workspace_id=wid)


@pytest.mark.parametrize("title", ["", "   ", "t" * 121, 123])
def test_invalid_title(store: WorkspaceStore, title):
    with pytest.raises(WorkspaceError):
        store.create(title)


def test_update_rename_and_status_timeline(store: WorkspaceStore):
    ws = store.create("旧标题")
    wid = ws["id"]

    updated = store.update(wid, title="新标题", status="solved", category="web")
    assert updated["title"] == "新标题"
    assert updated["status"] == "solved"
    assert updated["category"] == "web"
    assert any(e["kind"] == "update" for e in updated["timeline"])

    with pytest.raises(WorkspaceError):
        store.update(wid, status="done")


def test_add_entries_and_timeline_is_read_only(store: WorkspaceStore):
    wid = store.create("题目").get("id")
    _, fact = store.add_entry(wid, kind="fact", text="n 相同")
    _, attempt = store.add_entry(
        wid, kind="attempt", direction="先试共模", conclusion="能直接恢复 m",
        result="pending",
    )
    _, ref = store.add_entry(wid, kind="reference", title="RSA 专题",
                             path="crypto/rsa.md", text="先读这篇")

    loaded = store.load(wid)
    assert [e["kind"] for e in loaded["entries"]] == ["fact", "attempt", "reference"]
    assert loaded["entries"][0]["id"] == fact["id"]
    assert loaded["entries"][1]["result"] == "pending"
    assert loaded["entries"][1]["direction"] == "先试共模"
    assert loaded["entries"][1]["conclusion"] == "能直接恢复 m"
    assert loaded["entries"][2]["path"] == "crypto/rsa.md"

    kinds = [ev["kind"] for ev in store.timeline(wid)]
    assert kinds[0] == "create"
    assert kinds.count("entry") == 3
    assert all("ts" in ev and "summary" in ev for ev in store.timeline(wid))

    store.delete_entry(wid, ref["id"])
    loaded = store.load(wid)
    assert len(loaded["entries"]) == 2
    assert store.timeline(wid)[-1]["kind"] == "entry_delete"
    with pytest.raises(WorkspaceNotFound):
        store.delete_entry(wid, ref["id"])

    # 状态只改尝试条目
    updated, entry = store.update_entry(wid, attempt["id"], result="success")
    assert entry["result"] == "success"
    assert any(e["kind"] == "entry_update" for e in updated["timeline"])
    with pytest.raises(WorkspaceError):
        store.update_entry(wid, fact["id"], result="success")


@pytest.mark.parametrize("payload", [
    {"kind": "unknown", "text": "x"},
    {"kind": "fact", "text": ""},
    {"kind": "attempt", "text": "x", "result": "maybe"},
    {"kind": "reference", "title": "x", "url": "ftp://example.com"},
    {"kind": "fact", "text": "x" * 4001},
    {"kind": "reference", "title": "x", "path": "p" * 501},
    {"kind": "reference", "title": "x", "report": "not-an-object"},
    {"kind": "reference", "title": "x", "anchor": "sec"},
    {"kind": "reference", "title": "x", "path": "a.md", "anchor": "a" * 201},
    {"kind": "attempt", "direction": "d" * 501},
])
def test_add_entry_validation(store: WorkspaceStore, payload):
    wid = store.create("题目").get("id")
    with pytest.raises(WorkspaceError):
        store.add_entry(wid, **payload)


def test_export_markdown_contains_all_sections(store: WorkspaceStore):
    wid = store.create("Web 上传", "web").get("id")
    store.add_entry(wid, kind="fact", text="过滤了 <?")
    _, attempt = store.add_entry(wid, kind="attempt", direction="短标签绕过",
                                 conclusion="被过滤，无效")
    store.update_entry(wid, attempt["id"], result="failed")
    store.add_entry(wid, kind="reference", path="web/upload-bypass.md",
                    title="文件上传绕过", text="重点看后缀")

    md = store.export_markdown(wid)
    assert "# Web 上传" in md
    assert "## 事实" in md
    assert "过滤了 <?" in md
    assert "## 尝试" in md
    assert "`failed`" in md
    assert "方向：短标签绕过" in md
    assert "结论：被过滤，无效" in md
    assert "## 资料收藏" in md
    assert "`web/upload-bypass.md`" in md
    assert "## 时间线" in md


def test_writeup_export_is_traceable(store: WorkspaceStore, tmp_path: Path):
    kb = tmp_path / "kb"
    (kb / "crypto").mkdir(parents=True)
    (kb / "crypto" / "rsa.md").write_text(
        "---\ntitle: RSA\n---\n## 三、解题步骤\n正文\n", encoding="utf-8",
    )
    wid = store.create("RSA 共模", "crypto").get("id")
    _, fact = store.add_entry(wid, kind="fact", text="n 相同，e 不同")
    _, attempt = store.add_entry(
        wid, kind="attempt", direction="先试共模", conclusion="能直接恢复明文",
        result="success", text="脚本见下",
    )
    _, ref = store.add_entry(
        wid, kind="reference", title="RSA 共模攻击", path="crypto/rsa.md",
        anchor="三、解题步骤", text="重点看推导",
    )
    store.add_entry(wid, kind="reference", title="缺失资料",
                    path="crypto/missing.md")
    store.add_entry(
        wid, kind="reference", title="sample.png", source="analyze",
        path="work/attachments/x/upload_sample.png", text="附件报告",
        report={"executed": False, "file": {"name": "sample.png", "size": 3,
                                            "sha256": "abc"},
                "type": {"kind": "PNG", "is_text": False},
                "anomalies": [], "decoded": [], "warnings": []},
    )
    store.add_entry(wid, kind="fact", text="最终拿到 flag{writeup_demo}")

    md = store.export_writeup(wid, kb_root=kb)

    assert md.startswith("# Writeup 草稿：RSA 共模")
    assert "## 事实" in md
    assert "## 尝试（按时间序）" in md
    assert "## 用到的 kb 资料" in md
    assert "## Flag" in md
    assert "## 时间线" in md
    assert f"来源 #{fact['id']}" in md
    assert f"来源 #{attempt['id']}" in md
    assert f"来源 #{ref['id']}" in md
    assert f"<!-- entry:{fact['id']} -->" in md
    assert "`kb/crypto/rsa.md#三、解题步骤`" in md
    assert "kb 中存在" in md
    assert "kb 中未找到" in md
    assert "## 其他资料（附件 / 外部链接）" in md
    assert "`work/attachments/x/upload_sample.png`" in md
    assert "`flag{writeup_demo}`" in md
    assert "先试共模" in md and "有效" in md


def test_writeup_compresses_attachment_report_with_anomalies(store: WorkspaceStore):
    wid = store.create("附件题", "forensics").get("id")
    _, entry = store.add_entry(
        wid, kind="reference", title="sample.png", source="analyze",
        path="work/attachments/x/upload_sample.png",
        report={
            "executed": False,
            "file": {"name": "sample.png", "size": 12, "sha256": "abc"},
            "type": {"kind": "PNG", "is_text": False},
            "anomalies": ["尾部追加数据", "CRC 不符", "多余 chunk", "第四条"],
        },
    )

    md = store.export_writeup(wid)

    assert ("sample.png — PNG 图（附件报告：PNG 图，4 异常）"
            f"（来源 #{entry['id']}）") in md
    assert "`work/attachments/x/upload_sample.png`" in md
    assert "异常：尾部追加数据；CRC 不符；多余 chunk" in md
    assert "第四条" not in md


def test_only_kb_path_can_carry_anchor(store: WorkspaceStore):
    wid = store.create("锚点").get("id")
    with pytest.raises(WorkspaceError):
        store.add_entry(wid, kind="reference", title="x", anchor="节")
    _, entry = store.add_entry(wid, kind="reference", title="x",
                               path="crypto/rsa.md", anchor="#三节")
    assert entry["anchor"] == "#三节"


def test_attachment_report_is_stored_and_rendered(store: WorkspaceStore):
    wid = store.create("附件题").get("id")
    report = {
        "schema_version": 1,
        "executed": False,
        "file": {"name": "sample.png", "size": 12,
                 "sha256": "abc123", "saved": "work/attachments/x/upload_sample.png"},
        "type": {"kind": "PNG", "is_text": False, "extension": ".png",
                 "extension_mismatch": True},
        "carve": [{"type": "ZIP", "offset": 42, "offset_hex": "0x2a"}],
        "structures": {"png": {"width": 1}},
        "anomalies": ["扩展名 .png 与真实内容「ZIP」不符"],
        "decoded": [{"method": "base64", "decoded": "flag{p3}"}],
        "warnings": ["该扩展名属于可执行/脚本类型；本工具只读取字节，不会运行它。"],
        "storage": {"isolated": True, "saved": "work/attachments/x/upload_sample.png"},
    }
    _, entry = store.add_entry(
        wid, kind="reference", title="sample.png", source="analyze",
        path=report["file"]["saved"], text="附件报告", report=report,
    )
    assert entry["report"]["type"]["kind"] == "PNG"

    md = store.export_markdown(wid)
    assert "附件报告" in md
    assert "`sample.png`" in md
    assert "扩展名不符" in md
    assert "解码（base64）：flag{p3}" in md
    assert "只读分析" in md
    assert "不会运行" in md


def test_report_size_limit(store: WorkspaceStore):
    wid = store.create("题目").get("id")
    with pytest.raises(WorkspaceError):
        store.add_entry(wid, kind="reference", title="x",
                        report={"blob": "x" * (300 * 1024)})


# ---------------------------------------------------------------- HTTP API
@pytest.fixture()
def api_env(tmp_path: Path, monkeypatch):
    monkeypatch.setenv("AGENT_WORKSPACE_DIR", str(tmp_path / "workspaces"))
    monkeypatch.setenv("AGENT_ATTACHMENT_DIR", str(tmp_path / "attachments"))
    srv = ThreadingHTTPServer(("127.0.0.1", 0), server.Handler)
    th = threading.Thread(target=srv.serve_forever, daemon=True)
    th.start()
    try:
        yield {"port": srv.server_address[1], "tmp": tmp_path}
    finally:
        srv.shutdown()
        srv.server_close()
        th.join(timeout=5)


def call(env, method: str, path: str, body=None):
    conn = http.client.HTTPConnection("127.0.0.1", env["port"], timeout=10)
    try:
        data = None
        headers = {}
        if body is not None:
            data = json.dumps(body, ensure_ascii=False).encode("utf-8")
            headers["Content-Type"] = "application/json"
        conn.request(method, path, body=data, headers=headers)
        r = conn.getresponse()
        return r.status, r.read().decode("utf-8", errors="replace"), \
            r.getheader("Content-Type") or ""
    finally:
        conn.close()


def call_bytes(env, path: str, data: bytes):
    conn = http.client.HTTPConnection("127.0.0.1", env["port"], timeout=10)
    try:
        conn.request("POST", path, body=data, headers={
            "Content-Type": "application/octet-stream",
            "Content-Length": str(len(data)),
        })
        r = conn.getresponse()
        return r.status, r.read().decode("utf-8", errors="replace")
    finally:
        conn.close()


def test_api_workspace_crud_and_export(api_env):
    status, text, _ = call(api_env, "POST", "/api/workspaces",
                           {"title": "接口题", "id": "api-case", "category": "misc"})
    assert status == 200
    ws = json.loads(text)["workspace"]
    assert ws["id"] == "api-case"

    status, text, _ = call(api_env, "GET", "/api/workspaces")
    assert status == 200
    assert [w["id"] for w in json.loads(text)["workspaces"]] == ["api-case"]

    status, text, _ = call(api_env, "GET", "/api/workspaces/api-case")
    assert status == 200
    assert json.loads(text)["workspace"]["title"] == "接口题"

    status, text, _ = call(api_env, "POST", "/api/workspaces/api-case",
                           {"title": "改名", "status": "solved"})
    assert status == 200
    assert json.loads(text)["workspace"]["title"] == "改名"

    status, text, _ = call(api_env, "POST", "/api/workspaces/api-case/entries",
                           {"kind": "fact", "text": "已知 flag 格式"})
    entry = json.loads(text)["entry"]
    assert entry["kind"] == "fact"

    status, text, _ = call(api_env, "POST",
                           f"/api/workspaces/api-case/entries/{entry['id']}",
                           {"text": "补充：flag 前缀 flag{"})
    assert status == 200
    assert json.loads(text)["entry"]["text"].startswith("补充")

    status, text, _ = call(api_env, "GET", "/api/workspaces/api-case/timeline")
    assert status == 200
    assert len(json.loads(text)["timeline"]) >= 3

    status, text, ctype = call(api_env, "GET",
                               "/api/workspaces/api-case/export?format=md")
    assert status == 200
    assert ctype.startswith("text/markdown")
    assert "# 改名" in text
    assert "已知 flag 格式" in text or "补充" in text

    status, _, _ = call(api_env, "DELETE",
                        f"/api/workspaces/api-case/entries/{entry['id']}")
    assert status == 200
    status, _, _ = call(api_env, "DELETE", "/api/workspaces/api-case")
    assert status == 200
    status, _, _ = call(api_env, "GET", "/api/workspaces/api-case")
    assert status == 404


def test_api_workspace_conflict_and_validation(api_env):
    status, _, _ = call(api_env, "POST", "/api/workspaces",
                        {"title": "一", "id": "dup"})
    assert status == 200
    status, text, _ = call(api_env, "POST", "/api/workspaces",
                           {"title": "二", "id": "dup"})
    assert status == 409
    assert "已存在" in json.loads(text)["error"]

    status, text, _ = call(api_env, "POST", "/api/workspaces", {"title": ""})
    assert status == 400

    status, text, _ = call(api_env, "GET", "/api/workspaces/../etc")
    assert status == 404

    status, text, _ = call(api_env, "POST", "/api/workspaces/dup/entries",
                           {"kind": "attempt", "text": "x", "result": "maybe"})
    assert status == 400
    assert "pending / success / failed" in json.loads(text)["error"]


def test_api_writeup_export_mode(api_env, monkeypatch):
    kb = api_env["tmp"] / "kb"
    (kb / "crypto").mkdir(parents=True)
    (kb / "crypto" / "rsa.md").write_text(
        "---\ntitle: RSA\n---\n正文\n", encoding="utf-8",
    )
    monkeypatch.setattr(
        server, "_KB",
        SimpleNamespace(cfg=SimpleNamespace(kb_dir=kb)),
    )

    call(api_env, "POST", "/api/workspaces", {"title": "Writeup", "id": "wu"})
    call(api_env, "POST", "/api/workspaces/wu/entries",
         {"kind": "fact", "text": "flag{http_writeup}"})
    call(api_env, "POST", "/api/workspaces/wu/entries",
         {"kind": "reference", "title": "RSA", "path": "crypto/rsa.md",
          "anchor": "识别"})

    status, text, ctype = call(
        api_env, "GET", "/api/workspaces/wu/export?format=md&mode=writeup")
    assert status == 200
    assert ctype.startswith("text/markdown")
    assert "Writeup 草稿" in text
    assert "flag{http_writeup}" in text
    assert "kb/crypto/rsa.md#识别" in text
    assert "kb 中存在" in text

    status, text, _ = call(
        api_env, "GET", "/api/workspaces/wu/export?format=md&mode=bogus")
    assert status == 400
    assert "normal 或 writeup" in json.loads(text)["error"]


def test_api_attempt_status_update(api_env):
    call(api_env, "POST", "/api/workspaces", {"title": "尝试", "id": "try"})
    _, text, _ = call(api_env, "POST", "/api/workspaces/try/entries",
                      {"kind": "attempt", "direction": "爆破",
                       "conclusion": "先手工试", "result": "pending"})
    entry = json.loads(text)["entry"]
    assert entry["direction"] == "爆破"
    assert entry["conclusion"] == "先手工试"

    status, text, _ = call(api_env, "POST",
                           f"/api/workspaces/try/entries/{entry['id']}",
                           {"result": "success"})
    assert status == 200
    assert json.loads(text)["entry"]["result"] == "success"

    status, text, _ = call(api_env, "POST",
                           f"/api/workspaces/try/entries/{entry['id']}",
                           {"result": "maybe"})
    assert status == 400


def test_api_analyze_can_attach_report_to_workspace(api_env):
    call(api_env, "POST", "/api/workspaces", {"title": "附件", "id": "attach"})
    data = b"hello flag{p3_report}"
    status, text = call_bytes(api_env, "/api/analyze?name=note.txt&workspace=attach",
                              data)
    body = json.loads(text)

    assert status == 200
    assert body["workspace"]["id"] == "attach"
    assert body["workspace"]["entry_id"]

    status, text, _ = call(api_env, "GET", "/api/workspaces/attach")
    ws = json.loads(text)["workspace"]
    ref = [e for e in ws["entries"] if e["kind"] == "reference"][0]
    assert ref["source"] == "analyze"
    assert ref["report"]["file"]["name"] == "note.txt"
    assert ref["report"]["executed"] is False

    status, text, _ = call(api_env, "GET",
                           "/api/workspaces/attach/export?format=md")
    assert status == 200
    assert "附件报告" in text
    assert "只读分析" in text


def test_api_analyze_rejects_unknown_workspace(api_env):
    status, text = call_bytes(api_env, "/api/analyze?name=x.txt&workspace=missing",
                              b"hello")
    assert status == 404
    assert "不存在" in json.loads(text)["error"]
