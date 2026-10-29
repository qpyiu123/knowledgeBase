import { MantineProvider } from '@mantine/core';
import { fireEvent, render, screen, waitFor } from '@testing-library/react';
import { beforeEach, describe, expect, it, vi } from 'vitest';
import WorkspacePicker from './WorkspacePicker';
import { api } from '../api';
import type { WorkspaceSummary } from '../types';

vi.mock('../api', () => ({
  api: {
    workspaces: {
      list: vi.fn(),
      create: vi.fn(),
    },
  },
}));

const listMock = vi.mocked(api.workspaces.list);
const createMock = vi.mocked(api.workspaces.create);

const WS: WorkspaceSummary = {
  id: 'ws1',
  title: '示例工作区',
  category: null,
  status: 'open',
  created: '2026-10-28T00:00:00+00:00',
  updated: '2026-10-28T00:00:00+00:00',
  entries: 3,
  counts: { fact: 1, attempt: 1, reference: 1 },
};

beforeEach(() => {
  listMock.mockReset();
  createMock.mockReset();
  listMock.mockResolvedValue({ workspaces: [WS] });
});

describe('WorkspacePicker', () => {
  it('preselects the default workspace and does not create a new one', async () => {
    const onPicked = vi.fn();
    render(
      <MantineProvider>
        <WorkspacePicker
          opened
          onClose={() => {}}
          onPicked={onPicked}
          defaultId="ws1"
        />
      </MantineProvider>,
    );

    await waitFor(() =>
      expect(
        (screen.getByRole('button', { name: /^存入$/ }) as HTMLButtonElement)
          .disabled,
      ).toBe(false),
    );
    fireEvent.click(screen.getByRole('button', { name: /^存入$/ }));

    await waitFor(() =>
      expect(onPicked).toHaveBeenCalledWith({ id: 'ws1', title: '示例工作区' }),
    );
    expect(createMock).not.toHaveBeenCalled();
  });
});
