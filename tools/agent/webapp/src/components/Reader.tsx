import { Button, Code, Drawer, Group, Loader, ScrollArea, Stack, Text } from '@mantine/core';
import { useEffect, useMemo, useRef, useState } from 'react';
import { api } from '../api';
import Md from './Md';
import type { CodeResp, DocumentResp } from '../types';

export type ReaderTarget = { path: string; title?: string } | null;

export default function Reader({
  target,
  onClose,
}: {
  target: ReaderTarget;
  onClose: () => void;
}) {
  const [body, setBody] = useState('');
  const [active, setActive] = useState<ReaderTarget>(target);
  const [info, setInfo] = useState<DocumentResp | null>(null);
  const [code, setCode] = useState<CodeResp | null>(null);
  const [copied, setCopied] = useState(false);
  const [copyError, setCopyError] = useState('');
  const [error, setError] = useState('');
  const [loading, setLoading] = useState(false);
  const [heads, setHeads] = useState<{ id: string; text: string; lv: number }[]>([]);
  const docRef = useRef<HTMLDivElement>(null);
  const viewport = useRef<HTMLDivElement>(null);
  const isCode = !!active && !active.path.endsWith('.md');

  useEffect(() => setActive(target), [target]);

  useEffect(() => {
    if (!active) return;
    let alive = true;
    setLoading(true);
    setError('');
    setBody('');
    setHeads([]);
    setInfo(null);
    setCode(null);
    setCopied(false);
    setCopyError('');
    const request = isCode ? api.code(active.path) : api.doc(active.path);
    request
      .then((r) => {
        if (!alive) return;
        if ('error' in r && r.error) {
          setError(r.error);
          return;
        }
        if (isCode) {
          setCode(r as CodeResp);
        } else {
          setInfo(r as DocumentResp);
          setBody(String(r.body || '').replace(/^---\r?\n[\s\S]*?\r?\n---\r?\n/, ''));
        }
      })
      .catch((e) => alive && setError(String(e.message || e)))
      .finally(() => alive && setLoading(false));
    return () => {
      alive = false;
    };
  }, [active, isCode]);

  // 渲染完收集标题做目录
  useEffect(() => {
    if (!docRef.current) return;
    const els = docRef.current.querySelectorAll<HTMLElement>('h1, h2, h3');
    setHeads(
      Array.from(els)
        .filter((el) => el.id)
        .map((el) => ({
          id: el.id,
          text: el.textContent || '',
          lv: Number(el.tagName[1]),
        })),
    );
  }, [body]);

  const firstH1 = useMemo(() => heads.find((h) => h.lv === 1)?.text, [heads]);
  const raw = firstH1 || active?.title || active?.path || '';
  const title = String(raw).replace(/\.md$/i, '');
  const showToc = !isCode && heads.length > 1;

  return (
    <Drawer
      opened={!!target}
      onClose={onClose}
      position="right"
      size={920}
      withCloseButton
      keepMounted={false}
      title={
        <Text fw={650} size="md" style={{ overflowWrap: 'anywhere' }}>
          {title}
        </Text>
      }
      styles={{
        title: { flex: 1, minWidth: 0, paddingRight: 8 },
        body: { padding: 0, height: 'calc(100dvh - 60px)' },
        header: { borderBottom: '1px solid var(--border)', minHeight: 60 },
      }}
    >
      <ScrollArea h="100%" viewportRef={viewport} type="hover" offsetScrollbars>
        <div style={{ display: 'flex', gap: 26, padding: '24px 26px 60px' }}>
          {showToc && (
            <nav className="reader-toc">
              <p>目录</p>
              {heads.map((h) => (
                <button
                  key={h.id}
                  type="button"
                  className={h.lv === 3 ? 'lv3' : undefined}
                  onClick={() => {
                    const el = docRef.current?.querySelector<HTMLElement>('#' + CSS.escape(h.id));
                    el?.scrollIntoView({ behavior: 'smooth', block: 'start' });
                  }}
                >
                  {h.text}
                </button>
              ))}
            </nav>
          )}
          <div className="reader-doc" ref={docRef}>
            {loading && <Loader size="sm" />}
            {error && <Text c="orange">{error}</Text>}
            {!loading && !error && (
              <Stack gap="md">
                {active?.path !== target?.path && (
                  <Button variant="subtle" size="compact-sm" onClick={() => setActive(target)}>
                    返回原文档
                  </Button>
                )}
                {code ? (
                  <>
                    <Group justify="space-between">
                      <Text size="sm">{code.path}</Text>
                      <Button size="compact-sm" onClick={async () => {
                        try {
                          await navigator.clipboard.writeText(code.body);
                          setCopied(true);
                          setCopyError('');
                        } catch {
                          setCopyError('复制失败，请选择代码后按 Ctrl+C。');
                        }
                      }}>{copied ? '已复制' : '复制代码'}</Button>
                    </Group>
                    {copyError && <Text size="sm" c="orange">{copyError}</Text>}
                    {code.summary && <Text size="sm">{code.summary}</Text>}
                    <Text size="sm">第三方依赖：{code.dependencies.join('、') || '无'}</Text>
                    {code.arguments.length > 0 && <Text size="sm">输入参数：{code.arguments.join(' ')}</Text>}
                    <Code block>{code.body}</Code>
                  </>
                ) : (
                  <>
                    {info?.scripts?.length ? (
                      <Group gap="xs">
                        {info.scripts.map((script) => <Button key={script.path} size="compact-sm"
                          variant="light" onClick={() => setActive(script)}>查看代码 {script.title}</Button>)}
                      </Group>
                    ) : null}
                    {info?.methods?.length ? <Group gap="xs">
                      <Text size="sm" c="dimmed">相关方法</Text>
                      {info.methods.map((method) => <Button key={method.path} size="compact-sm"
                        variant="subtle" onClick={() => setActive(method)}>{method.title}</Button>)}
                    </Group> : null}
                    {info?.sources?.length ? (
                      <Group gap="xs">
                        <Text size="sm" c="dimmed">来源</Text>
                        {info.sources.map((source) => source.external ? (
                          <Button key={source.path} component="a" href={source.path} target="_blank"
                            rel="noopener noreferrer" variant="subtle" size="compact-sm">查看来源</Button>
                        ) : <Button key={source.path} variant="subtle" size="compact-sm"
                          onClick={() => setActive(source)}>{source.path.split('/').pop()}</Button>)}
                      </Group>
                    ) : null}
                    <Md text={body} />
                  </>
                )}
              </Stack>
            )}
          </div>
        </div>
      </ScrollArea>
    </Drawer>
  );
}
