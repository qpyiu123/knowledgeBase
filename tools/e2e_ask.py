#!/usr/bin/env python
"""真实模型 /api/ask 最小端到端冒烟（P10）。

只依赖标准库；不写入仓库，只在本地工作区目录建一个临时题目工作区。
默认连 http://127.0.0.1:8765，可用 --base-url 指向别的端口。

退出码：
    0  PASS 或 SKIP
    1  FAIL（有检查失败）
    0  SKIP（Web/Ollama/模型不可用时，原因写到 stdout）

说明：既有 SSE 契约固定为 tok / err / done（AGENTS.md 第 5 节），
服务端没有 start 事件。脚本对 brief 里的「首个非 tok 事件为 start」
记为 SKIP 并说明契约原因，终态 done 仍按硬要求断言。
"""
from __future__ import annotations

import argparse
import json
import sys
import time
import uuid
from dataclasses import dataclass, field
from urllib.error import HTTPError, URLError
from urllib.request import Request, urlopen

FACTS = [
    "题目给了同一个 n，两组 e 和 c：e1=65537, e2=65539，c1、c2 各一段。",
    "flag 格式是 flag{...}，明文长度明显小于 n。",
]
FAILED_ATTEMPT = {
    "text": "先直接试 RSA 共模攻击，想用扩展欧几里得恢复明文。",
    "direction": "crypto",
    "conclusion": "gcd(e1,e2) 不是 1，直接共模公式不成立，未解出明文。",
    "result": "failed",
}
ASK_PATHS = ["crypto/rsa-common-modulus-attack.md"]
ASK_QUESTION = (
    "这道题还能不能用共模攻击？请结合工作区里已经记录的已知条件和"
    "失败尝试回答，不要重复已经证明无效的思路。"
)


@dataclass
class Check:
    name: str
    status: str  # PASS / FAIL / SKIP
    detail: str = ""


@dataclass
class Run:
    checks: list[Check] = field(default_factory=list)
    answers: list[tuple[str, str]] = field(default_factory=list)

    def add(self, name: str, ok: bool | None, detail: str = "") -> None:
        status = "SKIP" if ok is None else ("PASS" if ok else "FAIL")
        self.checks.append(Check(name, status, detail))

    @property
    def failed(self) -> bool:
        return any(c.status == "FAIL" for c in self.checks)


def _request(method: str, url: str, payload=None, timeout: float = 15.0):
    data = None
    headers = {"Accept": "application/json"}
    if payload is not None:
        data = json.dumps(payload, ensure_ascii=False).encode("utf-8")
        headers["Content-Type"] = "application/json; charset=utf-8"
    req = Request(url, data=data, method=method, headers=headers)
    try:
        with urlopen(req, timeout=timeout) as resp:
            body = resp.read()
            ctype = resp.headers.get("Content-Type", "")
            return resp.status, ctype, body
    except HTTPError as e:
        return e.code, e.headers.get("Content-Type", ""), e.read()


def _json(method: str, url: str, payload=None, timeout: float = 15.0):
    status, _ctype, body = _request(method, url, payload, timeout)
    try:
        return status, json.loads(body.decode("utf-8", "replace"))
    except (json.JSONDecodeError, UnicodeDecodeError):
        return status, {"_raw": body.decode("utf-8", "replace")[:500]}


def _sse(url: str, payload: dict, timeout: float) -> tuple[int, str, list[dict], str]:
    data = json.dumps(payload, ensure_ascii=False).encode("utf-8")
    req = Request(url, data=data, method="POST", headers={
        "Content-Type": "application/json; charset=utf-8",
        "Accept": "text/event-stream",
    })
    events: list[dict] = []
    raw_parts: list[str] = []
    with urlopen(req, timeout=timeout) as resp:
        status = resp.status
        ctype = resp.headers.get("Content-Type", "")
        for line in resp:
            text = line.decode("utf-8", "replace").rstrip("\r\n")
            raw_parts.append(text)
            if not text.startswith("data:"):
                continue
            chunk = text[5:].strip()
            if not chunk:
                continue
            try:
                events.append(json.loads(chunk))
            except json.JSONDecodeError:
                events.append({"_bad": chunk})
    return status, ctype, events, "\n".join(raw_parts)


def _answer_text(events: list[dict]) -> str:
    return "".join(str(e.get("v", "")) for e in events if e.get("t") == "tok")


def _summary(text: str, limit: int = 200) -> str:
    one = " ".join(text.split())
    return one[:limit] + ("…" if len(one) > limit else "")


def _ensure_workspace(base: str, args, run: Run) -> str | None:
    title = args.title or f"P10 e2e 临时工作区 {time.strftime('%m-%d %H:%M')}"
    wid = args.workspace_id or f"p10-e2e-{uuid.uuid4().hex[:8]}"
    status, body = _json("POST", f"{base}/api/workspaces",
                         {"id": wid, "title": title, "category": "crypto"},
                         timeout=args.timeout)
    if status == 409 and args.workspace_id:
        status2, body2 = _json("GET", f"{base}/api/workspaces/{wid}")
        run.add("workspace_reuse", status2 == 200,
                f"复用已有工作区 {wid}" if status2 == 200 else str(body2)[:200])
        return wid if status2 == 200 else None
    run.add("workspace_create", status == 200 and body.get("ok") is True,
            f"id={wid} title={title!r} http={status}")
    if status != 200:
        return None

    for i, text in enumerate(FACTS, 1):
        st, b = _json("POST", f"{base}/api/workspaces/{wid}/entries",
                      {"kind": "fact", "text": text}, timeout=args.timeout)
        run.add(f"workspace_fact_{i}", st == 200 and b.get("ok") is True,
                f"http={st} text={text[:40]!r}")

    st, b = _json("POST", f"{base}/api/workspaces/{wid}/entries",
                  {"kind": "attempt", **FAILED_ATTEMPT}, timeout=args.timeout)
    run.add("workspace_failed_attempt",
            st == 200 and b.get("ok") is True
            and (b.get("entry") or {}).get("result") == "failed",
            f"http={st} entry={(b.get('entry') or {}).get('id')}")
    return wid


