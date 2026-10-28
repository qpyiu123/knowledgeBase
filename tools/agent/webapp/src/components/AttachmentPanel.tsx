import {
  Alert,
  Button,
  Card,
  Group,
  Loader,
  Stack,
  Text,
} from '@mantine/core';
import { Paperclip, Upload } from 'lucide-react';
import { useCallback, useState } from 'react';
import { api } from '../api';
import type { AttachmentReport } from '../types';
import AttachmentReportView from './AttachmentReport';

const FALLBACK_MAX = 8 * 1024 * 1024;

function bytes(n: number): string {
  if (n < 1024) return `${n} B`;
  if (n < 1024 * 1024) return `${(n / 1024).toFixed(1)} KiB`;
  return `${(n / 1024 / 1024).toFixed(2)} MiB`;
}

export default function AttachmentPanel({
  maxBytes,
  workspaceId,
  workspaceTitle,
  onAttached,
}: {
  maxBytes?: number;
  workspaceId?: string | null;
  workspaceTitle?: string;
  onAttached?: () => void;
}) {
  const limit = maxBytes && maxBytes > 0 ? maxBytes : FALLBACK_MAX;
  const [busy, setBusy] = useState(false);
  const [error, setError] = useState('');
  const [report, setReport] = useState<AttachmentReport | null>(null);
  const [name, setName] = useState('');
  const [attached, setAttached] = useState(false);
  const [dragging, setDragging] = useState(false);

  const upload = useCallback(
    async (file: File) => {
      setError('');
      setReport(null);
      setAttached(false);
      setName(file.name);
      // 只用 /api/health 的上限做预检；超限直接提示，不发请求。
      if (file.size > limit) {
        setError(
          `文件 ${bytes(file.size)} 超过上限 ${bytes(limit)}，已取消上传（未发送请求）。`,
        );
        return;
      }
      setBusy(true);
      try {
        const buf = await file.arrayBuffer();
        const result = await api.analyze(file.name, buf);
        setReport(result);
        if (result.error) setError(result.error);
      } catch (e) {
        setError(`附件分析失败：${String((e as Error).message || e)}`);
      } finally {
        setBusy(false);
      }
    },
    [limit],
  );

  const onPick = useCallback(
    (file: File | null) => {
      if (file) void upload(file);
    },
    [upload],
  );

  const attach = useCallback(async () => {
    if (!report || !workspaceId) return;
    setError('');
    try {
      await api.workspaces.addEntry(workspaceId, {
        kind: 'reference',
        title: report.file?.name || name || '附件',
        text: `附件分析报告（${report.type?.kind || '未知类型'}）`,
        path: report.storage?.saved || report.file?.saved || '',
        source: 'analyze',
        report,
      });
      setAttached(true);
      onAttached?.();
    } catch (e) {
      setError(`附到工作区失败：${String((e as Error).message || e)}`);
    }
  }, [report, workspaceId, name, onAttached]);

  return (
    <Card
      withBorder
      radius="lg"
      className="attachment-card"
      onDragOver={(e) => {
        e.preventDefault();
        setDragging(true);
      }}
      onDragLeave={() => setDragging(false)}
      onDrop={(e) => {
        e.preventDefault();
        setDragging(false);
        const file = e.dataTransfer.files?.[0];
        if (file) void upload(file);
      }}
      style={
        dragging
          ? { borderColor: 'var(--accent)', boxShadow: '0 0 0 3px var(--accent-soft)' }
          : undefined
      }
    >
      <Stack gap="md">
        <Group justify="space-between" align="flex-start" wrap="wrap">
          <div>
            <Group gap={8}>
              <Paperclip size={17} />
              <Text fw={650}>分析附件</Text>
            </Group>
            <Text size="xs" c="dimmed" mt={4}>
              选择或拖入文件，只做只读结构与编码嗅探；不会运行附件，上传前不做预览。
              上限 {bytes(limit)}。
            </Text>
          </div>
          <Group gap={8}>
            <Button
              component="label"
              variant="light"
              leftSection={<Upload size={15} />}
              loading={busy}
            >
              选择文件
              <input
                type="file"
                aria-label="选择附件"
                style={{ display: 'none' }}
                onChange={(e) => {
                  const file = e.currentTarget.files?.[0] || null;
                  onPick(file);
                  e.currentTarget.value = '';
                }}
              />
            </Button>
          </Group>
        </Group>

        {busy && (
          <Group gap="xs">
            <Loader size={15} />
            <Text size="sm" c="dimmed">
              正在上传并分析 {name}…
            </Text>
          </Group>
        )}

        {error && (
          <Alert color="orange" title="附件分析">
            {error}
          </Alert>
        )}

        {report && (
          <Stack gap="sm">
            <Group justify="space-between" wrap="wrap">
              <Text size="sm" fw={600}>
                分析结果：{report.file?.name}
              </Text>
              {workspaceId ? (
                <Button
                  size="compact-sm"
                  variant={attached ? 'light' : 'default'}
                  disabled={attached}
                  onClick={() => void attach()}
                >
                  {attached
                    ? `已附到「${workspaceTitle || workspaceId}」`
                    : `附到工作区${workspaceTitle ? `「${workspaceTitle}」` : ''}`}
                </Button>
              ) : (
                <Text size="xs" c="dimmed">
                  先在工作区页选择工作区，才能附着报告。
                </Text>
              )}
            </Group>
            <AttachmentReportView report={report} />
          </Stack>
        )}
      </Stack>
    </Card>
  );
}
