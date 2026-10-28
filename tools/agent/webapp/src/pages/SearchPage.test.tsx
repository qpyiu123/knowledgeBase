import { MantineProvider } from '@mantine/core';
import { fireEvent, render, screen, waitFor } from '@testing-library/react';
import { beforeEach, describe, expect, it, vi } from 'vitest';
import SearchPage from './SearchPage';
import { api, ask } from '../api';
import type { AskHandlers } from '../lib/sse';
import type { Hit } from '../types';

vi.mock('../api', () => ({
  api: {
    search: vi.fn(),
    health: vi.fn(),
    stats: vi.fn(),
    doc: vi.fn(),
    feedback: vi.fn(),
  },
  ask: vi.fn(),
}));

const STARTER_Q = 'PHP str_replace 过滤关键字 绕过';

const HIT: Hit = {
  title: '弱 RSA 共模攻击',
  category: 'crypto',
  path: 'crypto/rsa-common-modulus-attack.md',
  score: 1,
  snippet: 'n 相同，e 不同',
  section: '三、解题步骤',
  doc_type: 'topic',
  doc_type_label: '专题文档',
  match: {
    sources: ['fts', 'vec'],
    labels: ['词面命中', '语义相近'],
    terms: ['RSA', '共模攻击'],
    rrf: { fts: 0.016, vec: 0.016 },
  },
};

function renderPage() {
  return render(
    <MantineProvider>
      <SearchPage category="" onOpenDoc={() => {}} docs={1567} />
    </MantineProvider>,
  );
}

const searchMock = vi.mocked(api.search);
const askMock = vi.mocked(ask);
const feedbackMock = vi.mocked(api.feedback);

beforeEach(() => {
  searchMock.mockReset();
  askMock.mockReset();
  feedbackMock.mockReset();
  searchMock.mockResolvedValue({ hits: [], ms: 1 });
  feedbackMock.mockResolvedValue({ ok: true, saved: 1 });
});

describe('SearchPage 显式参数', () => {
  it('starter card searches with its own text, not stale state', async () => {
    renderPage();
    fireEvent.click(screen.getByRole('button', { name: /按特征查方法/ }));

    await waitFor(() => expect(searchMock).toHaveBeenCalledTimes(1));
    expect(searchMock.mock.calls[0][0]).toBe(STARTER_Q);
  });

  it('result card ask uses the card question and references its path', async () => {
    searchMock.mockResolvedValue({ hits: [HIT], ms: 2 });
    askMock.mockImplementation(async (_q: string, _paths: string[], handlers: AskHandlers) => {
      handlers.onToken('步骤一');
      handlers.onDone?.('12 tok · 1.0 tok/s');
    });

    renderPage();
    fireEvent.click(screen.getByRole('button', { name: /按特征查方法/ }));
    await screen.findByRole('button', { name: '问模型' });
    fireEvent.click(screen.getByRole('button', { name: '问模型' }));

    await waitFor(() => expect(askMock).toHaveBeenCalledTimes(1));
    const [question, paths] = askMock.mock.calls[0];
    expect(question).toContain(HIT.title);
    expect(question).not.toBe(STARTER_Q);
    expect(paths).toEqual([HIT.path]);

    await screen.findByText('12 tok · 1.0 tok/s');
    await screen.findByText(/步骤一/);
  });

  it('shows backend errors from the ask stream', async () => {
    searchMock.mockResolvedValue({ hits: [HIT], ms: 2 });
    askMock.mockImplementation(async (_q: string, _paths: string[], handlers: AskHandlers) => {
      handlers.onError?.('模型不可达');
    });

    renderPage();
    fireEvent.click(screen.getByRole('button', { name: /按特征查方法/ }));
    await screen.findByRole('button', { name: '问模型' });
    fireEvent.click(screen.getByRole('button', { name: '问模型' }));

    await screen.findByText('模型不可达');
  });

  it('passes the doc type filter to search', async () => {
    renderPage();
    fireEvent.click(screen.getByText('比赛卡片'));
    fireEvent.click(screen.getByRole('button', { name: /按特征查方法/ }));

    await waitFor(() => expect(searchMock).toHaveBeenCalledTimes(1));
    expect(searchMock.mock.calls[0][3]).toBe('card');
  });

  it('shows hit section, reason and matched terms', async () => {
    searchMock.mockResolvedValue({ hits: [HIT], ms: 2 });

    renderPage();
    fireEvent.click(screen.getByRole('button', { name: /按特征查方法/ }));

    await screen.findByText('命中原因：词面命中 + 语义相近');
    await screen.findByText('命中章节：三、解题步骤');
    await screen.findByText('命中词：RSA · 共模攻击');
  });

  it('shows applicability state and actionable prerequisite hint', async () => {
    searchMock.mockResolvedValue({
      hits: [
        {
          ...HIT,
          applicability: {
            status: 'unknown',
            status_label: '未知',
            hint: '缺少前提：已知同一 n 下的两组密文（unknown）',
          },
        },
      ],
      ms: 2,
    });

    renderPage();
    fireEvent.click(screen.getByRole('button', { name: /按特征查方法/ }));

    await screen.findByText('前提：未知');
    await screen.findByText(/缺少前提：已知同一 n 下的两组密文/);
  });

  it('records useful feedback for a result', async () => {
    searchMock.mockResolvedValue({ hits: [HIT], ms: 2 });

    renderPage();
    fireEvent.click(screen.getByRole('button', { name: /按特征查方法/ }));
    fireEvent.click(await screen.findByRole('button', { name: '有用' }));

    await waitFor(() =>
      expect(feedbackMock).toHaveBeenCalledWith(STARTER_Q, HIT.path, 'useful'),
    );
    await screen.findByText('已记录：有用');
  });

  it('renders graph related results separately', async () => {
    searchMock.mockResolvedValue({
      hits: [HIT],
      graph: [
        {
          title: 'RSA 维纳攻击',
          category: 'crypto',
          path: 'crypto/rsa-wiener-attack.md',
          score: 0,
          snippet: '',
          graph_via: 'relates_to',
        },
      ],
      ms: 2,
    });

    renderPage();
    fireEvent.click(screen.getByRole('button', { name: /按特征查方法/ }));

    await screen.findByText('关联阅读');
    await screen.findByText('RSA 维纳攻击');
    await screen.findByText('图谱 · relates_to');
  });
});
