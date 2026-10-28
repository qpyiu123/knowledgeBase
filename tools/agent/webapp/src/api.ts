import type { Health, SearchResp, Stats } from './types';
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
