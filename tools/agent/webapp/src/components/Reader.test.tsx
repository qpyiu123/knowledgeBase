import { MantineProvider } from '@mantine/core';
import { fireEvent, render, screen, waitFor } from '@testing-library/react';
import { beforeEach, describe, expect, it, vi } from 'vitest';
import Reader from './Reader';
import { api } from '../api';

vi.mock('../api', () => ({ api: { doc: vi.fn(), code: vi.fn() } }));

beforeEach(() => {
  vi.mocked(api.doc).mockReset().mockResolvedValue({
    path: '_methods/test.md', body: '## 使用方法\n这是一段方法说明。',
    scripts: [{ path: '_methods/scripts/test.py', title: 'test.py' }],
    sources: [{ path: 'misc/original.md', external: false }],
    methods: [{ path: '_methods/related.md', title: '关联的方法卡' }],
  });
  vi.mocked(api.code).mockReset().mockResolvedValue({
    path: '_methods/scripts/test.py', body: 'print("read only")', language: 'python',
    dependencies: ['sympy'], arguments: ['--number'], summary: '数字计算。',
  });
});

describe('Reader 只读代码', () => {
  it('opens the source section without sending the fragment to the document API', async () => {
    const scroll = vi.fn();
    HTMLElement.prototype.scrollIntoView = scroll;
    render(<MantineProvider><Reader target={{ path: 'misc/original.md#使用方法' }} onClose={() => {}} /></MantineProvider>);
    await screen.findByText('这是一段方法说明。');
    await waitFor(() => expect(scroll).toHaveBeenCalled());
    expect(api.doc).toHaveBeenCalledWith('misc/original.md');
    expect(api.code).not.toHaveBeenCalled();
  });
  it('opens a method explicitly linked from the source document', async () => {
    render(<MantineProvider><Reader target={{ path: 'misc/original.md' }} onClose={() => {}} /></MantineProvider>);
    fireEvent.click(await screen.findByRole('button', { name: '关联的方法卡' }));
    await waitFor(() => expect(api.doc).toHaveBeenLastCalledWith('_methods/related.md'));
  });
  it('opens a related script and copies its complete source', async () => {
    const copy = vi.fn().mockResolvedValue(undefined);
    Object.defineProperty(navigator, 'clipboard', { configurable: true, value: { writeText: copy } });
    render(<MantineProvider><Reader target={{ path: '_methods/test.md' }} onClose={() => {}} /></MantineProvider>);
    fireEvent.click(await screen.findByRole('button', { name: '查看代码 test.py' }));
    await screen.findByText('第三方依赖：sympy');
    await screen.findByText('输入参数：--number');
    fireEvent.click(screen.getByRole('button', { name: '复制代码' }));
    await waitFor(() => expect(copy).toHaveBeenCalledWith('print("read only")'));
    await screen.findByRole('button', { name: '已复制' });
    fireEvent.click(screen.getByRole('button', { name: '返回原文档' }));
    await screen.findByText('这是一段方法说明。');
  });

  it('keeps code visible when the clipboard is unavailable', async () => {
    Object.defineProperty(navigator, 'clipboard', { configurable: true,
      value: { writeText: vi.fn().mockRejectedValue(new Error('denied')) } });
    render(<MantineProvider><Reader target={{ path: '_methods/scripts/test.py' }} onClose={() => {}} /></MantineProvider>);
    fireEvent.click(await screen.findByRole('button', { name: '复制代码' }));
    await screen.findByText('复制失败，请选择代码后按 Ctrl+C。');
    expect(screen.getByText('print("read only")')).toBeTruthy();
    expect(api.doc).not.toHaveBeenCalled();
  });
});
