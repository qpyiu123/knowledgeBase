import {
  Alert,
  Badge,
  Button,
  Card,
  Checkbox,
  Center,
  Divider,
  Group,
  Loader,
  SegmentedControl,
  Select,
  Stack,
  Text,
  Textarea,
  Title,
  Tooltip,
} from '@mantine/core';
import {
  ArrowUpRight,
  BookmarkPlus,
  Check,
  Copy,
  Search,
  Sparkles,
  Square,
  ThumbsDown,
  ThumbsUp,
} from 'lucide-react';
import { useCallback, useEffect, useMemo, useRef, useState } from 'react';
import Md from '../components/Md';
import AttachmentPanel from '../components/AttachmentPanel';
import ConditionDetails from '../components/ConditionDetails';
import FocusReading from '../components/FocusReading';
import WorkspacePicker, {
  type PickedWorkspace,
} from '../components/WorkspacePicker';
import { api, ask } from '../api';
import type { DocType, Hit, SearchResp } from '../types';

const MODES = [
  { value: 'direct', label: '直接搜索' },
  { value: 'ask', label: '问模型' },
];

const MODE_DESC: Record<string, string> = {
  direct: '先查关键词，可选择补充语义相近的资料。',
  ask: '先检索相关资料，再让本地模型给出思路和脚本。',
};

const FEEDBACK_LABEL: Record<string, string> = {
  useful: '有用',
  useless: '无用',
  adopted: '已采用',
};

const STARTERS = [
  { t: '按特征查方法', d: '把报错、过滤规则或代码片段放在一起搜索。', q: 'PHP str_replace 过滤关键字 绕过' },
  { t: '遇到陌生函数', d: '查用法、参数、版本差异和题解中的实例。', q: 'Python 沙箱逃逸 __class__ 链' },
  { t: '找相似题目', d: '用关键机制或题目中的限制描述问题。', q: 'RSA 已知部分素数 分解 n' },
];

