import { Button, Stack, Text } from '@mantine/core';
import type { Applicability } from '../types';
import { slugify } from './Md';

export default function ConditionDetails({ app, onOpenDoc }: {
  app?: Applicability;
  onOpenDoc: (path: string, title?: string) => void;
}) {
  if (app?.error) return <Text size="sm" c="orange">{app.error}</Text>;
  if (!app || (!app.conditions?.length && !app.reading?.length)) return null;
  const guide = app.guide;
  return (
    <details>
      <summary>条件与下一步{app.conditions?.length ? ` · ${app.status_label}` : ''}</summary>
      <Stack gap="xs" mt="xs">
        {guide && <Text size="sm" fw={600}>{guide.title}</Text>}
        {app.conditions?.map((c) => <div key={c.id}>
          <Text size="sm" fw={500}>{c.status_label}：{c.label}</Text>
          <Text size="xs" style={{ overflowWrap: 'anywhere' }}>{c.evidence}</Text>
          {c.check && <Text size="xs" c="dimmed">核对：{c.check}</Text>}
        </div>)}
        {guide && <>
          <Text size="xs">依据：{guide.source.quote}</Text>
          <Button variant="subtle" size="compact-xs" style={{ alignSelf: 'flex-start' }}
            onClick={() => onOpenDoc(`${guide.source.path}#${slugify(guide.source.section)}`, guide.source.section)}>
            查看依据：{guide.source.section}
          </Button>
          {app.status !== 'unsatisfied' && <Text size="sm">
            {app.status === 'known' ? '下一步检查：' : '条件确认后：'}{guide.next_check}
          </Text>}
          <Text size="sm" fw={500}>相近方法怎么区分</Text>
          {guide.contrasts.map((c) => <div key={c.path}>
            <Text size="xs">{c.difference}</Text>
            <Button variant="subtle" size="compact-xs" onClick={() => onOpenDoc(c.path, c.title)}>{c.title}</Button>
          </div>)}
        </>}
        {!!app.reading?.length && <>
          <Text size="sm" fw={500}>阅读依赖</Text>
          {app.reading.map((r) => r.path ? <Button key={r.path} variant="subtle" size="compact-xs"
            style={{ alignSelf: 'flex-start' }} onClick={() => onOpenDoc(r.path!, r.title)}>
            {r.title}{r.present ? '（本次已查到）' : ''}
          </Button> : <Text key={r.title} size="xs">{r.title}（资料缺失）</Text>)}
        </>}
      </Stack>
    </details>
  );
}
