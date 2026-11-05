"""在 Edge 检查卡点资料、配套代码及首段前后取消，使用模型替身。"""
from __future__ import annotations

import json
import os
import re
import sys
import tempfile
import threading
import time
from http.server import ThreadingHTTPServer
from pathlib import Path
from unittest.mock import patch

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'tools'))

from playwright.sync_api import sync_playwright
from agent import server
from mock_llama_server import MockLlama


def main():
    out = ROOT / 'work/r33'
    out.mkdir(parents=True, exist_ok=True)
    with MockLlama() as model, tempfile.TemporaryDirectory(prefix='ui-', dir=out) as temp, \
            patch.dict(os.environ, {'AGENT_WORKSPACE_DIR': temp, 'KB_MODEL_PORT': str(model.port), 'KB_CHAT_MODEL': 'qwen35-9b'}):
        server.GENERATION_DISABLED = False
        store = server._workspace_store()
        store.create('卡点验收', workspace_id='focus-ui')
        store.update('focus-ui', goal='恢复 RSA 明文', pending_checks='同一个 n，不同指数的两组密文，检查 gcd')
        for text in ('n1=11413 n2=11413', 'e1=3 e2=17', '同一明文'):
            store.add_entry('focus-ui', 'fact', text=text)
        httpd = ThreadingHTTPServer(('127.0.0.1', 0), server.Handler)
        thread = threading.Thread(target=httpd.serve_forever, daemon=True)
        thread.start()
        try:
            with sync_playwright() as playwright:
                browser = playwright.chromium.launch(channel='msedge', headless=True)
                context = browser.new_context(viewport={'width': 1365, 'height': 1000})
                context.add_init_script("localStorage.setItem('last_workspace_id', JSON.stringify({id:'focus-ui',title:'卡点验收'}))")
                page = context.new_page()
                errors = []
                page.on('pageerror', lambda error: errors.append(str(error)))
                page.goto(f'http://127.0.0.1:{httpd.server_port}', wait_until='networkidle')
                box = page.get_by_label('搜索内容', exact=True)
                box.fill('下一步先查哪里')
                t0 = time.perf_counter()
                with page.expect_response('**/api/search'):
                    page.get_by_role('button', name='查找', exact=True).click()
                page.locator('article.hit').first.wait_for()
                plain_ms = round((time.perf_counter() - t0) * 1000, 1)
                plain = page.locator('article.hit .hit-path').all_text_contents()
                page.get_by_role('checkbox', name='参考当前卡点', exact=True).check()
                t0 = time.perf_counter()
                with page.expect_response('**/api/search'):
                    page.get_by_role('button', name='查找', exact=True).click()
                focus = page.locator('#focus-reading')
                focus.wait_for()
                focus_ms = round((time.perf_counter() - t0) * 1000, 1)
                assert plain == page.locator('article.hit .hit-path').all_text_contents()
                page.get_by_role('button', name=re.compile('^卡点资料')).click()
                focus.get_by_text('条件与下一步 · 已知', exact=True).first.click()
                focus.get_by_text('RSA 共模：指数互素路径', exact=True).first.wait_for()
                page.screenshot(path=str(out / 'focus-reading.png'), full_page=True)
                focus.get_by_role('button', name=re.compile('查看代码.*rsa_common_modulus.py')).first.click()
                page.get_by_role('dialog').get_by_role('button', name='复制代码', exact=True).wait_for()
                page.keyboard.press('Escape')
                page.locator('input[aria-label="使用方式"]').click()
                page.get_by_role('option', name='问模型', exact=True).click()
                cancelled = []
                for variant in ('首段前', '首段后'):
                    model.started.clear()
                    model.disconnected.clear()
                    box.fill('RSA【取消验收：' + variant + '】')
                    page.get_by_role('button', name='提问', exact=True).click()
                    assert model.started.wait(8)
                    if variant == '首段后':
                        page.get_by_text('第一段', exact=True).wait_for()
                    t0 = time.perf_counter()
                    page.get_by_role('button', name='取消解释', exact=True).click()
                    page.get_by_text('已取消', exact=True).wait_for()
                    assert model.disconnected.wait(2)
                    cancelled.append({'phase': variant, 'ms': round((time.perf_counter() - t0) * 1000, 1)})
                    page.screenshot(path=str(out / ('cancel-' + ('before' if variant == '首段前' else 'after') + '.png')))
                box.fill('RSA 共模先核对什么')
                page.get_by_role('button', name='提问', exact=True).click()
                page.get_by_text('1 段', exact=True).wait_for()
                assert not errors, errors
                browser.close()
            report = {'ok': True, 'plain_screen_ms': plain_ms, 'focus_screen_ms': focus_ms,
                      'primary_order_unchanged': True, 'paired_code_opened': True,
                      'cancel': cancelled, 'next_ask_after_cancel': True,
                      'mock_generation_requests': len(model.posts), 'real_model_calls': 0,
                      'personal_workspaces_accessed': False}
            (out / 'ui-result.json').write_text(json.dumps(report, ensure_ascii=False, indent=2), encoding='utf-8')
            print(json.dumps(report, ensure_ascii=False))
        finally:
            httpd.shutdown()
            httpd.server_close()
            thread.join()
    return 0


if __name__ == '__main__':
    sys.stdout.reconfigure(encoding='utf-8')
    raise SystemExit(main())
