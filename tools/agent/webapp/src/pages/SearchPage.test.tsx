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

beforeEach(() => {
  searchMock.mockReset();
  askMock.mockReset();
  searchMock.mockResolvedValue({ hits: [], ms: 1 });
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
});
