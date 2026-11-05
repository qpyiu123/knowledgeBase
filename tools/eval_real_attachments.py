"""用已整理的本地真题附件检查 HTTP 上传和搜索，不下载或执行附件。"""

import argparse
from contextlib import contextmanager
from hashlib import sha256
from http.server import ThreadingHTTPServer
import json
import os
from pathlib import Path
import tempfile
import threading
from urllib.parse import urlencode
from urllib.request import ProxyHandler, Request, build_opener

ROOT = Path(__file__).resolve().parents[1]


@contextmanager
def local_api(uploads):
    os.environ["AGENT_DISABLE_GENERATION"] = "1"
    os.environ["AGENT_ATTACHMENT_DIR"] = str(uploads)
    from agent.server import Handler

    with ThreadingHTTPServer(("127.0.0.1", 0), Handler) as httpd:
        worker = threading.Thread(target=httpd.serve_forever, daemon=True)
        worker.start()
        try:
            yield f"http://127.0.0.1:{httpd.server_port}"
        finally:
            httpd.shutdown()
            worker.join()


def evaluate(case, files, call):
    path = (files / case["file"]).resolve()
    if not path.is_relative_to(files):
        raise ValueError(f"{case['id']}: 附件路径越出测试集")
    data = path.read_bytes()
    if sha256(data).hexdigest() != case["sha256"]:
        raise ValueError(f"{case['id']}: 附件与清单不符")
    report = call(
        "/api/analyze?" + urlencode({"name": path.name}), data, "application/octet-stream"
    )
    if (
        not report["ok"]
        or report["executed"]
        or case["kind_contains"] not in report["type"]["kind"]
    ):
        raise ValueError(f"{case['id']}: 只读识别结果不符")
    searches, readable = [], set()
    for query in case["queries"]:
        for mode in ("fts", "hybrid"):
            request = {k: v for k, v in query.items() if k != "stage"}
            request.update(top_k=5, retrieval=mode, with_conditions=True)
            found = call("/api/search", json.dumps(request, ensure_ascii=False).encode())
            results = []
            for hit in found["hits"]:
                rel = hit["path"]
                if rel not in readable:
                    doc = call("/api/doc?" + urlencode({"path": rel}))
                    if not doc.get("body") or doc.get("error"):
                        raise ValueError(f"{case['id']}: 资料打不开：{rel}")
                    readable.add(rel)
                results.append({key: hit.get(key) for key in ("path", "title", "section")})
            searches.append(
                {"stage": query["stage"], "mode": mode, "ms": found["ms"], "hits": results}
            )
    return {
        "id": case["id"],
        "kind": report["type"]["kind"],
        "structures": report["structures"],
        "warnings": report["warnings"],
        "executed": report["executed"],
        "readable_docs": len(readable),
        "searches": searches,
    }


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--files", type=Path, default=ROOT / "work/r52/真题测试集")
    parser.add_argument("--cases", type=Path, default=ROOT / "eval/r52_real_cases.json")
    parser.add_argument("--out", type=Path, default=ROOT / "work/r52/results.json")
    args = parser.parse_args()
    cases = json.loads(args.cases.read_text(encoding="utf-8"))["cases"]
    files = args.files.resolve()
    args.out.parent.mkdir(parents=True, exist_ok=True)
    opener = build_opener(ProxyHandler({}))
    with tempfile.TemporaryDirectory(prefix="uploads-", dir=args.out.parent.resolve()) as uploads:
        with local_api(uploads) as base:

            def call(path, body=None, content_type="application/json"):
                request = Request(base + path, data=body, headers={"Content-Type": content_type})
                with opener.open(request, timeout=30) as response:
                    return json.load(response)

            health = call("/api/health")
            if not health["index_ok"] or health["generation_enabled"]:
                raise RuntimeError("验收需要索引就绪、模型解释关闭")
            results = [evaluate(case, files, call) for case in cases]
    args.out.write_text(json.dumps(results, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(f"{len(results)} 道题，{sum(len(r['searches']) for r in results)} 次本机查询：{args.out}")


if __name__ == "__main__":
    main()
