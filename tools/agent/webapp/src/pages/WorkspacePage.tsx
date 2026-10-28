import {
  Accordion,
  ActionIcon,
  Alert,
  Badge,
  Button,
  Card,
  Divider,
  Group,
  Loader,
  SegmentedControl,
  Select,
  Stack,
  Text,
  Textarea,
  TextInput,
  Title,
  Tooltip,
} from '@mantine/core';
import {
  Download,
  FolderPlus,
  Plus,
  RefreshCw,
  Trash2,
} from 'lucide-react';
import { useCallback, useEffect, useMemo, useState } from 'react';
import { api } from '../api';
import AttachmentReportView from '../components/AttachmentReport';
import type {
  AttemptResult,
  Workspace,
  WorkspaceEntry,
  WorkspaceEntryKind,
  WorkspaceStatus,
  WorkspaceSummary,
} from '../types';

const STATUS_LABEL: Record<WorkspaceStatus, string> = {
  open: '进行中',
  solved: '已解决',
  archived: '已归档',
};

const RESULT_LABEL: Record<AttemptResult, string> = {
  pending: '待验证',
  success: '有效',
  failed: '无效',
};

const KIND_LABEL: Record<WorkspaceEntryKind, string> = {
  fact: '事实',
  attempt: '尝试',
  reference: '资料收藏',
};

function errorText(e: unknown): string {
  return String((e as Error).message || e);
}

