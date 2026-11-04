"""实际浏览器保存当前卡点、分类失败原因并重新读取，不接触个人工作区。"""
from __future__ import annotations

import json
import os
import sys
import tempfile
import threading
from http.server import ThreadingHTTPServer
from pathlib import Path
from unittest.mock import patch

from playwright.sync_api import sync_playwright

from agent import server

ROOT = Path(__file__).resolve().parents[1]


def main():
    out = ROOT / 'work/r31'
    out.mkdir(parents=True, exist_ok=True)
    server.GENERATION_DISABLED = True
    with tempfile.TemporaryDirectory(prefix='ui-', dir=out) as temp, \
            patch.dict(os.environ, {'AGENT_WORKSPACE_DIR': temp}), \
            patch('requests.post', side_effect=AssertionError('题目记录不应调用生成服务')) as model:
        httpd = ThreadingHTTPServer(('127.0.0.1', 0), server.Handler)
        thread = threading.Thread(target=httpd.serve_forever, daemon=True)
        thread.start()
        try:
            with sync_playwright() as playwright:
                browser = playwright.chromium.launch(channel='msedge', headless=True)
                page = browser.new_page(viewport={'width': 1365, 'height': 1000})
                errors = []
                page.on('pageerror', lambda error: errors.append(str(error)))
                page.goto(f'http://127.0.0.1:{httpd.server_port}', wait_until='networkidle')
                page.locator('button').filter(has=page.get_by_text('工作区', exact=True)).click()
                page.get_by_label('新建工作区标题', exact=True).fill('R3.1 验收题目')
                page.get_by_label('自定义工作区 ID', exact=True).fill('focus-ui')
                page.get_by_role('button', name='创建', exact=True).click()
                page.get_by_label('当前目标', exact=True).fill('恢复整数 m')
                page.get_by_label('待验证假设', exact=True).fill('可能是同一明文')
                page.get_by_label('待查项', exact=True).fill('比较明文编码')
                with page.expect_response('**/api/workspaces/focus-ui'):
                    page.get_by_role('button', name='保存', exact=True).click()
                page.locator('label[for$="-attempt"]').click()
                page.get_by_label('尝试方向', exact=True).fill('运行共模脚本')
                page.get_by_label('尝试结论', exact=True).fill('缺少 sympy')
                page.locator('input[aria-label="尝试状态"]').click()
                page.get_by_role('option', name='无效', exact=True).click()
                state_y = page.locator('input[aria-label="尝试状态"]').bounding_box()['y']
                cause_y = page.locator('input[aria-label="失败原因"]').bounding_box()['y']
                assert abs(state_y - cause_y) < 50
                page.locator('input[aria-label="失败原因"]').click()
                page.get_by_role('option', name='运行出错', exact=True).click()
                with page.expect_response('**/api/workspaces/focus-ui/entries'):
                    page.get_by_role('button', name='添加', exact=True).click()
                page.get_by_text('结论：缺少 sympy', exact=True).wait_for()
                ws = server._workspace_store().load('focus-ui')
                assert ws['goal'] == '恢复整数 m' and ws['hypotheses'] == '可能是同一明文'
                assert ws['entries'][0]['failure_kind'] == 'runtime'
                page.reload(wait_until='networkidle')
                page.locator('button').filter(has=page.get_by_text('工作区', exact=True)).click()
                page.get_by_label('待查项', exact=True).wait_for()
                assert page.get_by_label('待查项', exact=True).input_value() == '比较明文编码'
                reason = page.get_by_label('失败原因 ' + ws['entries'][0]['id'], exact=True)
                assert reason.input_value() == '运行出错'
                reason.click()
                with page.expect_response('**/api/workspaces/focus-ui/entries/*'):
                    page.get_by_role('option', name='前提已排除', exact=True).click()
                exported = page.request.get(f'http://127.0.0.1:{httpd.server_port}/api/workspaces/focus-ui/export?format=md').text()
                assert '待验证假设' in exported and '失败原因：前提已排除' in exported
                assert not errors, errors
                page.screenshot(path=str(out / 'workspace-focus.png'), full_page=True)
                browser.close()
            result = {'ok': True, 'focus_save_reload': True, 'failure_reason_update': True,
                      'export': True, 'personal_workspaces_accessed': False, 'generation_calls': model.call_count}
            (out / 'ui-result.json').write_text(json.dumps(result, ensure_ascii=False, indent=2), encoding='utf-8')
            print(json.dumps(result, ensure_ascii=False))
        finally:
            httpd.shutdown()
            httpd.server_close()
            thread.join()
    return 0


if __name__ == '__main__':
    sys.stdout.reconfigure(encoding='utf-8')
    raise SystemExit(main())
