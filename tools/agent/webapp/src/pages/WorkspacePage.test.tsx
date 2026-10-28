import { MantineProvider } from '@mantine/core';
import { fireEvent, render, screen, waitFor } from '@testing-library/react';
import { beforeEach, describe, expect, it, vi } from 'vitest';
import WorkspacePage from './WorkspacePage';
import { api } from '../api';
import type { Workspace, WorkspaceSummary } from '../types';

vi.mock('../api', () => ({
  api: {
    workspaces: {
      list: vi.fn(),
      get: vi.fn(),
      create: vi.fn(),
      update: vi.fn(),
      remove: vi.fn(),
      addEntry: vi.fn(),
      updateEntry: vi.fn(),
      removeEntry: vi.fn(),
      timeline: vi.fn(),
      exportUrl: vi.fn(
        (id: string, mode: 'normal' | 'writeup' = 'normal') =>
          `/api/workspaces/${id}/export?format=md` +
          (mode === 'writeup' ? '&mode=writeup' : ''),
      ),
    },
  },
}));

const wsMock = api.workspaces;
const listMock = vi.mocked(wsMock.list);
const getMock = vi.mocked(wsMock.get);
const createMock = vi.mocked(wsMock.create);
const addEntryMock = vi.mocked(wsMock.addEntry);

function makeWorkspace(over: Partial<Workspace> = {}): Workspace {
  return {
    schema_version: 1,
    id: 'ws1',
    title: '示例题',
    category: 'web',
    status: 'open',
    created: '2026-10-28T00:00:00+00:00',
    updated: '2026-10-28T00:00:00+00:00',
    entries: [],
    timeline: [
      { ts: '2026-10-28T00:00:00+00:00', kind: 'create', summary: '创建工作区' },
    ],
    ...over,
  };
}

function summary(ws: Workspace): WorkspaceSummary {
  return {
    id: ws.id,
    title: ws.title,
    category: ws.category,
    status: ws.status,
    created: ws.created,
    updated: ws.updated,
    entries: ws.entries.length,
    counts: { fact: 0, attempt: 0, reference: 0 },
  };
}

function renderPage(currentId: string, onSelect = vi.fn()) {
  return render(
    <MantineProvider>
      <WorkspacePage currentId={currentId} onSelect={onSelect} />
    </MantineProvider>,
  );
}

beforeEach(() => {
  listMock.mockReset();
  getMock.mockReset();
  createMock.mockReset();
  addEntryMock.mockReset();
  listMock.mockResolvedValue({ workspaces: [] });
});

