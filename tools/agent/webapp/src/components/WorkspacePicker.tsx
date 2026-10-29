import {
  Alert,
  Button,
  Divider,
  Group,
  Modal,
  Select,
  Stack,
  Text,
  TextInput,
} from '@mantine/core';
import { FolderPlus } from 'lucide-react';
import { useCallback, useEffect, useMemo, useState } from 'react';
import { api } from '../api';
import type { WorkspaceSummary } from '../types';

export type PickedWorkspace = { id: string; title: string };

export default function WorkspacePicker({
  opened,
  onClose,
  onPicked,
  defaultId,
  hint,
}: {
  opened: boolean;
  onClose: () => void;
  onPicked: (ws: PickedWorkspace) => void | Promise<void>;
  defaultId?: string;
  hint?: string;
}) {
  const [list, setList] = useState<WorkspaceSummary[]>([]);
  const [selected, setSelected] = useState<string | null>(null);
  const [title, setTitle] = useState('');
  const [busy, setBusy] = useState(false);
  const [error, setError] = useState('');
  const [loading, setLoading] = useState(false);

  const options = useMemo(
    () =>
      list.map((w) => ({
        value: w.id,
        label: `${w.title}（${w.id}）· ${w.entries} 条`,
      })),
    [list],
  );

  useEffect(() => {
    if (!opened) return;
    let alive = true;
    setError('');
    setTitle('');
    setSelected(null);
    setLoading(true);
    api.workspaces
      .list()
      .then((r) => {
        if (!alive) return;
        const items = r.workspaces || [];
        setList(items);
        if (defaultId && items.some((w) => w.id === defaultId)) {
          setSelected(defaultId);
        }
      })
      .catch((e) => {
        if (alive) setError(`读取工作区失败：${String((e as Error).message || e)}`);
      })
      .finally(() => {
        if (alive) setLoading(false);
      });
    return () => {
      alive = false;
    };
  }, [opened, defaultId]);

  const submit = useCallback(async () => {
    setBusy(true);
    setError('');
    try {
      let picked: PickedWorkspace;
      if (selected) {
        const item = list.find((w) => w.id === selected);
        if (!item) throw new Error('选择的工作区不存在');
        picked = { id: item.id, title: item.title };
      } else {
        const name = title.trim();
        if (!name) throw new Error('输入标题即可新建工作区');
        const r = await api.workspaces.create(name);
        picked = { id: r.workspace.id, title: r.workspace.title };
      }
      await onPicked(picked);
      onClose();
    } catch (e) {
      setError(String((e as Error).message || e));
    } finally {
      setBusy(false);
    }
  }, [selected, list, title, onPicked, onClose]);

  return (
    <Modal opened={opened} onClose={onClose} title="存入工作区" centered>
      <Stack gap="md">
        {hint && (
          <Text size="sm" c="dimmed">
            {hint}
          </Text>
        )}
        {error && (
          <Alert color="orange" title="工作区">
            {error}
          </Alert>
        )}
        {list.length ? (
          <Select
            label="选择已有工作区"
            aria-label="选择已有工作区"
            data={options}
            value={selected}
            onChange={setSelected}
            placeholder={loading ? '读取中…' : '选择工作区'}
            searchable
            clearable
            disabled={loading}
          />
        ) : (
          <Text size="sm" c="dimmed">
            还没有工作区。输入标题即可新建，保存后会自动设为默认工作区。
          </Text>
        )}
        <Divider label="或新建" labelPosition="center" />
        <TextInput
          label="新工作区标题"
          aria-label="新工作区标题"
          placeholder="例如：ctfshow Web 上传"
          value={title}
          onChange={(e) => {
            setTitle(e.currentTarget.value);
            setSelected(null);
          }}
          onFocus={() => setSelected(null)}
        />
        <Group justify="flex-end">
          <Button variant="subtle" onClick={onClose}>
            取消
          </Button>
          <Button
            leftSection={<FolderPlus size={15} />}
            loading={busy}
            disabled={!selected && !title.trim()}
            onClick={() => void submit()}
          >
            存入
          </Button>
        </Group>
      </Stack>
    </Modal>
  );
}
