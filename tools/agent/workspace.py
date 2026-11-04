"""题目工作区：本地 JSON 持久化，不引入数据库框架。

每个工作区是一个独立的 JSON 文件，存放在可配置目录（默认
`work/workspaces/`）。记录四类内容：

  - 事实（fact）
  - 尝试（attempt，带 pending/success/failed）
  - 资料收藏（reference，可指向 kb 文档、URL 或已落盘附件）
  - 时间线（timeline，由创建/更新/增删条目自动生成）

安全与边界：
  - 工作区 ID 只允许 `[A-Za-z0-9_-]`，文件名由 ID 直接拼出，拒绝路径穿越；
  - 文本、标题、引用路径都有长度上限；
  - 只写本地文件，不执行任何内容；
  - 写入使用同目录临时文件 + os.replace，避免半截 JSON。
"""
from __future__ import annotations

import json
import os
import re
import tempfile
import threading
import time
import uuid
from datetime import datetime, timezone
from pathlib import Path

SCHEMA_VERSION = 1
ID_RE = re.compile(r"^[A-Za-z0-9_-]{1,64}$")
ENTRY_KINDS = ("fact", "attempt", "reference")
ATTEMPT_RESULTS = ("pending", "success", "failed")
FAILURE_LABELS = {'unknown': '原因待确认', 'runtime': '运行出错', 'condition': '前提已排除'}
FOCUS_LABELS = {'goal': '当前目标', 'hypotheses': '待验证假设', 'pending_checks': '待查项'}
STATUSES = ("open", "solved", "archived")

MAX_TITLE = 120
MAX_TEXT = 4000
MAX_DIRECTION = 500
MAX_CONCLUSION = 2000
MAX_REF_TITLE = 200
MAX_PATH = 500
MAX_ANCHOR = 200
MAX_URL = 1000
MAX_SOURCE = 120
MAX_CATEGORY = 40
MAX_ENTRIES = 500
MAX_TIMELINE = 1000
MAX_ATTACHMENT_VALUE = 1000
MAX_REPORT_BYTES = 256 * 1024

_LOCK = threading.RLock()


class WorkspaceError(ValueError):
    """输入或存储不合法。"""


class WorkspaceNotFound(WorkspaceError):
    """工作区不存在。"""


class WorkspaceExists(WorkspaceError):
    """用户指定的工作区 ID 已被占用。"""


def _now() -> str:
    return datetime.now(timezone.utc).isoformat(timespec="seconds")


def _clean_str(raw, field: str, limit: int, *, required: bool = False) -> str:
    if raw is None:
        raw = ""
    if not isinstance(raw, str):
        raise WorkspaceError(f"{field} 必须是字符串")
    s = raw.strip()
    if len(s) > limit:
        raise WorkspaceError(f"{field} 太长（最多 {limit} 字符）")
    if required and not s:
        raise WorkspaceError(f"{field} 不能为空")
    return s


def check_id(raw) -> str:
    if not isinstance(raw, str) or not ID_RE.fullmatch(raw):
        raise WorkspaceError("工作区 ID 不合法")
    return raw


def _clean_status(raw) -> str:
    if raw in (None, ""):
        return "open"
    if not isinstance(raw, str) or raw not in STATUSES:
        raise WorkspaceError("状态只能是 open / solved / archived")
    return raw


def _clean_category(raw):
    if raw in (None, ""):
        return None
    return _clean_str(raw, "category", MAX_CATEGORY) or None


def _counts(entries: list[dict]) -> dict[str, int]:
    out = {k: 0 for k in ENTRY_KINDS}
    for e in entries:
        k = e.get("kind")
        if k in out:
            out[k] += 1
    return out


def _summary(ws: dict) -> dict:
    entries = ws.get("entries") or []
    return {
        "id": ws.get("id"),
        "title": ws.get("title"),
        "category": ws.get("category"),
        "status": ws.get("status"),
        "created": ws.get("created"),
        "updated": ws.get("updated"),
        "entries": len(entries),
        "counts": _counts(entries),
    }


