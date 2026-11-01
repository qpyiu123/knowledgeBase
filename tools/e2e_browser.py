#!/usr/bin/env python
"""真实浏览器验收（Playwright，默认优先 Windows 自带 Edge）。

覆盖路径：
  1. 首页加载 → 搜索 → 结果卡片 → 看全文抽屉
  2. 收藏到题目工作区（WorkspacePicker 新建标题分支）
  3. 附件上传 → 存入工作区 → 报告落库
  4. 问模型（附件 + 工作区上下文；--skip-model 或 Ollama 不可用时标 SKIP）
  5. 工作区页 → Writeup 导出（format=md）→ 断言附件摘要行与来源 #id
  6. 关键状态截图写入 work/shots/

只读本机服务，不启动/停止 Ollama 或 Web，不下载浏览器内核。
默认用 channel=msedge；失败时回退到本机已存在的 Playwright chromium，
不会执行 `playwright install`。
"""

from __future__ import annotations

import argparse
import json
import os
import re
import sys
import time
import urllib.request
import zipfile
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
DEFAULT_Q = "RSA 已知部分素数 分解 n"
ATTACH_NAME = "p11_e2e_attachment.png"
ASK_TEXT = (
    "结合附件 p11_e2e_attachment.png 的结构分析和这道题已记录的事实，"
    "说明 ZIP 伪装成 PNG 时应该先检查什么。"
)


class StepFailure(RuntimeError):
    pass


class Runner:
    def __init__(self) -> None:
        self.results: list[dict] = []

    def pass_(self, name: str, note: str = "") -> None:
        self.results.append({"step": name, "status": "PASS", "note": note})
        print(f"  [PASS] {name}" + (f" — {note}" if note else ""))

    def skip(self, name: str, reason: str) -> None:
        self.results.append({"step": name, "status": "SKIP", "note": reason})
        print(f"  [SKIP] {name} — {reason}")

    def fail(self, name: str, reason: str) -> None:
        self.results.append({"step": name, "status": "FAIL", "note": reason})
        print(f"  [FAIL] {name} — {reason}")

    @property
    def ok(self) -> bool:
        return all(r["status"] != "FAIL" for r in self.results)


def _now() -> str:
    return datetime.now(timezone.utc).astimezone().isoformat(timespec="seconds")


def fetch_health(base: str, timeout: float = 5.0) -> dict | None:
    try:
        with urllib.request.urlopen(base + "/api/health", timeout=timeout) as r:
            return json.loads(r.read().decode("utf-8"))
    except Exception:
        return None


def make_attachment(tmp_dir: Path) -> Path:
    """造一个“扩展名是 .png 实际是 ZIP”的附件，触发真实结构解析与异常。"""
    tmp_dir.mkdir(parents=True, exist_ok=True)
    path = tmp_dir / ATTACH_NAME
    with zipfile.ZipFile(path, "w", zipfile.ZIP_DEFLATED) as z:
        z.writestr("note.txt", "flag{p11_e2e_attachment}\n")
        z.writestr("readme.md", "P11 真实浏览器验收附件；只读分析，不执行。\n")
    return path


def launch_browser(p, args, log) -> tuple[object, str]:
    """优先 msedge；其次本机已安装的 chromium（绝不下载）。"""
    attempts: list[str] = []
    headless = not args.headed
    if args.channel:
        try:
            b = p.chromium.launch(channel=args.channel, headless=headless)
            log(f"浏览器: channel={args.channel}")
            return b, f"channel={args.channel}"
        except Exception as e:  # noqa: BLE001
            attempts.append(f"channel={args.channel}: {e}")

    if args.executable:
        exe = Path(args.executable)
        if exe.exists():
            try:
                b = p.chromium.launch(executable_path=str(exe), headless=headless)
                log(f"浏览器: executable={exe}")
                return b, f"executable={exe}"
            except Exception as e:  # noqa: BLE001
                attempts.append(f"executable={exe}: {e}")
        else:
            attempts.append(f"executable 不存在: {exe}")

    try:
        bundled = Path(p.chromium.executable_path)
    except Exception as e:  # noqa: BLE001
        bundled = None
        attempts.append(f"读取 chromium.executable_path 失败: {e}")
    if bundled and bundled.exists():
        try:
            b = p.chromium.launch(executable_path=str(bundled), headless=headless)
            log(f"浏览器: 本机 chromium={bundled}")
            return b, f"executable={bundled}"
        except Exception as e:  # noqa: BLE001
            attempts.append(f"chromium={bundled}: {e}")

    raise StepFailure(
        "没有可用的浏览器（不会自动下载 chromium）。尝试过：\n  "
        + "\n  ".join(attempts)
        + "\n请确认 Edge 已安装，或指定 --executable <chrome.exe>。"
    )


