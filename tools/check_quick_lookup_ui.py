"""使用本机 Edge 检查关键词搜索、来源和代码复制；不启动生成模型。"""
from __future__ import annotations

import json
import threading
import time
from http.server import ThreadingHTTPServer
from pathlib import Path
from unittest.mock import patch

from playwright.sync_api import sync_playwright

from agent import server

ROOT = Path(__file__).resolve().parents[1]


def main() -> int:
    shots = ROOT / 'work/r1/shots'
    shots.mkdir(parents=True, exist_ok=True)
    httpd = ThreadingHTTPServer(('127.0.0.1', 0), server.Handler)
    thread = threading.Thread(target=httpd.serve_forever, daemon=True)
    thread.start()
    searches = []
    with patch('requests.post', side_effect=AssertionError('网页快查不应调用生成服务')):
        try:
            with sync_playwright() as playwright:
                browser = playwright.chromium.launch(channel='msedge', headless=True)
                context = browser.new_context(viewport={'width': 1365, 'height': 1000},
                                              permissions=['clipboard-read', 'clipboard-write'])
                page = context.new_page()
                page.on('request', lambda req: searches.append(req.post_data_json.get('retrieval'))
                        if req.url.endswith('/api/search') and req.post_data else None)
                page.goto(f'http://127.0.0.1:{httpd.server_port}', wait_until='networkidle')
                page.get_by_text('方法卡', exact=True).click()
                page.get_by_label('搜索内容', exact=True).fill('用户名欢迎语 7*7 回显 49')
                t0 = time.perf_counter()
                page.get_by_role('button', name='查找', exact=True).click()
                title = page.get_by_role('button', name='方法卡 · SSTI 识别与 Jinja2 沙箱逃逸（含无回显盲注通道）', exact=True)
                title.wait_for()
                first_screen_ms = round((time.perf_counter() - t0) * 1000, 1)
                page.screenshot(path=str(shots / 'keyword-results.png'), full_page=True)
                assert searches == ['fts'], searches
                title.click()
                dialog = page.get_by_role('dialog')
                dialog.get_by_role('button', name='查看代码 ssti_generic.py', exact=True).click()
                dialog.get_by_role('button', name='复制代码', exact=True).click()
                dialog.get_by_role('button', name='已复制', exact=True).wait_for()
                copied = page.evaluate('navigator.clipboard.readText()')
                expected = (ROOT / 'kb/_methods/scripts/ssti_generic.py').read_text(encoding='utf-8-sig')
                # Windows 剪贴板将换行转换为 CRLF，逐字符核对统一后的文本。
                assert copied.replace('\r\n', '\n') == expected
                page.screenshot(path=str(shots / 'code-reader.png'), full_page=True)
                dialog.get_by_role('button', name='返回原文档').click()
                dialog.get_by_role('button', name='ssti-template-injection.md', exact=True).click()
                dialog.get_by_text('模板引擎', exact=False).first.wait_for()
                context.close()
                browser.close()
            result = {'ok': True, 'retrieval_requests': searches, 'generation_calls': 0,
                      'first_screen_ms': first_screen_ms, 'copied_characters': len(copied),
                      'source_navigation': True, 'clipboard_crlf': '\r\n' in copied}
            (ROOT / 'work/r1/ui-result.json').write_text(json.dumps(result, ensure_ascii=False, indent=2), encoding='utf-8')
            print(json.dumps(result, ensure_ascii=False))
        finally:
            httpd.shutdown()
            httpd.server_close()
            thread.join()
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