def _event(ws: dict, kind: str, summary: str) -> None:
    ts = _now()
    timeline = ws.setdefault("timeline", [])
    timeline.append({"ts": ts, "kind": kind, "summary": summary})
    if len(timeline) > MAX_TIMELINE:
        del timeline[: len(timeline) - MAX_TIMELINE]
    ws["updated"] = ts


def _clean_attachment(raw):
    if raw is None:
        return None
    if not isinstance(raw, dict):
        raise WorkspaceError("attachment 必须是对象")
    allowed = ("name", "saved", "sha256", "size", "kind")
    out = {}
    for key in allowed:
        val = raw.get(key)
        if val in (None, ""):
            continue
        if isinstance(val, bool) or not isinstance(val, (str, int)):
            raise WorkspaceError(f"attachment.{key} 必须是字符串或整数")
        text = str(val)
        if len(text) > MAX_ATTACHMENT_VALUE:
            raise WorkspaceError(f"attachment.{key} 太长")
        out[key] = val
    return out or None


def _check_entry(
    kind,
    text,
    result,
    title,
    path,
    url,
    source,
    attachment,
    report=None,
    direction="",
    conclusion="",
    anchor="",
    failure_kind="unknown",
) -> dict:
    if not isinstance(kind, str) or kind not in ENTRY_KINDS:
        raise WorkspaceError("kind 只能是 fact / attempt / reference")
    text = _clean_str(text, "text", MAX_TEXT)
    title = _clean_str(title, "title", MAX_REF_TITLE)
    path = _clean_str(path, "path", MAX_PATH)
    anchor = _clean_str(anchor, "anchor", MAX_ANCHOR)
    url = _clean_str(url, "url", MAX_URL)
    source = _clean_str(source, "source", MAX_SOURCE)
    if anchor and not path:
        raise WorkspaceError("anchor 只用于 kb 路径收藏")
    if url and not re.match(r"^https?://", url):
        raise WorkspaceError("url 只允许 http:// 或 https://")
    if kind == "attempt":
        result = _clean_attempt_result(result)
        failure_kind = _clean_failure_kind(failure_kind) if result == 'failed' else 'unknown'
        direction = _clean_str(direction, "direction", MAX_DIRECTION)
        conclusion = _clean_str(conclusion, "conclusion", MAX_CONCLUSION)
    else:
        result = None
        direction = ""
        conclusion = ""
    if not any((text, title, path, url, direction, conclusion)):
        raise WorkspaceError("内容不能为空")
    return {
        "kind": kind,
        "text": text,
        "result": result,
        "title": title,
        "path": path,
        "anchor": anchor,
        "url": url,
        "source": source,
        "direction": direction,
        "conclusion": conclusion,
        "failure_kind": failure_kind if kind == 'attempt' else None,
        "attachment": _clean_attachment(attachment),
        "report": _clean_report(report) if kind == "reference" else None,
    }


def _clean_failure_kind(raw) -> str:
    if not isinstance(raw, str) or raw not in FAILURE_LABELS:
        raise WorkspaceError('失败原因只能是 unknown / runtime / condition')
    return raw


def _focus_lines(ws: dict) -> list[str]:
    lines = []
    for key, label in FOCUS_LABELS.items():
        if ws.get(key):
            lines.extend([f'## {label}', '', str(ws[key]), ''])
    return lines


def _clean_attempt_result(raw) -> str:
    if raw in (None, ""):
        return "pending"
    if not isinstance(raw, str) or raw not in ATTEMPT_RESULTS:
        raise WorkspaceError("尝试结果只能是 pending / success / failed")
    return raw


def _clean_report(raw):
    """附件分析报告按 JSON 原样保存，但有体积上限，避免工作区被撑爆。"""
    if raw is None:
        return None
    if not isinstance(raw, dict):
        raise WorkspaceError("report 必须是 JSON 对象")
    try:
        encoded = json.dumps(raw, ensure_ascii=False)
    except (TypeError, ValueError) as e:
        raise WorkspaceError(f"report 必须是可序列化的 JSON: {e}") from e
    if len(encoded.encode("utf-8")) > MAX_REPORT_BYTES:
        raise WorkspaceError(f"report 太大（最多 {MAX_REPORT_BYTES} 字节）")
    return raw


def _entry_label(entry: dict) -> str:
    if entry["kind"] == "fact":
        return "事实"
    if entry["kind"] == "attempt":
        return f"尝试（{entry.get('result') or 'pending'}）"
    return "资料收藏"