export default function WorkspacePage({
  currentId,
  onSelect,
}: {
  currentId: string;
  onSelect: (id: string, title: string) => void;
}) {
  const [list, setList] = useState<WorkspaceSummary[]>([]);
  const [ws, setWs] = useState<Workspace | null>(null);
  const [loading, setLoading] = useState(false);
  const [busy, setBusy] = useState(false);
  const [error, setError] = useState('');

  const [newTitle, setNewTitle] = useState('');
  const [newId, setNewId] = useState('');
  const [titleEdit, setTitleEdit] = useState('');
  const [statusEdit, setStatusEdit] = useState<WorkspaceStatus>('open');

  const [kind, setKind] = useState<WorkspaceEntryKind>('fact');
  const [entryText, setEntryText] = useState('');
  const [entryResult, setEntryResult] = useState<AttemptResult>('pending');
  const [direction, setDirection] = useState('');
  const [conclusion, setConclusion] = useState('');
  const [refTitle, setRefTitle] = useState('');
  const [refPath, setRefPath] = useState('');
  const [refAnchor, setRefAnchor] = useState('');
  const [refUrl, setRefUrl] = useState('');
  const [exportMode, setExportMode] = useState<'normal' | 'writeup'>('normal');

  const options = useMemo(
    () =>
      list.map((w) => ({
        value: w.id,
        label: `${w.title}（${w.id}）· ${w.entries} 条`,
      })),
    [list],
  );

  const loadList = useCallback(async () => {
    const r = await api.workspaces.list();
    setList(r.workspaces || []);
    return r.workspaces || [];
  }, []);

  const loadDetail = useCallback(async (id: string) => {
    if (!id) {
      setWs(null);
      return;
    }
    const r = await api.workspaces.get(id);
    setWs(r.workspace);
    setTitleEdit(r.workspace.title);
    setStatusEdit(r.workspace.status);
  }, []);

  const refresh = useCallback(async () => {
    setLoading(true);
    try {
      const items = await loadList();
      const id = currentId || items[0]?.id || '';
      if (!currentId && id) {
        const item = items.find((w) => w.id === id);
        onSelect(id, item?.title || '');
      }
      if ((currentId || id) && items.some((w) => w.id === (currentId || id))) {
        await loadDetail(currentId || id);
      } else if (!items.length) {
        setWs(null);
      }
    } catch (e) {
      setError(errorText(e));
    } finally {
      setLoading(false);
    }
  }, [currentId, loadDetail, loadList, onSelect]);

  useEffect(() => {
    void refresh();
    // 只在首次挂载和所选工作区变化时拉取，避免表单输入触发刷新。
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [currentId]);

  const create = useCallback(async () => {
    const title = newTitle.trim();
    if (!title) {
      setError('工作区标题不能为空');
      return;
    }
    setBusy(true);
    setError('');
    try {
      const r = await api.workspaces.create(title, newId.trim() || undefined);
      setNewTitle('');
      setNewId('');
      await loadList();
      onSelect(r.workspace.id, r.workspace.title);
      await loadDetail(r.workspace.id);
    } catch (e) {
      setError(errorText(e));
    } finally {
      setBusy(false);
    }
  }, [newTitle, newId, loadList, loadDetail, onSelect]);

  const saveMeta = useCallback(async () => {
    if (!ws) return;
    setBusy(true);
    setError('');
    try {
      const r = await api.workspaces.update(ws.id, {
        title: titleEdit.trim(),
        status: statusEdit,
      });
      setWs(r.workspace);
      onSelect(r.workspace.id, r.workspace.title);
      await loadList();
    } catch (e) {
      setError(errorText(e));
    } finally {
      setBusy(false);
    }
  }, [ws, titleEdit, statusEdit, onSelect, loadList]);

  const addEntry = useCallback(async () => {
    if (!ws) {
      setError('先选择或创建一个工作区');
      return;
    }
    const payload: Parameters<typeof api.workspaces.addEntry>[1] = { kind };
    if (kind === 'fact') {
      payload.text = entryText.trim();
    } else if (kind === 'attempt') {
      payload.direction = direction.trim();
      payload.conclusion = conclusion.trim();
      payload.text = entryText.trim();
      payload.result = entryResult;
    } else {
      payload.title = refTitle.trim();
      payload.path = refPath.trim();
      payload.anchor = refPath.trim() ? refAnchor.trim() : '';
      payload.url = refUrl.trim();
      payload.text = entryText.trim();
    }
    setBusy(true);
    setError('');
    try {
      const r = await api.workspaces.addEntry(ws.id, payload);
      setWs(r.workspace);
      setEntryText('');
      setDirection('');
      setConclusion('');
      setRefTitle('');
      setRefPath('');
      setRefAnchor('');
      setRefUrl('');
      await loadList();
    } catch (e) {
      setError(errorText(e));
    } finally {
      setBusy(false);
    }
  }, [
    ws,
    kind,
    entryText,
    entryResult,
    direction,
    conclusion,
    refTitle,
    refPath,
    refAnchor,
    refUrl,
    loadList,
  ]);

  const changeResult = useCallback(
    async (entry: WorkspaceEntry, result: string) => {
      if (!ws) return;
      setBusy(true);
      setError('');
      try {
        const r = await api.workspaces.updateEntry(ws.id, entry.id, { result });
        setWs(r.workspace);
      } catch (e) {
        setError(errorText(e));
      } finally {
        setBusy(false);
      }
    },
    [ws],
  );

  const removeEntry = useCallback(
    async (entry: WorkspaceEntry) => {
      if (!ws) return;
      setBusy(true);
      setError('');
      try {
        const r = await api.workspaces.removeEntry(ws.id, entry.id);
        setWs(r.workspace);
        await loadList();
      } catch (e) {
        setError(errorText(e));
      } finally {
        setBusy(false);
      }
    },
    [ws, loadList],
  );

  const removeWorkspace = useCallback(async () => {
    if (!ws) return;
    if (!window.confirm(`删除工作区「${ws.title}」？本地 JSON 会一并删除。`)) return;
    setBusy(true);
    setError('');
    try {
      await api.workspaces.remove(ws.id);
      const items = await loadList();
      const next = items[0];
      setWs(null);
      onSelect(next?.id || '', next?.title || '');
      if (next) await loadDetail(next.id);
    } catch (e) {
      setError(errorText(e));
    } finally {
      setBusy(false);
    }
  }, [ws, loadList, loadDetail, onSelect]);

  const grouped = useMemo(() => {
    const empty: Record<WorkspaceEntryKind, WorkspaceEntry[]> = {
      fact: [],
      attempt: [],
      reference: [],
    };
    for (const e of ws?.entries || []) empty[e.kind]?.push(e);
    return empty;
  }, [ws]);

  return (
    <Stack gap="lg">
      <div>
        <p className="eyebrow">题目工作区</p>
        <h1 className="page-title">把线索、尝试和资料留在一个本地文件里</h1>
        <p className="page-sub">
          工作区只存本地 JSON（`work/workspaces/`），可导出摘要 Markdown
          或可追溯的 Writeup 草稿；时间线由增删改自动生成且只读。
        </p>
      </div>

      {error && (
        <Alert color="orange" title="工作区">
          {error}
        </Alert>
      )}

      <Card withBorder radius="lg" className="workspace-card">
        <Stack gap="md">
          <Group justify="space-between" align="flex-end" wrap="wrap">
            <Group align="flex-end" wrap="wrap">
              <Select
                label="当前工作区"
                aria-label="当前工作区"
                data={options}
                value={currentId || null}
                onChange={(id) => {
                  const item = list.find((w) => w.id === id);
                  if (id) onSelect(id, item?.title || '');
                }}
                placeholder={list.length ? '选择工作区' : '还没有工作区'}
                w={330}
                searchable
                allowDeselect={false}
              />
              <Tooltip label="刷新列表与时间线">
                <ActionIcon
                  variant="default"
                  size="lg"
                  onClick={() => void refresh()}
                  aria-label="刷新工作区"
                >
                  <RefreshCw size={16} />
                </ActionIcon>
              </Tooltip>
            </Group>
            {ws && (
              <Group align="flex-end" wrap="wrap" gap={8}>
                <div>
                  <Text size="xs" fw={500} mb={4}>
                    导出内容
                  </Text>
                  <SegmentedControl
                    size="xs"
                    aria-label="导出内容"
                    value={exportMode}
                    onChange={(v) =>
                      setExportMode(v === 'writeup' ? 'writeup' : 'normal')
                    }
                    data={[
                      { label: '摘要', value: 'normal' },
                      { label: 'Writeup 草稿', value: 'writeup' },
                    ]}
                  />
                </div>
                <Button
                  component="a"
                  href={api.workspaces.exportUrl(ws.id, exportMode)}
                  download
                  leftSection={<Download size={16} />}
                  variant="light"
                >
                  {exportMode === 'writeup' ? '导出 Writeup' : '导出 Markdown'}
                </Button>
              </Group>
            )}
          </Group>

          <Divider />

          <Group align="flex-end" wrap="wrap">
            <TextInput
              label="新建工作区"
              aria-label="新建工作区标题"
              placeholder="例如：ctfshow Web 上传"
              value={newTitle}
              onChange={(e) => setNewTitle(e.currentTarget.value)}
              w={280}
            />
            <TextInput
              label="自定义 ID（可选）"
              aria-label="自定义工作区 ID"
              placeholder="字母数字 _ -，最多 64"
              value={newId}
              onChange={(e) => setNewId(e.currentTarget.value)}
              w={220}
            />
            <Button
              leftSection={<FolderPlus size={16} />}
              onClick={() => void create()}
              loading={busy}
              disabled={!newTitle.trim()}
            >
              创建
            </Button>
          </Group>
        </Stack>
      </Card>

      {loading && (
        <Group gap="xs">
          <Loader size={16} />
          <Text size="sm" c="dimmed">
            正在读取工作区…
          </Text>
        </Group>
      )}

      {!ws && !loading && (
        <Card withBorder>
          <Text size="sm" c="dimmed">
            还没有工作区。先在上面填标题创建一个，之后可添加事实、尝试和资料收藏。
          </Text>
        </Card>
      )}

      {ws && (
        <>
          <Card withBorder radius="lg">
            <Stack gap="md">
              <Group justify="space-between" align="flex-start" wrap="wrap">
                <div>
                  <Title order={3}>{ws.title}</Title>
                  <Text size="xs" c="dimmed" mt={4}>
                    ID：<code>{ws.id}</code> · 创建 {ws.created} · 更新 {ws.updated}
                  </Text>
                </div>
                <Group gap={8}>
                  <Badge variant="light">{STATUS_LABEL[ws.status]}</Badge>
                  <Badge variant="outline">{ws.entries.length} 条</Badge>
                </Group>
              </Group>
              <Group align="flex-end" wrap="wrap">
                <TextInput
                  label="标题"
                  aria-label="工作区标题"
                  value={titleEdit}
                  onChange={(e) => setTitleEdit(e.currentTarget.value)}
                  w={300}
                />
                <Select
                  label="状态"
                  aria-label="工作区状态"
                  data={Object.entries(STATUS_LABEL).map(([value, label]) => ({
                    value,
                    label,
                  }))}
                  value={statusEdit}
                  onChange={(v) => setStatusEdit((v as WorkspaceStatus) || 'open')}
                  allowDeselect={false}
                  w={150}
                />
                <Button variant="light" onClick={() => void saveMeta()} loading={busy}>
                  保存
                </Button>
                <Button
                  variant="subtle"
                  color="red"
                  leftSection={<Trash2 size={15} />}
                  onClick={() => void removeWorkspace()}
                >
                  删除工作区
                </Button>
              </Group>
            </Stack>
          </Card>

          <Card withBorder radius="lg">
            <Stack gap="md">
              <Group justify="space-between" align="center" wrap="wrap">
                <Title order={4}>添加条目</Title>
                <SegmentedControl
                  size="xs"
                  aria-label="条目类型"
                  value={kind}
                  onChange={(v) => setKind((v as WorkspaceEntryKind) || 'fact')}
                  data={[
                    { label: '事实', value: 'fact' },
                    { label: '尝试', value: 'attempt' },
                    { label: '资料收藏', value: 'reference' },
                  ]}
                />
              </Group>

              {kind === 'reference' && (
                <Group align="flex-end" wrap="wrap">
                  <TextInput
                    label="资料标题"
                    aria-label="资料标题"
                    value={refTitle}
                    onChange={(e) => setRefTitle(e.currentTarget.value)}
                    w={260}
                  />
                  <TextInput
                    label="kb 路径"
                    aria-label="资料 kb 路径"
                    placeholder="crypto/rsa.md"
                    value={refPath}
                    onChange={(e) => setRefPath(e.currentTarget.value)}
                    w={260}
                  />
                  <TextInput
                    label="章节锚点（可选）"
                    aria-label="资料章节锚点"
                    placeholder="一、识别信号"
                    value={refAnchor}
                    onChange={(e) => setRefAnchor(e.currentTarget.value)}
                    w={220}
                  />
                  <TextInput
                    label="或外部 URL"
                    aria-label="资料外部 URL"
                    placeholder="https://…"
                    value={refUrl}
                    onChange={(e) => setRefUrl(e.currentTarget.value)}
                    w={260}
                  />
                </Group>
              )}

              {kind === 'attempt' ? (
                <>
                  <Group align="flex-end" wrap="wrap">
                    <TextInput
                      label="方向"
                      aria-label="尝试方向"
                      placeholder="例如：短标签绕过"
                      value={direction}
                      onChange={(e) => setDirection(e.currentTarget.value)}
                      w={320}
                    />
                    <Select
                      label="尝试状态"
                      aria-label="尝试状态"
                      data={Object.entries(RESULT_LABEL).map(([value, label]) => ({
                        value,
                        label,
                      }))}
                      value={entryResult}
                      onChange={(v) =>
                        setEntryResult((v as AttemptResult) || 'pending')
                      }
                      allowDeselect={false}
                      w={160}
                    />
                  </Group>
                  <Textarea
                    label="结论"
                    aria-label="尝试结论"
                    placeholder="试过之后得到什么结论，是否有效"
                    autosize
                    minRows={2}
                    maxRows={6}
                    value={conclusion}
                    onChange={(e) => setConclusion(e.currentTarget.value)}
                  />
                  <Textarea
                    label="备注（可选）"
                    aria-label="尝试备注"
                    autosize
                    minRows={1}
                    maxRows={4}
                    value={entryText}
                    onChange={(e) => setEntryText(e.currentTarget.value)}
                  />
                </>
              ) : (
                <Textarea
                  label={kind === 'reference' ? '备注' : '内容'}
                  aria-label={kind === 'reference' ? '资料备注' : '条目内容'}
                  placeholder={
                    kind === 'fact'
                      ? '已经确定的事实，例如：过滤函数只替换一次'
                      : '为什么收藏这篇资料'
                  }
                  autosize
                  minRows={2}
                  maxRows={6}
                  value={entryText}
                  onChange={(e) => setEntryText(e.currentTarget.value)}
                />
              )}

              <Group justify="flex-end">
                <Button leftSection={<Plus size={16} />} onClick={() => void addEntry()}>
                  添加
                </Button>
              </Group>
            </Stack>
          </Card>

          <div className="workspace-grid">
            {(['fact', 'attempt', 'reference'] as WorkspaceEntryKind[]).map((k) => (
              <Card withBorder radius="lg" key={k}>
                <Group justify="space-between" mb="sm">
                  <Title order={5}>{KIND_LABEL[k]}</Title>
                  <Badge variant="outline">{grouped[k].length}</Badge>
                </Group>
                {!grouped[k].length ? (
                  <Text size="sm" c="dimmed">
                    暂无
                  </Text>
                ) : (
                  <Stack gap="sm">
                    {grouped[k].map((entry) => (
                      <div className="workspace-entry" key={entry.id}>
                        <Group justify="space-between" align="flex-start" wrap="wrap">
                          <div style={{ minWidth: 0 }}>
                            {k === 'reference' ? (
                              <>
                                <Text fw={600} size="sm">
                                  {entry.title || entry.path || entry.url || '资料'}
                                </Text>
                                {(entry.path || entry.url) && (
                                  <Text size="xs" c="dimmed" style={{ overflowWrap: 'anywhere' }}>
                                    {entry.path || entry.url}
                                    {entry.anchor ? `#${entry.anchor.replace(/^#/, '')}` : ''}
                                  </Text>
                                )}
                                {entry.text && <Text size="sm">{entry.text}</Text>}
                              </>
                            ) : k === 'attempt' ? (
                              <>
                                {entry.direction && (
                                  <Text size="sm" fw={600}>
                                    方向：{entry.direction}
                                  </Text>
                                )}
                                {entry.conclusion && (
                                  <Text size="sm">结论：{entry.conclusion}</Text>
                                )}
                                {entry.text && (
                                  <Text size="xs" c="dimmed">
                                    备注：{entry.text}
                                  </Text>
                                )}
                                {!entry.direction && !entry.conclusion && (
                                  <Text size="sm" style={{ whiteSpace: 'pre-wrap' }}>
                                    {entry.text}
                                  </Text>
                                )}
                              </>
                            ) : (
                              <Text size="sm" style={{ whiteSpace: 'pre-wrap' }}>
                                {entry.text}
                              </Text>
                            )}
                          </div>
                          <ActionIcon
                            variant="subtle"
                            color="red"
                            aria-label={`删除条目 ${entry.id}`}
                            onClick={() => void removeEntry(entry)}
                          >
                            <Trash2 size={14} />
                          </ActionIcon>
                        </Group>
                        {k === 'attempt' && (
                          <Select
                            size="xs"
                            mt={6}
                            aria-label={`尝试状态 ${entry.id}`}
                            data={Object.entries(RESULT_LABEL).map(([value, label]) => ({
                              value,
                              label,
                            }))}
                            value={entry.result || 'pending'}
                            onChange={(v) => v && void changeResult(entry, v)}
                            allowDeselect={false}
                            w={140}
                          />
                        )}
                        {entry.report && (
                          <Accordion variant="contained" mt="sm">
                            <Accordion.Item value="report">
                              <Accordion.Control>附件分析报告</Accordion.Control>
                              <Accordion.Panel>
                                <AttachmentReportView report={entry.report} compact />
                              </Accordion.Panel>
                            </Accordion.Item>
                          </Accordion>
                        )}
                        <Text size="xs" c="dimmed" mt={6}>
                          {entry.created}
                        </Text>
                      </div>
                    ))}
                  </Stack>
                )}
              </Card>
            ))}
          </div>

          <Card withBorder radius="lg">
            <Title order={4} mb="sm">
              时间线 <Text component="span" c="dimmed" size="sm">只读</Text>
            </Title>
            <Stack gap={4}>
              {ws.timeline.map((ev, i) => (
                <Group key={`${ev.ts}-${i}`} gap="sm" align="flex-start" wrap="nowrap">
                  <Text size="xs" c="dimmed" style={{ whiteSpace: 'nowrap' }}>
                    {ev.ts}
                  </Text>
                  <Badge size="xs" variant="outline">
                    {ev.kind}
                  </Badge>
                  <Text size="sm">{ev.summary}</Text>
                </Group>
              ))}
            </Stack>
          </Card>
        </>
      )}
    </Stack>
  );
}
