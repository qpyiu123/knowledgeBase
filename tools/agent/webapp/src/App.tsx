import {
  ActionIcon,
  AppShell,
  Badge,
  Burger,
  Divider,
  Group,
  Kbd,
  NavLink,
  ScrollArea,
  Stack,
  Text,
  Tooltip,
  useMantineColorScheme,
} from '@mantine/core';
import { useDisclosure } from '@mantine/hooks';
import { BookOpen, FolderKanban, Moon, Search, Sun } from 'lucide-react';
import { useEffect, useState } from 'react';
import Reader, { type ReaderTarget } from './components/Reader';
import SearchPage from './pages/SearchPage';
import WorkspacePage from './pages/WorkspacePage';
import { api } from './api';
import type { Health, Stats } from './types';

type Page = 'search' | 'workspace';
type CurrentWorkspace = { id: string; title: string };

const WS_KEY = 'ctf-kb-current-workspace';

function loadWorkspace(): CurrentWorkspace {
  try {
    const raw = localStorage.getItem(WS_KEY);
    if (raw) {
      const parsed = JSON.parse(raw) as CurrentWorkspace;
      if (parsed && typeof parsed.id === 'string') return parsed;
    }
  } catch {
    // 忽略损坏的本地记录。
  }
  return { id: '', title: '' };
}

const CAT_LABEL: Record<string, string> = {
  web: 'Web',
  crypto: 'Crypto',
  pwn: 'Pwn',
  reverse: 'Reverse',
  misc: 'Misc',
  forensics: '取证',
  mobile: '移动',
  hardware: '硬件',
  osint: 'OSINT',
  ai: 'AI',
  blockchain: '区块链',
};