def _report_lines(report: dict) -> list[str]:
    """把附件报告拼成 Markdown 附属条目，只做摘要，不堆整段 strings。"""
    lines: list[str] = []
    f = report.get("file") or {}
    t = report.get("type") or {}
    lines.append(f"  - 附件报告：`{f.get('name') or '附件'}`")
    lines.append(f"    - 类型：{t.get('kind') or '未知'}"
                 f"（文本：{'是' if t.get('is_text') else '否'}）")
    if t.get("extension_mismatch"):
        lines.append(f"    - 扩展名不符：`.{t.get('extension') or '?'}`")
    if f.get("size") is not None:
        lines.append(f"    - 大小：{f.get('size')} 字节")
    if f.get("sha256"):
        lines.append(f"    - SHA256：`{f.get('sha256')}`")
    saved = (report.get("storage") or {}).get("saved") or f.get("saved")
    if saved:
        lines.append(f"    - 落盘：`{saved}`")
    carve = report.get("carve") or []
    if carve:
        items = ", ".join(
            f"{c.get('type')}@{c.get('offset_hex') or c.get('offset')}"
            for c in carve[:10]
        )
        lines.append(f"    - 雕刻：{items}")
    structures = report.get("structures") or {}
    if structures:
        lines.append(f"    - 结构：{', '.join(sorted(structures))}")
    anomalies = report.get("anomalies") or []
    for msg in anomalies[:10]:
        lines.append(f"    - 异常：{msg}")
    decoded = report.get("decoded") or []
    for item in decoded[:10]:
        lines.append(f"    - 解码（{item.get('method')}）：{item.get('decoded')}")
    warnings = report.get("warnings") or []
    for msg in warnings[:10]:
        lines.append(f"    - 警告：{msg}")
    lines.append(f"    - 执行：{'是' if report.get('executed') else '否'}"
                 "（只读分析）")
    return lines