describe('WorkspacePage', () => {
  it('creates a user-named workspace and selects it', async () => {
    const created = makeWorkspace({ id: 'ws-new', title: '新题' });
    createMock.mockResolvedValue({ ok: true, workspace: created });
    getMock.mockResolvedValue({ workspace: created });
    const onSelect = vi.fn();

    renderPage('', onSelect);
    fireEvent.change(screen.getByLabelText('新建工作区标题'), {
      target: { value: '新题' },
    });
    fireEvent.change(screen.getByLabelText('自定义工作区 ID'), {
      target: { value: 'ws-new' },
    });
    fireEvent.click(screen.getByRole('button', { name: '创建' }));

    await waitFor(() =>
      expect(createMock).toHaveBeenCalledWith('新题', 'ws-new'),
    );
    await waitFor(() => expect(onSelect).toHaveBeenCalledWith('ws-new', '新题'));
  });

  it('adds a fact to the current workspace', async () => {
    const ws = makeWorkspace();
    listMock.mockResolvedValue({ workspaces: [summary(ws)] });
    getMock.mockResolvedValue({ workspace: ws });
    addEntryMock.mockResolvedValue({
      ok: true,
      workspace: makeWorkspace({
        entries: [
          {
            id: 'f1',
            created: '2026-10-28T00:01:00+00:00',
            kind: 'fact',
            text: '过滤只替换一次',
          },
        ],
      }),
      entry: {
        id: 'f1',
        created: '2026-10-28T00:01:00+00:00',
        kind: 'fact',
        text: '过滤只替换一次',
      },
    });

    renderPage('ws1');
    await screen.findByText('示例题');
    fireEvent.change(screen.getByLabelText('条目内容'), {
      target: { value: '过滤只替换一次' },
    });
    fireEvent.click(screen.getByRole('button', { name: '添加' }));

    await waitFor(() =>
      expect(addEntryMock).toHaveBeenCalledWith('ws1', {
        kind: 'fact',
        text: '过滤只替换一次',
      }),
    );
    await screen.findByText('过滤只替换一次');
  });

  it('adds an attempt with direction, conclusion and status', async () => {
    const ws = makeWorkspace();
    listMock.mockResolvedValue({ workspaces: [summary(ws)] });
    getMock.mockResolvedValue({ workspace: ws });
    addEntryMock.mockResolvedValue({
      ok: true,
      workspace: ws,
      entry: { id: 'a1', created: 'now', kind: 'attempt', text: '' },
    });

    renderPage('ws1');
    await screen.findByText('示例题');
    fireEvent.click(screen.getByRole('radio', { name: '尝试' }));
    fireEvent.change(screen.getByLabelText('尝试方向'), {
      target: { value: '短标签绕过' },
    });
    fireEvent.change(screen.getByLabelText('尝试结论'), {
      target: { value: '被过滤，无效' },
    });
    fireEvent.click(screen.getByRole('button', { name: '添加' }));

    await waitFor(() =>
      expect(addEntryMock).toHaveBeenCalledWith('ws1', {
        kind: 'attempt',
        direction: '短标签绕过',
        conclusion: '被过滤，无效',
        text: '',
        result: 'pending',
      }),
    );
  });

  it('shows timeline and exposes Markdown export', async () => {
    const ws = makeWorkspace();
    listMock.mockResolvedValue({ workspaces: [summary(ws)] });
    getMock.mockResolvedValue({ workspace: ws });

    renderPage('ws1');
    await screen.findByText('示例题');
    await screen.findByText('创建工作区');
    const link = screen.getByRole('link', { name: /导出 Markdown/ });
    expect(link.getAttribute('href')).toBe('/api/workspaces/ws1/export?format=md');
  });

  it('switches to traceable Writeup export', async () => {
    const ws = makeWorkspace();
    listMock.mockResolvedValue({ workspaces: [summary(ws)] });
    getMock.mockResolvedValue({ workspace: ws });

    renderPage('ws1');
    await screen.findByText('示例题');
    fireEvent.click(screen.getByRole('radio', { name: 'Writeup 草稿' }));

    const link = await screen.findByRole('link', { name: /导出 Writeup/ });
    expect(link.getAttribute('href')).toBe(
      '/api/workspaces/ws1/export?format=md&mode=writeup',
    );
  });

  it('adds a kb reference with a section anchor', async () => {
    const ws = makeWorkspace();
    listMock.mockResolvedValue({ workspaces: [summary(ws)] });
    getMock.mockResolvedValue({ workspace: ws });
    addEntryMock.mockResolvedValue({
      ok: true,
      workspace: ws,
      entry: { id: 'r2', created: 'now', kind: 'reference', text: '' },
    });

    renderPage('ws1');
    await screen.findByText('示例题');
    fireEvent.click(screen.getByRole('radio', { name: '资料收藏' }));
    fireEvent.change(screen.getByLabelText('资料标题'), {
      target: { value: 'RSA 共模' },
    });
    fireEvent.change(screen.getByLabelText('资料 kb 路径'), {
      target: { value: 'crypto/rsa.md' },
    });
    fireEvent.change(screen.getByLabelText('资料章节锚点'), {
      target: { value: '一、识别信号' },
    });
    fireEvent.click(screen.getByRole('button', { name: '添加' }));

    await waitFor(() =>
      expect(addEntryMock).toHaveBeenCalledWith('ws1', {
        kind: 'reference',
        title: 'RSA 共模',
        path: 'crypto/rsa.md',
        anchor: '一、识别信号',
        url: '',
        text: '',
      }),
    );
  });

  it('renders attached attachment report inside a reference entry', async () => {
    const ws = makeWorkspace({
      entries: [
        {
          id: 'r1',
          created: '2026-10-28T00:01:00+00:00',
          kind: 'reference',
          title: 'sample.png',
          text: '附件分析报告',
          source: 'analyze',
          report: {
            executed: false,
            file: { name: 'sample.png', size: 4, sha256: 'abc' },
            type: { kind: 'PNG', is_text: false, extension_mismatch: false },
            anomalies: [],
            decoded: [],
            strings: [],
            warnings: [],
          },
        },
      ],
    });
    listMock.mockResolvedValue({ workspaces: [summary(ws)] });
    getMock.mockResolvedValue({ workspace: ws });

    renderPage('ws1');
    await screen.findByText('sample.png');
    expect((await screen.findAllByText('附件分析报告')).length).toBeGreaterThan(0);
  });
});
