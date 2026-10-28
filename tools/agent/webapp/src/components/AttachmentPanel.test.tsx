import { MantineProvider } from '@mantine/core';
import { fireEvent, render, screen, waitFor } from '@testing-library/react';
import { beforeEach, describe, expect, it, vi } from 'vitest';
import AttachmentPanel from './AttachmentPanel';
import { api } from '../api';
import type { AttachmentReport } from '../types';

vi.mock('../api', () => ({
  api: {
    analyze: vi.fn(),
    workspaces: {
      addEntry: vi.fn(),
    },
  },
}));

const analyzeMock = vi.mocked(api.analyze);
const addEntryMock = vi.mocked(api.workspaces.addEntry);

const REPORT: AttachmentReport = {
  schema_version: 1,
  executed: false,
  file: {
    name: 'sample.png',
    size: 4,
    sha256: 'abc123',
    ext: '.png',
    saved: 'work/attachments/x/upload_sample.png',
  },
  type: {
    kind: 'PNG',
    detected: true,
    is_text: false,
    preview: '',
    extension: '.png',
    extension_mismatch: true,
  },
  carve: [{ type: 'ZIP', offset: 42, offset_hex: '0x2a', size: 8 }],
  structures: {
    png: { width: 1, height: 1, chunks: [{ type: 'IHDR', len: 13 }] },
  },
  anomalies: ['扩展名不符'],
  decoded: [{ method: 'base64', decoded: 'flag{p3}' }],
  strings: ['flag{p3}'],
  warnings: ['该扩展名属于可执行/脚本类型；本工具只读取字节，不会运行它。'],
  storage: {
    isolated: true,
    dir: 'work/attachments/x',
    saved: 'work/attachments/x/upload_sample.png',
  },
};

function renderPanel(maxBytes = 1024, workspaceId: string | null = 'ws1') {
  return render(
    <MantineProvider>
      <AttachmentPanel
        maxBytes={maxBytes}
        workspaceId={workspaceId}
        workspaceTitle="示例工作区"
      />
    </MantineProvider>,
  );
}

beforeEach(() => {
  analyzeMock.mockReset();
  addEntryMock.mockReset();
});

describe('AttachmentPanel', () => {
  it('pre-checks size and never sends an over-limit request', async () => {
    renderPanel(5);
    const file = new File([new Uint8Array(10)], 'big.bin');
    fireEvent.change(screen.getByLabelText('选择附件'), {
      target: { files: [file] },
    });

    await screen.findByText(/超过上限/);
    expect(analyzeMock).not.toHaveBeenCalled();
  });

  it('uploads raw bytes and shows the structured report', async () => {
    analyzeMock.mockResolvedValue(REPORT);
    renderPanel();

    const file = new File([new Uint8Array([1, 2, 3, 4])], 'sample.png');
    fireEvent.change(screen.getByLabelText('选择附件'), {
      target: { files: [file] },
    });

    await waitFor(() => expect(analyzeMock).toHaveBeenCalledTimes(1));
    const [name, data] = analyzeMock.mock.calls[0];
    expect(name).toBe('sample.png');
    expect(data).toBeInstanceOf(ArrayBuffer);
    expect((data as ArrayBuffer).byteLength).toBe(4);

    await screen.findByText('分析结果：sample.png');
    await screen.findByText('扩展名与真实内容不符');
    expect((await screen.findAllByText(/不会运行/)).length).toBeGreaterThan(0);
    await screen.findByText('未执行');
    await screen.findByText(/work\/attachments/);
  });

  it('attaches the full report JSON to the selected workspace', async () => {
    analyzeMock.mockResolvedValue(REPORT);
    addEntryMock.mockResolvedValue({
      ok: true,
      workspace: {} as never,
      entry: {} as never,
    });
    renderPanel();

    fireEvent.change(screen.getByLabelText('选择附件'), {
      target: { files: [new File(['x'], 'sample.png')] },
    });
    await screen.findByText('分析结果：sample.png');
    fireEvent.click(screen.getByRole('button', { name: /附到工作区/ }));

    await waitFor(() => expect(addEntryMock).toHaveBeenCalledTimes(1));
    const [id, entry] = addEntryMock.mock.calls[0];
    expect(id).toBe('ws1');
    expect(entry.kind).toBe('reference');
    expect(entry.report).toEqual(REPORT);
    await screen.findByText(/已附到「示例工作区」/);
  });

  it('does not offer attach without a current workspace', async () => {
    analyzeMock.mockResolvedValue(REPORT);
    renderPanel(1024, null);

    fireEvent.change(screen.getByLabelText('选择附件'), {
      target: { files: [new File(['x'], 'sample.png')] },
    });
    await screen.findByText('分析结果：sample.png');
    expect(screen.queryByRole('button', { name: /附到工作区/ })).toBeNull();
    await screen.findByText(/先在工作区页选择工作区/);
  });
});