class WorkspaceStore:
    """一个目录下的工作区集合。无框架、无缓存，便于测试切换目录。"""

    def __init__(self, root: str | Path):
        self.root = Path(root)

    def _path(self, workspace_id: str) -> Path:
        wid = check_id(workspace_id)
        return self.root / f"{wid}.json"

    def _save(self, ws: dict) -> None:
        wid = check_id(ws["id"])
        self.root.mkdir(parents=True, exist_ok=True)
        fd, tmp = tempfile.mkstemp(prefix=f".{wid}-", suffix=".tmp",
                                   dir=str(self.root))
        try:
            with os.fdopen(fd, "w", encoding="utf-8") as fh:
                json.dump(ws, fh, ensure_ascii=False, indent=2)
                fh.flush()
                os.fsync(fh.fileno())
            target = self._path(wid)
            # Windows 上杀软/索引服务偶尔短暂占用目标文件，重试几次。
            for attempt in range(6):
                try:
                    os.replace(tmp, target)
                    break
                except PermissionError:
                    if attempt == 5:
                        raise
                    time.sleep(0.05)
        except Exception:
            try:
                os.unlink(tmp)
            except OSError:
                pass
            raise

    def create(self, title, category=None, workspace_id=None) -> dict:
        title = _clean_str(title, "title", MAX_TITLE, required=True)
        category = _clean_category(category)
        if workspace_id in (None, ""):
            wid = uuid.uuid4().hex
        else:
            wid = check_id(workspace_id)
        ts = _now()
        ws = {
            "schema_version": SCHEMA_VERSION,
            "id": wid,
            "title": title,
            "category": category,
            "status": "open",
            "created": ts,
            "updated": ts,
            "entries": [],
            "timeline": [],
            **{key: '' for key in FOCUS_LABELS},
        }
        _event(ws, "create", f"创建工作区「{title}」")
        with _LOCK:
            if self._path(wid).exists():
                raise WorkspaceExists("该工作区 ID 已存在")
            self._save(ws)
        return ws

    def load(self, workspace_id: str) -> dict:
        p = self._path(workspace_id)
        if not p.is_file():
            raise WorkspaceNotFound("工作区不存在")
        try:
            ws = json.loads(p.read_text(encoding="utf-8"))
        except (OSError, json.JSONDecodeError) as e:
            raise WorkspaceError(f"工作区文件损坏: {e}") from e
        if not isinstance(ws, dict) or ws.get("id") != workspace_id:
            raise WorkspaceError("工作区文件损坏")
        ws.setdefault("entries", [])
        ws.setdefault("timeline", [])
        for key in FOCUS_LABELS:
            ws.setdefault(key, '')
        return ws

    def list(self) -> list[dict]:
        if not self.root.is_dir():
            return []
        out: list[dict] = []
        with _LOCK:
            for p in self.root.glob("*.json"):
                if not ID_RE.fullmatch(p.stem):
                    continue
                try:
                    ws = self.load(p.stem)
                except WorkspaceError:
                    continue
                out.append(_summary(ws))
        out.sort(key=lambda s: str(s.get("updated") or ""), reverse=True)
        return out

    def update(self, workspace_id: str, title=None, status=None, category=None,
               goal=None, hypotheses=None, pending_checks=None) -> dict:
        with _LOCK:
            ws = self.load(workspace_id)
            changes = []
            for key, value in (('goal', goal), ('hypotheses', hypotheses), ('pending_checks', pending_checks)):
                if value is not None:
                    cleaned = _clean_str(value, FOCUS_LABELS[key], MAX_TEXT)
                    if cleaned != ws.get(key):
                        ws[key] = cleaned
                        changes.append('更新' + FOCUS_LABELS[key])
            if title is not None:
                new_title = _clean_str(title, "title", MAX_TITLE, required=True)
                if new_title != ws.get("title"):
                    changes.append(f"标题改为「{new_title}」")
                    ws["title"] = new_title
            if status is not None:
                new_status = _clean_status(status)
                if new_status != ws.get("status"):
                    changes.append(f"状态改为 {new_status}")
                    ws["status"] = new_status
            if category is not None:
                new_cat = _clean_category(category)
                if new_cat != ws.get("category"):
                    changes.append(f"方向改为 {new_cat or '未分类'}")
                    ws["category"] = new_cat
            if changes:
                _event(ws, "update", "；".join(changes))
                self._save(ws)
            return ws

    def add_entry(
        self,
        workspace_id: str,
        kind: str,
        text="",
        result=None,
        title="",
        path="",
        url="",
        source="",
        attachment=None,
        report=None,
        direction="",
        conclusion="",
        anchor="",
        failure_kind="unknown",
    ) -> tuple[dict, dict]:
        cleaned = _check_entry(kind, text, result, title, path, url,
                               source, attachment, report, direction,
                               conclusion, anchor, failure_kind)
        with _LOCK:
            ws = self.load(workspace_id)
            entries = ws.setdefault("entries", [])
            if len(entries) >= MAX_ENTRIES:
                raise WorkspaceError(f"条目太多（最多 {MAX_ENTRIES} 条）")
            entry = {
                "id": uuid.uuid4().hex[:12],
                "created": _now(),
                **cleaned,
            }
            entries.append(entry)
            summary = (cleaned["text"] or cleaned["title"] or cleaned["path"]
                       or cleaned["url"] or cleaned["direction"]
                       or cleaned["conclusion"])
            _event(ws, "entry", f"{_entry_label(cleaned)}：{summary[:80]}")
            self._save(ws)
            return ws, entry

    def update_entry(
        self,
        workspace_id: str,
        entry_id: str,
        result=None,
        text=None,
        failure_kind=None,
    ) -> tuple[dict, dict]:
        """更新尝试状态（也允许补充事实/资料备注）。时间线只读，不在此改写。"""
        entry_id = _clean_str(entry_id, "entry_id", 64, required=True)
        with _LOCK:
            ws = self.load(workspace_id)
            entry = next(
                (e for e in ws.get("entries", []) if e.get("id") == entry_id),
                None,
            )
            if entry is None:
                raise WorkspaceNotFound("条目不存在")
            changes = []
            if failure_kind is not None:
                if entry.get('kind') != 'attempt' or (result or entry.get('result')) != 'failed':
                    raise WorkspaceError('失败原因只用于无效尝试')
                new_failure_kind = _clean_failure_kind(failure_kind)
                if new_failure_kind != entry.get('failure_kind', 'unknown'):
                    entry['failure_kind'] = new_failure_kind
                    changes.append('失败原因改为' + FAILURE_LABELS[new_failure_kind])
            if result is not None:
                if entry.get("kind") != "attempt":
                    raise WorkspaceError("只有尝试条目可以修改状态")
                new_result = _clean_attempt_result(result)
                if new_result != entry.get("result"):
                    entry["result"] = new_result
                    changes.append(f"状态改为 {new_result}")
                    if new_result != 'failed':
                        entry['failure_kind'] = 'unknown'
            if text is not None:
                new_text = _clean_str(text, "text", MAX_TEXT)
                if new_text != entry.get("text"):
                    entry["text"] = new_text
                    changes.append("更新内容")
            if changes:
                _event(ws, "entry_update", "；".join(changes))
                self._save(ws)
            return ws, entry

    def delete_entry(self, workspace_id: str, entry_id: str) -> dict:
        entry_id = _clean_str(entry_id, "entry_id", 64)
        with _LOCK:
            ws = self.load(workspace_id)
            entries = ws.setdefault("entries", [])
            keep = [e for e in entries if e.get("id") != entry_id]
            if len(keep) == len(entries):
                raise WorkspaceNotFound("条目不存在")
            ws["entries"] = keep
            _event(ws, "entry_delete", f"删除条目 {entry_id}")
            self._save(ws)
            return ws

    def delete(self, workspace_id: str) -> None:
        p = self._path(workspace_id)
        with _LOCK:
            if not p.is_file():
                raise WorkspaceNotFound("工作区不存在")
            try:
                p.unlink()
            except OSError as e:
                raise WorkspaceError(f"工作区删除失败: {e}") from e

    def timeline(self, workspace_id: str) -> list[dict]:
        """时间线只读：由创建/更新/条目事件自动追加，不提供写入接口。"""
        return list(self.load(workspace_id).get("timeline") or [])

    def export_markdown(self, workspace_id: str) -> str:
        ws = self.load(workspace_id)
        lines = [f"# {ws.get('title') or '未命名工作区'}", ""]
        if ws.get("category"):
            lines.append(f"- 方向：{ws['category']}")
        lines.append(f"- 状态：{ws.get('status') or 'open'}")
        lines.append(f"- 创建：{ws.get('created') or ''}")
        lines.append(f"- 更新：{ws.get('updated') or ''}")
        lines.append("")

        lines.extend(_focus_lines(ws))
        groups = (("fact", "事实"), ("attempt", "尝试"), ("reference", "资料收藏"))
        for kind, label in groups:
            items = [e for e in ws.get("entries", []) if e.get("kind") == kind]
            lines.append(f"## {label}")
            if not items:
                lines.append("")
                lines.append("_暂无_")
                lines.append("")
                continue
            for e in items:
                stamp = str(e.get("created") or "")
                if kind == "attempt":
                    res = e.get("result") or "pending"
                    body = e.get("text") or ""
                    head = f"- [{stamp}] `{res}`"
                    direction = e.get("direction") or ""
                    conclusion = e.get("conclusion") or ""
                    if direction:
                        head += f" 方向：{direction}"
                    if conclusion:
                        head += f"；结论：{conclusion}"
                    if res == 'failed':
                        head += '；失败原因：' + FAILURE_LABELS.get(e.get('failure_kind'), '原因待确认')
                    if body:
                        head += f"；备注：{body}"
                    lines.append(head.rstrip())
                elif kind == "reference":
                    title = e.get("title") or e.get("path") or e.get("url") or "资料"
                    target = e.get("path") or e.get("url") or ""
                    note = e.get("text") or ""
                    head = f"- [{stamp}] {title}"
                    if target:
                        head += f" — `{target}`"
                    if note:
                        head += f"：{note}"
                    lines.append(head.rstrip())
                    report = e.get("report")
                    if isinstance(report, dict) and report:
                        lines.extend(_report_lines(report))
                else:
                    lines.append(f"- [{stamp}] {e.get('text') or ''}".rstrip())
            lines.append("")

        lines.append("## 时间线")
        for ev in ws.get("timeline", []):
            lines.append(f"- [{ev.get('ts')}] {ev.get('summary')}")
        lines.append("")
        return "\n".join(lines)

    def export_writeup(self, workspace_id: str,
                       kb_root: str | Path | None = None) -> str:
        """由真实工作区记录生成 Writeup 草稿。

        每条事实/尝试/资料都带来源条目 ID；kb 引用带可点击路径锚点，
        能校验时标注是否存在。不编造条目之外的内容。
        """
        ws = self.load(workspace_id)
        root = Path(kb_root) if kb_root else None
        entries = ws.get("entries") or []
        facts = [e for e in entries if e.get("kind") == "fact"]
        attempts = [e for e in entries if e.get("kind") == "attempt"]
        refs = [e for e in entries if e.get("kind") == "reference"]
        attempts.sort(key=lambda e: str(e.get("created") or ""))

        lines = [f"# Writeup 草稿：{ws.get('title') or '未命名工作区'}", ""]
        lines.append("> 由题目工作区导出；每条信息后的 `来源 #entry-id` 可回溯到"
                     "工作区 JSON。请按需删改后再发布。")
        lines.append("")
        lines.append(f"- 题目名：{ws.get('title') or '未命名'}")
        lines.append(f"- 方向：{ws.get('category') or '未分类'}")
        lines.append(f"- 状态：{ws.get('status') or 'open'}")
        lines.append(f"- 工作区：`{ws.get('id')}`")
        lines.append(f"- 记录时间：{ws.get('created') or ''} → {ws.get('updated') or ''}")
        lines.append("")
        lines.extend(_focus_lines(ws))

        lines.append("## 事实")
        if not facts:
            lines.append("")
            lines.append("_未记录_")
            lines.append("")
        else:
            for e in facts:
                text = _one_line(e.get("text"))
                lines.append(
                    f"- {text or '（空）'}（来源 #{e.get('id')}）"
                    f"<!-- entry:{e.get('id')} -->"
                )
            lines.append("")

        lines.append("## 尝试（按时间序）")
        if not attempts:
            lines.append("")
            lines.append("_未记录_")
            lines.append("")
        else:
            for i, e in enumerate(attempts, 1):
                direction = _one_line(e.get("direction")) or "未记录"
                result = e.get("result") or "pending"
                result_label = {"pending": "待验证", "success": "有效",
                                "failed": "无效"}.get(result, result)
                conclusion = _one_line(e.get("conclusion")) or "未记录"
                note = _one_line(e.get("text"))
                line = (f"{i}. [{e.get('created') or ''}] {direction} → "
                        f"{result_label}（`{result}`）→ {conclusion}"
                        f"（来源 #{e.get('id')}）<!-- entry:{e.get('id')} -->")
                lines.append(line)
                if result == 'failed':
                    lines.append('   - 失败原因：' + FAILURE_LABELS.get(e.get('failure_kind'), '原因待确认'))
                if note:
                    lines.append(f"   - 备注：{note}")
            lines.append("")

        lines.append("## 用到的 kb 资料")
        kb_refs = [e for e in refs if _is_kb_ref(e)]
        if not kb_refs:
            lines.append("")
            lines.append("_未记录_")
            lines.append("")
        else:
            for e in kb_refs:
                rel = str(e.get("path") or "").replace("\\", "/")
                title = e.get("title") or rel
                link = _kb_link(rel, e.get("anchor"))
                exists = _kb_exists(root, rel)
                mark = ("kb 中存在" if exists is True else
                        "kb 中未找到" if exists is False else "未校验")
                lines.append(
                    f"- 《{title}》 — [`{link}`]({link}) （来源 #{e.get('id')}；"
                    f"{mark}）<!-- entry:{e.get('id')} -->"
                )
                if e.get("anchor"):
                    lines.append(f"  - 章节锚点：`{link}`")
                note = _one_line(e.get("text"))
                if note:
                    lines.append(f"  - 备注：{note}")
                report = e.get("report")
                if isinstance(report, dict) and report:
                    lines.extend(_report_lines(report))
            lines.append("")

        lines.append("## 其他资料（附件 / 外部链接）")
        others = [e for e in refs if not _is_kb_ref(e)]
        if not others:
            lines.append("")
            lines.append("_未记录_")
            lines.append("")
        else:
            for e in others:
                report = e.get("report")
                if isinstance(report, dict) and report:
                    lines.extend(_writeup_report_block(e, report))
                    continue
                title = e.get("title") or e.get("url") or e.get("path") or "资料"
                target = e.get("url") or ""
                line = f"- 《{title}》"
                if target:
                    line += f" — <{target}>"
                elif e.get("path"):
                    line += f" — `{str(e['path']).replace(chr(92), '/')}`"
                line += f"（来源 #{e.get('id')}）<!-- entry:{e.get('id')} -->"
                lines.append(line)
                note = _one_line(e.get("text"))
                if note:
                    lines.append(f"  - 备注：{note}")
            lines.append("")

        flags = _collect_flags(entries)
        lines.append("## Flag")
        if not flags:
            lines.append("")
            lines.append("_未记录_")
            lines.append("")
        else:
            for value, entry_ids in flags:
                src = "、".join(f"#{i}" for i in entry_ids)
                lines.append(f"- `{value}`（来源 {src}）")
            lines.append("")

        lines.append("## 时间线")
        for ev in ws.get("timeline", []):
            lines.append(f"- [{ev.get('ts')}] {ev.get('summary')}")
        lines.append("")
        return "\n".join(lines)


