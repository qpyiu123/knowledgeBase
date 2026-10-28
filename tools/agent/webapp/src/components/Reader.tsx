import { Drawer, Loader, ScrollArea, Text } from '@mantine/core';
import { useEffect, useMemo, useRef, useState } from 'react';
import { api } from '../api';
import Md from './Md';

export type ReaderTarget = { path: string; title?: string } | null;

export default function Reader({
  target,
  onClose,
}: {
  target: ReaderTarget;
  onClose: () => void;
}) {
  const [body, setBody] = useState('');
  const [error, setError] = useState('');
  const [loading, setLoading] = useState(false);
  const [heads, setHeads] = useState<{ id: string; text: string; lv: number }[]>([]);
  const docRef = useRef<HTMLDivElement>(null);
  const viewport = useRef<HTMLDivElement>(null);

  useEffect(() => {
    if (!target) return;
    let alive = true;
    setLoading(true);
    setError('');
    setBody('');
    setHeads([]);
    api
      .doc(target.path)
      .then((r) => {
        if (!alive) return;
        if (r.error) {
          setError(r.error);
          return;
        }
        // 去掉 front-matter
        setBody(String(r.body || '').replace(/^---\n[\s\S]*?\n---\n/, ''));
      })
      .catch((e) => alive && setError(String(e.message || e)))
      .finally(() => alive && setLoading(false));
    return () => {
      alive = false;
    };
  }, [target]);

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
  const raw = firstH1 || target?.title || target?.path || '';
  const title = String(raw).replace(/\.md$/i, '');
  const showToc = heads.length > 1;

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
            {!loading && !error && <Md text={body} />}
          </div>
        </div>
      </ScrollArea>
    </Drawer>
  );
}