def wait_idle_button(page, timeout_ms: int) -> None:
    """等待“停止接收”按钮消失（后端生成结束）。"""
    page.wait_for_function(
        """() => {
            const buttons = Array.from(document.querySelectorAll('button'));
            return !buttons.some((b) => (b.textContent || '').includes('停止接收'));
        }""",
        timeout=timeout_ms,
    )


def main() -> int:
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8")
    if hasattr(sys.stderr, "reconfigure"):
        sys.stderr.reconfigure(encoding="utf-8")

    ap = argparse.ArgumentParser(description="P11 真实浏览器验收")
    ap.add_argument("--base-url", default="http://127.0.0.1:8765")
    ap.add_argument("--channel", default="msedge", help="Playwright channel，默认 msedge")
    ap.add_argument("--executable", default="", help="自定义浏览器可执行文件")
    ap.add_argument("--headed", action="store_true", help="显示浏览器窗口")
    ap.add_argument("--skip-model", action="store_true", help="跳过问模型步骤并标 SKIP")
    ap.add_argument("--keep-workspace", action="store_true", help="保留本次创建的工作区")
    ap.add_argument("--timeout", type=int, default=20000, help="普通操作超时（毫秒）")
    ap.add_argument("--ask-timeout", type=int, default=360000, help="模型回答超时（毫秒）")
    ap.add_argument(
        "--shots-dir", default=str(ROOT / "work" / "shots"), help="截图目录"
    )
    ap.add_argument(
        "--tmp-dir", default=str(ROOT / "work" / "e2e_tmp"), help="临时文件目录"
    )
    ap.add_argument(
        "--out",
        default=str(ROOT / "work" / "e2e_browser_result.json"),
        help="结果 JSON 路径",
    )
    args = ap.parse_args()

    base = args.base_url.rstrip("/")
    shots_dir = Path(args.shots_dir)
    shots_dir.mkdir(parents=True, exist_ok=True)
    tmp_dir = Path(args.tmp_dir)
    tmp_dir.mkdir(parents=True, exist_ok=True)
    out_path = Path(args.out)
    out_path.parent.mkdir(parents=True, exist_ok=True)

    runner = Runner()
    started = _now()
    health = fetch_health(base)
    browser_note = ""
    workspace_id = ""
    workspace_title = f"P11 E2E 浏览器验收 {datetime.now().strftime('%H%M%S')}"
    shots: list[str] = []

    def log(msg: str) -> None:
        print(f"  {msg}")

    def shot(page, name: str) -> str:
        p = shots_dir / f"{name}.png"
        page.screenshot(path=str(p), full_page=True)
        rel = str(p.relative_to(ROOT)).replace("\\", "/")
        shots.append(rel)
        log(f"截图 {rel}")
        return rel

    def expect(cond, msg: str) -> None:
        if not cond:
            raise StepFailure(msg)

    print("=" * 66)
    print("P11 真实浏览器验收")
    print(f"  服务: {base}")
    print(f"  截图: {shots_dir}")
    print(f"  时间: {started}")
    if health is None:
        print(f"  [FAIL] {base}/api/health 不可达；请先启动 .\\start.ps1")
        runner.fail("服务可达", f"{base}/api/health 不可达")
        _write_result(out_path, runner, started, base, browser_note, workspace_id, shots)
        return 1
    log(
        f"health: ok={health.get('ok')} model_ok={health.get('model_ok')} "
        f"index_ok={health.get('index_ok')} build={health.get('build')}"
    )
    print("=" * 66)

    try:
        from playwright.sync_api import sync_playwright
    except Exception as e:  # noqa: BLE001
        runner.fail("Playwright 可用", f"import playwright 失败: {e}")
        _write_result(out_path, runner, started, base, browser_note, workspace_id, shots)
        return 1

    with sync_playwright() as p:
        try:
            browser, browser_note = launch_browser(p, args, log)
        except Exception as e:  # noqa: BLE001
            runner.fail("启动浏览器", str(e))
            _write_result(out_path, runner, started, base, browser_note, workspace_id, shots)
            return 1

        context = browser.new_context(
            viewport={"width": 1440, "height": 1000}, accept_downloads=True
        )
        page = context.new_page()
        page.set_default_timeout(args.timeout)

        def wait_enabled(locator, timeout_ms: int | None = None) -> None:
            limit = (timeout_ms or args.timeout) / 1000
            deadline = time.time() + limit
            while time.time() < deadline:
                if locator.is_enabled():
                    return
                page.wait_for_timeout(100)
            raise StepFailure("控件在超时内仍不可用")

        try:
            # ---------------------------------------------------- 1. 首页/搜索/抽屉
            name = "首页加载、搜索、结果卡片、看全文抽屉"
            try:
                page.goto(base + "/", wait_until="domcontentloaded")
                page.get_by_role("heading", name="从线索找到下一步").wait_for()
                page.get_by_text("CTF 知识库", exact=True).first.wait_for()
                shot(page, "01_home")

                box = page.locator("textarea[aria-label='搜索内容']")
                expect(box.count() == 1, "找不到搜索输入框")
                box.fill(DEFAULT_Q)
                page.get_by_role("button", name="查找", exact=True).click()
                page.locator("article.hit").first.wait_for()
                hits = page.locator("article.hit")
                expect(hits.count() > 0, "搜索结果为空")
                first_title = page.locator("article.hit .hit-title").first.inner_text().strip()
                expect(bool(first_title), "首条结果没有标题")
                expect(
                    page.locator("article.hit .hit-path").count() > 0,
                    "结果卡片没有来源路径",
                )
                shot(page, "02_search_results")

                page.locator("article.hit").first.get_by_role(
                    "button", name="阅读资料"
                ).click()
                page.locator(".reader-doc").wait_for()
                page.wait_for_function(
                    """() => {
                        const el = document.querySelector('.reader-doc');
                        return el && (el.innerText || '').trim().length > 40;
                    }"""
                )
                shot(page, "03_reader_drawer")
                page.keyboard.press("Escape")
                page.locator(".reader-doc").wait_for(state="detached")
                runner.pass_(name, f"首条：{first_title[:40]}")
            except Exception as e:  # noqa: BLE001
                shot(page, "fail_01_search")
                runner.fail(name, str(e))
                raise

            # ---------------------------------------------------- 2. 收藏到工作区
            name = "收藏到题目工作区（WorkspacePicker 新建标题分支）"
            try:
                page.locator("article.hit").first.get_by_role(
                    "button", name=re.compile("收藏到题目工作区")
                ).click()
                dialog = page.get_by_role("dialog")
                dialog.wait_for()
                title_input = dialog.locator("input[aria-label='新工作区标题']")
                title_input.fill(workspace_title)
                shot(page, "04_workspace_picker")
                dialog.get_by_role("button", name="存入", exact=True).click()
                dialog.wait_for(state="hidden")
                page.get_by_role("button", name="已收藏", exact=True).first.wait_for()
                page.get_by_text(
                    f"默认工作区：{workspace_title}", exact=False
                ).first.wait_for()
                # 记录实际工作区 id，供后续注入上下文与清理。
                page.wait_for_function(
                    """() => !!localStorage.getItem('last_workspace_id')"""
                )
                workspace_id = page.evaluate(
                    "() => localStorage.getItem('last_workspace_id') || ''"
                )
                expect(bool(workspace_id), "前端没有保存默认工作区 id")
                # 前端存的是 {id,title} JSON；取出 id 供后端请求与清理。
                try:
                    parsed = json.loads(workspace_id)
                    if isinstance(parsed, dict) and parsed.get("id"):
                        workspace_id = str(parsed["id"])
                except (ValueError, TypeError):
                    pass
                log(f"工作区: {workspace_id} / {workspace_title}")
                runner.pass_(name, f"新建 {workspace_id}")
            except Exception as e:  # noqa: BLE001
                shot(page, "fail_02_workspace")
                runner.fail(name, str(e))
                raise

            # 给工作区注入一条事实，确保问模型时确实带上下文。
            try:
                r = context.request.post(
                    f"{base}/api/workspaces/{workspace_id}/entries",
                    data=json.dumps(
                        {
                            "kind": "fact",
                            "text": "P11 验收：附件是扩展名 .png、内容为 ZIP 的文件。",
                        },
                        ensure_ascii=False,
                    ).encode("utf-8"),
                    headers={"Content-Type": "application/json"},
                )
                expect(r.ok, f"写入工作区事实失败 HTTP {r.status}")
            except Exception as e:  # noqa: BLE001
                log(f"警告：写入工作区事实失败: {e}")

            # ---------------------------------------------------- 3. 附件 → 工作区
            name = "附件「存入工作区」→ 报告落库"
            try:
                attach_path = make_attachment(tmp_dir)
                page.locator("input[aria-label='选择附件']").set_input_files(
                    str(attach_path)
                )
                page.get_by_text(f"分析结果：{ATTACH_NAME}", exact=False).wait_for(
                    timeout=max(args.timeout, 60000)
                )
                panel = page.locator(".attachment-card")
                expect(
                    panel.get_by_text("ZIP", exact=False).count() > 0,
                    "附件报告没有识别出 ZIP 类型",
                )
                expect(
                    panel.get_by_text("异常", exact=False).count() > 0,
                    "附件报告没有异常/异常区",
                )
                shot(page, "05_attachment_report")

                panel.get_by_role("button", name="存入工作区", exact=True).click()
                dialog = page.get_by_role("dialog")
                dialog.wait_for()
                select = dialog.locator("input[aria-label='选择已有工作区']")
                select.wait_for()
                wait_enabled(select)
                # 已通过 defaultId 自动选中；再次点同一项会把可清空 Select 清掉。
                if not select.input_value().strip():
                    select.click()
                    option = page.get_by_role(
                        "option", name=re.compile(re.escape(workspace_title))
                    )
                    option.wait_for()
                    option.click()
                submit = dialog.get_by_role("button", name="存入", exact=True)
                wait_enabled(submit)
                submit.click()
                dialog.wait_for(state="hidden")
                panel.get_by_text("已存入工作区", exact=True).wait_for()
                runner.pass_(name, f"{ATTACH_NAME} → {workspace_id}")
            except Exception as e:  # noqa: BLE001
                shot(page, "fail_03_attachment")
                runner.fail(name, str(e))
                raise

            # ---------------------------------------------------- 4. 问模型
            name = "问模型（附件 + 工作区上下文）"
            skip_reason = ""
            if args.skip_model:
                skip_reason = "--skip-model：按执行注意跳过真实模型问答"
            elif health.get("model_ok") is not True:
                skip_reason = (
                    "Ollama/模型不可用（health.model_ok != true），"
                    "真实模型问答不执行"
                )
            if skip_reason:
                runner.skip(name, skip_reason)
            else:
                try:
                    mode_input = page.locator("input[aria-label='使用方式']")
                    mode_input.click()
                    page.get_by_role("option", name="问模型", exact=True).click()
                    page.locator("textarea[aria-label='搜索内容']").fill(ASK_TEXT)
                    page.get_by_role("button", name="提问", exact=True).click()
                    page.locator(".answer-card").wait_for()
                    wait_idle_button(page, args.ask_timeout)
                    body = page.locator(".answer-body").inner_text().strip()
                    errors = page.locator(".mantine-Alert")
                    err_text = ""
                    if errors.count() > 0:
                        err_text = " ".join(
                            errors.nth(i).inner_text().strip()
                            for i in range(errors.count())
                        )
                    expect(
                        not err_text,
                        f"页面出现错误提示：{err_text[:200]}",
                    )
                    expect(len(body) > 20, f"模型回答过短：{body[:80]!r}")
                    shot(page, "06_ask_answer")
                    runner.pass_(
                        name,
                        f"回答 {len(body)} 字符，含工作区 {workspace_id}",
                    )
                except Exception as e:  # noqa: BLE001
                    shot(page, "fail_04_ask")
                    runner.fail(name, str(e))
                    raise

            # ---------------------------------------------------- 5. 工作区导出
            name = "工作区页 → Writeup 导出（format=md）"
            try:
                page.locator(".mantine-AppShell-navbar").get_by_role(
                    "button", name=re.compile("工作区")
                ).first.click()
                page.get_by_text("Writeup 草稿", exact=True).wait_for()
                page.get_by_role("heading", name=workspace_title).first.wait_for()
                page.get_by_text("Writeup 草稿", exact=True).click()
                shot(page, "07_workspace_page")

                export_file = tmp_dir / "p11_writeup_export.md"
                with page.expect_download(timeout=max(args.timeout, 30000)) as dl:
                    page.get_by_role(
                        "link", name="导出 Writeup", exact=True
                    ).click()
                dl.value.save_as(str(export_file))
                text = export_file.read_text(encoding="utf-8")

                expect(
                    ATTACH_NAME in text,
                    f"Writeup 导出里没有附件名 {ATTACH_NAME}",
                )
                expect(
                    "（附件报告：" in text,
                    "Writeup 导出里没有附件摘要行（附件报告：…）",
                )
                expect("异常" in text, "Writeup 导出里没有附件异常信息")
                expect("来源 #" in text, "Writeup 导出里没有来源 #id 标记")
                expect(
                    bool(re.search(r"来源 #\w+", text)),
                    "来源标记后面没有条目 id",
                )
                lines = [ln for ln in text.splitlines() if ATTACH_NAME in ln]
                runner.pass_(
                    name,
                    f"下载 {export_file.name}，附件摘要行：{(lines[0][:80] if lines else '')}",
                )
            except Exception as e:  # noqa: BLE001
                shot(page, "fail_05_export")
                runner.fail(name, str(e))
                raise

        finally:
            # 清理本次创建的工作区，避免污染用户数据。
            if workspace_id and not args.keep_workspace:
                try:
                    r = context.request.delete(
                        f"{base}/api/workspaces/{workspace_id}"
                    )
                    if r.ok:
                        log(f"已清理工作区 {workspace_id}")
                    else:
                        log(f"清理工作区失败 HTTP {r.status}")
                except Exception as e:  # noqa: BLE001
                    log(f"清理工作区失败: {e}")
            try:
                page.evaluate(
                    "() => localStorage.removeItem('last_workspace_id')"
                )
            except Exception:  # noqa: BLE001
                pass
            context.close()
            browser.close()

    _write_result(out_path, runner, started, base, browser_note, workspace_id, shots)

    print("=" * 66)
    passed = sum(1 for r in runner.results if r["status"] == "PASS")
    skipped = sum(1 for r in runner.results if r["status"] == "SKIP")
    failed = sum(1 for r in runner.results if r["status"] == "FAIL")
    print(
        f"结果: {passed} PASS / {skipped} SKIP / {failed} FAIL"
        f" · 截图 {len(shots)} 张 · {out_path.relative_to(ROOT)}"
    )
    print(f"STATUS: {'PASS' if runner.ok else 'FAIL'}")
    if skipped:
        for r in runner.results:
            if r["status"] == "SKIP":
                print(f"  SKIP {r['step']}: {r['note']}")
    return 0 if runner.ok else 1


def _write_result(
    path: Path,
    runner: Runner,
    started: str,
    base: str,
    browser_note: str,
    workspace_id: str,
    shots: list[str],
) -> None:
    data = {
        "started": started,
        "finished": _now(),
        "base_url": base,
        "browser": browser_note,
        "workspace_id": workspace_id,
        "shots": shots,
        "steps": runner.results,
        "status": "PASS" if runner.ok else "FAIL",
        "counts": {
            "pass": sum(1 for r in runner.results if r["status"] == "PASS"),
            "skip": sum(1 for r in runner.results if r["status"] == "SKIP"),
            "fail": sum(1 for r in runner.results if r["status"] == "FAIL"),
        },
    }
    path.write_text(
        json.dumps(data, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
    )


if __name__ == "__main__":
    try:
        sys.exit(main())
    except StepFailure as e:
        print(f"STATUS: FAIL — {e}")
        sys.exit(1)