def _run_ask(base: str, payload: dict, args, label: str, run: Run) -> str:
    started = time.time()
    try:
        status, ctype, events, raw = _sse(f"{base}/api/ask", payload,
                                          timeout=args.timeout)
    except URLError as e:
        run.add(f"{label}_http", False, f"请求失败: {e}")
        return ""
    elapsed = time.time() - started

    run.add(f"{label}_http", status == 200 and "text/event-stream" in ctype,
            f"http={status} content-type={ctype} events={len(events)} "
            f"elapsed={elapsed:.1f}s")
    run.add(f"{label}_events", bool(events), f"{len(events)} 个事件")
    if not events:
        return ""

    first_non_tok = next((e for e in events if e.get("t") != "tok"), None)
    run.add(f"{label}_terminal_done",
            bool(first_non_tok) and first_non_tok.get("t") == "done",
            f"首个非 tok 事件={first_non_tok}")

    # 既有契约没有 start 事件：如实标 SKIP，不伪造也不改服务端契约。
    run.add(f"{label}_first_non_tok_start", None,
            "SSE 契约固定为 tok/err/done（AGENTS.md §5），无 start 事件；"
            "按契约改为断言首个非 tok 事件为 done")

    toks = [e for e in events if e.get("t") == "tok"]
    text = _answer_text(events)
    run.add(f"{label}_has_tokens", bool(toks), f"{len(toks)} 个 tok 事件")
    run.add(f"{label}_non_empty", bool(text.strip()),
            f"正文 {len(text)} 字符")
    run.add(f"{label}_no_err", not any(e.get("t") == "err" for e in events),
            "未出现 err" if not any(e.get("t") == "err" for e in events)
            else f"err={[e.get('v') for e in events if e.get('t') == 'err']}")
    run.answers.append((label, text))
    return text


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description="真实模型 /api/ask 端到端冒烟")
    ap.add_argument("--base-url", default="http://127.0.0.1:8765")
    ap.add_argument("--workspace-id", default="",
                    help="复用指定工作区；不填则新建一个临时工作区")
    ap.add_argument("--title", default="")
    ap.add_argument("--timeout", type=float, default=300.0,
                    help="单次 ask 超时秒数（默认 300）")
    ap.add_argument("--keep-workspace", action="store_true",
                    help="结束后不删除临时工作区")
    ap.add_argument("--out", default="",
                    help="可选：把结果 JSON 写到指定路径")
    args = ap.parse_args(argv)
    base = args.base_url.rstrip("/")
    run = Run()

    print(f"[e2e] base_url={base}")
    try:
        status, health = _json("GET", f"{base}/api/health", timeout=8)
    except (URLError, OSError) as e:
        print(f"STATUS: SKIP")
        print(f"  原因: Web 服务不可达 {base}: {e}")
        return 0

    print(f"[e2e] health http={status} model_ok={health.get('model_ok')} "
          f"index_ok={health.get('index_ok')} model={health.get('model')}")
    if status != 200:
        print("STATUS: SKIP")
        print(f"  原因: /api/health 返回 {status}: {str(health)[:300]}")
        return 0
    if not health.get("index_ok"):
        run.add("index_ok", False, f"索引不可用: {health.get('index')}")
    if not health.get("model_ok"):
        print("STATUS: SKIP")
        print(f"  原因: 模型不可达/Ollama 未就绪: {health.get('error') or health.get('models')}")
        return 0

    run.add("index_ok", True, f"docs={health.get('docs')}")

    wid = _ensure_workspace(base, args, run)
    if wid is None:
        return _finish(run, args, None)

    payload = {"q": ASK_QUESTION, "paths": ASK_PATHS, "workspace_id": wid}
    _run_ask(base, payload, args, "with_workspace", run)

    payload_no_ctx = {"q": ASK_QUESTION, "paths": ASK_PATHS}
    _run_ask(base, payload_no_ctx, args, "no_workspace", run)

    return _finish(run, args, wid)


def _finish(run: Run, args, wid: str | None) -> int:
    if wid and not args.keep_workspace:
        st, body = _json("DELETE", f"{args.base_url.rstrip('/')}/api/workspaces/{wid}",
                         timeout=15)
        run.add("workspace_cleanup", st == 200,
                f"删除临时工作区 {wid} http={st}")

    print()
    print("检查清单：")
    for c in run.checks:
        print(f"  [{c.status:<4}] {c.name}: {c.detail}")

    for label, text in run.answers:
        print()
        print(f"[{label}] 回答摘要（前 200 字）：")
        print("  " + (_summary(text) or "<空>"))

    status = "FAIL" if run.failed else "PASS"
    print()
    print(f"STATUS: {status}")
    if run.failed:
        print("  失败项: " + ", ".join(c.name for c in run.checks
                                       if c.status == "FAIL"))

    if args.out:
        payload = {
            "status": status,
            "base_url": args.base_url,
            "workspace_id": wid,
            "checks": [c.__dict__ for c in run.checks],
            "answers": [{"label": k, "summary": _summary(v), "chars": len(v)}
                        for k, v in run.answers],
        }
        with open(args.out, "w", encoding="utf-8") as fh:
            json.dump(payload, fh, ensure_ascii=False, indent=2)
        print(f"  结果已写入 {args.out}")

    return 1 if run.failed else 0


if __name__ == "__main__":
    sys.exit(main())