_IMAGE_KINDS = {"PNG", "JPEG", "JPG", "GIF", "BMP", "WEBP", "TIFF"}


def _writeup_report_block(entry: dict, report: dict) -> list[str]:
    """Writeup 里把附件类型与异常数压成一行；异常 >0 时列出前 3 条。"""
    f = report.get("file") or {}
    t = report.get("type") or {}
    name = _one_line(entry.get("title") or f.get("name")) or "附件"
    kind = _one_line(t.get("kind")) or "未知类型"
    kind_label = kind + " 图" if kind.upper() in _IMAGE_KINDS else kind
    anomalies = report.get("anomalies") or []
    line = (f"- {name} — {kind_label}"
            f"（附件报告：{kind_label}，{len(anomalies)} 异常）"
            f"（来源 #{entry.get('id')}）")
    saved = entry.get("path") or f.get("saved") \
        or (report.get("storage") or {}).get("saved")
    if saved:
        line += f" — `{str(saved).replace(chr(92), '/')}`"
    line += f"<!-- entry:{entry.get('id')} -->"
    out = [line]
    if anomalies:
        out.append("  - 异常：" + "；".join(
            _one_line(a) for a in anomalies[:3]))
    note = _one_line(entry.get("text"))
    if note:
        out.append(f"  - 备注：{note}")
    return out


