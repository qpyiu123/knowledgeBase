import {
  Accordion,
  Alert,
  Badge,
  Code,
  Group,
  List,
  Stack,
  Table,
  Text,
} from '@mantine/core';
import type { AttachmentReport } from '../types';

function bytes(n?: number | null): string {
  if (n == null) return '未知';
  if (n < 1024) return `${n} B`;
  if (n < 1024 * 1024) return `${(n / 1024).toFixed(1)} KiB`;
  return `${(n / 1024 / 1024).toFixed(2)} MiB`;
}

function SimpleList({ items, empty }: { items?: string[]; empty?: string }) {
  if (!items?.length) {
    return (
      <Text size="sm" c="dimmed">
        {empty || '无'}
      </Text>
    );
  }
  return (
    <List size="sm" spacing={4}>
      {items.map((item, i) => (
        <List.Item key={i}>
          <Text size="sm" style={{ overflowWrap: 'anywhere' }}>
            {item}
          </Text>
        </List.Item>
      ))}
    </List>
  );
}

export default function AttachmentReportView({
  report,
  compact = false,
}: {
  report: AttachmentReport;
  compact?: boolean;
}) {
  const strings = report.strings || [];
  const shownStrings = compact ? strings.slice(0, 20) : strings;
  const structures = report.structures || {};
  const hasStructures = Boolean(
    structures.png || structures.wav || structures.zip,
  );

  return (
    <Stack gap="sm">
      <Group gap={6} wrap="wrap">
        <Badge variant="light" color="brand">
          {report.type?.kind || '未知类型'}
        </Badge>
        <Badge variant="outline" color={report.type?.is_text ? 'teal' : 'gray'}>
          {report.type?.is_text ? '文本' : '二进制'}
        </Badge>
        <Badge variant="outline">{bytes(report.file?.size)}</Badge>
        {report.executed === false && (
          <Badge variant="outline" color="orange">
            未执行
          </Badge>
        )}
      </Group>

      {report.type?.extension_mismatch && (
        <Alert color="orange" title="扩展名与真实内容不符">
          扩展名 {report.type.extension || '未知'} 与检测到的
          「{report.type.kind}」不一致，文件可能被改过名。
        </Alert>
      )}
      {report.warnings?.length ? (
        <Alert color="yellow" title="安全提示">
          <Stack gap={4}>
            {report.warnings.map((w, i) => (
              <Text size="sm" key={i}>
                {w}
              </Text>
            ))}
            <Text size="xs" c="dimmed">
              {report.execution_note || '只读分析：不会运行附件中的任何内容。'}
            </Text>
          </Stack>
        </Alert>
      ) : null}

      <Accordion variant="separated" multiple defaultValue={['file', 'type']}>
        <Accordion.Item value="file">
          <Accordion.Control>文件与落盘</Accordion.Control>
          <Accordion.Panel>
            <Stack gap={4}>
              <Text size="sm">名称：{report.file?.name}</Text>
              <Text size="sm">大小：{bytes(report.file?.size)}</Text>
              <Text size="sm" style={{ overflowWrap: 'anywhere' }}>
                SHA256：<Code>{report.file?.sha256}</Code>
              </Text>
              {(report.storage?.saved || report.file?.saved) && (
                <Text size="sm" style={{ overflowWrap: 'anywhere' }}>
                  落盘路径：
                  <Code>{report.storage?.saved || report.file?.saved}</Code>
                </Text>
              )}
              {report.storage?.isolated && (
                <Text size="xs" c="dimmed">
                  已复制到隔离目录，原始上传不会被修改。
                </Text>
              )}
            </Stack>
          </Accordion.Panel>
        </Accordion.Item>

        <Accordion.Item value="type">
          <Accordion.Control>类型</Accordion.Control>
          <Accordion.Panel>
            <Stack gap={4}>
              <Text size="sm">真实类型：{report.type?.kind || '未知'}</Text>
              <Text size="sm">扩展名：{report.type?.extension || '无'}</Text>
              <Text size="sm">
                扩展名不符：{report.type?.extension_mismatch ? '是' : '否'}
              </Text>
              {report.type?.preview && (
                <Text size="sm" style={{ whiteSpace: 'pre-wrap' }}>
                  预览：{report.type.preview}
                </Text>
              )}
            </Stack>
          </Accordion.Panel>
        </Accordion.Item>

        <Accordion.Item value="carve">
          <Accordion.Control>雕刻（内嵌文件）</Accordion.Control>
          <Accordion.Panel>
            {report.carve?.length ? (
              <Table withTableBorder>
                <Table.Thead>
                  <Table.Tr>
                    <Table.Th>类型</Table.Th>
                    <Table.Th>偏移</Table.Th>
                    <Table.Th>大小</Table.Th>
                  </Table.Tr>
                </Table.Thead>
                <Table.Tbody>
                  {report.carve.map((c, i) => (
                    <Table.Tr key={i}>
                      <Table.Td>{c.type || '未知'}</Table.Td>
                      <Table.Td>
                        {c.offset_hex || (c.offset ?? '?')}
                      </Table.Td>
                      <Table.Td>{bytes(c.size)}</Table.Td>
                    </Table.Tr>
                  ))}
                </Table.Tbody>
              </Table>
            ) : (
              <Text size="sm" c="dimmed">
                未发现内嵌文件。
              </Text>
            )}
          </Accordion.Panel>
        </Accordion.Item>

        <Accordion.Item value="structures">
          <Accordion.Control>PNG / WAV / ZIP 结构</Accordion.Control>
          <Accordion.Panel>
            {!hasStructures ? (
              <Text size="sm" c="dimmed">
                没有可展示的 PNG/WAV/ZIP 结构。
              </Text>
            ) : (
              <Stack gap="sm">
                {structures.png && (
                  <div>
                    <Text size="sm" fw={600}>
                      PNG
                    </Text>
                    <Text size="sm">
                      {structures.png.width} × {structures.png.height}，chunk{' '}
                      {structures.png.chunks?.length || 0} 个
                      {structures.png.truncated ? '（已截断）' : ''}
                    </Text>
                  </div>
                )}
                {structures.wav && (
                  <div>
                    <Text size="sm" fw={600}>
                      WAV
                    </Text>
                    <Text size="sm">
                      格式 {structures.wav.format || '?'} · 声道{' '}
                      {structures.wav.channels ?? '?'} · 采样率{' '}
                      {structures.wav.sample_rate ?? '?'} · chunk{' '}
                      {structures.wav.chunks?.length || 0} 个
                    </Text>
                    {structures.wav.tail_text && (
                      <Text size="sm" style={{ overflowWrap: 'anywhere' }}>
                        尾部文本：{structures.wav.tail_text}
                      </Text>
                    )}
                  </div>
                )}
                {structures.zip && (
                  <div>
                    <Text size="sm" fw={600}>
                      ZIP
                    </Text>
                    <Text size="sm">
                      条目 {structures.zip.count ?? 0} 个
                      {structures.zip.encrypted ? ' · 含加密条目' : ''}
                      {structures.zip.truncated ? '（列表已截断）' : ''}
                    </Text>
                    {structures.zip.entries?.length ? (
                      <List size="sm" spacing={2}>
                        {structures.zip.entries.map((e, i) => (
                          <List.Item key={i}>
                            {e.name}（{bytes(e.size)}
                            {e.encrypted ? ' · 加密' : ''}）
                          </List.Item>
                        ))}
                      </List>
                    ) : null}
                  </div>
                )}
              </Stack>
            )}
          </Accordion.Panel>
        </Accordion.Item>

        <Accordion.Item value="anomalies">
          <Accordion.Control>异常</Accordion.Control>
          <Accordion.Panel>
            <SimpleList items={report.anomalies} empty="未发现结构异常。" />
          </Accordion.Panel>
        </Accordion.Item>

        <Accordion.Item value="decoded">
          <Accordion.Control>base64 / hex / URL 解码</Accordion.Control>
          <Accordion.Panel>
            {report.decoded?.length ? (
              <Stack gap={6}>
                {report.decoded.map((d, i) => (
                  <div key={i}>
                    <Badge size="xs" variant="outline">
                      {d.method}
                    </Badge>
                    <Text size="sm" style={{ whiteSpace: 'pre-wrap' }}>
                      {d.decoded}
                      {d.truncated ? '…' : ''}
                    </Text>
                  </div>
                ))}
              </Stack>
            ) : (
              <Text size="sm" c="dimmed">
                没有通过严格过滤的可信解码结果。
              </Text>
            )}
          </Accordion.Panel>
        </Accordion.Item>

        <Accordion.Item value="strings">
          <Accordion.Control>
            关键字符串（{strings.length}）
          </Accordion.Control>
          <Accordion.Panel>
            {shownStrings.length ? (
              <Stack gap={2}>
                {shownStrings.map((s, i) => (
                  <Text
                    size="xs"
                    key={i}
                    style={{
                      fontFamily: 'var(--mantine-font-family-monospace)',
                      overflowWrap: 'anywhere',
                    }}
                  >
                    {s}
                  </Text>
                ))}
                {compact && strings.length > shownStrings.length && (
                  <Text size="xs" c="dimmed">
                    仅显示前 {shownStrings.length} 条，完整内容见导出的工作区。
                  </Text>
                )}
              </Stack>
            ) : (
              <Text size="sm" c="dimmed">
                没有提取到关键字符串。
              </Text>
            )}
          </Accordion.Panel>
        </Accordion.Item>
      </Accordion>
    </Stack>
  );
}
