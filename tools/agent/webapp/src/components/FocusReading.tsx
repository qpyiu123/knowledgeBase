import { Button, Stack, Text, Title } from '@mantine/core';
import type { SearchResp } from '../types';
import ConditionDetails from './ConditionDetails';

export default function FocusReading({ focus, onOpenDoc }: {
  focus?: SearchResp['focus'];
  onOpenDoc: (path: string, title?: string) => void;
}) {
  if (!focus) return null;
  return <Stack gap="sm" id="focus-reading">
    <Title order={3}>当前卡点资料 · {focus.title}</Title>
    {focus.basis.filter((b) => b.missing).map((b) => <Text key={b.field} size="sm" style={{ overflowWrap: 'anywhere' }}>
      未查到完整名称：{b.text}。请核对名称或补充对应文档。
    </Text>)}
    {!focus.basis.length && <Text size="sm">先在工作区记录当前目标或待查项。</Text>}
    {!!focus.basis.length && !focus.hits.length && <Text size="sm">当前卡点没有找到相关资料，请补充具体参数或对应文档。</Text>}
    {focus.hits.map((hit) => <div key={hit.path}>
      <Button variant="subtle" size="compact-sm" onClick={() => onOpenDoc(hit.path, hit.title)}>{hit.title}</Button>
      {hit.section && <Text size="xs" c="dimmed">命中小节：{hit.section}</Text>}
      <Text size="xs" style={{ overflowWrap: 'anywhere' }}>根据：{hit.focus_basis?.map((b) => `${b.label}「${b.text.slice(0, 120)}${b.text.length > 120 ? '…' : ''}」`).join('；')}</Text>
      {hit.scripts?.map((script) => <Button key={script.path} variant="subtle" size="compact-xs"
        onClick={() => onOpenDoc(script.path, script.title)}>查看代码 {script.title || script.path}</Button>)}
      {hit.applicability?.status !== 'unsatisfied' && <ConditionDetails app={hit.applicability} onOpenDoc={onOpenDoc} />}
    </div>)}
    {!!focus.excluded.length && <details>
      <summary>条件不符的路径（{focus.excluded.length}）</summary>
      {focus.excluded.map((hit) => <div key={hit.path}>
        <Button variant="subtle" size="compact-sm" onClick={() => onOpenDoc(hit.path, hit.title)}>{hit.applicability?.guide?.title || hit.title}</Button>
        <ConditionDetails app={hit.applicability} onOpenDoc={onOpenDoc} />
      </div>)}
    </details>}
  </Stack>;
}
