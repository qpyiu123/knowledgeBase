"""在现有页面检查条件证据、区别和原文小节；模型请求会使测试失败。"""
from __future__ import annotations

import json
import sys
import threading
import time
from http.server import ThreadingHTTPServer
from pathlib import Path
from unittest.mock import patch

from playwright.sync_api import sync_playwright

from agent import server

ROOT = Path(__file__).resolve().parents[1]


def main():
    out = ROOT / 'work/r2'
    shots = out / 'shots'
    shots.mkdir(parents=True, exist_ok=True)
    server.GENERATION_DISABLED = True
    httpd = ThreadingHTTPServer(('127.0.0.1', 0), server.Handler)
    thread = threading.Thread(target=httpd.serve_forever, daemon=True)
    thread.start()
    records, requests = [], []
    query = 'RSA 同一个 n，同一明文，两个指数互素'
    with patch('requests.post', side_effect=AssertionError('条件关联不应调用生成服务')) as model:
        try:
            with sync_playwright() as playwright:
                browser = playwright.chromium.launch(channel='msedge', headless=True)
                page = browser.new_page(viewport={'width': 1365, 'height': 1000})
                page.on('request', lambda req: requests.append(req.post_data_json)
                        if req.url.endswith('/api/search') and req.post_data else None)
                page.goto(f'http://127.0.0.1:{httpd.server_port}', wait_until='networkidle')
                box = page.get_by_label('搜索内容', exact=True)
                box.fill(query)
                t0 = time.perf_counter()
                page.get_by_role('button', name='查找', exact=True).click()
                page.locator('article.hit').first.wait_for()
                first_screen = round((time.perf_counter() - t0) * 1000, 1)
                assert page.locator('details').count() == 0
                a_paths = page.locator('article.hit .hit-path').all_text_contents()
                page.get_by_role('checkbox', name='显示条件关联', exact=True).check()
                with page.expect_response('**/api/search'):
                    page.get_by_role('button', name='查找', exact=True).click()
                common = page.locator('article.hit').filter(has=page.get_by_role('button', name='弱 RSA 共模攻击', exact=True))
                # 标题随原资料维护，按库内路径定位对应结果。
                if common.count() == 0:
                    common = page.locator('article.hit').filter(has=page.locator('.hit-path').filter(has_text='crypto/rsa-common-modulus-attack.md'))
                detail = common.locator('details')
                detail.locator('summary').click()
                detail.get_by_text('已知：gcd(e1,e2)=1', exact=True).wait_for()
                assert page.locator('article.hit .hit-path').all_text_contents() == a_paths
                page.screenshot(path=str(shots / 'known.png'), full_page=True)
                t0 = time.perf_counter()
                detail.get_by_role('button', name='查看依据：二、原理', exact=True).click()
                heading = page.get_by_role('dialog').locator('[id="二-原理"]')
                heading.wait_for()
                page.wait_for_timeout(250)
                assert 50 < heading.bounding_box()['y'] < 950
                source_ms = round((time.perf_counter() - t0) * 1000, 1)
                page.screenshot(path=str(shots / 'source-section.png'))
                page.keyboard.press('Escape')
                for name, text, state in (
                    ('unknown', 'RSA 同一个 n，两组密文', '未知'),
                    ('excluded', 'RSA 不同 n，同一明文，两个指数互素', '不满足'),
                ):
                    box.fill(text)
                    with page.expect_response('**/api/search'):
                        page.get_by_role('button', name='查找', exact=True).click()
                    common.locator('summary').wait_for()
                    # React 保留同一路径节点的展开状态。
                    if not detail.get_attribute('open') == '':
                        detail.locator('summary').click()
                    assert state in detail.locator('summary').inner_text()
                    assert detail.get_by_text('相近方法怎么区分', exact=True).is_visible()
                    if state == '不满足':
                        assert detail.get_by_text('下一步检查：', exact=False).count() == 0
                    page.screenshot(path=str(shots / f'{name}.png'), full_page=True)
                    records.append({'case': name, 'status': state})
                assert requests[0]['with_conditions'] is False
                assert requests[1]['with_conditions'] is True
                assert requests[0]['q'] == requests[1]['q'] == query
                assert not page.get_by_role('dialog').count()
                browser.close()
            report = {'ok': True, 'cases': records, 'same_result_order': True, 'original_query_preserved': True,
                      'source_section_visible': True, 'generation_calls': model.call_count,
                      'first_screen_ms': first_screen, 'source_open_ms': source_ms,
                      'clicks_to_source': 4, 'screenshots': str(shots.relative_to(ROOT))}
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
