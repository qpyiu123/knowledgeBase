import { MantineProvider } from '@mantine/core';
import { fireEvent, render, screen } from '@testing-library/react';
import { expect, it, vi } from 'vitest';
import ResizableDrawer from './ResizableDrawer';

it('两个侧栏的宽度分别保留，并随窗口收窄', () => {
  vi.stubGlobal('innerWidth', 1365);
  const view = (articleOpen: boolean) => (
    <MantineProvider>
      <ResizableDrawer opened={articleOpen} onClose={() => {}} title="文章"
        defaultWidth={920} resizeLabel="调整文章侧栏宽度" withOverlay={false} trapFocus={false}>
        文章正文
      </ResizableDrawer>
      <ResizableDrawer opened onClose={() => {}} title="深度搜索结果"
        defaultWidth={620} resizeLabel="调整结果侧栏宽度" withOverlay={false} trapFocus={false}>
        搜索结果
      </ResizableDrawer>
    </MantineProvider>
  );
  const article = () => screen.getByRole('separator', { name: '调整文章侧栏宽度' });
  const result = () => screen.getByRole('separator', { name: '调整结果侧栏宽度' });
  const width = (handle: HTMLElement) => handle.getAttribute('aria-valuenow');

  try {
    const { rerender } = render(view(true));
    fireEvent.keyDown(article(), { key: 'ArrowRight' });
    expect(width(article())).toBe('896');
    expect(width(result())).toBe('620');
    rerender(view(false));
    rerender(view(true));
    expect(width(article())).toBe('896');

    vi.stubGlobal('innerWidth', 390);
    fireEvent(window, new Event('resize'));
    expect(width(article())).toBe('390');
    expect(width(result())).toBe('390');
    vi.stubGlobal('innerWidth', 1365);
    fireEvent(window, new Event('resize'));
    expect(width(article())).toBe('896');
    expect(width(result())).toBe('620');
  } finally {
    vi.unstubAllGlobals();
  }
});