/** 摘要清洗：去掉 Markdown 记号，避免结果卡片里一片 ## 和链接。 */
function cleanSnippet(s: string, title?: string): string {
  let t = String(s || '');
  if (title) {
    const ttl = title.trim();
    t = t
      .split('\n')
      .filter((ln) => ln.trim().replace(/^#+\s*/, '') !== ttl)
      .join('\n');
  }
  return t
    .replace(/^#{1,6}\s+/gm, '')
    .replace(/^\s*>\s?/gm, '')
    .replace(/!\[([^\]]*)\]\([^)]*\)/g, '[图：$1]')
    .replace(/\[([^\]]+)\]\([^)]*\)/g, '$1')
    .replace(/\*\*(.+?)\*\*/g, '$1')
    .replace(/`([^`]+)`/g, '$1')
    .replace(/^\s*[-*+]\s+/gm, '· ')
    .replace(/\n{3,}/g, '\n\n')
    .trim();
}

export default function SearchPage({
  category,
  onOpenDoc,
  docs,
  workspaceId,
  workspaceTitle,
  onSelectWorkspace,
  attachmentMaxBytes,
}: {
  category: string;
  onOpenDoc: (path: string, title?: string) => void;
  docs: number;
  workspaceId?: string;
  workspaceTitle?: string;
  onSelectWorkspace?: (id: string, title: string) => void;
  attachmentMaxBytes?: number;
}) {
  const [q, setQ] = useState('');
  const [mode, setMode] = useState('direct');
  const [docType, setDocType] = useState<'all' | DocType>('all');
  const [busy, setBusy] = useState(false);
  const [phase, setPhase] = useState('');
  const [error, setError] = useState('');
  const [hits, setHits] = useState<Hit[]>([]);
  const [graph, setGraph] = useState<Hit[]>([]);
  const [counts, setCounts] = useState<{ topic: number; card: number; method?: number } | null>(null);
  const [semantic, setSemantic] = useState(false);
  const [withConditions, setWithConditions] = useState(false);
  const [withFocus, setWithFocus] = useState(false);
  const [focus, setFocus] = useState<SearchResp['focus']>();
  const selectedWorkspace = useRef(workspaceId);
  selectedWorkspace.current = workspaceId;
  const [supplementing, setSupplementing] = useState(false);
  const searchRequest = useRef(0);
  const searchAbort = useRef<AbortController | null>(null);
  const [resultQuery, setResultQuery] = useState('');
  const [feedback, setFeedback] = useState<Record<string, string>>({});
  const [savedToWorkspace, setSavedToWorkspace] = useState<Record<string, boolean>>({});
  const [ms, setMs] = useState<number | null>(null);
  const [searched, setSearched] = useState(false);
  const [answer, setAnswer] = useState('');
  const [answerOpen, setAnswerOpen] = useState(false);
  const [elapsed, setElapsed] = useState(0);
  const [doneInfo, setDoneInfo] = useState('');
  const [copied, setCopied] = useState(false);
  const [pickerHit, setPickerHit] = useState<Hit | null>(null);
  const [defaultPickerOpen, setDefaultPickerOpen] = useState(false);
  const ta = useRef<HTMLTextAreaElement>(null);
  const ctrl = useRef<AbortController | null>(null);
  const t0 = useRef(0);

  useEffect(() => {
    const onKey = (e: KeyboardEvent) => {
      if ((e.ctrlKey || e.metaKey) && e.key.toLowerCase() === 'k') {
        e.preventDefault();
        ta.current?.focus();
        ta.current?.select();
      }
    };
    window.addEventListener('keydown', onKey);
    return () => window.removeEventListener('keydown', onKey);
  }, []);

  const runSearch = useCallback(async (override?: string) => {
    const text = (override ?? q).trim();
    if (!text) return;
    const request = ++searchRequest.current;
    searchAbort.current?.abort();
    const searchController = new AbortController();
    searchAbort.current = searchController;
    setSupplementing(false);
    setQ(text);
    setBusy(true);
    setError('');
    setPhase('正在查找资料…');
    setSearched(true);
    setAnswerOpen(false);
    setAnswer('');
    setDoneInfo('');
    setFeedback({});
    try {
      const r = await api.search(
        text,
        10,
        category,
        docType === 'all' ? null : docType,
        'fts',
        searchController.signal,
        withConditions,
        withFocus ? workspaceId : undefined,
      );
      if (request !== searchRequest.current) return;
      if (r.error) setError(r.error);
      setHits(r.hits || []);
      setGraph(r.graph || []);
      setCounts(r.counts || null);
      setFocus(r.focus?.workspace_id === selectedWorkspace.current ? r.focus : undefined);
      setResultQuery(text);
      setMs(r.ms ?? null);
      setBusy(false);
      setPhase('');
      if (semantic) {
        setSupplementing(true);
        try {
          const extra = await api.search(text, 10, category,
            docType === 'all' ? null : docType, 'hybrid', searchController.signal, withConditions);
          if (request !== searchRequest.current) return;
          if (extra.error) throw new Error(extra.error);
          const have = new Set((r.hits || []).map((h) => h.path));
          const combined = [...(r.hits || []), ...(extra.hits || []).filter((h) => !have.has(h.path))];
          setHits(combined);
          setCounts(combined.reduce((total, hit) => {
            const type = hit.doc_type || 'topic';
            total[type] = (total[type] || 0) + 1;
            return total;
          }, { topic: 0, card: 0, method: 0 }));
          setGraph(extra.graph || []);
        } catch (e) {
          if (request === searchRequest.current && (e as Error).name !== 'AbortError') {
            setError(`语义补充失败：${String((e as Error).message || e)}。关键词结果已保留。`);
          }
        }
      }
    } catch (e) {
      if (request === searchRequest.current && (e as Error).name !== 'AbortError') {
        setError(String((e as Error).message || e));
      }
    } finally {
      if (request === searchRequest.current) {
        setBusy(false);
        setPhase('');
        setSupplementing(false);
      }
    }
  }, [q, category, docType, semantic, withConditions, withFocus, workspaceId]);

  useEffect(() => () => {
    ++searchRequest.current;
    searchAbort.current?.abort();
  }, []);

  const runAsk = useCallback(async (override?: string) => {
    const text = (override ?? q).trim();
    if (!text) return;
    ++searchRequest.current;
    searchAbort.current?.abort();
    setSupplementing(false);
    setQ(text);
    setBusy(true);
    setError('');
    setAnswerOpen(true);
    setAnswer('');
    setDoneInfo('');
    setPhase('正在检索资料…');
    setFeedback({});
    t0.current = Date.now();
    ctrl.current?.abort();
    const c = new AbortController();
    ctrl.current = c;
    try {
      const r = await api.search(
        text,
        3,
        category,
        docType === 'all' ? null : docType,
        'hybrid',
        c.signal,
        true,
        withFocus ? workspaceId : undefined,
      );
      const selected = [...(r.focus?.hits || []), ...(r.hits || [])]
        .filter((hit, index, all) => all.findIndex((h) => h.path === hit.path) === index)
        .slice(0, 3);
      setHits(selected);
      setFocus(r.focus);
      setGraph(r.graph || []);
      setCounts(r.counts || null);
      setResultQuery(text);
      setMs(r.ms ?? null);
      setSearched(true);
      const paths = selected.map((h) => h.path);
      if (!paths.length) {
        setAnswer('> 没有检索到可用的资料，换个关键词试试。');
        return;
      }
      setPhase('模型正在整理思路…');
      let acc = '';
      await ask(
        text,
        paths,
        {
          onToken: (t) => {
            acc += t;
            setAnswer(acc);
            setElapsed((Date.now() - t0.current) / 1000);
          },
          onError: (m) => {
            setError(m);
            if (!acc.trim()) setAnswer('> 未收到模型内容，请查看上方提示。');
          },
          onDone: (info) => {
            setDoneInfo(info);
            setElapsed((Date.now() - t0.current) / 1000);
          },
          onNotice: (m) => setError(m),
        },
        c.signal,
        workspaceId,
        Object.fromEntries(selected.filter((hit) => hit.section).map((hit) => [hit.path, hit.section!])),
      );
      if (!acc.trim()) setAnswer('> 模型没有返回内容。确认本地模型已启动。');
    } catch (e) {
      if ((e as Error).name === 'AbortError') {
        setAnswer((old) => old.trim() ? old : '> 已取消本次解释。');
        setDoneInfo((old) => old || '已取消');
      } else {
        setError(String((e as Error).message || e));
        setAnswer('> 生成中断。');
      }
    } finally {
      setBusy(false);
      setPhase('');
    }
  }, [q, category, docType, workspaceId, withFocus]);

  const run = useCallback(() => {
    if (mode === 'ask') runAsk();
    else runSearch();
  }, [mode, runAsk, runSearch]);

  const stop = useCallback(() => {
    ctrl.current?.abort();
    setPhase('正在取消…');
    setError('');
  }, []);

  const sendFeedback = useCallback(
    async (h: Hit, verdict: 'useful' | 'useless' | 'adopted') => {
      if (!resultQuery) return;
      try {
        const r = await api.feedback(resultQuery, h.path, verdict);
        if (r.error || r.ok === false) throw new Error(r.error || '反馈保存失败');
        setFeedback((m) => ({ ...m, [h.path]: verdict }));
      } catch (e) {
        setError(`反馈未保存：${String((e as Error).message || e)}`);
      }
    },
    [resultQuery],
  );

  const refs = useMemo(() => hits.slice(0, 3), [hits]);

  const saveHitToWorkspace = useCallback(
    async (h: Hit, ws: PickedWorkspace) => {
      // 图谱展开命中优先用 doc_id；没有时退回 path。
      const target = h.doc_id || h.path;
      if (!target) throw new Error('这条命中没有可收藏的文档路径');
      await api.workspaces.addEntry(ws.id, {
        kind: 'reference',
        title: h.title,
        path: target,
        text: '从搜索结果收藏',
      });
      onSelectWorkspace?.(ws.id, ws.title);
      setSavedToWorkspace((m) => ({ ...m, [target]: true }));
    },
    [onSelectWorkspace],
  );

  // #q=关键词 / #ask=问题 自动执行（方便分享与测试）
  useEffect(() => {
    const h = decodeURIComponent(location.hash.replace(/^#/, ''));
    if (h.startsWith('ask=')) {
      const text = h.slice(4);
      setQ(text);
      setMode('ask');
      void runAsk(text);
      return;
    }
    if (h.startsWith('q=')) {
      const text = h.slice(2);
      setQ(text);
      void runSearch(text);
    }
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, []);

  return (
    <Stack gap="lg">
      <div>
        <p className="eyebrow">搜索与助手</p>
        <h1 className="page-title">从线索找到下一步</h1>
        <p className="page-sub">
          输入题面特征、函数名、报错信息，或描述已经试过的方法。
          {category ? ` 当前只看「${category}」方向。` : ''}
        </p>
        <Group gap={8} mt={6} wrap="wrap">
          <Text size="xs" c="dimmed">
            {workspaceId
              ? `默认工作区：${workspaceTitle || workspaceId}`
              : '尚未选择默认工作区；问模型与收藏会先让你选择或新建。'}
          </Text>
          {onSelectWorkspace && (
            <>
              <Button
                variant="subtle"
                size="compact-xs"
                onClick={() => setDefaultPickerOpen(true)}
              >
                {workspaceId ? '切换' : '选择工作区'}
              </Button>
              {workspaceId && (
                <Button
                  variant="subtle"
                  size="compact-xs"
                  color="gray"
                  onClick={() => onSelectWorkspace('', '')}
                >
                  清除
                </Button>
              )}
            </>
          )}
        </Group>
      </div>

      <Card withBorder radius="lg" className="search-card">
        <Stack gap="md">
          <Textarea
            ref={ta}
            aria-label="搜索内容"
            placeholder="例如：PHP str_replace 过滤了关键字，还能从哪些条件判断过滤方式？"
            autosize
            minRows={3}
            maxRows={12}
            value={q}
            onChange={(e) => setQ(e.currentTarget.value)}
            onKeyDown={(e) => {
              if ((e.ctrlKey || e.metaKey) && e.key === 'Enter') {
                e.preventDefault();
                run();
              }
            }}
          />
          <Group justify="space-between" align="flex-end" wrap="wrap">
            <Group gap="md" align="flex-end" wrap="wrap">
              <Select
                label="使用方式"
                aria-label="使用方式"
                data={MODES}
                value={mode}
                onChange={(v) => setMode(v || 'direct')}
                w={150}
                allowDeselect={false}
              />
              <div>
                <Text size="xs" fw={500} mb={4}>
                  资料类型
                </Text>
                <SegmentedControl
                  size="xs"
                  aria-label="资料类型"
                  value={docType}
                  onChange={(v) => setDocType((v as 'all' | DocType) || 'all')}
                  data={[
                    { label: '全部', value: 'all' },
                    { label: '专题', value: 'topic' },
                    { label: '比赛卡片', value: 'card' },
                    { label: '方法卡', value: 'method' },
                  ]}
                />
              </div>
              {mode === 'direct' && (
                <Checkbox label="补充语义相近资料" checked={semantic}
                  onChange={(event) => setSemantic(event.currentTarget.checked)} />
              )}
              {mode === 'direct' && <Checkbox label="显示条件关联" checked={withConditions}
                onChange={(event) => setWithConditions(event.currentTarget.checked)} />}
              {workspaceId && <Checkbox label="参考当前卡点" checked={withFocus}
                onChange={(event) => setWithFocus(event.currentTarget.checked)} />}
            </Group>
            <Group gap={8}>
              {busy && mode === 'ask' ? (
                <Button
                  variant="light"
                  color="gray"
                  leftSection={<Square size={14} />}
                  onClick={stop}
                  disabled={phase === '正在取消…'}
                >
                  取消解释
                </Button>
              ) : (
                <Button
                  leftSection={mode === 'ask' ? <Sparkles size={16} /> : <Search size={16} />}
                  onClick={run}
                  disabled={busy || !q.trim()}
                >
                  {mode === 'ask' ? '提问' : '查找'}
                </Button>
              )}
            </Group>
          </Group>
          <Group justify="space-between">
            <Text size="sm" c="dimmed">
              {MODE_DESC[mode]}
              <span className="desktop-hint" style={{ marginLeft: 10 }}>
                Ctrl + Enter 提交
              </span>
            </Text>
          </Group>
        </Stack>
      </Card>

      <AttachmentPanel
        maxBytes={attachmentMaxBytes}
        workspaceId={workspaceId}
        workspaceTitle={workspaceTitle}
        onSelectWorkspace={onSelectWorkspace}
      />

      {(busy || supplementing) && (
        <Group gap="xs">
          <Loader size={16} />
          <Text size="sm" c="dimmed">
            {supplementing ? '正在补充语义资料，关键词结果可先阅读…' : phase}
            {elapsed > 0 && mode === 'ask' ? ` · ${elapsed.toFixed(1)} 秒` : ''}
          </Text>
        </Group>
      )}

      {error && (
        <Alert color="orange" title="本次请求">
          {error}
        </Alert>
      )}

      {answerOpen && (
        <Card withBorder className="answer-card">
          <Group justify="space-between" mb="md">
            <Group gap={10}>
              <Badge variant="light">解题提示</Badge>
              {elapsed > 0 && (
                <Text size="xs" c="dimmed">
                  {elapsed.toFixed(1)} 秒
                </Text>
              )}
              {doneInfo && (
                <Text size="xs" c="dimmed">
                  {doneInfo}
                </Text>
              )}
            </Group>
            <Tooltip label="复制回答">
              <Button
                variant="subtle"
                size="compact-sm"
                leftSection={<Copy size={14} />}
                onClick={() =>
                  navigator.clipboard.writeText(answer).then(() => {
                    setCopied(true);
                    window.setTimeout(() => setCopied(false), 1400);
                  })
                }
              >
                {copied ? '已复制' : '复制'}
              </Button>
            </Tooltip>
          </Group>
          <div className="answer-body">
            {answer ? (
              <Md text={answer} />
            ) : (
              <Text size="sm" c="dimmed">
                {phase || '等待模型输出…'}
              </Text>
            )}
          </div>
          {refs.length > 0 && answer && (
            <>
              <Divider my="md" />
              <Text size="sm" fw={600} mb="xs">
                引用资料
              </Text>
              <Stack gap={4}>
                {refs.map((r, i) => (
                  <Button
                    key={r.path}
                    variant="subtle"
                    size="compact-sm"
                    justify="flex-start"
                    onClick={() => onOpenDoc(r.path, r.title)}
                  >
                    [{i + 1}] {r.title}
                  </Button>
                ))}
              </Stack>
            </>
          )}
        </Card>
      )}

      {searched && mode === 'direct' && (
        <div>
          <Group justify="space-between" mb="md" align="baseline">
            <Title order={3}>
              相关资料{' '}
              <Text component="span" c="dimmed" size="sm">
                {hits.length} 条
              </Text>
            </Title>
            <Group gap="sm">
              {focus && focus.workspace_id === workspaceId && <Button variant="subtle" size="compact-xs"
                onClick={() => document.getElementById('focus-reading')?.scrollIntoView({ behavior: 'smooth' })}>
                卡点资料 {focus.hits.length}
              </Button>}
              {counts && (counts.topic + counts.card + (counts.method || 0) > 0) && (
                <Text size="xs" c="dimmed">
                  专题 {counts.topic} · 比赛卡片 {counts.card}
                  {counts.method ? ` · 方法卡 ${counts.method}` : ''}
                </Text>
              )}
              {ms != null && (
                <Text size="xs" c="dimmed">
                  用时 {ms} ms
                </Text>
              )}
            </Group>
          </Group>
          <div className="hit-list">
            {hits.map((h, i) => {
              const snip = cleanSnippet(h.snippet, h.title);
              return (
                <article className="hit" key={h.path + '-' + i}>
                  <Group gap={6} mb={8} wrap="wrap">
                    <Badge size="xs" variant="light" color="brand">
                      {h.category || '资料'}
                    </Badge>
                    <Badge
                      size="xs"
                      variant="outline"
                      color={h.doc_type === 'card' ? 'grape' : 'teal'}
                    >
                      {h.kind_label || h.doc_type_label || (h.doc_type === 'card' ? '比赛卡片' : '专题文档')}
                    </Badge>
                    {h.graph_via && (
                      <Badge size="xs" variant="outline">
                        图谱 · {h.graph_via}
                      </Badge>
                    )}
                    {h.score ? (
                      <Badge size="xs" variant="default">
                        {Number(h.score).toFixed(4)}
                      </Badge>
                    ) : null}
                  </Group>
                  <button
                    className="hit-title"
                    type="button"
                    onClick={() => onOpenDoc(h.path, h.title)}
                  >
                    {h.title}
                  </button>
                  {snip && (
                    <p className="hit-snippet">
                      {snip.length > 260 ? snip.slice(0, 260) + '…' : snip}
                    </p>
                  )}
                  {h.sources?.length ? (
                    <Group gap="xs" my="xs">
                      <Text size="xs" c="dimmed">来源</Text>
                      {h.sources.map((source) => source.external ? (
                        <Button key={source.path} component="a" href={source.path} target="_blank"
                          rel="noopener noreferrer" variant="subtle" size="compact-xs">查看来源</Button>
                      ) : (
                        <Button key={source.path} variant="subtle" size="compact-xs"
                          onClick={() => onOpenDoc(source.path)}>{source.path.split('/').pop()}</Button>
                      ))}
                    </Group>
                  ) : null}
                  {h.methods?.length ? <Group gap="xs" my="xs">
                    <Text size="xs" c="dimmed">相关方法</Text>
                    {h.methods.map((method) => <Button key={method.path} size="compact-xs"
                      variant="subtle" onClick={() => onOpenDoc(method.path, method.title)}>{method.title}</Button>)}
                  </Group> : null}
                  {h.scripts?.length ? (
                    <Group gap="xs" my="xs">
                      {h.scripts.map((script) => (
                        <Button key={script.path} variant="light" size="compact-xs"
                          onClick={() => onOpenDoc(script.path, script.title)}>代码 {script.title}</Button>
                      ))}
                    </Group>
                  ) : null}
                  {(h.match?.labels?.length || h.match?.terms?.length || h.section) && (
                    <div className="hit-why">
                      {h.match?.labels?.length ? (
                        <Text size="xs" c="dimmed">
                          命中原因：{h.match.labels.join(' + ')}
                        </Text>
                      ) : null}
                      {h.section ? (
                        <Text size="xs" c="dimmed">
                          命中章节：{h.section}
                        </Text>
                      ) : null}
                      {h.match?.terms?.length ? (
                        <Text size="xs" c="dimmed">
                          命中词：{h.match.terms.join(' · ')}
                        </Text>
                      ) : null}
                    </div>
                  )}
                  <ConditionDetails app={h.applicability} onOpenDoc={onOpenDoc} />
                  <Group justify="space-between" mt={10} wrap="wrap" gap={8}>
                    <span className="hit-path">{h.path}</span>
                    <Group gap={4}>
                      <Button
                        variant="subtle"
                        size="compact-sm"
                        rightSection={<ArrowUpRight size={14} />}
                        onClick={() => onOpenDoc(h.path, h.title)}
                      >
                        阅读资料
                      </Button>
                      <Button
                        variant="subtle"
                        size="compact-sm"
                        onClick={() => {
                          const question = `结合《${h.title}》说明这类题的判断依据和解题步骤`;
                          setQ(question);
                          setMode('ask');
                          void runAsk(question);
                        }}
                      >
                        问模型
                      </Button>
                      <Tooltip
                        label={
                          workspaceId
                            ? `收藏到「${workspaceTitle || workspaceId}」，可另选或新建`
                            : '选择已有工作区或输入标题新建'
                        }
                      >
                        <Button
                          variant={
                            savedToWorkspace[h.doc_id || h.path] ? 'light' : 'subtle'
                          }
                          size="compact-sm"
                          leftSection={<BookmarkPlus size={14} />}
                          disabled={
                            !(h.doc_id || h.path) ||
                            savedToWorkspace[h.doc_id || h.path]
                          }
                          onClick={() => setPickerHit(h)}
                        >
                          {savedToWorkspace[h.doc_id || h.path]
                            ? '已收藏'
                            : '收藏到题目工作区'}
                        </Button>
                      </Tooltip>
                    </Group>
                  </Group>
                  <Group justify="space-between" mt={6} wrap="wrap" gap={8}>
                    <Group gap={4}>
                      <Button
                        variant={feedback[h.path] === 'useful' ? 'light' : 'subtle'}
                        size="compact-sm"
                        leftSection={<ThumbsUp size={13} />}
                        onClick={() => void sendFeedback(h, 'useful')}
                      >
                        有用
                      </Button>
                      <Button
                        variant={feedback[h.path] === 'useless' ? 'light' : 'subtle'}
                        size="compact-sm"
                        leftSection={<ThumbsDown size={13} />}
                        onClick={() => void sendFeedback(h, 'useless')}
                      >
                        无用
                      </Button>
                      <Button
                        variant={feedback[h.path] === 'adopted' ? 'light' : 'subtle'}
                        size="compact-sm"
                        leftSection={<Check size={13} />}
                        onClick={() => void sendFeedback(h, 'adopted')}
                      >
                        采用
                      </Button>
                    </Group>
                    {feedback[h.path] && (
                      <Text size="xs" c="teal">
                        已记录：{FEEDBACK_LABEL[feedback[h.path]] || feedback[h.path]}
                      </Text>
                    )}
                  </Group>
                </article>
              );
            })}
            {!busy && !hits.length && (
              <Center py={56} style={{ flexDirection: 'column', gap: 8 }}>
                <Search size={26} opacity={0.4} />
                <Text fw={600}>没有找到相关资料</Text>
                <Text size="sm" c="dimmed">
                  试试函数名、题目特征或更短的关键词。
                </Text>
              </Center>
            )}
          </div>
          {graph.length > 0 && (
            <div style={{ marginTop: 28 }}>
              <Group justify="space-between" mb="xs" align="baseline">
                <Title order={4}>
                  关联阅读{' '}
                  <Text component="span" c="dimmed" size="sm">
                    {graph.length} 条
                  </Text>
                </Title>
                <Text size="xs" c="dimmed">
                  来自图谱关系，未参与主排名
                </Text>
              </Group>
              <Stack gap={0}>
                {graph.map((h, i) => (
                  <Group
                    key={h.path + '-related-' + i}
                    justify="space-between"
                    wrap="wrap"
                    gap={8}
                    py={6}
                    style={{ borderBottom: '1px solid var(--border)' }}
                  >
                    <Button
                      variant="subtle"
                      size="compact-sm"
                      justify="flex-start"
                      onClick={() => onOpenDoc(h.path, h.title)}
                    >
                      {h.title}
                    </Button>
                    <Group gap={6}>
                      <Badge size="xs" variant="outline">
                        图谱 · {h.graph_via || '关联'}
                      </Badge>
                      <Text size="xs" c="dimmed">
                        {h.path}
                      </Text>
                    </Group>
                  </Group>
                ))}
              </Stack>
            </div>
          )}
        </div>
      )}

      {!searched && (
        <div className="starter-grid">
          {STARTERS.map((s) => (
            <button
              className="starter"
              key={s.t}
              type="button"
              onClick={() => {
                setQ(s.q);
                setMode('direct');
                void runSearch(s.q);
              }}
            >
              <b>{s.t}</b>
              <p>{s.d}</p>
              <em>{s.q} →</em>
            </button>
          ))}
        </div>
      )}

      {!searched && docs > 0 && (
        <Text size="xs" c="dimmed" ta="center">
          知识库共 {docs} 篇 · 支持 Ctrl + K 快速聚焦
        </Text>
      )}

      <FocusReading focus={focus?.workspace_id === workspaceId ? focus : undefined} onOpenDoc={onOpenDoc} />

      <WorkspacePicker
        opened={pickerHit !== null}
        onClose={() => setPickerHit(null)}
        defaultId={workspaceId}
        hint={
          pickerHit
            ? `收藏《${pickerHit.title}》到题目工作区；选择已有工作区或输入标题新建。`
            : undefined
        }
        onPicked={async (ws) => {
          if (pickerHit) await saveHitToWorkspace(pickerHit, ws);
          setPickerHit(null);
        }}
      />

      <WorkspacePicker
        opened={defaultPickerOpen}
        onClose={() => setDefaultPickerOpen(false)}
        defaultId={workspaceId}
        hint="选择默认工作区后，问模型会带上该题已确认的事实与失败尝试。"
        onPicked={async (ws) => {
          onSelectWorkspace?.(ws.id, ws.title);
          setDefaultPickerOpen(false);
        }}
      />
    </Stack>
  );
}
