import type {
  AttachmentReport,
  Health,
  SearchResp,
  Stats,
  TimelineEvent,
  Workspace,
  WorkspaceEntry,
  WorkspaceEntryKind,
  WorkspaceStatus,
  WorkspaceSummary,
} from './types';
import { readAskStream, type AskHandlers } from './lib/sse';

export type { AskHandlers } from './lib/sse';

async function errorMessage(r: Response): Promise<string> {
  let detail = '';
  try {
    const j = (await r.json()) as { error?: string };
    if (j && typeof j.error === 'string') detail = j.error;
  } catch {
    // 非 JSON 错误体，保留 HTTP 状态。
  }
  return detail ? `${detail}（HTTP ${r.status}）` : `HTTP ${r.status}`;
}

async function getJSON<T>(url: string, init?: RequestInit): Promise<T> {
  const r = await fetch(url, init);
  if (!r.ok) throw new Error(await errorMessage(r));
  return (await r.json()) as T;
}

function postJSON<T>(url: string, body: unknown): Promise<T> {
  return getJSON<T>(url, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(body),
  });
}

function delJSON<T>(url: string): Promise<T> {
  return getJSON<T>(url, { method: 'DELETE' });
}

const wsPath = (id: string) => '/api/workspaces/' + encodeURIComponent(id);

export const api = {
  health: () => getJSON<Health>('/api/health'),
  stats: () => getJSON<Stats>('/api/stats'),
  doc: (path: string) =>
    getJSON<{ path: string; body: string; error?: string }>(
      '/api/doc?path=' + encodeURIComponent(path),
    ),
  search: (q: string, top_k = 10, category?: string | null, doc_type?: string | null) =>
    getJSON<SearchResp>('/api/search', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        q,
        top_k,
        category: category || null,
        doc_type: doc_type || null,
      }),
    }),
  feedback: (
    query: string,
    path: string,
    verdict: 'useful' | 'useless' | 'adopted',
    note = '',
  ) =>
    getJSON<{ ok: boolean; saved: number; error?: string }>('/api/feedback', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ query, path, verdict, note }),
    }),

  /** 原始字节上传（不是 multipart），附件由后端隔离落盘后只读解析。 */
  analyze: async (
    name: string,
    data: ArrayBuffer,
    workspaceId?: string | null,
  ): Promise<AttachmentReport> => {
    const qs =
      '?name=' +
      encodeURIComponent(name) +
      (workspaceId ? '&workspace=' + encodeURIComponent(workspaceId) : '');
    const r = await fetch('/api/analyze' + qs, {
      method: 'POST',
      headers: { 'Content-Type': 'application/octet-stream' },
      body: data,
    });
    if (!r.ok) throw new Error(await errorMessage(r));
    return (await r.json()) as AttachmentReport;
  },

  workspaces: {
    list: () => getJSON<{ workspaces: WorkspaceSummary[] }>('/api/workspaces'),
    get: (id: string) => getJSON<{ workspace: Workspace }>(wsPath(id)),
    create: (title: string, id?: string, category?: string | null) =>
      postJSON<{ ok: boolean; workspace: Workspace }>('/api/workspaces', {
        title,
        id: id || undefined,
        category: category || undefined,
      }),
    update: (
      id: string,
      patch: { title?: string; status?: WorkspaceStatus; category?: string | null },
    ) =>
      postJSON<{ ok: boolean; workspace: Workspace }>(wsPath(id), patch),
    remove: (id: string) => delJSON<{ ok: boolean }>(wsPath(id)),
    addEntry: (
      id: string,
      entry: {
        kind: WorkspaceEntryKind;
        text?: string;
        result?: string;
        direction?: string;
        conclusion?: string;
        title?: string;
        path?: string;
        anchor?: string;
        url?: string;
        source?: string;
        attachment?: Record<string, unknown> | null;
        report?: AttachmentReport | null;
      },
    ) =>
      postJSON<{ ok: boolean; workspace: Workspace; entry: WorkspaceEntry }>(
        wsPath(id) + '/entries',
        entry,
      ),
    updateEntry: (
      id: string,
      entryId: string,
      patch: { result?: string; text?: string },
    ) =>
      postJSON<{ ok: boolean; workspace: Workspace; entry: WorkspaceEntry }>(
        wsPath(id) + '/entries/' + encodeURIComponent(entryId),
        patch,
      ),
    removeEntry: (id: string, entryId: string) =>
      delJSON<{ ok: boolean; workspace: Workspace }>(
        wsPath(id) + '/entries/' + encodeURIComponent(entryId),
      ),
    timeline: (id: string) =>
      getJSON<{ timeline: TimelineEvent[] }>(wsPath(id) + '/timeline'),
    exportUrl: (id: string, mode: 'normal' | 'writeup' = 'normal') =>
      wsPath(id) +
      '/export?format=md' +
      (mode === 'writeup' ? '&mode=writeup' : ''),
  },
};

/** POST /api/ask，按 SSE 契约逐段回调 tok / err / done。 */
export async function ask(
  q: string,
  paths: string[],
  handlers: AskHandlers,
  signal?: AbortSignal,
): Promise<void> {
  const r = await fetch('/api/ask', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ q, paths }),
    signal,
  });
  if (!r.ok || !r.body) throw new Error(await errorMessage(r));

  handlers.onStart?.();
  const { tokens, terminal } = await readAskStream(r.body, handlers, signal);
  if (!terminal) {
    if (tokens === 0) {
      handlers.onError?.('模型没有返回内容。确认本地模型已启动。');
    } else {
      handlers.onDone?.('完成');
    }
  }
}