export default function App() {
  const [opened, { toggle, close }] = useDisclosure();
  const { colorScheme, toggleColorScheme } = useMantineColorScheme();
  const [stats, setStats] = useState<Stats | null>(null);
  const [health, setHealth] = useState<Health | null>(null);
  const [category, setCategory] = useState<string>('');
  const [reader, setReader] = useState<ReaderTarget>(null);
  const [page, setPage] = useState<Page>('search');
  const [currentWorkspace, setCurrentWorkspace] =
    useState<CurrentWorkspace>(loadWorkspace);

  const selectWorkspace = (id: string, title: string) => {
    const next = { id, title: title || id };
    setCurrentWorkspace(next);
    try {
      if (id) localStorage.setItem(WS_KEY, JSON.stringify(next));
      else localStorage.removeItem(WS_KEY);
    } catch {
      // localStorage 不可用时只保留内存状态。
    }
  };

  useEffect(() => {
    api.stats().then(setStats).catch(() => setStats(null));
    api.health().then(setHealth).catch(() => setHealth(null));
  }, []);

  // #doc=路径 直接打开阅读器
  useEffect(() => {
    const h = decodeURIComponent(location.hash.replace(/^#/, ''));
    if (h.startsWith('doc=')) {
      const p = h.slice(4);
      setReader({ path: p, title: (p.split('/').pop() || '').replace(/\.md$/i, '') });
    }
  }, []);

  const cats = Object.entries(stats?.categories || {}).sort((a, b) => b[1] - a[1]);
  const total = stats?.docs || cats.reduce((s, [, n]) => s + n, 0);

  return (
    <>
      <AppShell
        header={{ height: 64 }}
        navbar={{ width: 224, breakpoint: 'sm', collapsed: { mobile: !opened } }}
        padding={0}
      >
        <AppShell.Header>
          <Group h="100%" px="lg" justify="space-between" wrap="nowrap">
            <Group gap={12} wrap="nowrap">
              <ActionIcon hiddenFrom="sm" variant="subtle" onClick={toggle} aria-label="展开导航">
                <Burger opened={opened} size="sm" />
              </ActionIcon>
              <div className="brand-icon">
                <BookOpen size={21} />
              </div>
              <div className="brand-text">
                <b>CTF 知识库</b>
                <span>从线索找到下一步</span>
              </div>
            </Group>
            <Group gap={10} wrap="nowrap">
              <Badge
                variant="light"
                color={health?.ok ? 'brand' : 'gray'}
                leftSection={
                  <span
                    style={{
                      width: 7,
                      height: 7,
                      borderRadius: '50%',
                      background: health?.ok ? 'var(--accent)' : '#c04b4b',
                      display: 'inline-block',
                    }}
                  />
                }
                visibleFrom="xs"
                tt="none"
              >
                {health?.ok ? health.model || '模型就绪' : '模型未连接'}
                {total ? ` · ${total} 篇` : ''}
              </Badge>
              <Tooltip label="切换明暗主题">
                <ActionIcon
                  variant="default"
                  size="lg"
                  onClick={toggleColorScheme}
                  aria-label="切换明暗主题"
                >
                  {colorScheme === 'dark' ? <Sun size={17} /> : <Moon size={17} />}
                </ActionIcon>
              </Tooltip>
            </Group>
          </Group>
        </AppShell.Header>

        <AppShell.Navbar p="md">
          <Text size="xs" c="dimmed" px="sm" mb="sm" fw={700} tt="uppercase">
            页面
          </Text>
          <Stack gap={2} mb="sm">
            <NavLink
              component="button"
              active={page === 'search'}
              onClick={() => {
                setPage('search');
                close();
              }}
              leftSection={<Search size={15} />}
              label={<span style={{ fontSize: 13.5 }}>搜索与助手</span>}
            />
            <NavLink
              component="button"
              active={page === 'workspace'}
              onClick={() => {
                setPage('workspace');
                close();
              }}
              leftSection={<FolderKanban size={15} />}
              label={<span style={{ fontSize: 13.5 }}>工作区</span>}
              rightSection={
                currentWorkspace.id ? (
                  <Badge size="xs" variant="light">
                    {currentWorkspace.title || currentWorkspace.id}
                  </Badge>
                ) : undefined
              }
            />
          </Stack>
          <Divider mb="sm" />
          {page === 'search' ? (
            <>
              <Text size="xs" c="dimmed" px="sm" mb="sm" fw={700} tt="uppercase">
                方向
              </Text>
              <ScrollArea style={{ flex: 1 }} type="hover" offsetScrollbars>
                <Stack gap={2}>
                  <NavLink
                    component="button"
                    active={category === ''}
                    onClick={() => {
                      setCategory('');
                      close();
                    }}
                    label={<span style={{ fontSize: 13.5 }}>全部</span>}
                    rightSection={<span className="cat-count">{total}</span>}
                  />
                  {cats.map(([k, n]) => (
                    <NavLink
                      key={k}
                      component="button"
                      active={category === k}
                      onClick={() => {
                        setCategory(k);
                        close();
                      }}
                      label={<span style={{ fontSize: 13.5 }}>{CAT_LABEL[k] || k}</span>}
                      rightSection={<span className="cat-count">{n}</span>}
                    />
                  ))}
                </Stack>
              </ScrollArea>
            </>
          ) : (
            <div style={{ flex: 1 }} />
          )}
          <div className="sidebar-bottom">
            <Text size="xs" c="dimmed" mb={6}>
              <Kbd size="xs">Ctrl</Kbd> + <Kbd size="xs">K</Kbd> 聚焦搜索
            </Text>
            <Text size="xs" c="dimmed" mb={6}>
              <Kbd size="xs">Ctrl</Kbd> + <Kbd size="xs">Enter</Kbd> 提交
            </Text>
            <Text size="xs" c="dimmed">
              <Kbd size="xs">Esc</Kbd> 关闭阅读
            </Text>
          </div>
        </AppShell.Navbar>

        <AppShell.Main>
          <div className="page">
            {page === 'search' ? (
              <SearchPage
                category={category}
                onOpenDoc={(path, title) => setReader({ path, title })}
                docs={total}
                workspaceId={currentWorkspace.id || undefined}
                workspaceTitle={currentWorkspace.title || undefined}
                attachmentMaxBytes={health?.attachment?.max_bytes}
              />
            ) : (
              <WorkspacePage
                currentId={currentWorkspace.id}
                onSelect={selectWorkspace}
              />
            )}
          </div>
        </AppShell.Main>
      </AppShell>

      <Reader target={reader} onClose={() => setReader(null)} />
    </>
  );
}
