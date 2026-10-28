import type { Health, SearchResp, Stats } from './types';

async function getJSON<T>(url: string, init?: RequestInit): Promise<T> {
  const r = await fetch(url, init);
  if (!r.ok) throw new Error(`HTTP ${r.status}`);
  return (await r.json()) as T;
}

export const api = {
  health: () => getJSON<Health>('/api/health'),
  stats: () => getJSON<Stats>('/api/stats'),
  doc: (path: string) =>
    getJSON<{ path: string; body: string; error?: string }>(
      '/api/doc?path=' + encodeURIComponent(path),
    ),
  search: (q: string, top_k = 10, category?: string | null) =>
    getJSON<SearchResp>('/api/search', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ q, top_k, category: category || null }),
    }),
};

export type AskHandlers = {
  onStart?: () => void;
  onToken: (text: string) => void;
  onError?: (message: string) => void;
};

/** POST /api/ask，按 SSE 逐段回调。 */
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
  if (!r.ok || !r.body) throw new Error(`HTTP ${r.status}`);

  handlers.onStart?.();
  const reader = r.body.getReader();
  const dec = new TextDecoder();
  let buf = '';

  for (;;) {
    const { done, value } = await reader.read();
    if (done) break;
    buf += dec.decode(value, { stream: true });
    let nl: number;
    while ((nl = buf.indexOf('\n\n')) >= 0) {
      const chunk = buf.slice(0, nl);
      buf = buf.slice(nl + 2);
      for (const line of chunk.split('\n')) {
        if (!line.startsWith('data: ')) continue;
        let ev: { t?: string; v?: string; err?: string };
        try {
          ev = JSON.parse(line.slice(6));
        } catch {
          continue;
        }
        if (ev.t === 'tok' && typeof ev.v === 'string') handlers.onToken(ev.v);
        else if (ev.err) handlers.onError?.(ev.err);
      }
    }
  }
}
