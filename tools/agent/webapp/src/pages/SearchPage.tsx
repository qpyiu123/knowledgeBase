import {
  Alert,
  Badge,
  Button,
  Card,
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
import { api, ask } from '../api';
import type { DocType, Hit } from '../types';

const MODES = [
  { value: 'direct', label: '直接搜索' },
  { value: 'ask', label: '问模型' },
];

const MODE_DESC: Record<string, string> = {
  direct: '按关键词和语义查找资料，只看知识库。',
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
}: {
  category: string;
  onOpenDoc: (path: string, title?: string) => void;
  docs: number;
}) {
  const [q, setQ] = useState('');
  const [mode, setMode] = useState('direct');
  const [docType, setDocType] = useState<'all' | DocType>('all');
  const [busy, setBusy] = useState(false);
  const [phase, setPhase] = useState('');
  const [error, setError] = useState('');
  const [hits, setHits] = useState<Hit[]>([]);
  const [graph, setGraph] = useState<Hit[]>([]);
  const [counts, setCounts] = useState<{ topic: number; card: number } | null>(null);
  const [resultQuery, setResultQuery] = useState('');
  const [feedback, setFeedback] = useState<Record<string, string>>({});
  const [ms, setMs] = useState<number | null>(null);
  const [searched, setSearched] = useState(false);
  const [answer, setAnswer] = useState('');
  const [answerOpen, setAnswerOpen] = useState(false);
  const [elapsed, setElapsed] = useState(0);
  const [doneInfo, setDoneInfo] = useState('');
  const [copied, setCopied] = useState(false);
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
      );
      if (r.error) setError(r.error);
      setHits(r.hits || []);
      setGraph(r.graph || []);
      setCounts(r.counts || null);
      setResultQuery(text);
      setMs(r.ms ?? null);
    } catch (e) {
      setError(String((e as Error).message || e));
    } finally {
      setBusy(false);
      setPhase('');
    }
  }, [q, category, docType]);

  const runAsk = useCallback(async (override?: string) => {
    const text = (override ?? q).trim();
    if (!text) return;
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
      );
      setHits(r.hits || []);
      setGraph(r.graph || []);
      setCounts(r.counts || null);
      setResultQuery(text);
      setMs(r.ms ?? null);
      setSearched(true);
      const paths = (r.hits || []).map((h) => h.path);
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
        },
        c.signal,
      );
      if (!acc.trim()) setAnswer('> 模型没有返回内容。确认本地模型已启动。');
    } catch (e) {
      if ((e as Error).name !== 'AbortError') {
        setError(String((e as Error).message || e));
        setAnswer('> 生成中断。');
      }
    } finally {
      setBusy(false);
      setPhase('');
    }
  }, [q, category, docType]);

  const run = useCallback(() => {
    if (mode === 'ask') runAsk();
    else runSearch();
  }, [mode, runAsk, runSearch]);

  const stop = useCallback(() => {
    ctrl.current?.abort();
    setBusy(false);
    setPhase('');
    setError('已停止接收本次回答；本地连接已断开，后端模型可能仍在收尾。');
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
                  ]}
                />
              </div>
            </Group>
            <Group gap={8}>
              {busy && mode === 'ask' ? (
                <Button
                  variant="light"
                  color="gray"
                  leftSection={<Square size={14} />}
                  onClick={stop}
                >
                  停止接收
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

      {busy && (
        <Group gap="xs">
          <Loader size={16} />
          <Text size="sm" c="dimmed">
            {phase}
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
              {counts && (counts.topic + counts.card > 0) && (
                <Text size="xs" c="dimmed">
                  专题 {counts.topic} · 比赛卡片 {counts.card}
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
                      {h.doc_type_label || (h.doc_type === 'card' ? '比赛卡片' : '专题文档')}
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
    </Stack>
  );
}