def _is_kb_ref(entry: dict) -> bool:
    """只有真正指向 kb 文档的收藏才进“用到 kb 资料”一节。"""
    return bool(entry.get("path")) and not entry.get("report") \
        and entry.get("source") != "analyze"


def _one_line(value) -> str:
    return re.sub(r"\s+", " ", str(value or "")).strip()


def _kb_link(rel: str, anchor=None) -> str:
    rel = rel.strip().replace("\\", "/")
    target = rel if rel.startswith("kb/") else f"kb/{rel}"
    if anchor:
        target += "#" + str(anchor).strip().lstrip("#")
    return target


def _kb_exists(root: Path | None, rel: str) -> bool | None:
    if root is None:
        return None
    rel = rel.strip().replace("\\", "/")
    if rel.startswith("kb/"):
        rel = rel[3:]
    try:
        p = (Path(root) / rel).resolve()
        p.relative_to(Path(root).resolve())
    except (OSError, ValueError):
        return False
    return p.is_file()


_FLAG_RE = re.compile(r"flag\{[^}\s]{1,300}\}", re.IGNORECASE)


def _collect_flags(entries: list[dict]) -> list[tuple[str, list[str]]]:
    seen: dict[str, list[str]] = {}
    for e in entries:
        for field in ("text", "title", "direction", "conclusion"):
            for m in _FLAG_RE.finditer(str(e.get(field) or "")):
                value = m.group(0)
                ids = seen.setdefault(value, [])
                if e.get("id") and e["id"] not in ids:
                    ids.append(e["id"])
    return list(seen.items())
